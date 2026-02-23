#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path


VERSION_RE = re.compile(r'(?m)^(\s*version\s*=\s*")(\d+)\.(\d+)\.(\d+)(".*)$')


def bump(text: str, part: str) -> tuple[str, str]:
    match = VERSION_RE.search(text)
    if not match:
        raise ValueError('version = "x.y.z" not found')

    major = int(match.group(2))
    minor = int(match.group(3))
    patch = int(match.group(4))

    if part == "patch":
        patch += 1
    elif part == "minor":
        minor += 1
        patch = 0
    elif part == "major":
        major += 1
        minor = 0
        patch = 0
    else:
        raise ValueError(f"unsupported part: {part}")

    next_version = f"{major}.{minor}.{patch}"
    replacement = f'{match.group(1)}{next_version}{match.group(5)}'
    return VERSION_RE.sub(replacement, text, count=1), next_version


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bump semantic version in pyproject.toml."
    )
    parser.add_argument("--file", default="pyproject.toml", help="Target TOML file")
    parser.add_argument(
        "--part",
        choices=("patch", "minor", "major"),
        default="patch",
        help="Version part to bump",
    )
    args = parser.parse_args()

    target = Path(args.file)
    if not target.exists():
        print(f"Error: file not found: {target}", file=sys.stderr)
        return 1

    content = target.read_text(encoding="utf-8")
    try:
        updated, version = bump(content, args.part)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    target.write_text(updated, encoding="utf-8")
    print(f"Bumped {target} to {version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
