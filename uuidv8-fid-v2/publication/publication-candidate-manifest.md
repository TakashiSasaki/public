# UUIDv8-FID-v2 Publication Candidate Manifest

## Purpose

This document is non-normative. This document does not declare a final release.

This manifest defines the boundaries of the publication candidate package for pre-publication review. The canonical specification remains the split files under `uuidv8-fid-v2/`.

## 1. Canonical split specification files

| Path | Role | Status | Notes |
| --- | --- | --- | --- |
| [../00-index.md](../00-index.md) | Main index | `canonical specification` | Entry point for reading the specification. |
| [../01-status-scope.md](../01-status-scope.md) | Status and scope | `canonical specification` | Defines the scope of the specification. |
| [../02-terminology.md](../02-terminology.md) | Terminology | `canonical specification` | Defines key terms. |
| [../03-string-representation.md](../03-string-representation.md) | String representation | `canonical specification` | Specifies how UUIDs are formatted as strings. |
| [../04-bit-layout.md](../04-bit-layout.md) | Bit layout | `canonical specification` | Describes the bit-level structure of the UUID. |
| [../05-part3-part4-layout.md](../05-part3-part4-layout.md) | Part 3 and Part 4 layout | `canonical specification` | Details the internal structure of Parts 3 and 4. |
| [../06-format-id-fields.md](../06-format-id-fields.md) | Format ID fields | `canonical specification` | Defines the extraction and meaning of format IDs. |
| [../07-parsing-generation.md](../07-parsing-generation.md) | Parsing and generation | `canonical specification` | Rules for parsing and generating UUIDs. |
| [../08-extraction-construction.md](../08-extraction-construction.md) | Extraction and construction | `canonical specification` | How to extract fields and construct UUIDs. |
| [../09-validation.md](../09-validation.md) | Validation | `canonical specification` | Criteria for validating UUIDs. |
| [../11-compatibility-security.md](../11-compatibility-security.md) | Compatibility and security | `canonical specification` | Discusses backward compatibility and security considerations. |
| [../12-examples-summary.md](../12-examples-summary.md) | Examples and summary | `canonical specification` | Provides examples and summarizes the specification. |
| [../20-registry.md](../20-registry.md) | Registry | `canonical specification` | Describes the registry of format IDs. |

## 2. Registry and format-specific files

| Path | Role | Status | Notes |
| --- | --- | --- | --- |
| [../formats/00-index.md](../formats/00-index.md) | Formats index | `format-specific specification` | Index of format-specific documents. |
| [../formats/template.md](../formats/template.md) | Format template | `format-specific specification` | Template for format documents. |
| [../formats/10-time48-rand.md](../formats/10-time48-rand.md) | time48-rand specification | `format-specific specification` | Details the time48-rand format. |

## 3. Conformance material

| Path | Role | Status | Notes |
| --- | --- | --- | --- |
| [../conformance/00-index.md](../conformance/00-index.md) | Conformance index | `derived conformance material` | Index of conformance material. |
| [../conformance/structural-test-vectors.md](../conformance/structural-test-vectors.md) | Markdown test vectors | `derived conformance material` | Test vectors formatted in Markdown. |
| [../conformance/structural-test-vectors.json](../conformance/structural-test-vectors.json) | JSON test vectors | `derived conformance material` | Test vectors formatted in JSON. |

## 4. Implementation support material

| Path | Role | Status | Notes |
| --- | --- | --- | --- |
| [../implementation/00-index.md](../implementation/00-index.md) | Implementation index | `derived implementation support` | Index of implementation guidance. |
| [../implementation/pseudocode.md](../implementation/pseudocode.md) | Pseudocode | `derived implementation support` | Language-neutral pseudocode examples. |
| [../implementation/implementation-checklist.md](../implementation/implementation-checklist.md) | Implementation checklist | `derived implementation support` | Checklist for implementers. |

## 5. Audit material

