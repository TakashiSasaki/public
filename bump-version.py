#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")
PYPROJECT_RE = re.compile(r'(?m)^(\s*version\s*=\s*")(\d+)\.(\d+)\.(\d+)(".*)$')
JSON_VERSION_RE = re.compile(r'("version"\s*:\s*")(\d+)\.(\d+)\.(\d+)(")')

SKIP_DIRS = {
    ".git",
    ".venv",
    ".tox",
    ".mypy_cache",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "target",
    "vendor",
}
ALLOWED_TYPES = {"pyproject", "packagejson", "manifest"}


@dataclass(frozen=True)
class BumpResult:
    path: Path
    previous: str
    current: str


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


def bump_pyproject(path: Path, part: str) -> BumpResult | None:
    with open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    match = PYPROJECT_RE.search(text)
    if not match:
        return None

    previous = f"{match.group(2)}.{match.group(3)}.{match.group(4)}"
    current = next_version(previous, part)
    replacement = f'{match.group(1)}{current}{match.group(5)}'
    updated = PYPROJECT_RE.sub(replacement, text, count=1)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(updated)
    return BumpResult(path=path, previous=previous, current=current)


def bump_json_version(path: Path, part: str) -> BumpResult | None:
    with open(path, "r", encoding="utf-8", newline="") as f:
        text = f.read()
    match = JSON_VERSION_RE.search(text)
    if not match:
        return None

    previous = f"{match.group(2)}.{match.group(3)}.{match.group(4)}"
    current = next_version(previous, part)
    replacement = f'{match.group(1)}{current}{match.group(5)}'
    updated = JSON_VERSION_RE.sub(replacement, text, count=1)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(updated)
    return BumpResult(path=path, previous=previous, current=current)


def parse_paths(raw: str) -> list[str]:
    if not raw.strip():
        return []
    return [item for item in re.split(r"[,\s;]+", raw.strip()) if item]


def discover_targets(root: Path, types: set[str]) -> dict[str, list[Path]]:
    targets: dict[str, list[Path]] = {key: [] for key in ("pyproject", "packagejson", "manifest")}
    for dirpath, dirnames, filenames in os.walk(root):
        current = Path(dirpath)
        dirnames[:] = [name for name in dirnames if name not in SKIP_DIRS]

        if current != root and (current / ".git").exists():
            dirnames[:] = []
            continue

        for filename in filenames:
            if "pyproject" in types and filename == "pyproject.toml":
                targets["pyproject"].append(current / filename)
            elif "packagejson" in types and filename == "package.json":
                targets["packagejson"].append(current / filename)
            elif "manifest" in types and filename == "manifest.webmanifest":
                targets["manifest"].append(current / filename)
    return targets


def unique_existing(paths: Iterable[Path]) -> list[Path]:
    unique: dict[str, Path] = {}
    for path in paths:
        resolved = str(path.resolve())
        if resolved in unique:
            continue
        if path.exists() and path.is_file():
            unique[resolved] = path
    return list(unique.values())


def git_repo_root(start: Path) -> Path:
    result = subprocess.run(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        check=True,
        text=True,
        capture_output=True,
    )
    return Path(result.stdout.strip())


def stage_files(root: Path, paths: list[Path]) -> None:
    if not paths:
        return
    rel = [str(path.relative_to(root)) for path in paths]
    subprocess.run(["git", "-C", str(root), "add", "--", *rel], check=True)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Bump semantic versions for pyproject.toml, package.json, and manifest.webmanifest."
    )
    parser.add_argument("--part", choices=("patch", "minor", "major"), default="patch")
    parser.add_argument(
        "--type",
        action="append",
        choices=("pyproject", "packagejson", "manifest"),
        help="Target type. Can be specified multiple times. Default: all types.",
    )
    parser.add_argument("--pyproject-path", action="append", default=[])
    parser.add_argument("--package-json-path", action="append", default=[])
    parser.add_argument("--manifest-path", action="append", default=[])
    parser.add_argument("--no-discover", action="store_true", help="Disable auto discovery.")
    parser.add_argument("--stage", action="store_true", help="Run git add for changed files.")
    args = parser.parse_args()

    try:
        root = git_repo_root(Path.cwd())
    except subprocess.CalledProcessError:
        print("error: not inside a git repository", file=sys.stderr)
        return 1

    env_types = parse_paths(os.getenv("BUMP_TYPES", ""))
    types = set(args.type or env_types or ["pyproject", "packagejson", "manifest"])
    invalid_types = sorted(t for t in types if t not in ALLOWED_TYPES)
    if invalid_types:
        print(f"error: unsupported type(s): {', '.join(invalid_types)}", file=sys.stderr)
        return 1
    targets: dict[str, list[Path]] = {key: [] for key in ("pyproject", "packagejson", "manifest")}

    pyproject_paths = args.pyproject_path + parse_paths(os.getenv("BUMP_PYPROJECT_PATHS", ""))
    package_json_paths = args.package_json_path + parse_paths(os.getenv("BUMP_PACKAGE_JSON_PATHS", ""))
    manifest_paths = args.manifest_path + parse_paths(os.getenv("BUMP_MANIFEST_PATHS", ""))

    targets["pyproject"].extend(root / path for path in pyproject_paths)
    targets["packagejson"].extend(root / path for path in package_json_paths)
    targets["manifest"].extend(root / path for path in manifest_paths)

    if not args.no_discover:
        discovered = discover_targets(root, types)
        for key in targets:
            targets[key].extend(discovered[key])

    changed: list[BumpResult] = []
    failures: list[str] = []

    for path in unique_existing(targets["pyproject"]):
        try:
            result = bump_pyproject(path, args.part)
            if result is None:
                failures.append(f"{path.relative_to(root)}: version field not found")
            else:
                changed.append(result)
        except ValueError as exc:
            failures.append(f"{path.relative_to(root)}: {exc}")

    for path in unique_existing(targets["packagejson"]):
        try:
            result = bump_json_version(path, args.part)
            if result is None:
                failures.append(f"{path.relative_to(root)}: version field not found")
            else:
                changed.append(result)
        except ValueError as exc:
            failures.append(f"{path.relative_to(root)}: {exc}")

    for path in unique_existing(targets["manifest"]):
        try:
            result = bump_json_version(path, args.part)
            if result is None:
                failures.append(f"{path.relative_to(root)}: version field not found")
            else:
                changed.append(result)
        except ValueError as exc:
            failures.append(f"{path.relative_to(root)}: {exc}")

    for result in changed:
        print(f"bumped {result.path.relative_to(root)}: {result.previous} -> {result.current}")

    if args.stage and changed:
        stage_files(root, [result.path for result in changed])

    if failures:
        for failure in failures:
            print(f"error: {failure}", file=sys.stderr)
        return 1

    if not changed:
        print("no version files found, skip.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
