# Scripts Directory

This directory contains development utilities, maintenance scripts, and troubleshooting tools for the `get-a-grip` project. These scripts are intended for developers and CI/CD pipelines, not as part of the production application logic.

## Utility Scripts

### `check_purls.py`
- **Purpose**: Scans the `schema/` directory for all `https://purl.org/gag/` prefixed URLs and checks their HTTP reachability.
- **Output**: Updates `schema/url_availability_report.txt` with the results.
- **Usage**:
  ```powershell
  python scripts/check_purls.py
  ```

### `validate_schema.py`
- **Purpose**: Validates a JSON/JSON-LD data file against a specific JSON Schema definition.
- **Usage**:
  ```powershell
  python scripts/validate_schema.py <path_to_data_file> <path_to_schema_file>
  ```

### `debug_identity.py`
- **Purpose**: A diagnostic tool to verify how user identity (UID, UPN, etc.) is being retrieved from the current OS environment.

### `test_everything_ipc.py`
- **Purpose**: Low-level integration test for the Everything IPC interface. Verifies that the `Everything64.dll` is working correctly and can communicate with the Everything service.

## Usage Guidelines
- Always run these scripts from the project root.
- Ensure your environment is set up via `poetry install` before running scripts that have external dependencies.