| Path | Role | Status | Notes |
| --- | --- | --- | --- |
| [../audit/00-index.md](../audit/00-index.md) | Audit index | `derived audit material` | Index of audit material. |
| [../audit/consistency-checklist.md](../audit/consistency-checklist.md) | Consistency checklist | `derived audit material` | Checklist for ensuring internal consistency. |
| [../audit/release-readiness.md](../audit/release-readiness.md) | Release readiness | `derived audit material` | Notes on release readiness. |
| [../audit/known-non-goals.md](../audit/known-non-goals.md) | Known non-goals | `derived audit material` | Outlines topics out of scope. |

## 6. Publication guidance

| Path | Role | Status | Notes |
| --- | --- | --- | --- |
| [00-index.md](00-index.md) | Publication index | `derived publication guidance` | Index of publication and reader guidance. |
| [reader-guide.md](reader-guide.md) | Reader guide | `derived publication guidance` | Guide on how to navigate the documents. |
| [source-map.md](source-map.md) | Source map | `derived publication guidance` | Records the role of each file. |
| [single-file-assembly-plan.md](single-file-assembly-plan.md) | Single-file assembly plan | `derived publication guidance` | Plan for assembling a single-file publication. |
| [navigation-smoke-test.md](navigation-smoke-test.md) | Navigation smoke test | `derived publication guidance` | Manual navigation checks. |
| [release-candidate-checklist.md](release-candidate-checklist.md) | Release candidate checklist | `derived publication guidance` | Checklist for release candidates. |
| [publication-candidate-manifest.md](publication-candidate-manifest.md) | Publication candidate manifest | `derived publication guidance` | The document you are reading. |
| [publication-package-verification.md](publication-package-verification.md) | Publication package verification | `derived publication guidance` | Checklist for verifying the publication candidate package. |

## 7. Release-readiness material

| Path | Role | Status | Notes |
| --- | --- | --- | --- |
| [../release/00-index.md](../release/00-index.md) | Release index | `derived release-readiness material` | Index of release readiness material. |
| [../release/release-candidate-notes.md](../release/release-candidate-notes.md) | Release candidate notes | `derived release-readiness material` | Release candidate readiness notes. |
| [../release/publication-readiness-summary.md](../release/publication-readiness-summary.md) | Publication readiness summary | `derived release-readiness material` | Summary table of release readiness. |
| [../release/post-publication-work.md](../release/post-publication-work.md) | Post-publication work | `derived release-readiness material` | Potential future tasks post-publication. |
| [../release/pre-publication-sweep.md](../release/pre-publication-sweep.md) | Pre-publication sweep | `derived release-readiness material` | Final pre-publication check list and sweep notes. |
| [../release/release-candidate-execution-record.md](../release/release-candidate-execution-record.md) | Execution record | `derived release-readiness material` | Release candidate execution record. |

## 8. Local tooling

| Path | Role | Status | Notes |
| --- | --- | --- | --- |
| [../tools/README.md](../tools/README.md) | Tooling README | `local tooling` | Instructions for local tools. |
| [../tools/check_consistency.py](../tools/check_consistency.py) | Consistency checker | `local tooling` | Python script for checking local consistency. |
| [../tools/test_check_consistency.py](../tools/test_check_consistency.py) | Checker harness | `local tooling` | Local self-test harness for the consistency checker. |

## 9. Top-level non-normative entry points

| Path | Role | Status | Notes |
| --- | --- | --- | --- |
| [../../uuidv8-fid-v2.md](../../uuidv8-fid-v2.md) | Specification stub | `non-normative entry point` | Entry-point stub for the specification. |
| [../../uuidv8-fid-v2-registry.md](../../uuidv8-fid-v2-registry.md) | Registry stub | `non-normative entry point` | Entry-point stub for the registry. |

## 10. Explicitly excluded/generated artifacts

| Artifact | Status | Notes |
| --- | --- | --- |
| generated single-file specification artifacts | `excluded generated artifact` | Must not be checked in during this stride. |
| rendered HTML package artifacts | `excluded generated artifact` | Must not be checked in during this stride. |
| CI workflow outputs | `excluded generated artifact` | Must not be added during this stride. |
| historical drafts unless explicitly marked historical | `excluded generated artifact` | Not included. |

## Tooling Execution

A valid package must pass the local consistency checks. The following commands should exit with code 0:

```text
python uuidv8-fid-v2/tools/check_consistency.py
python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings
python uuidv8-fid-v2/tools/test_check_consistency.py
```
