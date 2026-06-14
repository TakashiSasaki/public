# UUIDv8-FID-v2 Local Consistency Tooling

This directory contains local, manually runnable consistency checks for UUIDv8-FID-v2.

These tools do not define the specification and do not introduce new normative requirements.

## Release-candidate use

Run this checker before treating the document set as a release candidate.

Warnings should be reviewed. Warnings do not cause a nonzero exit code unless a hard check fails.

## Coverage

The checker validates selected file existence, registry invariants, conformance-vector structure, source-map entries, release-candidate references, public entry-point references, local relative Markdown links, and generated-single-file guards. The checker harness tests this functionality.

## Harness

```text
python uuidv8-fid-v2/tools/test_check_consistency.py
```

## Assembly Tooling

The assembly tool generates or verifies a single-file document. To regenerate the allowed committed single-file artifact, run:

```text
python uuidv8-fid-v2/tools/assemble_single_file.py --output uuidv8-fid-v2/publication/uuidv8-fid-v2-single-file.md --force
```

To verify the committed artifact matches the regenerated output exactly, run:

```text
python uuidv8-fid-v2/tools/assemble_single_file.py --verify-output uuidv8-fid-v2/publication/uuidv8-fid-v2-single-file.md
```

The tool can also perform a dry run without writing a file:

```text
python uuidv8-fid-v2/tools/assemble_single_file.py --check
```

The assembly test harness ensures its functionality remains correct:

```text
python uuidv8-fid-v2/tools/test_assemble_single_file.py
```

* the harness tests the consistency checker against baseline and temporary mutated copies;
* it writes only to temporary directories;
* it uses only Python standard library;
* it is local tooling and not CI.

## Usage

```text
python uuidv8-fid-v2/tools/check_consistency.py
```

This is the normal local consistency check.

For a stricter release-candidate readiness check, you can optionally run:

```text
python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings
```

## Expected Behavior

* exits with status code 0 if all checks pass;
* exits with nonzero status code if any check fails;
* prints a concise pass/fail summary.
* if run with `--fail-on-warnings`, it will also exit with a nonzero status code if any warnings are present.

Note: The script is intentionally local tooling and is not CI in this stride.
