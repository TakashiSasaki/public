# AGENTS.md - Git Related Branch Detector

This document outlines the technical decisions and architecture for the Git Related Branch Detector tool.

## Technical Decisions

### 1. Language and Framework
- **Python 3**: Chosen for its ubiquity and ease of development on Windows environments.
- **Tkinter / ttk**: Used for the GUI. It is part of the Python standard library, ensuring the tool runs without requiring `pip install` of third-party GUI frameworks. `ttk` is used for a more modern, themed look.

### 2. Git Integration
- **`subprocess`**: Used to invoke Git commands directly. This avoids a dependency on `GitPython`, keeping the tool lightweight and portable within environments where only Git and Python are present.
- **Command Set**:
  - `git branch --show-current`: To identify the reference point.
  - `git for-each-ref`: To efficiently list all local and remote branches.
  - `git log -g --all --format="%H %gd"`: To extract all reflog entries (added in v0.2.0). 
  - `git merge-base`: To determine the relationship (Ancestor, Tip, Independent).
  - `git rev-parse`: To get branch hashes and repository root path.

### 3. Performance Optimization (Caching)
- **Hash-based Execution Cache**: Reflogs often produce hundreds of entries pointing to a limited set of unique commit hashes. To prevent `git merge-base` from hanging the GUI due to repeated sub-process calls, the relationship status is cached per commit hash.

### 4. Single Instance Enforcement
- **TCP Socket Binding**: The application attempts to bind to localhost port `52941` on startup.
- **Rationale**: This is a robust, cross-platform way to ensure only one instance is running without relying on file locks which might be left behind if the process crashes.

### 5. Versioning Policy
- **Semantic Versioning**: The software uses semantic versioning.
- **Automated/AI Updates**: Implicit version bumps made by AI agents or automated scripts must *only* increment the **patch** level (e.g., `0.2.0` -> `0.2.1`).
- **Human Updates**: Bumping the minor or major version numbers is strictly reserved for human developers to perform manually indicating significant feature additions or breaking changes.

### 6. Package Layout
- **uv Structure**: Designed as a standard Python package following `src/` layout.
- **Package Name**: Main logic resides in `src/branch_detect`.
- **Command Line**: Defined in `pyproject.toml` as `git-detect-related-branch` via the `[project.scripts]` table.

## Maintainer Notes
- When adding new features, maintain compatibility with the built-in `tkinter` to avoid external dependencies.
- Ensure any `subprocess` calls handle potential errors (e.g., directory not being a git repo) gracefully.
- **Python Interpreter Details**: If a required Python interpreter appears to be missing, note that the environment might be managed by `uv`. Use `uv run` to correctly resolve the managed environment instead of invoking `python` directly.
