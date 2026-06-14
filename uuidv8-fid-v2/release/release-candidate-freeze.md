# Release Candidate Freeze

This document is explicitly non-normative. It does not declare a final release.

## Purpose

This document defines what the "release-candidate freeze" means for UUIDv8-FID-v2. The freeze establishes a strict review boundary to allow humans to review the complete publication package before any future final-release decision is made.

## Freeze Principles

* **Canonical Specification**: The canonical specification remains the split files under the `uuidv8-fid-v2/` directory.
* **Review Boundary**: The freeze is purely a review boundary, not a final release.
* **Publication Package**: The publication candidate package is strictly defined by `publication/publication-candidate-manifest.md`.
* **Package Verification**: The package verification checklist is defined by `publication/publication-package-verification.md`.
* **Change Semantics**: After the freeze, any changes to canonical specification files should be treated as requiring a new review pass.
* **Derived Material**: Changes to derived publication/release/tooling material may still occur, but must preserve the freeze boundary and must strictly not alter normative semantics.
* **No Single-File Artifacts**: No generated single-file artifact is part of the freeze or committed to the repository.
* **No Rendered HTML**: No rendered HTML package artifact is part of the freeze or committed to the repository.
* **No CI**: No CI workflow is introduced by this freeze.

## Frozen review boundary

| Area | Included? | Role | Review expectation |
|---|---|---|---|
| Canonical split specification | Yes | Core normative text | Full review of invariants and semantics |
| Registry and format-specific files | Yes | Non-normative tracking | Verification of specific assignments |
| Conformance material | Yes | Structural validation cases | Ensuring exact expected vectors |
| Implementation support material | Yes | Language-neutral pseudocode | Verification of correct algorithmic logic |
| Publication candidate package documents | Yes | Package bounds | Ensuring exact file inclusion |
| Release-readiness documents | Yes | Human checkpoints | Completing checklists and reviews |
| Local tooling | Yes | Consistency enforcement | Execution yielding zero errors |
| Excluded generated artifacts | No | Build products | Must remain completely absent |
