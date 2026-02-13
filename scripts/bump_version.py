import re
import os

def bump_version():
    pyproject_path = "pyproject.toml"
    if not os.path.exists(pyproject_path):
        print(f"Error: {pyproject_path} not found.")
        return False

    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Look for version = "x.y.z" under [project]
    # This regex is simple but effective for standard pyproject.toml
    match = re.search(r'(^version\s*=\s*")(\d+\.\d+\.)(\d+)(")', content, re.MULTILINE)
    if not match:
        print("Error: Could not find version string in pyproject.toml")
        return False

    prefix, base, patch, suffix = match.groups()
    new_patch = int(patch) + 1
    new_version = f"{base}{new_patch}"
    
    new_content = content[:match.start()] + f'{prefix}{new_version}{suffix}' + content[match.end():]
    
    with open(pyproject_path, "w", encoding="utf-8", newline='\n') as f:
        f.write(new_content)
    
    print(f"Bumped version: {base}{patch} -> {new_version}")
    return True

if __name__ == "__main__":
    if bump_version():
        exit(0)
    else:
        exit(1)
