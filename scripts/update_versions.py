import re
import sys
import json
from pathlib import Path

def update_versions():
    root_dir = Path(__file__).parent.parent
    pyproject_path = root_dir / "pyproject.toml"
    package_json_path = root_dir / "pictogram" / "package.json"

    if not pyproject_path.exists():
        print("Error: pyproject.toml not found.", file=sys.stderr)
        sys.exit(1)

    # 1. Bump pyproject.toml version
    content = pyproject_path.read_text(encoding="utf-8")
    version_pattern = re.compile(r'^(version\s*=\s*")(\d+)\.(\d+)\.(\d+)(".*)$', re.MULTILINE)
    match = version_pattern.search(content)
    if not match:
        print("Error: Could not find version string in pyproject.toml", file=sys.stderr)
        sys.exit(1)

    prefix, major, minor, patch, suffix = match.groups()
    new_patch = int(patch) + 1
    new_version = f"{major}.{minor}.{new_patch}"
    new_version_string = f'{prefix}{new_version}{suffix}'
    
    print(f"Bumping pyproject.toml: {major}.{minor}.{patch} -> {new_version}")
    
    new_content = content[:match.start()] + new_version_string + content[match.end():]
    pyproject_path.write_text(new_content, encoding="utf-8")

    # 2. Sync to package.json
    if not package_json_path.exists():
        print(f"Warning: {package_json_path} not found. Skipping sync.")
        return

    with open(package_json_path, "r", encoding="utf-8") as f:
        package_data = json.load(f)

    old_package_version = package_data.get("version")
    if old_package_version != new_version:
        print(f"Syncing package.json: {old_package_version} -> {new_version}")
        package_data["version"] = new_version
        with open(package_json_path, "w", encoding="utf-8") as f:
            json.dump(package_data, f, indent=2)
            f.write("\n")
    else:
        print(f"package.json is already at version {new_version}")

if __name__ == "__main__":
    update_versions()
