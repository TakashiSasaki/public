#!/usr/bin/env sh
set -eu

# Template hook for JavaScript / TypeScript projects.
# This file is not active in this branch unless copied/linked to pre-commit.

PACKAGE_JSON_PATH="${PACKAGE_JSON_PATH:-package.json}"
BUMP_PART="${BUMP_PART:-patch}"
BUMP_SCRIPT="${BUMP_SCRIPT:-githooks/bump-packagejson-version.py}"

if [ ! -f "$PACKAGE_JSON_PATH" ]; then
  echo "pre-commit(package.json): $PACKAGE_JSON_PATH not found, skip."
  exit 0
fi

if [ ! -f "$BUMP_SCRIPT" ]; then
  echo "pre-commit(package.json): $BUMP_SCRIPT not found."
  exit 1
fi

if command -v uv >/dev/null 2>&1; then
  uv run --no-sync python "$BUMP_SCRIPT" --file "$PACKAGE_JSON_PATH" --part "$BUMP_PART"
elif command -v python >/dev/null 2>&1; then
  python "$BUMP_SCRIPT" --file "$PACKAGE_JSON_PATH" --part "$BUMP_PART"
elif command -v python3 >/dev/null 2>&1; then
  python3 "$BUMP_SCRIPT" --file "$PACKAGE_JSON_PATH" --part "$BUMP_PART"
else
  echo "pre-commit(package.json): python runtime not found."
  exit 1
fi

git add -- "$PACKAGE_JSON_PATH"
