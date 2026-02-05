# get-a-grip

`get-a-grip` is a Python-based command-line tool designed to scan and map directory structures with high interpersonal and machine interoperability. It focuses on providing detailed file metadata in semantic formats to facilitate the analysis of complex folder hierarchies.

## 🌟 Key Features

- **Recursive Directory Scanning:** Traverse any folder tree and collect all file information.
- **Semantic Data Export (JSON-LD):** Outputs data using JSON-LD, leveraging Schema.org and custom vocabularies for semantic clarity.
- **Windows-Specific Metadata:**
  - **FILETIME Timestamps:** Captures creation and modification dates as 64-bit FILETIME values.
  - **Attribute Flags:** Records Windows file attribute bits (e.g., Read-only, Hidden, System).
- **Interoperability-First Design:**
  - **Context Identification:** Uses a stable URN (`urn:uuid:fbd0009d-e91b-414f-9f4f-db3fbd3a16ee`) for semantic context identification.
  - **Schema-Driven:** All input/output formats are strictly defined in `schemas/` using JSON Schema.
  - **Compatible Naming:** Uses compatible property names (e.g., `Filename` for full paths) to integrate with existing ecosystems.

## 🛠 Tech Stack

- **Language:** Python 3.12+
- **Dependency Management:** [Poetry](https://python-poetry.org/)
- **Data Formats:** JSON-LD, JSON Schema

## 📂 Directory Structure

- `src/get_a_grip/`: Core application logic and context definitions.
- `schemas/`: Official JSON Schema specifications for interoperability.
- `docs/`: Documentation and example output files.
- `tests/`: Project test suite.
- `AGENTS.md`: Technical guidance for coding agents and developers.

## 🚀 Getting Started

### Prerequisites

- Python 3.12 or higher
- [Poetry](https://python-poetry.org/docs/#installation)

### Installation

```bash
poetry install
```

### Basic Usage

To scan a directory and output a JSON-LD file:

```powershell
$env:PYTHONPATH="src"
poetry run python src/get_a_grip/main.py <target_directory> [-o output_file.json]
```

If no output filename is specified, it defaults to `fbd0009d-e91b-414f-9f4f-db3fbd3a16ee.json`.

## 📜 Principles

This project follows a "Schema-First" approach. We believe that explicitly defined interfaces are more important than implementation details. For more details on development standards, refer to [AGENTS.md](./AGENTS.md).
