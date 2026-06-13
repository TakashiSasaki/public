# UUIDv8-FID-v2 Source Map

## Purpose

This document records the role of each source file without duplicating normative content.

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
| [uuidv8-fid-v2/publication/source-map.md](source-map.md) | Source map | `derived publication guidance` | The document you are reading. |
| [uuidv8-fid-v2/publication/single-file-assembly-plan.md](single-file-assembly-plan.md) | Single-file assembly plan | `derived publication guidance` | Plan for assembling a single-file publication. |
| [uuidv8-fid-v2/publication/release-candidate-checklist.md](release-candidate-checklist.md) | Release candidate checklist | `derived publication guidance` | Checklist for release candidates. |
| [uuidv8-fid-v2/release/00-index.md](../release/00-index.md) | Release index | `derived release-readiness material` | Index of release readiness material. |
| [uuidv8-fid-v2/release/release-candidate-notes.md](../release/release-candidate-notes.md) | Release candidate notes | `derived release-readiness material` | Release candidate readiness notes. |
| [uuidv8-fid-v2/release/publication-readiness-summary.md](../release/publication-readiness-summary.md) | Publication readiness summary | `derived release-readiness material` | Summary table of release readiness. |
| [uuidv8-fid-v2/release/post-publication-work.md](../release/post-publication-work.md) | Post-publication work | `derived release-readiness material` | Potential future tasks post-publication. |
| [uuidv8-fid-v2/tools/README.md](../tools/README.md) | Tooling README | `derived local tooling` | Instructions for local tools. |
| [uuidv8-fid-v2/tools/check_consistency.py](../tools/check_consistency.py) | Consistency checker | `derived local tooling` | Python script for checking local consistency. |
| [uuidv8-fid-v2.md](../../uuidv8-fid-v2.md) | Top-level specification stub | `non-normative entry-point stub` | Entry-point stub for the specification. |
| [uuidv8-fid-v2-registry.md](../../uuidv8-fid-v2-registry.md) | Top-level registry stub | `non-normative entry-point stub` | Entry-point stub for the registry. |
