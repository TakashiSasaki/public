# Project Notes

- Git hook and version bump scripts are centralized in the `githooks` submodule so they can be reused across repositories.
- Use `githooks/setup-hooks.ps1` on Windows or `githooks/setup-hooks.sh` on Linux/macOS to set `core.hooksPath`.
- `githooks/pre-commit` supports `pyproject.toml`, `package.json`, and `manifest.webmanifest` with auto discovery.
- Repository-local `scripts/` hook helpers were removed to avoid duplication with the shared submodule.
