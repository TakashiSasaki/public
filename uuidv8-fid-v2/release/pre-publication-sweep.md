# UUIDv8-FID-v2 Pre-Publication Sweep

This document is non-normative.
This document does not declare a final release.
This document records the final checks to perform before publication.
The canonical specification remains the split files under `uuidv8-fid-v2/`.

## 1. Required local command

```text
python uuidv8-fid-v2/tools/check_consistency.py
python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings
python uuidv8-fid-v2/tools/test_check_consistency.py
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
- [ ] Confirm no new Format ID was assigned.
- [ ] Confirm `0x10` remains the only assigned concrete Format ID.
- [ ] Confirm `0x11..0xef` remains unassigned.
- [ ] Confirm `0x00..0x0f` and `0xf0..0xff` remain reserved.
- [ ] Confirm `0x7a` remains an unassigned extraction/conformance example only.
- [ ] Confirm top-level stubs remain non-normative.
- [ ] Confirm release-candidate notes do not declare a final release.
- [ ] Confirm no generated single-file specification was introduced.
- [ ] Confirm no CI workflow was added for UUIDv8-FID-v2 in this stride.

## 3. Acceptable remaining future work

The following may remain future work after publication:

* CI integration for the local checker;
* generated single-file publication artifact;
* rendered HTML packaging;
* language-specific implementation examples;
* additional Format ID assignments only when binary payload layout or normative interpretation changes.
