import json
import tomllib
from pathlib import Path

def sync_versions():
    root_dir = Path(__file__).parent.parent
    pyproject_path = root_dir / "pyproject.toml"
    package_json_path = root_dir / "gallery-app" / "package.json"

    if not pyproject_path.exists():
        print(f"Error: {pyproject_path} not found.")
        return

    if not package_json_path.exists():
        print(f"Warning: {package_json_path} not found. Skipping synchronization.")
        return

    # Read version from pyproject.toml
    with open(pyproject_path, "rb") as f:
        pyproject_data = tomllib.load(f)
    
    version = pyproject_data.get("project", {}).get("version")
    if not version:
        # Fallback for poetry style
        version = pyproject_data.get("tool", {}).get("poetry", {}).get("version")

    if not version:
        print("Error: Could not find version in pyproject.toml")
        return

    # Read package.json
    with open(package_json_path, "r", encoding="utf-8") as f:
        package_data = json.load(f)

    # Update version if different
    if package_data.get("version") != version:
        print(f"Syncing version: {package_data.get('version')} -> {version}")
        package_data["version"] = version
        with open(package_json_path, "w", encoding="utf-8") as f:
            json.dump(package_data, f, indent=2)
            f.write("\n")
        print("Successfully updated gallery-app/package.json")
    else:
        print(f"Versions are already in sync ({version})")

if __name__ == "__main__":
    sync_versions()
