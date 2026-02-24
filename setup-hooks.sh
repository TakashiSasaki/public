#!/usr/bin/env sh
set -eu

SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
REPO_ROOT="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel)"

case "$SCRIPT_DIR/" in
  "$REPO_ROOT"/*)
    HOOKS_PATH="${SCRIPT_DIR#$REPO_ROOT/}"
    ;;
  *)
    echo "setup-hooks: failed to resolve hooks path relative to repository root." >&2
    exit 1
    ;;
esac

git -C "$REPO_ROOT" config core.hooksPath "$HOOKS_PATH"
echo "Configured core.hooksPath=$HOOKS_PATH (repo: $REPO_ROOT)"
