# Reports Directory

This directory contains various test results, validation reports, and status information for the get-a-grip project.

## Directory Structure

```
reports/
├── purl-availability/      # PURL accessibility check results
│   ├── latest.json         # JSON format (for automation)
│   ├── latest.jsonld       # JSON-LD format (for schema browser)
│   ├── latest.txt          # Human-readable text format
│   └── README.md
└── README.md               # This file
```

## Available Reports

### PURL Availability

**Location**: `purl-availability/`

Checks the HTTP accessibility of all PURLs (Persistent URLs) used in the project's schema files.

- **Script**: `scripts/check_purls.py`
- **Formats**: JSON, JSON-LD, TXT
- **Status**: ✅ Passed / ❌ Failed (based on URL accessibility)

## Planned Reports

Future reports that may be added:

- **`tests/`** - pytest test results
- **`coverage/`** - Code coverage reports
- **`schema-validation/`** - JSON Schema validation results
- **`individual-tests/`** - Detailed results from individual test scripts

## Git Management

This directory follows these rules in `.gitignore`:

- ✅ **Tracked**: `latest.*` files (current status)
- ✅ **Tracked**: `README.md` files (documentation)
- ❌ **Ignored**: Historical reports (timestamped files like `2026-*.json`)
- ❌ **Ignored**: Large HTML reports

## Usage

### Generate Reports

```bash
# PURL availability check
python scripts/check_purls.py

# Run all tests (future)
pytest --json-report --json-report-file=reports/tests/latest.json
```

### View Reports

```bash
# Human-readable text report
cat reports/purl-availability/latest.txt

# JSON report (for scripts)
cat reports/purl-availability/latest.json

# JSON-LD report (for semantic web)
cat reports/purl-availability/latest.jsonld
```

## Integration

These reports can be integrated into:

- **CI/CD pipelines** - Automated checks on every commit
- **Status badges** - Display current status in README
- **Monitoring systems** - Track project health over time
- **Documentation** - Embed current status in docs
