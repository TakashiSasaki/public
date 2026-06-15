# UUIDv8-FID-v2 Pre-Publication Sweep

This document is non-normative.
This document does not declare a final release.
This document records the final checks to perform before publication.
The canonical specification remains the split files under `uuidv8-fid-v2/`.

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

## 1. Required local command

```text
python uuidv8-fid-v2/tools/check_consistency.py
python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings
python uuidv8-fid-v2/tools/test_check_consistency.py
python uuidv8-fid-v2/tools/assemble_single_file.py --check
python uuidv8-fid-v2/tools/assemble_single_file.py --verify-output uuidv8-fid-v2/publication/uuidv8-fid-v2-single-file.md
python uuidv8-fid-v2/tools/test_assemble_single_file.py
```

All commands must exit with status code 0 before publication.
The strict warning-mode command should exit with status code 0 for warning-free release-candidate readiness.

Command execution results may be recorded in `release-candidate-execution-record.md`.

## 2. Required manual review

- [ ] Confirm the checker harness exits with status code 0.
- [ ] Confirm `uuidv8-fid-v2/README.md` remains non-normative.
- [ ] Confirm public entry-point stubs point to the public landing page and canonical specification.
- [ ] Confirm `publication-candidate-manifest.md` is reviewed.
- [ ] Confirm `publication-package-verification.md` is reviewed.
- [ ] Confirm the navigation smoke test is current.
- [ ] Confirm publication-facing relative links resolve locally.
- [ ] Confirm dual-form-publication-verification-record.md is current.
- [ ] Confirm no new Format ID was assigned.
- [ ] Confirm `0x10` remains the only assigned concrete Format ID.
- [ ] Confirm `0x11..0xef` remains unassigned.
- [ ] Confirm `0x00..0x0f` and `0xf0..0xff` remain reserved.
- [ ] Confirm `0x7a` remains an unassigned extraction/conformance example only.
- [ ] Confirm top-level stubs remain non-normative.
- [ ] Confirm release-candidate notes do not declare a final release.
- [ ] Confirm exactly one generated single-file specification artifact is committed at the allowed path.
- [ ] Confirm no CI workflow was added for UUIDv8-FID-v2 in this stride.

## 2.5 Release candidate freeze and human review gate

- [ ] Confirm `release-candidate-freeze.md` has been established.
- [ ] Confirm `human-review-record.md` checklists are complete and invariants are upheld.
- [ ] Confirm `release-decision-gate.md` criteria are satisfied for this candidate package.

## 3. Acceptable remaining future work

The following may remain future work after publication:

* CI integration for the local checker;
* rendered HTML packaging;
* language-specific implementation examples;
* additional Format ID assignments only when binary payload layout or normative interpretation changes.
