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

    - `cli.py`: CLI interface layer. Orchestrates tools and handles user interaction (print/input).
    - `tools/`: **Pure Logic Layer**. Contains core implementations of tools (e.g., `filelist.py`).
      - `filelist.py`: Local directory traversal.
      - `efu_converter.py`: Conversions between JSON-LD and Everything EFU files.
      - `filelist_http.py`: Remote scanning via Everything HTTP server.
      - `filelist_ipc.py`: IPC-based scanning using Everything64.dll.
      - `whoami.py`: User identity retrieval.
      - `probe.py`: Environment data collection.
      - Code here must be pure: **NO print()**, **NO sys.exit()**, **NO user prompts**.
      - Should return raw data (dicts, objects) to be consumed by interfaces (CLI, TUI, MCP).
- `tests/`: Test suite for automated verification.
- `scripts/`: Development utilities and troubleshooting scripts (not for production logic).
- `schema/`: Single source of truth for semantic and structural specifications.
- `pyproject.toml`: Project configuration and dependencies.

## Schema Management
To ensure interoperability and clear specifications:
- **Directory:** All input/output specifications, including **JSON Schema**, **JSON-LD Contexts**, and **Example Data files**, must be placed in the `/schema` directory at the repository root.
- **Formats:** 
  - Use [JSON Schema](https://json-schema.org/) for defining data structures.
  - Use JSON-LD Contexts for defining semantic mappings.
- **PURL Namespace Ownership:**
  - The developer owns the `https://purl.org/gag` namespace. 
  - Authoritative terms (e.g., `gag:winAttributes`) must be mapped to this prefix in JSON-LD contexts.
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
  - **Tools (`src/get_a_grip/tools/`)**: Pure business logic only. Returns data structures.
  - **Interfaces (`cli.py`, `tui.py`, `mcp.py`)**: Handles presentation, user I/O, and orchestration.
- **Round-Trip Verification:** When building data conversion tools, ALWAYS perform round-trip verification (Format A -> Format B -> Format A) to ensure data integrity and losslessness.

## Development Workflow
1. **Adding Dependencies:** Use `poetry add <package>`.
2. **Running Locally:**
   - **Standard:** `poetry run get-a-grip filelist <args>`
   - **Alias:** `poetry run gag filelist <args>` (Short for "get-a-grip")
   - **Module:** `poetry run python -m get_a_grip filelist <args>`
3. **Testing:** 
   - Run tests with `poetry run pytest`.
   - Ensure new features have corresponding tests in `tests/`.
   - **URL Verification:** Run `pytest tests/test_url_accessibility.py` after modifying schemas to ensure all external references are stable.

### `src/get_a_grip/tools/filelist_http.py`
A module that interfaces with the "Everything" search engine's HTTP server to perform file system scans. It fetches search results in JSON format and converts them into the project's standard schema. It supports raw response inspection and customizing the number of results.

### `src/get_a_grip/tools/filelist_ipc.py`
A module that interfaces directly with the "Everything" search engine via IPC (Inter-Process Communication) using the `Everything64.dll`. This method allows for retrieving metadata that might be restricted or unavailable via the HTTP API, such as "Date Created". It requires the DLL to be present in the `bin/` directory.

### `src/get_a_grip/tools/efu_converter.py`
- **Versioning:**
    - Start from version `0.1.0`.
    - Always increment the patch level (e.g., `0.1.0` -> `0.1.1`) whenever ANY change, however small, is made to the source code.
- **Commit Messages:**
    - Use detailed commit messages.
    - Prefer `git commit -F commit_message.txt` for multi-line messages.
- **OS Environment:** Be aware that this project is primarily developed in a Windows environment (Powershell). Use appropriate commands (e.g., `dir`, `move`).
- **File Lists:** Use `es.exe -export-efu filelist.efu -path .` (C:\bin\es.exe) to generate file lists if needed.
