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
  - `git merge-base`: To determine the relationship (Ancestor, Tip, Independent).
  - `git rev-parse`: To get branch hashes and repository root path.

### 3. Single Instance Enforcement
- **TCP Socket Binding**: The application attempts to bind to localhost port `54321` on startup.
- **Rationale**: This is a robust, cross-platform way to ensure only one instance is running without relying on file locks which might be left behind if the process crashes.

### 4. Versioning
- **Semantic Versioning**: Starting from `0.1.0`. The version is defined within `detect_gui.py`.

## Maintainer Notes
- When adding new features, maintain compatibility with the built-in `tkinter` to avoid external dependencies.
- Ensure any `subprocess` calls handle potential errors (e.g., directory not being a git repo) gracefully.
