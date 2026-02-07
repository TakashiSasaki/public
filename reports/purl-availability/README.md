# PURL Availability Reports

This directory contains reports on the availability and accessibility of PURLs (Persistent URLs) used in the project's schema files.

## Generated Files

- **`latest.txt`** - Human-readable text report with detailed status for each URL
- **`latest.json`** - Machine-readable JSON format for status integration and automation
- **`latest.jsonld`** - JSON-LD format for semantic web applications and schema browsers

## How to Generate

Run the PURL availability check script:

```bash
python scripts/check_purls.py
```

This script:
1. Scans all files in the `schema/` directory for PURLs matching `https://purl.org/gag/*`
2. Checks the HTTP accessibility of each URL
3. Generates three report formats in this directory

## Report Structure

### JSON Format (`latest.json`)

```json
{
  "timestamp": "2026-02-07T12:30:00+09:00",
  "status": "passed",
  "summary": {
    "total": 10,
    "accessible": 10,
    "inaccessible": 0
  },
  "results": [
    {
      "url": "https://purl.org/gag/schema/...",
      "status_code": 200,
      "message": "OK",
      "ok": true
    }
  ]
}
```

### JSON-LD Format (`latest.jsonld`)

Uses the `gag:AvailabilityReport` schema for semantic web compatibility.

## Git Management

- **Tracked**: `latest.*` files (current status)
- **Ignored**: Historical reports (if implemented)

## Related Files

- **Script**: `scripts/check_purls.py`
- **Schema**: `schema/availability.jsonld` (JSON-LD context definition)
