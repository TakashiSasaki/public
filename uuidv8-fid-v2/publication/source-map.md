# UUIDv8-FID-v2 Source Map

## Purpose

This document records the role of each source file without duplicating normative content.

## Status

Current milestone: Dual-Form Publication Package Candidate.
Next gate: Final Publication Decision Gate.
This stride adds derived release-readiness material for making that future decision.
Decision status: pending.

See derived release-readiness material:
- [release/final-publication-decision-gate.md](../release/final-publication-decision-gate.md)
- [release/final-publication-decision-checklist.md](../release/final-publication-decision-checklist.md)
- [release/final-publication-preflight-record.md](../release/final-publication-preflight-record.md)
- [release/final-publication-decision-summary.md](../release/final-publication-decision-summary.md)

| Path | Role | Normative status | Notes |
| --- | --- | --- | --- |
| [uuidv8-fid-v2/00-index.md](../00-index.md) | Main index | `canonical specification` | Entry point for reading the specification. |
| [uuidv8-fid-v2/01-status-scope.md](../01-status-scope.md) | Status and scope | `canonical specification` | Defines the scope of the specification. |
| [uuidv8-fid-v2/02-terminology.md](../02-terminology.md) | Terminology | `canonical specification` | Defines key terms. |
| [uuidv8-fid-v2/03-string-representation.md](../03-string-representation.md) | String representation | `canonical specification` | Specifies how UUIDs are formatted as strings. |
| [uuidv8-fid-v2/04-bit-layout.md](../04-bit-layout.md) | Bit layout | `canonical specification` | Describes the bit-level structure of the UUID. |
| [uuidv8-fid-v2/05-part3-part4-layout.md](../05-part3-part4-layout.md) | Part 3 and Part 4 layout | `canonical specification` | Details the internal structure of Parts 3 and 4. |
| [uuidv8-fid-v2/06-format-id-fields.md](../06-format-id-fields.md) | Format ID fields | `canonical specification` | Defines the extraction and meaning of format IDs. |
| [uuidv8-fid-v2/07-parsing-generation.md](../07-parsing-generation.md) | Parsing and generation | `canonical specification` | Rules for parsing and generating UUIDs. |
| [uuidv8-fid-v2/08-extraction-construction.md](../08-extraction-construction.md) | Extraction and construction | `canonical specification` | How to extract fields and construct UUIDs. |
| [uuidv8-fid-v2/09-validation.md](../09-validation.md) | Validation | `canonical specification` | Criteria for validating UUIDs. |
| [uuidv8-fid-v2/11-compatibility-security.md](../11-compatibility-security.md) | Compatibility and security | `canonical specification` | Discusses backward compatibility and security considerations. |
| [uuidv8-fid-v2/12-examples-summary.md](../12-examples-summary.md) | Examples and summary | `canonical specification` | Provides examples and summarizes the specification. |
| [uuidv8-fid-v2/20-registry.md](../20-registry.md) | Registry | `canonical specification` | Describes the registry of format IDs. |
| [uuidv8-fid-v2/formats/00-index.md](../formats/00-index.md) | Formats index | `format-specific specification` | Index of format-specific documents. |
| [uuidv8-fid-v2/formats/10-time48-rand.md](../formats/10-time48-rand.md) | time48-rand specification | `format-specific specification` | Details the time48-rand format. |
| [uuidv8-fid-v2/conformance/00-index.md](../conformance/00-index.md) | Conformance index | `derived conformance material` | Index of conformance material. |
| [uuidv8-fid-v2/conformance/structural-test-vectors.md](../conformance/structural-test-vectors.md) | Markdown test vectors | `derived conformance material` | Test vectors formatted in Markdown. |
| [uuidv8-fid-v2/conformance/structural-test-vectors.json](../conformance/structural-test-vectors.json) | JSON test vectors | `derived conformance material` | Test vectors formatted in JSON. |
| [uuidv8-fid-v2/implementation/00-index.md](../implementation/00-index.md) | Implementation index | `derived implementation guidance` | Index of implementation guidance. |
| [uuidv8-fid-v2/implementation/pseudocode.md](../implementation/pseudocode.md) | Pseudocode | `derived implementation guidance` | Language-neutral pseudocode examples. |
| [uuidv8-fid-v2/implementation/implementation-checklist.md](../implementation/implementation-checklist.md) | Implementation checklist | `derived implementation guidance` | Checklist for implementers. |
| [uuidv8-fid-v2/audit/00-index.md](../audit/00-index.md) | Audit index | `derived audit material` | Index of audit material. |
| [uuidv8-fid-v2/audit/consistency-checklist.md](../audit/consistency-checklist.md) | Consistency checklist | `derived audit material` | Checklist for ensuring internal consistency. |
| [uuidv8-fid-v2/audit/release-readiness.md](../audit/release-readiness.md) | Release readiness | `derived audit material` | Notes on release readiness. |
| [uuidv8-fid-v2/audit/known-non-goals.md](../audit/known-non-goals.md) | Known non-goals | `derived audit material` | Outlines topics out of scope. |
| [uuidv8-fid-v2/publication/00-index.md](00-index.md) | Publication index | `derived publication guidance` | Index of publication and reader guidance. |
| [uuidv8-fid-v2/publication/reader-guide.md](reader-guide.md) | Reader guide | `derived publication guidance` | Guide on how to navigate the documents. |
| [uuidv8-fid-v2/publication/navigation-smoke-test.md](navigation-smoke-test.md) | Navigation smoke test | `derived publication guidance` | Manual navigation checks for publication readiness. |
| [uuidv8-fid-v2/publication/source-map.md](source-map.md) | Source map | `derived publication guidance` | The document you are reading. |
| [uuidv8-fid-v2/publication/single-file-assembly-plan.md](single-file-assembly-plan.md) | Single-file assembly plan | `derived publication guidance` | Plan for assembling a single-file publication. |
| [uuidv8-fid-v2/publication/single-file-assembly-dry-run.md](single-file-assembly-dry-run.md) | Single-file assembly dry run | `derived publication guidance` | Instructions for running the assembly dry-run tool. |
| [uuidv8-fid-v2/publication/dual-form-publication-package.md](dual-form-publication-package.md) | Dual-form publication package | `derived publication guidance` | Details on the dual-form publication approach. |
| [uuidv8-fid-v2/publication/uuidv8-fid-v2-single-file.md](uuidv8-fid-v2-single-file.md) | Generated single-file artifact | `generated derivative publication form` | The derived single-file document. |
| [uuidv8-fid-v2/publication/release-candidate-checklist.md](release-candidate-checklist.md) | Release candidate checklist | `derived publication guidance` | Checklist for release candidates. |
| [uuidv8-fid-v2/publication/publication-candidate-manifest.md](publication-candidate-manifest.md) | Publication candidate manifest | `derived publication guidance` | Defines the boundaries of the publication candidate package. |
| [uuidv8-fid-v2/publication/publication-package-verification.md](publication-package-verification.md) | Publication package verification | `derived publication guidance` | Verification checklist for the publication package. |
| [uuidv8-fid-v2/release/00-index.md](../release/00-index.md) | Release index | `derived release-readiness material` | Index of release readiness material. |
| [uuidv8-fid-v2/release/release-candidate-notes.md](../release/release-candidate-notes.md) | Release candidate notes | `derived release-readiness material` | Release candidate readiness notes. |
| [uuidv8-fid-v2/release/release-candidate-execution-record.md](../release/release-candidate-execution-record.md) | Release candidate execution record | `derived release-readiness material` | Release candidate execution record. |
| [uuidv8-fid-v2/release/single-file-assembly-dry-run-record.md](../release/single-file-assembly-dry-run-record.md) | Single-file assembly dry run record | `derived release-readiness material` | Single-file assembly dry run execution record. |
| [uuidv8-fid-v2/release/dual-form-publication-verification-record.md](../release/dual-form-publication-verification-record.md) | Dual-form publication verification record | `derived release-readiness material` | Dual-form publication verification record. |
| [uuidv8-fid-v2/release/publication-readiness-summary.md](../release/publication-readiness-summary.md) | Publication readiness summary | `derived release-readiness material` | Summary table of release readiness. |
| [uuidv8-fid-v2/release/release-candidate-freeze.md](../release/release-candidate-freeze.md) | Release candidate freeze | `derived release-readiness material` | Release candidate freeze boundary definition. |
| [uuidv8-fid-v2/release/human-review-record.md](../release/human-review-record.md) | Human review record | `derived release-readiness material` | Template for manual review of invariants. |
| [uuidv8-fid-v2/release/release-decision-gate.md](../release/release-decision-gate.md) | Release decision gate | `derived release-readiness material` | Conditions and allowed outcomes for release. |
| [uuidv8-fid-v2/release/post-publication-work.md](../release/post-publication-work.md) | Post-publication work | `derived release-readiness material` | Potential future tasks post-publication. |
| [uuidv8-fid-v2/release/pre-publication-sweep.md](../release/pre-publication-sweep.md) | Pre-publication sweep | `derived release-readiness material` | Final pre-publication check list and sweep notes. |
| [uuidv8-fid-v2/release/final-publication-decision-gate.md](../release/final-publication-decision-gate.md) | Final publication decision gate | `derived release-readiness material` | Decision gate definitions for final publication. |
| [uuidv8-fid-v2/release/final-publication-decision-checklist.md](../release/final-publication-decision-checklist.md) | Final publication decision checklist | `derived release-readiness material` | Checklist for making the final publication decision. |
| [uuidv8-fid-v2/release/final-publication-preflight-record.md](../release/final-publication-preflight-record.md) | Final publication preflight record | `derived release-readiness material` | Preflight command execution record for the decision gate. |
| [uuidv8-fid-v2/release/final-publication-decision-summary.md](../release/final-publication-decision-summary.md) | Final publication decision summary | `derived release-readiness material` | Current readiness state summary for the decision gate. |
| [uuidv8-fid-v2/tools/README.md](../tools/README.md) | Tooling README | `derived local tooling` | Instructions for local tools. |
| [uuidv8-fid-v2/tools/assemble_single_file.py](../tools/assemble_single_file.py) | Single-file assembly tool | `derived local tooling` | Python script for single-file assembly dry run. |
| [uuidv8-fid-v2/tools/test_assemble_single_file.py](../tools/test_assemble_single_file.py) | Assembly tool test harness | `derived local tooling` | Test harness for the assembly tool. |
| [uuidv8-fid-v2/tools/check_consistency.py](../tools/check_consistency.py) | Consistency checker | `derived local tooling` | Python script for checking local consistency. |
| [uuidv8-fid-v2/tools/test_check_consistency.py](../tools/test_check_consistency.py) | Checker harness | `derived local tooling` | Local self-test harness for the consistency checker. |
| [uuidv8-fid-v2/README.md](../README.md) | Public landing page | `non-normative public landing page` | Public entry point for readers. |
| [uuidv8-fid-v2.md](../../uuidv8-fid-v2.md) | Top-level specification stub | `non-normative entry-point stub` | Entry-point stub for the specification. |
| [uuidv8-fid-v2-registry.md](../../uuidv8-fid-v2-registry.md) | Top-level registry stub | `non-normative entry-point stub` | Entry-point stub for the registry. |
