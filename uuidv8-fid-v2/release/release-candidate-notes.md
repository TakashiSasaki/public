# UUIDv8-FID-v2 Release Candidate Notes

This document is non-normative.
This document describes release-candidate readiness only.
It does not declare a final release.
The canonical specification remains under `uuidv8-fid-v2/`.

## 1. Current release-candidate scope

* UUIDv8-FID-v2 defines an 8-bit logical Format ID model.
* `format_type` and `format_subtype` are physically placed in UUIDv8-compatible fields.
* `format_id = (format_type << 4) | format_subtype`.
* The initial registry assigns only `0x10 time48-rand`.
* `0x11..0xef` remains unassigned.
* `0x00..0x0f` and `0xf0..0xff` remain reserved.

## 2. Included supporting material

* conformance vectors;
* JSON fixture;
* implementation pseudocode;
* implementation checklist;
* audit checklist;
* publication guidance;
* local consistency tooling.

## 3. Required pre-publication checks

* run `python uuidv8-fid-v2/tools/check_consistency.py`;
* confirm no hard failures;
* review any warnings;
* verify top-level stubs remain non-normative;
* verify no new Format ID was introduced accidentally;
* verify no generated single-file artifact is allowed except the committed generated derivative publication form at `uuidv8-fid-v2/publication/uuidv8-fid-v2-single-file.md`.

## 4. Not included in this release candidate

* no additional concrete Format IDs;
* no CI workflow;
* no formal external registry process;
* no language-specific reference implementation.
