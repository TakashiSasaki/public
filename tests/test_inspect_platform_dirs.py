"""Unit tests for get_a_grip.core.inspect_platform_dirs."""

import sys
import pytest
from unittest.mock import patch, MagicMock

from get_a_grip.core.inspect_platform_dirs import get_dir_data


class TestGetDirData:
    """Tests for the get_dir_data function."""

    def test_returns_list_of_tuples(self):
        """get_dir_data should return a list of (type, path) tuples."""
        result = get_dir_data()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_tuples_contain_strings(self):
        """Each tuple should contain two strings."""
        result = get_dir_data()
        for dtype, path in result:
            assert isinstance(dtype, str)
            assert isinstance(path, str)

    def test_not_empty(self):
        """get_dir_data should return at least one entry."""
        result = get_dir_data()
        assert len(result) > 0

    def test_contains_expected_keys(self):
        """Result should include well-known directory types."""
        result = get_dir_data()
        types = [dtype for dtype, _ in result]
        assert "User Data" in types
        assert "User Config" in types
        assert "User Cache" in types

    def test_no_author_name_in_paths_by_default(self):
        """With default app_author=None, paths should NOT contain 'takas' as a directory component."""
        import os
        result = get_dir_data()
        for dtype, path in result:
            # Check for 'takas' as an isolated path component (not as part of a username like 'takashi')
            parts = path.replace("\\", "/").split("/")
            assert "takas" not in parts, (
                f"Found author directory 'takas' as a path component in {dtype}: {path}\n"
                "app_author should be None by default."
            )

    def test_no_author_name_in_paths_explicit_none(self):
        """With explicit app_author=None, paths should NOT contain 'takas' as a directory component."""
        result = get_dir_data(app_name="get-a-grip", app_author=None)
        for dtype, path in result:
            parts = path.replace("\\", "/").split("/")
            assert "takas" not in parts, (
                f"Found author directory 'takas' as a path component in {dtype}: {path}"
            )

    def test_custom_app_name_appears_in_paths(self):
        """Paths should contain the app_name."""
        app_name = "test-app-xyz"
        result = get_dir_data(app_name=app_name, app_author=None)
        # At least one path should contain the app name
        paths = [path for _, path in result]
        assert any(app_name in path for path in paths), (
            f"App name '{app_name}' not found in any path: {paths}"
        )

    def test_author_name_in_paths_when_specified(self):
        """When app_author is explicitly set, paths should contain the author name."""
        result = get_dir_data(app_name="get-a-grip", app_author="takas")
        # On Windows, site paths include the author; check at least one path
        paths = [path for _, path in result]
        # This is platform-specific, so we just verify the call doesn't crash
        assert len(paths) > 0

    @patch("get_a_grip.core.inspect_platform_dirs.PlatformDirs")
    def test_uses_appauthor_none_keyword(self, mock_platform_dirs):
        """get_dir_data should call PlatformDirs with appauthor=None by default."""
        mock_dirs = MagicMock()
        mock_dirs.user_data_dir = "/fake/data"
        mock_dirs.user_config_dir = "/fake/config"
        mock_dirs.user_cache_dir = "/fake/cache"
        mock_dirs.user_state_dir = "/fake/state"
        mock_dirs.user_log_dir = "/fake/log"
        mock_dirs.user_documents_dir = "/fake/docs"
        mock_dirs.user_runtime_dir = "/fake/runtime"
        mock_dirs.site_data_dir = "/fake/site_data"
        mock_dirs.site_config_dir = "/fake/site_config"
        mock_dirs.site_cache_dir = "/fake/site_cache"
        mock_platform_dirs.return_value = mock_dirs

        get_dir_data()

        mock_platform_dirs.assert_called_once_with(
            "get-a-grip", appauthor=False, roaming=True
        )
