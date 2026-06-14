# UUIDv8-FID-v2 Release-Candidate Execution Record

This document is strictly non-normative and does not declare a final release. The canonical specification remains the split files under `uuidv8-fid-v2/`.

## Command Execution Results

Commit SHA: `0d58657d131cfa40e3bb71de2431e2614039869a`

| Command | Status | Exit code | Summary | Notes |
|---------|--------|-----------|---------|-------|
| `python uuidv8-fid-v2/tools/check_consistency.py` | PASS | 0 | PASS with warnings | 1 warning regarding stale phrase |
| `python uuidv8-fid-v2/tools/test_check_consistency.py` | PASS | 0 | PASS | All mutations passed |

```text
WARN: uuidv8-fid-v2/20-registry.md:9 - Found stale phrase 'registry scaffold'
```

## Manual Invariant Review

- [x] `0x10` remains the only assigned concrete Format ID
- [x] `0x11..0xef` remains unassigned
- [x] `0x00..0x0f` remains reserved
- [x] `0xf0..0xff` remains reserved
- [x] `0x7a` remains an unassigned extraction/conformance example only
- [x] top-level stubs remain non-normative
- [x] final release is not declared
- [x] no generated single-file specification artifact exists
- [x] no CI workflow was added in this stride

## Limitations

This document is an execution and release-readiness record only. It does not change any specification semantics or introduce normative requirements.
