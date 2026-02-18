"""Core logic for inspecting platform directories using platformdirs."""

import sys

try:
    from platformdirs import PlatformDirs
except ImportError:
    print("Error: 'platformdirs' library is not installed.")
    print("Please install it using: pip install platformdirs")
    sys.exit(1)


def get_dir_data(app_name: str = "get-a-grip", app_author: str | None = None) -> list[tuple[str, str]]:
    """
    platformdirs から各種ディレクトリ情報を取得し、リスト形式で返します。

    Returns:
        list of (directory_type, path) tuples.
    """
    dirs = PlatformDirs(app_name, appauthor=False if app_author is None else app_author, roaming=True)

    data = [
        ("User Data", dirs.user_data_dir),
        ("User Config", dirs.user_config_dir),
        ("User Cache", dirs.user_cache_dir),
        ("User State", dirs.user_state_dir),
        ("User Log", dirs.user_log_dir),
        ("User Documents", dirs.user_documents_dir),
        ("User Runtime", dirs.user_runtime_dir),
        ("Site Data", dirs.site_data_dir),
        ("Site Config", dirs.site_config_dir),
        ("Site Cache", dirs.site_cache_dir),
    ]
    return data
