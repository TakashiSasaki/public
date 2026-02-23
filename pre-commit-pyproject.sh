#!/usr/bin/env sh
set -eu

# Template hook for Python projects.
# This file is not active in this branch unless copied/linked to pre-commit.

PYPROJECT_PATH="${PYPROJECT_PATH:-pyproject.toml}"
BUMP_PART="${BUMP_PART:-patch}"
BUMP_SCRIPT="${BUMP_SCRIPT:-githooks/bump-pyproject-version.py}"

if [ ! -f "$PYPROJECT_PATH" ]; then
  echo "pre-commit(pyproject): $PYPROJECT_PATH not found, skip."
  exit 0
fi

if [ ! -f "$BUMP_SCRIPT" ]; then
  echo "pre-commit(pyproject): $BUMP_SCRIPT not found."
  exit 1
fi

if command -v uv >/dev/null 2>&1; then
  uv run --no-sync python "$BUMP_SCRIPT" --file "$PYPROJECT_PATH" --part "$BUMP_PART"
elif command -v python >/dev/null 2>&1; then
  python "$BUMP_SCRIPT" --file "$PYPROJECT_PATH" --part "$BUMP_PART"
elif command -v python3 >/dev/null 2>&1; then
  python3 "$BUMP_SCRIPT" --file "$PYPROJECT_PATH" --part "$BUMP_PART"
else
  echo "pre-commit(pyproject): python runtime not found."
  exit 1
fi

git add -- "$PYPROJECT_PATH"
