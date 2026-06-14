# UUIDv8-FID-v2 Single-File Assembly Dry Run

## Non-Normative Status

This document is derived publication guidance and is strictly non-normative. It does not introduce any new requirements and does not declare a final release. The canonical specification remains the split files under `uuidv8-fid-v2/`.

## Purpose

This document explains the single-file assembly dry-run process. A tool has been implemented to perform a trial run of assembling the UUIDv8-FID-v2 specification into a single file, following the plan outlined in `single-file-assembly-plan.md`.

In this stride, the generated single-file artifact is not committed. Any future committed generated single-file artifact requires an explicit separate decision.

## Tooling

The assembly tool is written in Python (standard library only) and can be executed from the repository root.

### Check Mode

To perform a dry run that verifies all required files are present and properly assembled with invariants intact (without writing any output):

```text
python uuidv8-fid-v2/tools/assemble_single_file.py --check
```

### Inspect Output

To assemble the document and print it to stdout for inspection:

```text
python uuidv8-fid-v2/tools/assemble_single_file.py --stdout
```

### Write to Temporary File

To write the assembled output to an external path (e.g., for viewing in a Markdown reader), use the `--output` flag. The tool refuses to write within the repository tree to prevent accidental commits.

```text
python uuidv8-fid-v2/tools/assemble_single_file.py --output /tmp/uuidv8-fid-v2.single.md
```

### Testing the Tool

The tool has an automated test harness to ensure its behavior remains correct:

```text
python uuidv8-fid-v2/tools/test_assemble_single_file.py
```
