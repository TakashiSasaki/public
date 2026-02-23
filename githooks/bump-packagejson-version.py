#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path


SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def next_version(version: str, part: str) -> str:
    match = SEMVER_RE.match(version)
    if not match:
        raise ValueError(f"unsupported version format: {version}")

    major = int(match.group(1))
    minor = int(match.group(2))
    patch = int(match.group(3))

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

    return f"{major}.{minor}.{patch}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bump semantic version in package.json."
    )
    parser.add_argument("--file", default="package.json", help="Target package.json")
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

    data = json.loads(target.read_text(encoding="utf-8"))
    current = data.get("version")
    if not isinstance(current, str):
        print(f'Error: "version" is missing in {target}', file=sys.stderr)
        return 1

    try:
        bumped = next_version(current, args.part)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    data["version"] = bumped
    target.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Bumped {target}: {current} -> {bumped}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
