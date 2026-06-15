# Release Decision Gate

This document is explicitly non-normative. It does not declare a final release.

## Purpose

This document defines what must be true before a future final-release decision can be made. It establishes the mandatory checks, reviews, and allowable outcomes for evaluating the release candidate package.

## Inputs

The decision gate operates on the defined release candidate package, bounded by:
* The canonical specifications under `uuidv8-fid-v2/`
* `publication/publication-candidate-manifest.md`
* `release/release-candidate-freeze.md`

## Required local checks

All local consistency checks and test harnesses must execute successfully with no failures:
* `python uuidv8-fid-v2/tools/check_consistency.py`
* `python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings`
* `python uuidv8-fid-v2/tools/test_check_consistency.py`
* `python uuidv8-fid-v2/tools/assemble_single_file.py --check`
* `python uuidv8-fid-v2/tools/test_assemble_single_file.py`

## Required human review

A complete review must be recorded and passed, satisfying the constraints set out in:
* `release/human-review-record.md`
* `release/dual-form-publication-verification-record.md`

## Status

Current milestone: Dual-Form Publication Package Candidate.
Next gate: Final Publication Decision Gate.
This stride adds derived release-readiness material for making that future decision.
Decision status: pending.

See derived release-readiness material:
* `final-publication-decision-gate.md`
* `final-publication-decision-checklist.md`
* `final-publication-preflight-record.md`
* `final-publication-decision-summary.md`

## Allowed outcomes

Following the completion of the required checks and review, the allowed outcomes are strictly limited to:

* continue review
* revise publication package
* prepare a future final release PR
* defer publication

## Explicit non-outcomes

* This document does not itself publish or finalize UUIDv8-FID-v2.
* This document does not declare a final release.
* This document does not generate a single-file artifact.
