import re
import sys
from pathlib import Path

def bump_version():
    pyproject_path = Path(__file__).parent.parent / "pyproject.toml"

    if not pyproject_path.exists():
        print("Error: pyproject.toml not found.", file=sys.stderr)
        sys.exit(1)

    content = pyproject_path.read_text(encoding="utf-8")
    version_pattern = re.compile(r'^(version\s*=\s*")(\d+)\.(\d+)\.(\d+)(".*)$', re.MULTILINE)
    match = version_pattern.search(content)
    if not match:
        print("Error: Could not find version string in pyproject.toml", file=sys.stderr)
        sys.exit(1)

    prefix, major, minor, patch, suffix = match.groups()
    new_patch = int(patch) + 1
    new_version = f"{major}.{minor}.{new_patch}"
    print(f"Bumping version: {major}.{minor}.{patch} -> {new_version}")

    new_content = content[:match.start()] + f'{prefix}{new_version}{suffix}' + content[match.end():]
    pyproject_path.write_text(new_content, encoding="utf-8")

if __name__ == "__main__":
    bump_version()
