# UUIDv8-FID-v2 Navigation Smoke Test

This document is non-normative.
This document does not define the specification.
This document records manual navigation checks for publication readiness.
This document does not declare a final release.

## 1. Public entry path

- [ ] Open `uuidv8-fid-v2/README.md`.
- [ ] Follow the link to `00-index.md`.
- [ ] Follow the link to `20-registry.md`.
- [ ] Follow the link to `formats/10-time48-rand.md`.

## 2. Implementer path

- [ ] From `uuidv8-fid-v2/README.md`, follow links to the Markdown conformance vectors.
- [ ] From `uuidv8-fid-v2/README.md`, follow links to the JSON conformance vectors.
- [ ] From `uuidv8-fid-v2/README.md`, follow links to `implementation/pseudocode.md`.
- [ ] From `uuidv8-fid-v2/README.md`, follow links to `implementation/implementation-checklist.md`.

## 3. Release-candidate path

- [ ] From `uuidv8-fid-v2/README.md`, follow the link to `publication/reader-guide.md`.
- [ ] From `uuidv8-fid-v2/README.md`, follow the link to `publication/source-map.md`.
- [ ] From `uuidv8-fid-v2/README.md`, follow the link to `publication/release-candidate-checklist.md`.
- [ ] From `uuidv8-fid-v2/README.md`, follow the link to `release/pre-publication-sweep.md`.
- [ ] From `uuidv8-fid-v2/README.md`, follow the link to `tools/README.md`.

## 4. Local checker

```text
python uuidv8-fid-v2/tools/check_consistency.py
```

The checker should exit with status code 0 before publication.
