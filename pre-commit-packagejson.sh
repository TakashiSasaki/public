#!/usr/bin/env sh
set -eu

# Compatibility wrapper for legacy usage.
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
export BUMP_TYPES="packagejson"
export BUMP_DISCOVER="0"
export BUMP_PACKAGE_JSON_PATHS="${PACKAGE_JSON_PATH:-package.json}"
exec "$SCRIPT_DIR/pre-commit"
