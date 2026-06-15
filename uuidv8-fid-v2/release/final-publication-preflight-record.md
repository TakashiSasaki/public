# Final Publication Preflight Record

This document is strictly non-normative and does not declare a final release.

## Command Execution Record

| Command | Status | Exit code | Summary | Notes |
|---|---|---|---|---|
| `python uuidv8-fid-v2/tools/assemble_single_file.py --check` | PASS | 0 | Check passed successfully. | No issues. |
| `python uuidv8-fid-v2/tools/assemble_single_file.py --verify-output uuidv8-fid-v2/publication/uuidv8-fid-v2-single-file.md` | PASS | 0 | Verified: matches regenerated output. | No issues. |
| `python uuidv8-fid-v2/tools/test_assemble_single_file.py` | PASS | 0 | Ran 9 tests in 0.495s OK | All tests passed. |
| `python uuidv8-fid-v2/tools/check_consistency.py` | PASS | 0 | UUIDv8-FID-v2 consistency checks: PASS | No failures. |
| `python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings` | PASS | 0 | UUIDv8-FID-v2 consistency checks: PASS | No warnings. |
| `python uuidv8-fid-v2/tools/test_check_consistency.py` | PASS | 0 | UUIDv8-FID-v2 checker harness: PASS | All test mutation scenarios passed. |
