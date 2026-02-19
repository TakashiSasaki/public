import re
import sys
from pathlib import Path

def bump_version(part='patch'):
    pyproject_path = Path("pyproject.toml")
    if not pyproject_path.exists():
        print("Error: pyproject.toml not found")
        sys.exit(1)

    content = pyproject_path.read_text(encoding="utf-8")
    
    # Regex to find version = "x.y.z"
    # Handling potential spaces around = and "
    version_pattern = r'version\s*=\s*\"(\d+)\.(\d+)\.(\d+)\"'
    
    match = re.search(version_pattern, content)
    if not match:
        print("Error: version not found in pyproject.toml")
        sys.exit(1)
    
    major, minor, patch = map(int, match.groups())
    
    if part == 'patch':
        patch += 1
    elif part == 'minor':
        minor += 1
        patch = 0
    elif part == 'major':
        major += 1
        minor = 0
        patch = 0
        
    new_version = f"{major}.{minor}.{patch}"
    new_content = re.sub(version_pattern, f'version = "{new_version}"', content)
    
    pyproject_path.write_text(new_content, encoding="utf-8")
    print(f"Bumped version to {new_version}")

if __name__ == "__main__":
    bump_version()
