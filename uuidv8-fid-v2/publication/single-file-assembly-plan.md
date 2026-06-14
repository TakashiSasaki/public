# UUIDv8-FID-v2 Single-File Assembly Plan

## Purpose

This document describes how a future generated single-file publication could be assembled, without actually generating it in this stride and without duplicating normative content manually.

**Important Notes:**

* This document is non-normative.
* This document is an assembly plan only.
* The canonical source remains the split files under `uuidv8-fid-v2/`.
* A generated single-file artifact, if produced in the future, should be treated as generated output unless explicitly designated otherwise.
* See [single-file-assembly-dry-run.md](single-file-assembly-dry-run.md) for how this plan is executed as a dry run.

## Proposed assembly order

1. Title and status note
2. Canonical sections in numeric order:
   * [01-status-scope.md](../01-status-scope.md)
   * [02-terminology.md](../02-terminology.md)
   * [03-string-representation.md](../03-string-representation.md)
   * [04-bit-layout.md](../04-bit-layout.md)
   * [05-part3-part4-layout.md](../05-part3-part4-layout.md)
   * [06-format-id-fields.md](../06-format-id-fields.md)
   * [07-parsing-generation.md](../07-parsing-generation.md)
   * [08-extraction-construction.md](../08-extraction-construction.md)
   * [09-validation.md](../09-validation.md)
   * [11-compatibility-security.md](../11-compatibility-security.md)
   * [12-examples-summary.md](../12-examples-summary.md)
   * [20-registry.md](../20-registry.md)
3. Format-specific documents:
   * [formats/10-time48-rand.md](../formats/10-time48-rand.md)
4. Optional appendices:
   * conformance vectors
   * implementation guidance
   * audit/release-readiness notes
   * publication guidance

## Do not include by default

* top-level non-normative stubs as normative body;
* generated files as source of truth;
* obsolete historical drafts unless explicitly marked historical.
