# Dual-Form Publication Package

This document is non-normative and does not declare a final release.

This document describes the dual-form publication approach for UUIDv8-FID-v2.

## Publication Forms

The UUIDv8-FID-v2 specification is published in two forms:

1. **Split Canonical Specification Files**: The split files under `uuidv8-fid-v2/` are the canonical source and serve as a canonical publication form.
2. **Generated Single-File Artifact**: A single-file document is generated from the split files to serve as a derived publication form.

The split files remain the canonical source; the committed single-file document is a generated derivative publication form.

## Generated Artifact

The allowed generated artifact path is exactly:
`uuidv8-fid-v2/publication/uuidv8-fid-v2-single-file.md`

This generated artifact is produced by `tools/assemble_single_file.py`. It must be completely reproducible from the split source. A checker must fail if the committed artifact is stale compared to the regenerated output.

## Package Status

The dual-form package is a publication candidate package, not a final release. Future final-release or publication decisions are separate.
