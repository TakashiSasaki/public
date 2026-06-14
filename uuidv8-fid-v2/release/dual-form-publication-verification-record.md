# Dual-Form Publication Verification Record

This document is non-normative and does not declare a final release.

This checklist records the execution results for the dual-form publication package candidate milestone.

## Execution Record

| Command | Status | Exit code | Summary | Notes |
|---------|--------|-----------|---------|-------|
| `python uuidv8-fid-v2/tools/assemble_single_file.py --check` | PASS | 0 | Checked generated assembly | Verified generated output invariants |
| `python uuidv8-fid-v2/tools/assemble_single_file.py --output uuidv8-fid-v2/publication/uuidv8-fid-v2-single-file.md --force` | PASS | 0 | Generated single-file artifact | Written to exact allowed path |
| `python uuidv8-fid-v2/tools/assemble_single_file.py --verify-output uuidv8-fid-v2/publication/uuidv8-fid-v2-single-file.md` | PASS | 0 | Verified single-file artifact | Checked for staleness |
| `python uuidv8-fid-v2/tools/assemble_single_file.py --stdout > /dev/null` | PASS | 0 | Streamed stdout assembly | Stdout output works correctly |
| `python uuidv8-fid-v2/tools/test_assemble_single_file.py` | PASS | 0 | Assembly tests | Verified assembly harness logic |
| `python uuidv8-fid-v2/tools/check_consistency.py` | PASS | 0 | Local consistency check | Verified invariants |
| `python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings` | PASS | 0 | Strict consistency check | Verified no warnings |
| `python uuidv8-fid-v2/tools/test_check_consistency.py` | PASS | 0 | Consistency checker tests | Verified checker harness logic |
