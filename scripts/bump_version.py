import re
import sys
from pathlib import Path

def bump_patch_version():
    target_file = Path("pyproject.toml")
    
    if not target_file.exists():
        print("Error: pyproject.toml not found.", file=sys.stderr)
        sys.exit(1)
        
    content = target_file.read_text(encoding="utf-8")
    
    # version = "x.y.z" の形式にマッチする正規表現
    # 例: version = "0.1.0"
    version_pattern = re.compile(r'^(version\s*=\s*")(\d+)\.(\d+)\.(\d+)(".*)$', re.MULTILINE)
    
    match = version_pattern.search(content)
    if not match:
        print("Error: Could not find version string in pyproject.toml", file=sys.stderr)
        sys.exit(1)
        
    prefix = match.group(1)
    major = int(match.group(2))
    minor = int(match.group(3))
    patch = int(match.group(4))
    suffix = match.group(5)
    
    # パッチバージョンをインクリメント
    new_patch = patch + 1
    new_version_string = f"{prefix}{major}.{minor}.{new_patch}{suffix}"
    
    print(f"Bumping version: {major}.{minor}.{patch} -> {major}.{minor}.{new_patch}")
    
    # 内容の置換
    new_content = content[:match.start()] + new_version_string + content[match.end():]
    
    # ファイルへ書き戻し
    target_file.write_text(new_content, encoding="utf-8")

if __name__ == "__main__":
    bump_patch_version()
