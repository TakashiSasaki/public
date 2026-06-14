import argparse
import os
import sys

# Canonical list of files to assemble, in explicit order.
CANONICAL_FILES = [
    "uuidv8-fid-v2/01-status-scope.md",
    "uuidv8-fid-v2/02-terminology.md",
    "uuidv8-fid-v2/03-string-representation.md",
    "uuidv8-fid-v2/04-bit-layout.md",
    "uuidv8-fid-v2/05-part3-part4-layout.md",
    "uuidv8-fid-v2/06-format-id-fields.md",
    "uuidv8-fid-v2/07-parsing-generation.md",
    "uuidv8-fid-v2/08-extraction-construction.md",
    "uuidv8-fid-v2/09-validation.md",
    "uuidv8-fid-v2/11-compatibility-security.md",
    "uuidv8-fid-v2/12-examples-summary.md",
    "uuidv8-fid-v2/20-registry.md",
    "uuidv8-fid-v2/formats/10-time48-rand.md",
]

GENERATED_NOTICE = (
    "This is generated dry-run output assembled from the split UUIDv8-FID-v2 source files. "
    "The canonical specification remains the split files under uuidv8-fid-v2/."
)

INVARIANT_STRINGS = [
    "format_id = (format_type << 4) | format_subtype",
    "xxxxxxxx-xxxx-8T00-8S00-xxxxxxxxxxxx",
    "0x10",
    "0x7a"
]

def get_repo_root():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.abspath(os.path.join(script_dir, "..", ".."))

def assemble_document(repo_root):
    parts = []
    parts.append(GENERATED_NOTICE)

    for rel_path in CANONICAL_FILES:
        full_path = os.path.join(repo_root, rel_path)
        if not os.path.exists(full_path):
            print(f"Error: Missing required source file: {rel_path}", file=sys.stderr)
            return None

        try:
            with open(full_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            print(f"Error: Could not read {rel_path}: {e}", file=sys.stderr)
            return None

        parts.append(f"\n\n<!-- Source: {rel_path} -->\n\n{content}")

    return "".join(parts)

def is_inside_repo(path, repo_root):
    abs_path = os.path.abspath(path)
    abs_repo_root = os.path.abspath(repo_root)
    # commonpath will return abs_repo_root if abs_path is inside abs_repo_root
    try:
        common = os.path.commonpath([abs_path, abs_repo_root])
        return common == abs_repo_root
    except ValueError:
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Assemble UUIDv8-FID-v2 into a single file.",
        allow_abbrev=False
    )
    parser.add_argument("--check", action="store_true", help="Perform a dry run and verify the assembled content.")
    parser.add_argument("--stdout", action="store_true", help="Print the assembled content to stdout.")
    parser.add_argument("--output", type=str, help="Write the assembled content to the specified path.")
    parser.add_argument("--force", action="store_true", help="Allow writing output inside the repository.")
    parser.add_argument("--verify-output", type=str, metavar="<path>", help="Verify the specified committed artifact matches regenerated output exactly.")
    parser.add_argument("--repo-root", type=str, metavar="<path>", help="Explicitly specify the repository root. Defaults to inferring from __file__.")

    args = parser.parse_args()

    if not args.check and not args.stdout and not args.output and not args.verify_output:
        print("Error: Must specify one of --check, --stdout, --output, or --verify-output.", file=sys.stderr)
        sys.exit(1)

    if args.repo_root:
        repo_root = os.path.abspath(args.repo_root)
    else:
        repo_root = get_repo_root()

    if args.output:
        # Keep user-facing behavior of writing to output path based on cwd
        out_path = os.path.abspath(args.output)
        if is_inside_repo(out_path, repo_root) and not args.force:
            print("Error: Refusing to write output inside the repository without --force.", file=sys.stderr)
            sys.exit(1)

    content = assemble_document(repo_root)
    if content is None:
        sys.exit(1)

    if args.check:
        if GENERATED_NOTICE not in content:
            print("Error: Generated-output notice is missing from the assembled document.", file=sys.stderr)
            sys.exit(1)

        for inv in INVARIANT_STRINGS:
            if inv not in content:
                print(f"Error: Invariant string missing from the assembled document: {inv}", file=sys.stderr)
                sys.exit(1)
        print("Check passed successfully.")

    if args.verify_output:
        verify_path = args.verify_output
        if not os.path.isabs(verify_path):
            verify_path = os.path.join(repo_root, verify_path)
        try:
            with open(verify_path, "r", encoding="utf-8") as f:
                committed_content = f.read()
        except FileNotFoundError:
            print(f"Error: artifact file is missing: {verify_path}", file=sys.stderr)
            sys.exit(1)
        except Exception as e:
            print(f"Error: could not read artifact file {verify_path}: {e}", file=sys.stderr)
            sys.exit(1)

        def normalize_newlines(s):
            return s.replace("\r\n", "\n").replace("\r", "\n")

        if normalize_newlines(committed_content) != normalize_newlines(content):
            print(f"Error: regenerated output does not match the committed artifact: {args.verify_output}", file=sys.stderr)
            sys.exit(1)

        print("Verified: committed single-file artifact matches regenerated output.")

    if args.stdout:
        print(content)

    if args.output:
        try:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Successfully wrote output to {args.output}")
        except Exception as e:
            print(f"Error: Could not write to {args.output}: {e}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main()
