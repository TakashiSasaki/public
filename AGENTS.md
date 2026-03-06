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
  - `git log -g --all --format="%H %gd"`: To extract all reflog entries.
  - `git merge-base`: To determine relationship (Ancestor, Tip, Independent).
  - `git rev-parse`: To get branch hashes and repository root path.
  - `git status`: To check for dirty worktree and display details (added in v0.2.5).
  - `git branch -vv`: To parse tracking status (ahead/behind/gone) (added in v0.2.10).
  - `git branch -r`: To list remote-only branches (added in v0.2.10).
  - `git fetch --all`: To update remote tracking caches (added in v0.2.10).
  - `git remote -v`: To list registered remotes (added in v0.2.13).
  - `git remote rename`: To rename registered remotes (added in v0.2.15).

### 3. Performance and Robustness
- **Hash-based Execution Cache**: Relationship status is cached per commit hash to prevent UI hangs.
- **Multibyte Character Support**: Subprocess calls explicitly use `encoding="utf-8"` with `errors="replace"`. This is critical for Windows environments where the system locale (e.g., CP932) may conflict with Git's UTF-8 output (fixed in v0.2.12).

### 4. UI Architecture
- **Tabbed Navigation**: Uses `ttk.Notebook` to separate Related Branches, Git Status, and Remote Tracking features.
- **Global Information Area**: The "System Information" frame (CWD, Repo Root, and Navigation buttons) resides outside the notebook to remain persistently visible across all tabs (added in v0.2.14).

### 5. Single Instance Enforcement
- **TCP Socket Binding**: The application binds to localhost port `52941`.
- **Rationale**: Robust cross-platform way to ensure single instance without stale lock files.

### 6. Versioning Policy
- **Semantic Versioning**: AI agents/automated scripts increment **patch** level (e.g., `0.2.0` -> `0.2.1`). Humans reserve minor/major bumps.

### 7. Package Layout
- **uv Structure**: Standard `src/` layout. Package logic in `src/branch_detect`.

## Maintainer Notes
- **Safety First**: Repository-modifying actions must be safe. For example, `git fetch` is used without `--prune` to prevent automatic cache deletion (v0.2.11).
- **Built-in Only**: Maintain compatibility with built-in `tkinter` and `ttk` to avoid external dependencies.
- **Subprocess Handling**: Ensure any `subprocess` calls handle errors gracefully and use the defined encoding standards.
- **Environment**: If a required Python interpreter appears to be missing, use `uv run` to resolve the managed environment instead of invoking `python` directly.
