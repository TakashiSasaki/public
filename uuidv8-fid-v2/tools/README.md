# UUIDv8-FID-v2 Local Consistency Tooling

This directory contains local, manually runnable consistency checks for UUIDv8-FID-v2.

These tools do not define the specification and do not introduce new normative requirements.

## Release-candidate use

Run this checker before treating the document set as a release candidate.

Warnings should be reviewed. Warnings do not cause a nonzero exit code unless a hard check fails.

## Usage

```text
python uuidv8-fid-v2/tools/check_consistency.py
```

## Expected Behavior

* exits with status code 0 if all checks pass;
* exits with nonzero status code if any check fails;
* prints a concise pass/fail summary.

Note: The script is intentionally local tooling and is not CI in this stride.
