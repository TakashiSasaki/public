# UUIDv8-FID-v2 Reader Guide

## Purpose

This document explains how different readers should navigate the document set.

## 1. For public readers

Start here:

- [../README.md](../README.md)
- [../00-index.md](../00-index.md)

## 2. For specification readers

We recommend reading the canonical section files in numeric order:

- [01-status-scope.md](../01-status-scope.md)
- [02-terminology.md](../02-terminology.md)
- [03-string-representation.md](../03-string-representation.md)
- [04-bit-layout.md](../04-bit-layout.md)
- [05-part3-part4-layout.md](../05-part3-part4-layout.md)
- [06-format-id-fields.md](../06-format-id-fields.md)
- [07-parsing-generation.md](../07-parsing-generation.md)
- [08-extraction-construction.md](../08-extraction-construction.md)
- [09-validation.md](../09-validation.md)
- [11-compatibility-security.md](../11-compatibility-security.md)
- [12-examples-summary.md](../12-examples-summary.md)
- [20-registry.md](../20-registry.md)

## 3. For registry readers

To understand the registry state and defined formats, point to:

- [20-registry.md](../20-registry.md)
- [formats/10-time48-rand.md](../formats/10-time48-rand.md)

The current registry assigns only `0x10 time48-rand`, leaves `0x11..0xef` unassigned, and reserves `0x00..0x0f` and `0xf0..0xff`.

## 4. For implementers

For implementing the specification, point to:

- [07-parsing-generation.md](../07-parsing-generation.md)
- [08-extraction-construction.md](../08-extraction-construction.md)
- [09-validation.md](../09-validation.md)
- [formats/10-time48-rand.md](../formats/10-time48-rand.md)
- [conformance/structural-test-vectors.md](../conformance/structural-test-vectors.md)
- [conformance/structural-test-vectors.json](../conformance/structural-test-vectors.json)
- [implementation/pseudocode.md](../implementation/pseudocode.md)
- [implementation/implementation-checklist.md](../implementation/implementation-checklist.md)

## 5. For reviewers

Reviewers checking consistency and readiness should point to:

- [audit/consistency-checklist.md](../audit/consistency-checklist.md)
- [audit/release-readiness.md](../audit/release-readiness.md)
- [audit/known-non-goals.md](../audit/known-non-goals.md)

## 6. For publication/package maintainers

Maintainers managing the document set should point to:

- [publication/source-map.md](source-map.md)
- [publication/navigation-smoke-test.md](navigation-smoke-test.md)
- [publication/single-file-assembly-plan.md](single-file-assembly-plan.md)
- [publication/single-file-assembly-dry-run.md](single-file-assembly-dry-run.md)
- [publication/release-candidate-checklist.md](release-candidate-checklist.md)
- [publication/publication-candidate-manifest.md](publication-candidate-manifest.md)
- [publication/publication-package-verification.md](publication-package-verification.md)

## 7. For release reviewers

Reviewers preparing a release candidate should point to:

- [release/release-candidate-notes.md](../release/release-candidate-notes.md)
- [release/release-candidate-execution-record.md](../release/release-candidate-execution-record.md)
- [release/release-candidate-freeze.md](../release/release-candidate-freeze.md)
- [release/human-review-record.md](../release/human-review-record.md)
- [release/release-decision-gate.md](../release/release-decision-gate.md)
- [release/publication-readiness-summary.md](../release/publication-readiness-summary.md)
- [release/post-publication-work.md](../release/post-publication-work.md)
- [release/pre-publication-sweep.md](../release/pre-publication-sweep.md)
- [tools/README.md](../tools/README.md)
- [tools/check_consistency.py](../tools/check_consistency.py)
- [tools/test_check_consistency.py](../tools/test_check_consistency.py)
