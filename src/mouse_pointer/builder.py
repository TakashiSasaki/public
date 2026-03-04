import PyInstaller.__main__
import sys
import os
from pathlib import Path

def main():
    """
    Builds the Mouse Pointer Generator as a standalone executable.
    """
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)

    # Path to assets
    assets_json = Path("pictogram/src/assets/pictograms.json")
    if not assets_json.exists():
        print(f"Error: {assets_json} not found. Make sure the pictogram submodule is initialized.")
        sys.exit(1)

    # Build command arguments
    args = [
        'src/mouse_pointer/cli.py',  # Entry point
        '--name', 'MousePointerGenerator',
        '--onefile',
        '--windowed',
        '--noconfirm',
        '--clean',
        '--add-data', f"{assets_json};assets",
    ]

    print(f"Building executable with arguments: {' '.join(args)}")
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    main()
