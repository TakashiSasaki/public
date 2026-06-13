# UUIDv8-FID-v2 Specification

This directory contains the canonical UUIDv8-FID-v2 specification.

Read the files in numeric order.

## Sections

1. `01-status-scope.md`
2. `02-terminology.md`
3. `03-string-representation.md`
4. `04-bit-layout.md`
5. `05-part3-part4-layout.md`
6. `06-format-id-fields.md`
7. `07-parsing-generation.md`
8. `08-extraction-construction.md`
9. `09-validation.md`
10. `11-compatibility-security.md`
11. `12-examples-summary.md`
12. `20-registry.md`

The top-level files `../uuidv8-fid-v2.md` and `../uuidv8-fid-v2-registry.md` are non-normative entry-point stubs only.

## Format-Specific Documents

Concrete UUIDv8-FID-v2 Format ID specifications are placed under:

- `formats/`

The directory currently includes the specification sections. The first assigned format is `formats/10-time48-rand.md` for `format_id = 0x10`.

## Conformance Material

Derived conformance material for implementers to verify parsing, extraction, and validation behavior is placed under:

- `conformance/`

## Implementation Guidance

Derived non-normative implementation guidance, pseudocode, and checklists for UUIDv8-FID-v2 are placed under:

- `implementation/`

## Audit and Release Readiness

Derived non-normative audit and release-readiness material is placed under:

- `audit/`

## Publication and Reader Guidance

Derived non-normative publication and reader guidance is placed under:

- `publication/`
