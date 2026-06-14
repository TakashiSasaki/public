# UUIDv8-FID-v2 Publication Package Verification

## Purpose

This document is non-normative. This document does not declare a final release.

This document provides a concise verification checklist for a reviewer preparing the publication candidate package.

## Verification Checklist

- [ ] Review publication-candidate-manifest.md.
- [ ] Confirm all manifest paths exist.
- [ ] Confirm canonical split files remain under `uuidv8-fid-v2/`.
- [ ] Confirm top-level stubs remain non-normative.
- [ ] Confirm no generated single-file specification artifact exists.
- [ ] Review single-file-assembly-dry-run-record.md.
- [ ] Confirm no rendered HTML package artifact is committed.
- [ ] Confirm no CI workflow was added in this stride.
- [ ] Run `python uuidv8-fid-v2/tools/check_consistency.py`.
- [ ] Run `python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings`.
- [ ] Run `python uuidv8-fid-v2/tools/test_check_consistency.py`.
- [ ] Confirm release-candidate-execution-record.md is current.
- [ ] Confirm human-review-record.md invariants are successfully verified.
- [ ] Confirm release-decision-gate.md checks and review requirements are met.
- [ ] Confirm final release is not declared.
