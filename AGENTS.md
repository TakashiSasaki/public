# AGENTS.md

This document provides instructions and context for AI coding agents and human developers working on the `get-a-grip` project.

## Project Overview
`get-a-grip` is a Python application designed to search through directory structures.

## Tech Stack
- **Language:** Python 3.10+
- **Dependency Management:** [Poetry](https://python-poetry.org/)
- **Testing:** [pytest](https://docs.pytest.org/)

## Directory Structure
Follow the standard Python src-layout:
- `src/get_a_grip/`: Main package source code.
- `src/get_a_grip/`: Main package source code.
    - `cli.py`: CLI interface layer. Orchestrates tools and handles user interaction (print/input).
    - `tools/`: **Pure Logic Layer**. Contains core implementations of tools (e.g., `scanner.py`).
      - Code here must be pure: **NO print()**, **NO sys.exit()**, **NO user prompts**.
      - Should return raw data (dicts, objects) to be consumed by interfaces (CLI, TUI, MCP).
- `tests/`: Test suite.
- `pyproject.toml`: Project configuration and dependencies.

## Schema Management
To ensure interoperability and clear specifications:
- **Directory:** All input/output specifications, including **JSON Schema**, **JSON-LD Contexts**, and **Example Data files**, must be placed in the `/schemas` directory at the repository root.
- **Formats:** 
  - Use [JSON Schema](https://json-schema.org/) for defining data structures.
  - Use JSON-LD Contexts for defining semantic mappings.
- **Usage:** Developers and agents should refer to these schemas instead of implementation details for interoperability.
- **Versioning:** Any change to the output format must be reflected in the corresponding schema.

## Coding Standards & Patterns
- **Type Hinting:** Use PEP 484 type hints for all functions and classes.
- **Docstrings:** Use Google-style docstrings for non-trivial functions.
- **Async:** Use `asyncio` where appropriate for directory I/O if performance is critical.
- **Separation of Concerns (Core vs Interface):**
  - **Tools (`src/get_a_grip/tools/`)**: Pure business logic only. Returns data structures.
  - **Interfaces (`cli.py`, `tui.py`, `mcp.py`)**: Handles presentation, user I/O, and orchestration.

## Development Workflow
1. **Adding Dependencies:** Use `poetry add <package>`.
2. **Running Locally:** Use `poetry run python src/get_a_grip/cli.py scanner <args>`, or install locally and run `get-a-grip scanner`.
3. **Testing:** Run tests with `poetry run pytest`. Ensure new features have corresponding tests in `tests/`.

## Repository Rules
- **Versioning:**
    - Start from version `0.1.0`.
    - Always increment the patch level (e.g., `0.1.0` -> `0.1.1`) whenever ANY change, however small, is made to the source code.
- **Commit Messages:**
    - Use detailed commit messages.
    - Prefer `git commit -F commit_message.txt` for multi-line messages.
- **OS Environment:** Be aware that this project is primarily developed in a Windows environment (Powershell). Use appropriate commands (e.g., `dir`, `move`).
- **File Lists:** Use `es.exe -export-efu filelist.efu -path .` (C:\bin\es.exe) to generate file lists if needed.
