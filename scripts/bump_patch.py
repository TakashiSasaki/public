from __future__ import annotations

from pathlib import Path
import re
import sys


def bump_patch(version: str) -> str:
    parts = version.split(".")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError(f"unsupported version format: {version}")
    major, minor, patch = (int(x) for x in parts)
    return f"{major}.{minor}.{patch + 1}"


def main() -> int:
    pyproject = Path("pyproject.toml")
    text = pyproject.read_text(encoding="utf-8")

    match = re.search(r'^version\s*=\s*"([^"]+)"\s*$', text, flags=re.MULTILINE)
    if not match:
        print("version field not found in pyproject.toml", file=sys.stderr)
        return 1

    current = match.group(1)
    next_version = bump_patch(current)
    updated = text[: match.start(1)] + next_version + text[match.end(1) :]
    pyproject.write_text(updated, encoding="utf-8")

    init_py = Path("src/my_mdns/__init__.py")
    init_text = init_py.read_text(encoding="utf-8")
    init_updated = re.sub(
        r'__version__\s*=\s*"[^"]+"',
        f'__version__ = "{next_version}"',
        init_text,
        count=1,
    )
    init_py.write_text(init_updated, encoding="utf-8")

    print(f"version bumped: {current} -> {next_version}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
