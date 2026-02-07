# Test Reports

This directory contains pytest test execution results.

## Generated Files

- **`latest.json`** - JSON format test report (pytest-json-report)
- **`latest.xml`** - JUnit XML format (for CI/CD integration)
- **`latest.html`** - HTML format test report (human-readable)

## How to Generate

Test reports are automatically generated when running pytest:

```bash
poetry run pytest
```

Or using the shortcut:

```bash
poetry run test
```

## Report Structure

### JSON Format (`latest.json`)

```json
{
  "created": "2026-02-07T12:44:00+09:00",
  "duration": 5.23,
  "exitcode": 0,
  "root": "/path/to/project",
  "environment": {...},
  "summary": {
    "total": 42,
    "passed": 42,
    "failed": 0,
    "skipped": 0
  },
  "tests": [...]
}
```

### XML Format (`latest.xml`)

JUnit XML format, compatible with most CI/CD systems (GitHub Actions, Jenkins, etc.)

### HTML Format (`latest.html`)

Self-contained HTML report with detailed test results, including:
- Test execution time
- Pass/fail status
- Error messages and tracebacks
- Test metadata

## Git Management

- **Tracked**: `latest.*` files (current status)
- **Ignored**: Historical reports (timestamped files)
- **Ignored**: HTML reports (can be large)

See `.gitignore` for details.

## Related Files

- **Configuration**: `pyproject.toml` ([tool.pytest.ini_options])
- **Coverage Reports**: `../coverage/`
- **Test Source**: `../../tests/`
