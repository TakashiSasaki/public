# UUIDv8-FID-v2 Release Candidate Checklist

## Purpose

This document provides a checklist for preparing a release candidate without declaring a release.

## 1. Source consistency

- [ ] Run the audit consistency checklist.
- [ ] Run `python uuidv8-fid-v2/tools/check_consistency.py`.
- [ ] Confirm the checker exits with status code 0.
- [ ] Run `python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings`.
- [ ] Confirm the strict checker exits with status code 0.
- [ ] Run `python uuidv8-fid-v2/tools/test_check_consistency.py`.
- [ ] Confirm the checker harness exits with status code 0.
- [ ] Review any checker warnings.
- [ ] Review `uuidv8-fid-v2/release/pre-publication-sweep.md`.
- [ ] Verify `00-index.md` links to all major directories.
- [ ] Verify the source map is up to date.
- [ ] Verify top-level stubs remain non-normative.

## 2. Registry consistency

- [ ] Verify `0x10` is the only assigned concrete Format ID.
- [ ] Verify `0x11..0xef` remains unassigned.
- [ ] Verify `0x00..0x0f` and `0xf0..0xff` remain reserved.
- [ ] Verify `0x7a` remains an unassigned example only.

## 3. Test-vector consistency

- [ ] Verify Markdown conformance vectors contain cases A through I.
- [ ] Verify JSON conformance vectors contain cases A through I.
- [ ] Verify JSON parses as valid JSON.
- [ ] Verify deterministic `time48-rand` vectors are unchanged.

## 4. Publication preparation

- [ ] Review `publication-candidate-manifest.md`.
- [ ] Review `publication-package-verification.md`.
- [ ] Review `release-candidate-execution-record.md`.
- [ ] Confirm `release-candidate-execution-record.md` does not declare a final release.
- [ ] Confirm all local commands are recorded in `release-candidate-execution-record.md`.
- [ ] Confirm command outcomes in `release-candidate-execution-record.md` are not fabricated.
- [ ] Confirm `--fail-on-warnings` mode was run when refreshing the release-candidate execution record.
- [ ] Confirm no stale warnings remain, or any remaining warnings are explicitly explained.
- [ ] Verify `uuidv8-fid-v2/README.md` is current.
- [ ] Verify top-level entry-point stubs point to the public landing page and canonical specification.
- [ ] Verify public-facing entry points remain non-normative.
- [ ] Verify the reader guide is current.
- [ ] Verify `uuidv8-fid-v2/publication/navigation-smoke-test.md` is current.
- [ ] Verify all relative Markdown links used by publication-facing documents resolve locally.
- [ ] Verify the single-file assembly plan is current.
- [ ] Verify the single-file assembly dry run executes successfully.
- [ ] Verify `single-file-assembly-dry-run-record.md` is current.
- [ ] Verify `dual-form-publication-verification-record.md` is current.
- [ ] Verify the single-file artifact exactly matches regenerated output.
- [ ] Verify exactly one generated single-file artifact is allowed, at `uuidv8-fid-v2/publication/uuidv8-fid-v2-single-file.md`, and it was not manually edited as source of truth.
- [ ] Verify release-candidate notes are current.
- [ ] Verify publication-readiness summary is current.
- [ ] Verify pre-publication sweep notes are current.
- [ ] Verify post-publication work does not assign new Format IDs.
- [ ] Verify no final release is declared unless explicitly intended.

## 4.5. Release candidate freeze and human review gate

- [ ] Verify `release-candidate-freeze.md` bounds the package review correctly.
- [ ] Verify `human-review-record.md` captures all invariants accurately.
- [ ] Verify `release-decision-gate.md` correctly defines the required inputs, review, and explicit non-outcomes.

## 5. Scope control

- [ ] Verify no new Format ID was assigned accidentally.
- [ ] Verify no normative requirements were added to derived conformance, implementation, audit, publication, or release documents.
- [ ] Verify no normative requirements were added to top-level stubs.
