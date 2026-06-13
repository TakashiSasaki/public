# UUIDv8-FID-v2 Release Candidate Checklist

## Purpose

This document provides a checklist for preparing a release candidate without declaring a release.

## 1. Source consistency

- [ ] Run the audit consistency checklist.
- [ ] Run `python uuidv8-fid-v2/tools/check_consistency.py`.
- [ ] Confirm the checker exits with status code 0.
- [ ] Review any checker warnings.
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

- [ ] Verify the reader guide is current.
- [ ] Verify the single-file assembly plan is current.
- [ ] Verify no generated single-file artifact was manually edited as source of truth.
- [ ] Verify release-candidate notes are current.
- [ ] Verify publication-readiness summary is current.
- [ ] Verify post-publication work does not assign new Format IDs.
- [ ] Verify no final release is declared unless explicitly intended.

## 5. Scope control

- [ ] Verify no new Format ID was assigned accidentally.
- [ ] Verify no normative requirements were added to derived conformance, implementation, audit, or publication documents.
- [ ] Verify no normative requirements were added to top-level stubs.
