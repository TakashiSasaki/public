"""CLI output for platform directory information."""

import sys
from pathlib import Path
import argparse

from get_a_grip.core.inspect_platform_dirs import get_dir_data

try:
    from platformdirs import PlatformDirs
except ImportError:
    PlatformDirs = None


def run_cli(app_name: str, app_author: str):
    """コンソールにディレクトリ情報を表示します。"""
    data = get_dir_data(app_name, app_author)

    print(f"--- platformdirs information for '{app_name}' (Author: '{app_author}') ---")
    print(f"OS Platform: {sys.platform}")
    print("-" * 70)

    for dtype, path in data:
        print(f"{dtype:15}: {path}")

    print("-" * 70)

    # 実用例: pathlib との組み合わせ
    if PlatformDirs:
        dirs = PlatformDirs(app_name, appauthor=None, roaming=True)
        config_dir = Path(dirs.user_config_dir)
        print("[Pathlib Integration Example]")
        print(f"  Potential config file: {config_dir / 'settings.json'}")
        print(f"  Directory exists?      {config_dir.exists()}")


def main():
    parser = argparse.ArgumentParser(description="Inspect platform directories.")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode (default).")
    parser.add_argument("--gui", action="store_true", help="Open GUI viewer.")
    args = parser.parse_args()

    app_name = "get-a-grip"
    app_author = None

    if args.gui:
        from get_a_grip.gui.platform_dirs_viewer import main as gui_main
        gui_main()
    else:
        run_cli(app_name, app_author)


if __name__ == "__main__":
    main()
