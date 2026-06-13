# UUIDv8-FID-v2

This README is a non-normative public landing page.

The canonical specification remains the split section files under `uuidv8-fid-v2/`.

Start with `00-index.md` for the canonical read order.

Do not add normative requirements to this README.

## Start here

[00-index.md](00-index.md)

The canonical specification should be read in numeric order from the index.

## Current registry state

- `0x10`        assigned: time48-rand
- `0x11..0xef`  unassigned
- `0x00..0x0f`  reserved
- `0xf0..0xff`  reserved

See:
- [20-registry.md](20-registry.md)
- [formats/10-time48-rand.md](formats/10-time48-rand.md)

## Implementer material

See:
- [conformance/structural-test-vectors.md](conformance/structural-test-vectors.md)
- [conformance/structural-test-vectors.json](conformance/structural-test-vectors.json)
- [implementation/pseudocode.md](implementation/pseudocode.md)
- [implementation/implementation-checklist.md](implementation/implementation-checklist.md)

Implementation material is derived support material and does not redefine the specification.

## Publication and release-candidate material

See:
- [publication/reader-guide.md](publication/reader-guide.md)
- [publication/source-map.md](publication/source-map.md)
- [publication/release-candidate-checklist.md](publication/release-candidate-checklist.md)
- [release/release-candidate-notes.md](release/release-candidate-notes.md)
- [release/pre-publication-sweep.md](release/pre-publication-sweep.md)
- [tools/README.md](tools/README.md)

These documents are non-normative and do not declare a final release.

## Local consistency check

```text
python uuidv8-fid-v2/tools/check_consistency.py
```

The checker should exit with status code 0 before treating the document set as publication-ready.
