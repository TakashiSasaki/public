# get-a-grip

`get-a-grip` is a Python-based command-line tool designed to scan and map directory structures with high interpersonal and machine interoperability. It focuses on providing detailed file metadata in semantic formats to facilitate the analysis of complex folder hierarchies.

## 🌟 Key Features

- **Recursive Directory Scanning:** Traverse any folder tree and collect all file information.
- **Semantic Data Export (JSON-LD):** Outputs data using JSON-LD, leveraging Schema.org and custom vocabularies for semantic clarity.
- **Windows-Specific Metadata:**
  - **FILETIME Timestamps:** Captures creation and modification dates as 64-bit FILETIME values.
  - **Attribute Flags:** Records Windows file attribute bits (e.g., Read-only, Hidden, System).
- **Interoperability-First Design:**
  - **Schema-Driven:** All input/output formats are strictly defined in `schema/` using JSON Schema.
- **Linked Data & Namespace Ownership:**
  - **Owned Namespace:** The project uses the authoritative namespace `https://purl.org/gag`, which is owned and managed by the developer of this repository.
  - **Interoperable Metadata:** By using Persistent URLs (PURLs), the project ensures that metadata terms remain stable and unambiguous across different systems.
  - **Context Identification:** Uses a stable URN (`urn:uuid:fbd0009d-e91b-414f-9f4f-db3fbd3a16ee`) for persistent semantic context identification.
  - **Compatible Naming:** Uses compatible property names (e.g., `Filename` for full paths) to integrate with existing ecosystems.

## 🛠 Tech Stack

- **Language:** Python 3.12+
- **Dependency Management:** [Poetry](https://python-poetry.org/)
- **Data Formats:** JSON-LD, JSON Schema

## 📂 Directory Structure

- `src/get_a_grip/`: Core application logic and context definitions.
- `schema/`: Official JSON Schema specifications, JSON-LD contexts, and data examples.
- `scripts/`: Development utilities and troubleshooting scripts.
- `docs/`: Human-readable documentation.
- `tests/`: Project test suite.
- `AGENTS.md`: Technical guidance for coding agents and developers.

## � Schemas and Metadata

This project adheres to a "Schema-First" philosophy. The `schema/` directory contains:
- **JSON Schemas (`*.schema.json`)**: Define the structural requirements for inputs and outputs.
- **JSON-LD Contexts (`context.json`)**: Map local property names to global semantic vocabularies like Schema.org and CIM.
- **Examples**: Reference implementations showing the schemas in action.

### Namespace Ownership
The developer of this project owns and maintains the `https://purl.org/gag` namespace. This ensures:
- **Stability**: Vocabulary terms like `gag:winAttributes` will not change unexpectedly.
- **Discovery**: Metadata reflects the specific semantics of the `get-a-grip` ecosystem while remaining compatible with the wider Semantic Web.

## �🚀 Getting Started

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
poetry run python src/get_a_grip/cli.py scanner <target_directory> [-o output_file.json]
```

If no output filename is specified, it defaults to `fbd0009d-e91b-414f-9f4f-db3fbd3a16ee.json`.

## 📜 Principles

This project follows a "Schema-First" approach. We believe that explicitly defined interfaces are more important than implementation details. For more details on development standards, refer to [AGENTS.md](./AGENTS.md).
