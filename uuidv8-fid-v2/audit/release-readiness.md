# UUIDv8-FID-v2 Release Readiness Notes

This document describes the current release-readiness state and future review items without declaring a formal release.

## 1. Current stable core

The current specification establishes a stable foundation:

- 8-bit logical Format ID model is defined.
- physical placement of `format_type` and `format_subtype` is defined.
- registry policy is defined.
- first assigned format `0x10 time48-rand` is defined.
- conformance vectors exist.
- implementation guidance exists.

## 2. Remaining review items before tagging a release

Reviewers should perform the following checks before a final release:

- run `python uuidv8-fid-v2/tools/check_consistency.py`.
- run a cross-file grep for stale phrases such as:
  - `No concrete payload format is assigned`
  - `does not assign concrete values`
  - `registry scaffold` when used in a scaffold-only sense
  - accidental `0x11` assignment
  - accidental `0x7a` assignment
- verify JSON conformance vectors parse as valid JSON.
- verify Markdown and JSON conformance vectors are aligned.
- verify all internal links are correct.
- verify top-level stubs remain non-normative.
- verify no new Format ID was introduced accidentally.

## 3. Future work candidates

The following items are listed as non-commitments for possible future exploration:

- additional concrete formats only when a distinct binary payload layout or normative interpretation is needed.
- possible machine-check scripts for conformance vectors.
- possible implementation examples in a programming language.
- possible publication packaging or generated single-file spec.

Publication-preparation notes are provided under `publication/`.
