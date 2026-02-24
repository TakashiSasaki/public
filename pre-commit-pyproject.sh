#!/usr/bin/env sh
set -eu

# Compatibility wrapper for legacy usage.
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
export BUMP_TYPES="pyproject"
export BUMP_DISCOVER="0"
export BUMP_PYPROJECT_PATHS="${PYPROJECT_PATH:-pyproject.toml}"
exec "$SCRIPT_DIR/pre-commit"
