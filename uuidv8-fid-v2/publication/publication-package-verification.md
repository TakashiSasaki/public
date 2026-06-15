# UUIDv8-FID-v2 Publication Package Verification

## Purpose

This document is non-normative. This document does not declare a final release.

This document provides a concise verification checklist for a reviewer preparing the publication candidate package.

## Status

Current milestone: Dual-Form Publication Package Candidate.
Next gate: Final Publication Decision Gate.
This stride adds derived release-readiness material for making that future decision.
Decision status: pending.

See derived release-readiness material:
- [../release/final-publication-decision-gate.md](../release/final-publication-decision-gate.md)
- [../release/final-publication-decision-checklist.md](../release/final-publication-decision-checklist.md)
- [../release/final-publication-preflight-record.md](../release/final-publication-preflight-record.md)
- [../release/final-publication-decision-summary.md](../release/final-publication-decision-summary.md)

## Verification Checklist

- [ ] Review publication-candidate-manifest.md.
- [ ] Confirm all manifest paths exist.
- [ ] Confirm canonical split files remain under `uuidv8-fid-v2/`.
- [ ] Confirm top-level stubs remain non-normative.
- [ ] Confirm only the allowed generated single-file artifact exists at `uuidv8-fid-v2/publication/uuidv8-fid-v2-single-file.md`.
- [ ] Review single-file-assembly-dry-run-record.md.
- [ ] Review dual-form-publication-verification-record.md.
- [ ] Confirm no rendered HTML package artifact is committed.
- [ ] Confirm no CI workflow was added in this stride.
- [ ] Run `python uuidv8-fid-v2/tools/check_consistency.py`.
- [ ] Run `python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings`.
- [ ] Run `python uuidv8-fid-v2/tools/test_check_consistency.py`.
- [ ] Confirm release-candidate-execution-record.md is current.
- [ ] Confirm human-review-record.md invariants are successfully verified.
- [ ] Confirm release-decision-gate.md checks and review requirements are met.
- [ ] Confirm final release is not declared.
