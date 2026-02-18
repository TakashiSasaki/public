# AGENTS.md

This document provides instructions and context for AI coding agents and human developers working on the `get-a-grip` project.

> **Document roles:**
> - **[README.md](./README.md)** — The **user-facing** document. Written for developers who want to install and use the tool (via `uv tool install` from GitHub). Keep it accurate and up to date whenever the CLI interface or installation process changes.
> - **AGENTS.md** (this file) — Internal guidance for AI coding agents and contributors. Contains architecture decisions, coding standards, and implementation details not needed by end users.

## Project Overview
`get-a-grip` is a Python application designed to search through directory structures.

## Tech Stack
- **Language:** Python 3.10+
- **Dependency Management:** [uv](https://github.com/astral-sh/uv)
- **Testing:** [pytest](https://docs.pytest.org/)

## Directory Structure
Follow the standard Python src-layout:
- `src/get_a_grip/`: Main package source code.

    - `cli/`: **CLI Interface & Tools**. Contains CLI entry points and command implementations.
      - `main.py`: Main entry point for the consolidated `gag` CLI.
      - `filelist/`: **File Scanning Package**.
        - `__init__.py`: Provides a robust `scan()` function that validates multiple methods (`scandir`, `walk`, `rglob`).
        - `types.py`: Compatibility export for filelist types and `FileScanner` protocol.
        - `utils.py`: Shared utilities for saving results and comparing file lists.
        - `scandir.py`, `walk.py`, `rglob.py`: Individual scanning strategies.
        - `http.py`, `ipc.py`: Everything-based scanning strategies.
      - `dirtree.py`: Recursive directory tree traversal (hierarchical output).
      - `filelist2dirtree.py`: Converter tool from flat `filelist.json` to hierarchical `dirtree.json`.
      - `efu_converter.py`: Conversions between JSON-LD and Everything EFU files.
      - `efu/`: **EFU Tools**.
        - `update-efu.py`: Updates existing EFU files with new scan results using `es.exe` or HTTP.
        - `merge-efu.py`: Merges multiple EFU files into a single master file, resolving duplicates by `Last Seen`.
      - `git/`: **Git Repository Tools**.
        - `git_types.py`: Compatibility export for unified `GitRepoInfo` TypedDict and related Git contracts.
        - `utils.py`: Shared Git utility functions and backend initialization.
        - `find_git_repo.py`: Finds .git directories/files and returns `GitRepoInfo`.
        - `find_git_worktree.py`: Finds Git worktrees, cross-verifies status, and returns `GitWorktreeList`.
        - `find_github_dir.py`: Finds repositories specifically inside folders named 'GitHub'.
      - `whoami.py`: User identity retrieval.
      - `probe.py`: Environment data collection.
      - `path_viewer.py`: CLI tool for analyzing and verifying PATH environment variables.
      - `inspect_platform_dirs.py`: Tool to inspect OS-specific directory paths provided by `platformdirs`.
      - `inspect_app_data.py`: GUI tool to inspect the contents of the `AppDataStorage` database.
    - `tui/`: **TUI Interface**. Textual-based terminal user interface.
    - `gui/`: **GUI Interface**. Tkinter-based graphical user interface.
      - `launcher.py`: **GUI Launcher**. Central entry point for all GUI tools.
      - `efu_gui.py`: GUI for EFU Update and Merge tools.
      - `event_viewer.py`: GUI tool for viewing detailed environment variables and PATH information.
      - `env_viewer.py`: GUI tool for viewing detailed environment variables.
      - `shortcut_manager.py`: Manages Start Menu shortcuts for the application.
    - `mcp/`: **MCP Server**. Interface for Model Context Protocol.
    - `env_info.py`: **Environment Info Schema**. Defines data structures for environment capture.
    - `identifiers.py`: **Central Identifier Management**. Provides `APP_NAMESPACE_UUID` and `generate_id_v5()`.
    - `storage.py`: **Application Data Storage**. Simple KVS interface (settings/cache) backed by SQLite.
    - `core/`: **Pure Logic Layer**. Contains core implementations of tools.
      - `env_internal.py`: Core logic for environment variable retrieval and parsing.
      - `event_log.py`: Core logic for Windows Event Log retrieval.
      - `path_parser.py`: Core logic for PATH string parsing and command search.
      - `everything_ipc.py`: Low-level ctypes wrapper for Everything SDK IPC.
      - Code in `core/` must be pure: **NO print()**, **NO sys.exit()**, **NO user prompts**.
      - Should return raw data (dicts, objects) to be consumed by interfaces (CLI, TUI, GUI, MCP).
    - `contracts/`: **Data Contract Layer**. Shared TypedDict schemas for cross-module and external interoperability.
- `tests/`: Test suite for automated verification.
- `scripts/`: Development utilities and troubleshooting scripts (not for production logic).
  - `check_purls.py`: Validates accessibility of all PURLs used in schema files. Outputs to `reports/purl-availability/`.
  - `validate_schema.py`: Validates JSON data against JSON Schema definitions.
  - `test_everything_ipc.py`: Test script for Everything IPC functionality.
  - `debug_identity.py`: Debug script for identity/authentication testing.
- `reports/`: **Test results and status reports**. Contains validation results, test outputs, and project status information.
  - `tests/`: pytest test execution results (generated automatically by `uv run pytest`).
    - `latest.json`: JSON format test report for automation and CI/CD.
    - `latest.xml`: JUnit XML format for CI/CD integration.
    - `latest.html`: Self-contained HTML report for human viewing.
  - `coverage/`: Code coverage reports (generated automatically by `uv run pytest`).

    - `latest.json`: JSON format coverage data.
    - `html/`: Interactive HTML coverage report with line-by-line analysis.
  - `purl-availability/`: PURL accessibility check results (generated by `scripts/check_purls.py`).
    - `latest.txt`: Human-readable text report.
    - `latest.json`: Machine-readable JSON format for automation and status integration.
    - `latest.jsonld`: JSON-LD format for semantic web compatibility.
  - **Git Policy**: `reports/` directory is **untracked** via `.gitignore` to prevent repository clutter. Do not commit test reports.
- `examples/`: **Example files** demonstrating tool usage and output formats.
  - Contains sample input files (e.g., `.efu`) and expected output files (e.g., `.jsonld`).
  - Organized by tool or use case (structure to be refined).
  - **Purpose**: Learning, testing, and quick-start references for users and developers.
- `docs/`: **Documentation**. Additional documentation files for developers.
  - `SYMLINKS.md`: Guide for working with symbolic links on Windows.
  - `WINDOWS_PYTHON_ENV.md`: Python environment setup on Windows.
  - `json-schema-jsonld-guide.md`: Guide for JSON Schema and JSON-LD usage.
- `.github/`: **GitHub-specific files**.
  - `workflows/`: GitHub Actions workflow definitions for CI/CD.
- `.githooks/`: **Git Hooks**.
  - `pre-commit`: Automatically bumps the patch version in `pyproject.toml` on every commit.
- `bin/`: **Binary files**. External dependencies and DLLs.
  - `Everything64.dll`: Required for IPC-based file scanning (`filelist_ipc.py`).
- `work/`: **Local Work Directory**. Use this for all temporary files, test outputs, and diagnostic results. Contents are ignored by Git.
- `schema/`: Single source of truth for semantic and structural specifications.
- `pyproject.toml`: Project configuration and dependencies.

## Schema Management
To ensure interoperability and clear specifications:
- **Directory:** All input/output specifications, including **JSON Schema**, **JSON-LD Contexts**, and **Example Data files**, must be placed in the `/schema` directory at the repository root.
- **Formats:** 
  - Use [JSON Schema](https://json-schema.org/) for defining data structures.
  - Use JSON-LD Contexts for defining semantic mappings.
- **Vocabulary Source of Truth:**
  - `schema/vocab.jsonld` is the ultimate source of truth for the `gag` namespace. 
  - All proprietary terms must be defined here as `rdfs:Class` or `Property` before being used in contexts.
- **PURL Namespace Ownership:**
  - The developer owns the `https://purl.org/gag` namespace. 
  - Authoritative terms (e.g., `gag:winAttributes`) must be mapped to this prefix in JSON-LD contexts.
- **Metadata Structure (Observer/Target Pattern):**
  - For consistency across tools (e.g., `probe`, `dirtree`), metadata should follow a hierarchical structure:
    - `observer`: Identity information of the agent/user performing the action (e.g., `uid`, `userPrincipalName`).
    - `target`: Information about the system or resource being observed (e.g., OS info, hostname).
- **Federated Vocabularies:**
  - Prioritize standard vocabularies for mapping:
    - **General Concepts:** [Schema.org](https://schema.org/)
    - **Systems Management:** [DMTF CIM](http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/)
    - **Directory Services:** [LDAP](https://purl.org/net/ldap#) / [Active Directory](https://purl.org/identity/ad/)
    - **Network Management:** [SNMP](http://www.w3.org/ns/snmp#)
- **Usage:** Developers and agents should refer to these schemas instead of implementation details for interoperability.
- **Versioning:** Any change to the output format must be reflected in the corresponding schema.

## Coding Standards & Patterns
- **Type Hinting:** Use PEP 484 type hints for all functions and classes.
- **Docstrings:** Use Google-style docstrings for non-trivial functions.
- **Async:** Use `asyncio` where appropriate for directory I/O if performance is critical.
- **Separation of Concerns (Core vs Interface):**
  - **Core (`src/get_a_grip/core/`)**: Pure business logic only. Returns data structures.
    - **MUST NOT** depend on `cli.py` or `tui.py`.
    - **MUST NOT** use `input()` or `sys.exit()`. Raise exceptions instead.
    - **UI Feedback:** If a tool requires progress reporting, use an optional, injectable callback or a dedicated tracker class that defaults to no-op. Avoid direct `print()` calls in core logic.
  - **Interfaces (`cli/`, `tui/`, `gui/`, `mcp/`)**: Handles presentation, user I/O, and orchestration.
    - Responsible for catching exceptions from tools and presenting them to the user.
- **Data Contracts:**
  - Place shared exchange types in `src/get_a_grip/contracts/` (e.g., filelist/git TypedDict definitions).
  - Keep runtime behaviors and protocols (e.g., `FileScanner`) in `src/get_a_grip/core/`.
- **Strategy Pattern for Scanners:**
  - All file scanners must implement the `FileScanner` protocol (defined in `src/get_a_grip/core/filelist/types.py`).
  - `FileList` / `FileItem` contract types are defined in `src/get_a_grip/contracts/filelist.py`.
  - Required interface: `scan(target: str) -> FileList`.
  - Use `@runtime_checkable` on the protocol to allow `isinstance(obj, FileScanner)` checks.
- **Robustness & Validation:**
  - The default `filelist.scan()` function acts as a validator by running `scandir`, `walk`, and `rglob` sequentially and verifying that their results match exactly (counts and metadata).
  - Use `compare_filelists()` from `utils.py` for this validation. (Note: Directory size is ignored during comparison on Windows to handle API-specific inconsistencies).
- **Round-Trip Verification:** When building data conversion tools, ALWAYS perform round-trip verification (Format A -> Format B -> Format A) to ensure data integrity and losslessness.

## Identifiers & UUIDs
To ensure consistency across the application and avoid collisions with other systems, we use a fixed application-wide Namespace UUID for creating UUIDv5 identifiers.

- **Namespace UUID:** `c31a2332-47da-4ecf-a93a-80880c593533`
- **Usage:**
  - Import `APP_NAMESPACE_UUID` or use `generate_id_v5(name)` from `src/get_a_grip/identifiers.py`.
  - **DO NOT** hardcode this UUID in other files. Always reuse the constant.
  - Used for: Generating deterministic UUIDs for file items, user identities, or any resource that needs a consistent ID based on a string key (e.g., path).

### SQLite Database Conventions
To maintain data integrity and consistency, **all database operations must be centralized in `src/get_a_grip/storage.py`**. Other modules must not use `sqlite3` directly; they should interact with the database via `AppDataStorage`.

General conventions:
- **Application ID:** Use the first 32 bits of `APP_NAMESPACE_UUID` (`0xc31a2332`) as the `PRAGMA application_id`. This ensures the database file is uniquely identified as belonging to this application.
- **Schema Versioning:** Use `PRAGMA user_version` to track the database schema version. Do not use a separate metadata table for this purpose.
- **Storage Location:** Use `platformdirs.user_data_dir()` to place database files in the correct OS-specific location (typically `AppData/Local` on Windows).
- **Implementation:**
  - Use `AppDataStorage.get_instance()` for a shared connection.
  - Supports persistent `settings`, TTL-based `cache`, and specialized tables like `event_logs`.
  - Automatic JSON serialization/deserialization for values.
  - Multi-thread safe for use in GUI/TUI environments.

### Git Backend Libraries Best Practices

When working with Git libraries in Python, be aware of the following quirks and best practices to ensure performance and consistency:

1.  **GitPython (`git`):**
    *   **Performance Trap:** Avoid `repo.untracked_files`. It recursively lists all untracked files, causing extreme performance degradation or hangs in large directories (e.g., home directories with `node_modules`).
    *   **Solution:** Use `repo.git.ls_files('--others', '--exclude-standard', '--directory')`. This lists directory roots instead of recursing, drastically improving speed.
    *   **Subprocess:** GitPython spawns `git.exe` subprocesses. Use `concurrent.futures.ThreadPoolExecutor` for timeouts, but be aware that it cannot forcefully kill the underlying process.
    *   **Untracked Directories:** When using `ls-files --directory` to check for untracked files, always include `--no-empty-directory`. Without it, empty directories (which Git typically ignores) are reported as untracked, causing inconsistencies with `git status` or other libraries.

2.  **pygit2 (`pygit2`):**
    *   **Unborn Branches:** Accessing `repo.head` on a fresh repository (no commits) raises a `GitError`.
    *   **Solution:** Catch this exception, check `repo.head_is_unborn`, and if true, inspect the symbol target of HEAD via `repo.lookup_reference("HEAD").target`.
    *   **Detached HEAD:** `repo.head.shorthand` returns `"HEAD"` instead of a branch name or OID when detached.
    *   **Solution:** explicitly check `repo.head_is_detached` before accessing shorthand.

3.  **Dulwich (`dulwich`):**
    *   **Status Check:** `porcelain.status(repo)` returns a tuple `(staged, unstaged, untracked)`.
    *   **Trap:** `staged` is a dictionary `{'add': [], ...}`. Even if empty (`{'add': [], ...}`), it evaluates to `True` in boolean context because the dictionary keys exist.
    *   **Solution:** Use `any(staged.values())` to check if there are actual staged files.
    *   **Windows/CRLF:** Dulwich's porcelain status does not automatically handle `core.autocrlf` the same way Git CLI does, potentially leading to false-positive modified files.
    *   **HEAD Reference Parsing:** `repo.refs.read_ref(b'HEAD')` returns the raw ref string (e.g., `b'ref: refs/heads/feature/branch'`). Simply splitting by `/` truncates hierarchical branch names. Check for `b'ref: refs/heads/'` prefix and slice the string instead.

### Git Status Standardization

To ensure consistent behavior across different Git libraries and CLI tools, `get-a-grip` adopts the following definitions:

-   **Dirty:** The working tree has **staged** or **unstaged** modifications to tracked files.
-   **Clean:** No staged or unstaged modifications to tracked files.
-   **Untracked:** The presence of untracked files is reported separately (e.g., `[untracked]`) and **does NOT** affect the Dirty/Clean status.
    -   *Rationale:* Including untracked files in "Dirty" status (like `git status --porcelain` does by default) makes it difficult to distinguish between "active work in progress" and "just added a temporary file".
    -   *Implementation:* Always disable untracked checking in the primary dirty check (e.g., `repo.is_dirty(untracked_files=False)` in GitPython) and perform a separate check for untracked files.

### Cloud Storage / OneDrive Issues

When dealing with repositories stored in cloud-synced folders (OneDrive, Dropbox, Google Drive) on Windows:

-   **Symptoms:**
    -   `pygit2` raises `GitError: failed to resolve reference 'HEAD': The cloud file provider is not running.` (or localized message).
    -   `Dulwich` raises `OSError: [Errno 22] Invalid argument`.
    -   `GitPython` usually succeeds because it delegates to the `git.exe` process, which handles file hydration better than Python's direct file access.
-   **Cause:** "Files On-Demand" features keep files as placeholders (reparse points) until accessed. Python libraries may fail to read these placeholders if the sync client is not running or if they use low-level file APIs that don't trigger hydration.
-   **Mitigation:** Treat these errors as "Repository Inaccessible" (return `None` or error state) rather than crashing. Users must ensure the repo is fully synced or the cloud provider is running.

### Repository Ownership / Safe Directory

Git has security measures preventing access to repositories owned by other users (e.g., specific folders owned by `SYSTEM` or `Administrators`).

-   **Symptoms:**
    -   `pygit2` raises `GitError: repository path '...' is not owned by current user`.
    -   `Dulwich` and `GitPython` may succeed depending on their implementation and configuration, but `pygit2` (libgit2-based) is strict by default.
-   **Mitigation:**
    -   Report as `[Owner Mismatch]` to inform the user why access failed.
    -   Users can whitelist directories using `git config --global --add safe.directory <path>`, but `pygit2` might not respect this depending on how it's built/configured vs `git.exe`.

### Everything Search Strategy

For efficient filesystem scanning on Windows, `get-a-grip` leverages "Everything" via IPC or HTTP.

-   **Finding Git Roots:**
    -   Instead of searching for *any* `.git` folder (which returns thousands of subdirectories), compare:
        -   `folder: exact:.git` -> Finds standard repository roots.
        -   `file: exact:.git` -> Finds **submodules** and **worktrees** (where `.git` is a file pointing to the actual dir).
    -   Combining these two queries covers all types of Git working directories.
-   **Speed:** Everything is orders of magnitude faster than Python's `os.walk` or `glob` for whole-drive searches. Always prefer Everything for initial discovery.
1. **Adding Dependencies:** Use `uv add <package>`.
2. **Running Locally:**
   - **Unified CLI:** `uv run gag <command>` or `get-a-grip <command>`
     - `gag efu update ...` / `gag efu merge ...`
     - `gag efu gui`: Launch EFU tools GUI
     - `gag env`: Launch Environment Viewer GUI
     - `gag path`: Launch Path Viewer
     - `gag launch`: Launch GUI Launcher
     - `gag shortcut install`: Install Start Menu shortcut
   - **GUI Launcher:** `get-a-grip` (launches dashboard)
3. **Testing:** 
   - **General Test Run:** `uv run pytest` (uses automated root-directory resolver).
   - **Poe Tasks:**
     - `uv run poe test`: Run all primary tests (excludes slow URL checks).
     - `uv run poe test-consistency`: Specifically run filelist consistency tests.
     - `uv run poe test-urls`: Run external URL accessibility checks (long-running).
   - **URL Verification:** After modifying schemas, running `poe test-urls` is recommended.
   - **PURL Accessibility Check:** Run `python scripts/check_purls.py` to verify all PURLs in schema files are accessible. Results are saved to `reports/purl-availability/`.
   - **Schema Validation:** Use `python scripts/validate_schema.py <data_file> <schema_file>` to verify output against JSON Schema definitions.

### Troubleshooting: uv Command Not Found
If the `uv` command is not found in your shell:
1. Ensure `uv` is installed (`pip install uv` or via installer).
2. Ensure the installation directory is in your `PATH`.

### Automatic Version Bumping
The project's patch version in `pyproject.toml` is automatically incremented on every commit using a Git hook.

- **How it works:** A `pre-commit` hook executes `scripts/bump_version.py` which increments the patch level and adds the updated `pyproject.toml` to the commit.
- **Initial Setup (after clone):**
  Git hooks are local to your machine. You must manually set up the hook after cloning the repository:

  **Windows (Powershell):**
  ```powershell
  Copy-Item scripts/pre-commit .git/hooks/pre-commit
  ```

  **Linux / macOS (Bash):**
  ```bash
  cp scripts/pre-commit .git/hooks/pre-commit
  chmod +x .git/hooks/pre-commit
  ```
- **Manual Override:** To commit without bumping the version, use `git commit --no-verify`.
- **Note:** `scripts/bump_version.py` is included in the repository to ensure consistent behavior across environments.

### `src/get_a_grip/core/dirtree.py`

A recursive directory scanner that outputs a hierarchical JSON structure conforming to `schema/dirtree.json`. It captures the filesystem structure as a nested tree where keys are path segments.

### `src/get_a_grip/core/filelist2dirtree.py`
A converter tool that takes the flat list output from Everything-based scanners (which conform to `schema/filelist.json`) and transforms them into a hierarchical structure (`schema/dirtree.json`). This is the preferred way to generate trees from IPC/HTTP scans.

### `src/get_a_grip/core/filelist/http.py`
A module that interfaces with the "Everything" search engine's HTTP server to perform file system scans. It fetches search results in JSON format and converts them into the project's standard schema. It supports raw response inspection and customizing the number of results.

### `src/get_a_grip/core/filelist/ipc.py`
A module that interfaces directly with the "Everything" search engine via IPC (Inter-Process Communication) using the `Everything64.dll`. This method allows for retrieving metadata that might be restricted or unavailable via the HTTP API, such as "Date Created". It requires the DLL to be present in the `bin/` directory.

### `src/get_a_grip/core/efu_converter.py`
- **Versioning:**
    - Start from version `0.1.0`.
    - Always increment the patch level (e.g., `0.1.0` -> `0.1.1`) whenever ANY change, however small, is made to the source code.
- **Commit Messages:**
    - Use detailed commit messages.
    - Prefer `git commit -F commit_message.txt` for multi-line messages.
- **OS Environment:** Be aware that this project is primarily developed in a Windows environment (Powershell). Use appropriate commands (e.g., `dir`, `move`).
- **Temporary Files:** Always use the `work/` directory for temporary scan results, debugging logs, or any other intermediate files to keep the project root clean.
- **File Lists:** Use `es.exe -export-efu filelist.efu -path .` (C:\bin\es.exe) to generate file lists if needed.
