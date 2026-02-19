#!/bin/sh
#
# Pre-commit hook to increment version in pyproject.toml
#

echo "Bumping version in pyproject.toml..."

# Use 'uv run --no-sync' to ensure we use the project environment 
# without triggering a build/sync that might fail due to package layout.
if [ -f "scripts/bump_version.py" ]; then
    uv run --no-sync python scripts/bump_version.py
    if [ $? -eq 0 ]; then
        git add pyproject.toml
    else
        echo "Error: Failed to bump version."
        exit 1
    fi
else
    echo "Warning: scripts/bump_version.py not found. Skipping version bump."
fi

exit 0
