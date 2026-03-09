# get-a-grip

`get-a-grip` is a Python toolkit for inspecting Windows system environments — directory structures, platform paths, shell folders, environment variables, and event logs — via a unified CLI (`gag`) and optional GUI launcher.

> **Target audience:** Developers comfortable with `uv`, Python, and the command line who want to install directly from source on GitHub.

---

## Requirements

- Python 3.12+
- [uv](https://github.com/astral-sh/uv)

Install `uv` on Windows (PowerShell):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

---

## Installation

### As a standalone tool (recommended for users)

Installs `gag` into an isolated environment — no virtual environment setup required:

```powershell
uv tool install git+https://github.com/TakashiSasaki/get-a-grip.git@get-a-grip
```

Upgrade to the latest version:

```powershell
uv tool upgrade get-a-grip
```

### For development (editable install)

```powershell
git clone https://github.com/TakashiSasaki/get-a-grip.git
cd get-a-grip
uv sync
```

Changes to source files are immediately reflected without reinstalling.

Set up the automatic version-bump Git hook (increments patch on every commit):

```powershell
git config core.hooksPath .githooks
```

---

## Usage

```powershell
gag --help                       # Show all subcommands
gag version                      # Show version and check for updates
gag launch                       # Open the GUI Launcher
gag inspect-dirs --cli     # Show platform directory paths (CLI)
gag inspect-dirs --gui     # Show platform directory paths (GUI)
gag env                          # Launch Environment Viewer GUI
gag path                         # Analyze PATH environment variable
gag filelist <dir>               # Scan a directory and export JSON-LD
gag shortcut install             # Install Start Menu shortcut (Windows)
```

---

## Running the Test Suite

Tests are managed with [pytest](https://docs.pytest.org/) and run via `uv`:

```powershell
# Run all tests
uv run pytest

# Run a specific test file
uv run pytest tests/test_inspect_platform_dirs.py -v

# Run with coverage report
uv run pytest --cov=src/get_a_grip --cov-report=html

# Poe shortcuts (using poethepoet)
uv run poe test               # All primary tests (excludes slow URL checks)
uv run poe test-consistency   # Filelist consistency tests only
uv run poe test-urls          # External URL accessibility checks (slow)
```

Test reports are saved to `reports/tests/` (HTML, JSON, JUnit XML) and are excluded from Git.

---

## Directory Structure

```
src/get_a_grip/
  cli/          CLI entry points and tools
  gui/          Tkinter-based GUI (launcher.py is the main entry point)
  tui/          Textual-based TUI
  core/         Pure business logic — no print(), no sys.exit()
  contracts/    Shared TypedDict schemas
  mcp/          Model Context Protocol server
schema/         JSON Schema and JSON-LD context definitions
tests/          pytest test suite
scripts/        Dev utilities (version bump, PURL check, schema validation)
reports/        Auto-generated test and coverage reports (git-ignored)
dev-docs/       Additional documentation
```

---

## Key Design Principles

- **Separation of concerns**: `core/` is pure logic; `cli/`, `gui/`, `tui/` handle presentation.
- **Schema-first**: All I/O formats are defined in `schema/` using JSON Schema and JSON-LD.
- **Namespace ownership**: The `https://purl.org/gag` namespace is owned by the author for stable semantic terms.

For contributor guidelines, architecture details, and coding standards, see [AGENTS.md](./AGENTS.md).

---

## License

MIT
