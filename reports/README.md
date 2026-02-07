# Reports Directory

This directory contains various test results, validation reports, and status information for the get-a-grip project.

## Directory Structure

```
reports/
├── tests/                  # pytest test execution results
│   ├── latest.json         # JSON format (for automation)
│   ├── latest.xml          # JUnit XML (for CI/CD)
│   ├── latest.html         # HTML format (human-readable)
│   └── README.md
├── coverage/               # Code coverage reports
│   ├── latest.json         # JSON format coverage data
│   ├── html/               # Interactive HTML report
│   └── README.md
├── purl-availability/      # PURL accessibility check results
│   ├── latest.json         # JSON format (for automation)
│   ├── latest.jsonld       # JSON-LD format (for schema browser)
│   ├── latest.txt          # Human-readable text format
│   └── README.md
└── README.md               # This file
```

## Available Reports

### Test Results

**Location**: `tests/`

Pytest test execution results in multiple formats.

- **Script**: `poetry run pytest` or `poetry run test`
- **Formats**: JSON, XML (JUnit), HTML
- **Status**: ✅ Passed / ❌ Failed (based on test results)

### Code Coverage

**Location**: `coverage/`

Code coverage analysis showing which lines of code are tested.

- **Script**: `poetry run pytest` (coverage is included automatically)
- **Formats**: JSON, HTML
- **Target**: 85% coverage

### PURL Availability

**Location**: `purl-availability/`

Checks the HTTP accessibility of all PURLs (Persistent URLs) used in the project's schema files.

- **Script**: `python scripts/check_purls.py`
- **Formats**: JSON, JSON-LD, TXT
- **Status**: ✅ Passed / ❌ Failed (based on URL accessibility)

## Usage

### Generate Reports

```bash
# Run all tests and generate reports
poetry run pytest
# or
poetry run test

# PURL availability check
python scripts/check_purls.py
```

### View Reports

```bash
# Test results (JSON)
cat reports/tests/latest.json

# Test results (HTML)
start reports/tests/latest.html  # Windows
open reports/tests/latest.html   # Mac/Linux

# Coverage (JSON)
cat reports/coverage/latest.json

# Coverage (HTML)
start reports/coverage/html/index.html  # Windows
open reports/coverage/html/index.html   # Mac/Linux

# PURL availability (human-readable)
cat reports/purl-availability/latest.txt

# PURL availability (JSON)
cat reports/purl-availability/latest.json
```

## Integration

These reports can be integrated into:

- **CI/CD pipelines** - Automated checks on every commit
- **Status badges** - Display current status in README
- **Monitoring systems** - Track project health over time
- **Documentation** - Embed current status in docs
