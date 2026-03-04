import PyInstaller.__main__
import sys
import os
import tomllib
from pathlib import Path

def get_version(project_root: Path) -> str:
    """Reads the version from pyproject.toml."""
    pyproject_path = project_root / "pyproject.toml"
    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)
    return data.get("project", {}).get("version", "unknown")

def main():
    """
    Builds the Mouse Pointer Generator as a standalone executable with version in filename.
    """
    project_root = Path(__file__).parent.parent.parent
    os.chdir(project_root)

    version = get_version(project_root)
    exe_name = f"MousePointerGenerator_v{version}"

    # Path to assets
    assets_json = Path("pictogram/src/assets/pictograms.json")
    if not assets_json.exists():
        print(f"Error: {assets_json} not found. Make sure the pictogram submodule is initialized.")
        sys.exit(1)

    # Build command arguments
    args = [
        'src/mouse_pointer/cli.py',  # Entry point
        '--name', exe_name,
        '--onefile',
        '--windowed',
        '--noconfirm',
        '--clean',
        '--add-data', f"{assets_json};assets",
    ]

    print(f"Building executable: {exe_name}.exe")
    print(f"Building with arguments: {' '.join(args)}")
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    main()
