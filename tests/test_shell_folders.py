"""Unit tests for get_a_grip.core.shell_folders."""

import os
import sys
import pytest
from unittest.mock import patch, MagicMock

# Skip entire module on non-Windows
pytestmark = pytest.mark.skipif(sys.platform != "win32", reason="Windows-only tests")

from get_a_grip.core.shell_folders import get_shell_folders


class TestGetShellFolders:
    """Tests for the get_shell_folders function."""

    def test_returns_list_of_tuples(self):
        """get_shell_folders should return a list of (name, path) tuples."""
        result = get_shell_folders()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple)
            assert len(item) == 2

    def test_tuples_contain_strings(self):
        """Each tuple should contain two strings."""
        result = get_shell_folders()
        for name, path in result:
            assert isinstance(name, str)
            assert isinstance(path, str)

    def test_not_empty(self):
        """At least some shell folders should be found on any Windows system."""
        result = get_shell_folders()
        assert len(result) > 0

    def test_contains_well_known_folders(self):
        """Well-known folders like Desktop and Personal should be present."""
        result = get_shell_folders()
        names = [name for name, _ in result]
        assert "Desktop" in names
        assert "Personal" in names

    def test_results_are_sorted(self):
        """Results should be sorted alphabetically by name (case-insensitive)."""
        result = get_shell_folders()
        names = [name for name, _ in result]
        assert names == sorted(names, key=str.lower)

    def test_no_warning_entries(self):
        """Registry warning entries (names starting with '!') should be filtered out."""
        result = get_shell_folders()
        names = [name for name, _ in result]
        for name in names:
            assert not name.startswith("!"), f"Warning entry found: {name}"

    def test_paths_are_expanded(self):
        """Paths should not contain unexpanded environment variables like %USERPROFILE%."""
        result = get_shell_folders()
        for name, path in result:
            assert "%" not in path, f"Unexpanded variable in {name}: {path}"

    def test_desktop_path_exists(self):
        """The Desktop folder path should actually exist on the filesystem."""
        result = get_shell_folders()
        desktop_entries = [(n, p) for n, p in result if n == "Desktop"]
        assert len(desktop_entries) == 1
        _, desktop_path = desktop_entries[0]
        assert os.path.exists(desktop_path), f"Desktop path does not exist: {desktop_path}"

    @patch("get_a_grip.core.shell_folders.winreg")
    def test_handles_registry_error_gracefully(self, mock_winreg):
        """If the registry keys cannot be opened, return an empty list."""
        mock_winreg.HKEY_CURRENT_USER = 0x80000001
        mock_winreg.OpenKey.side_effect = OSError("Registry key not found")
        result = get_shell_folders()
        assert result == []

    @patch("get_a_grip.core.shell_folders.winreg")
    def test_skips_non_string_values(self, mock_winreg):
        """Non-string registry values should be skipped."""
        mock_winreg.HKEY_CURRENT_USER = 0x80000001
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value.__enter__ = MagicMock(return_value=mock_key)
        mock_winreg.OpenKey.return_value.__exit__ = MagicMock(return_value=False)

        # The function iterates over two registry keys, so we need side_effects for both
        mock_winreg.EnumValue.side_effect = [
            ("SomeKey", 12345, 4),  # REG_DWORD, not a string
            OSError("No more values"),
            OSError("No more values"),  # Second registry key
        ]
        result = get_shell_folders()
        assert result == []

    @patch("get_a_grip.core.shell_folders.winreg")
    def test_skips_empty_string_values(self, mock_winreg):
        """Empty string values should be skipped."""
        mock_winreg.HKEY_CURRENT_USER = 0x80000001
        mock_key = MagicMock()
        mock_winreg.OpenKey.return_value.__enter__ = MagicMock(return_value=mock_key)
        mock_winreg.OpenKey.return_value.__exit__ = MagicMock(return_value=False)

        mock_winreg.EnumValue.side_effect = [
            ("EmptyFolder", "", 1),
            OSError("No more values"),
            OSError("No more values"),  # Second registry key
        ]
        result = get_shell_folders()
        assert result == []
