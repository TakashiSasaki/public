import os
import sys
import json
import re
import urllib.parse
import argparse
from pathlib import Path

# Determine repo root relative to the script location
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

# Base path for UUIDv8-FID-v2
BASE_DIR = REPO_ROOT / "uuidv8-fid-v2"

# Global state to track status
has_failures = False
has_warnings = False

def report_pass(group_name):
    print(f"PASS: {group_name}")

def report_fail(group_name, message):
    global has_failures
    has_failures = True
    print(f"FAIL: {group_name} - {message}")

def report_warn(file_path, line_no, message):
    global has_warnings
    has_warnings = True
    # For warnings, we just print them. They do not fail a group on their own.
    print(f"WARN: {file_path}:{line_no} - {message}")

def check_file_existence():
    group = "1. File existence checks"
    required_files = [
        "uuidv8-fid-v2/README.md",
        "uuidv8-fid-v2/00-index.md",
        "uuidv8-fid-v2/20-registry.md",
        "uuidv8-fid-v2/formats/10-time48-rand.md",
        "uuidv8-fid-v2/conformance/structural-test-vectors.md",
        "uuidv8-fid-v2/conformance/structural-test-vectors.json",
        "uuidv8-fid-v2/implementation/pseudocode.md",
        "uuidv8-fid-v2/audit/consistency-checklist.md",
        "uuidv8-fid-v2/audit/release-readiness.md",
        "uuidv8-fid-v2/publication/source-map.md",
        "uuidv8-fid-v2/publication/release-candidate-checklist.md",
        "uuidv8-fid-v2/publication/navigation-smoke-test.md",
        "uuidv8-fid-v2/publication/publication-candidate-manifest.md",
        "uuidv8-fid-v2/publication/publication-package-verification.md",
        "uuidv8-fid-v2/release/00-index.md",
        "uuidv8-fid-v2/release/release-candidate-notes.md",
        "uuidv8-fid-v2/release/publication-readiness-summary.md",
        "uuidv8-fid-v2/release/post-publication-work.md",
        "uuidv8-fid-v2/release/pre-publication-sweep.md",
        "uuidv8-fid-v2/release/release-candidate-freeze.md",
        "uuidv8-fid-v2/release/human-review-record.md",
        "uuidv8-fid-v2/release/release-decision-gate.md",
        "uuidv8-fid-v2/tools/test_check_consistency.py",
        "uuidv8-fid-v2.md",
        "uuidv8-fid-v2-registry.md",
    ]

    missing = []
    for f in required_files:
        if not (REPO_ROOT / f).is_file():
            missing.append(f)

    if missing:
        report_fail(group, f"Missing files: {', '.join(missing)}")
    else:
        report_pass(group)

def check_json_validity():
    group = "2. JSON validity checks"
    json_path = BASE_DIR / "conformance" / "structural-test-vectors.json"

    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if data.get("profile") != "UUIDv8-FID-v2":
            report_fail(group, "profile != 'UUIDv8-FID-v2'")
            return None
        if data.get("kind") != "structural-conformance-test-vectors":
            report_fail(group, "kind != 'structural-conformance-test-vectors'")
            return None
        if data.get("normative") is not False:
            report_fail(group, "normative != false")
            return None

        report_pass(group)
        return data
    except Exception as e:
        report_fail(group, f"Error parsing JSON: {e}")
        return None

def check_json_registry_state(data):
    group = "3. JSON registry-state checks"
    if not data:
        report_fail(group, "Skipped due to previous JSON load failure")
        return

    registry = data.get("registry_state", {})
    assigned = registry.get("assigned", {})
    unassigned = registry.get("unassigned_ranges", [])
    reserved = registry.get("reserved_ranges", [])

    errors = []
    if assigned.get("0x10") != "time48-rand":
        errors.append("0x10 not assigned to time48-rand")
    if set(assigned.keys()) != {"0x10"}:
        errors.append("Other keys than 0x10 in assigned")

    if "0x11..0xef" not in unassigned:
        errors.append("0x11..0xef not in unassigned_ranges")

    if "0x00..0x0f" not in reserved:
        errors.append("0x00..0x0f not in reserved_ranges")
    if "0xf0..0xff" not in reserved:
        errors.append("0xf0..0xff not in reserved_ranges")

    if errors:
        report_fail(group, "; ".join(errors))
    else:
        report_pass(group)

def check_json_vectors(data):
    group = "4. JSON vector checks"
    if not data:
        report_fail(group, "Skipped due to previous JSON load failure")
        return

    vectors = data.get("vectors", [])
    cases = [v.get("case") for v in vectors]
    expected_cases = ["A", "B", "C", "D", "E", "F", "G", "H", "I"]

    if cases != expected_cases:
        report_fail(group, f"Vectors do not exactly match expected cases A through I. Found: {cases}")
        return

    errors = []
    for v in vectors:
        case = v.get("case")
        status = v.get("format_id_status")
        extracted_fid = v.get("extracted", {}).get("format_id")
        allowed = v.get("generation_allowed_by_this_version")
        strict_val = v.get("validation", {}).get("strict")

        if case == "A":
            if status != "assigned": errors.append("Case A format_id_status != assigned")
            if extracted_fid != "0x10": errors.append("Case A extracted format_id != 0x10")
            if allowed is not True: errors.append("Case A generation_allowed != true")
        elif case == "B":
            if status != "unassigned": errors.append("Case B format_id_status != unassigned")
            if extracted_fid != "0x7a": errors.append("Case B extracted format_id != 0x7a")
            if allowed is not False: errors.append("Case B generation_allowed != false")
        elif case in ["C", "D"]:
            if status != "reserved": errors.append(f"Case {case} format_id_status != reserved")
        elif case in ["H", "I"]:
            if status != "assigned": errors.append(f"Case {case} format_id_status != assigned")
            if strict_val != "fail": errors.append(f"Case {case} strict validation != fail")

        if case != "A" and allowed is True:
            errors.append(f"Case {case} generation_allowed is true but should only be true for A")

    if errors:
        report_fail(group, "; ".join(errors))
    else:
        report_pass(group)

def check_markdown_conformance_vectors():
    group = "5. Markdown conformance vector checks"
    md_path = BASE_DIR / "conformance" / "structural-test-vectors.md"
    try:
        content = md_path.read_text(encoding='utf-8')
        missing = []
        for case in ["Case A", "Case B", "Case C", "Case D", "Case E", "Case F", "Case G", "Case H", "Case I"]:
            if case not in content:
                missing.append(case)
        if missing:
            report_fail(group, f"Missing cases in Markdown: {', '.join(missing)}")
        else:
            report_pass(group)
    except Exception as e:
        report_fail(group, f"Error reading markdown: {e}")

def check_registry_text():
    group = "6. Registry text checks"
    reg_path = BASE_DIR / "20-registry.md"
    try:
        content = reg_path.read_text(encoding='utf-8')
        lines = content.splitlines()

        missing = []
        for s in ["0x10", "time48-rand", "0x11..0xef", "0x00..0x0f", "0xf0..0xff"]:
            if s not in content:
                missing.append(s)

        errors = []
        if missing:
            errors.append(f"Missing required strings: {', '.join(missing)}")

        # Conservative check: fail if a row in a Markdown table appears to assign 0x11 or 0x7a.
        # Markdown table row starts with |
        assign_11_re = re.compile(r"^\|.*`0x11`\s*\|")
        assign_7a_re = re.compile(r"^\|.*`0x7a`\s*\|")

        for i, line in enumerate(lines):
            line_trim = line.strip()
            if line_trim.startswith("|"):
                if assign_11_re.search(line_trim):
                    errors.append(f"Line {i+1} appears to assign 0x11: {line_trim}")
                if assign_7a_re.search(line_trim):
                    errors.append(f"Line {i+1} appears to assign 0x7a: {line_trim}")

        if errors:
            report_fail(group, "; ".join(errors))
        else:
            report_pass(group)
    except Exception as e:
        report_fail(group, f"Error reading registry: {e}")

def check_top_level_stubs():
    group = "7. Top-level stub checks"
    try:
        stub1 = (REPO_ROOT / "uuidv8-fid-v2.md").read_text(encoding='utf-8')
        stub2 = (REPO_ROOT / "uuidv8-fid-v2-registry.md").read_text(encoding='utf-8')

        errors = []
        if "non-normative" not in stub1 or "Do not add normative requirements" not in stub1:
            errors.append("uuidv8-fid-v2.md missing non-normative phrasing")
        if "non-normative" not in stub2 or "Do not add normative requirements" not in stub2:
            errors.append("uuidv8-fid-v2-registry.md missing non-normative phrasing")

        if errors:
            report_fail(group, "; ".join(errors))
        else:
            report_pass(group)
    except Exception as e:
        report_fail(group, f"Error reading stubs: {e}")

def check_source_map():
    group = "8. Source-map checks"
    map_path = BASE_DIR / "publication" / "source-map.md"
    try:
        content = map_path.read_text(encoding='utf-8')
        required = [
            "uuidv8-fid-v2/README.md",
            "uuidv8-fid-v2/20-registry.md",
            "uuidv8-fid-v2/formats/10-time48-rand.md",
            "uuidv8-fid-v2/conformance/structural-test-vectors.json",
            "uuidv8-fid-v2/implementation/pseudocode.md",
            "uuidv8-fid-v2/audit/consistency-checklist.md",
            "uuidv8-fid-v2/publication/release-candidate-checklist.md",
            "uuidv8-fid-v2/publication/navigation-smoke-test.md",
            "uuidv8-fid-v2/publication/publication-candidate-manifest.md",
            "uuidv8-fid-v2/publication/publication-package-verification.md",
            "uuidv8-fid-v2/release/00-index.md",
            "uuidv8-fid-v2/release/release-candidate-notes.md",
            "uuidv8-fid-v2/release/publication-readiness-summary.md",
            "uuidv8-fid-v2/release/post-publication-work.md",
            "uuidv8-fid-v2/release/pre-publication-sweep.md",
            "uuidv8-fid-v2/tools/README.md",
            "uuidv8-fid-v2/tools/check_consistency.py",
            "uuidv8-fid-v2/tools/test_check_consistency.py",
            "uuidv8-fid-v2.md",
            "uuidv8-fid-v2-registry.md"
        ]

        missing = [r for r in required if r not in content]
        if missing:
            report_fail(group, f"Missing source-map entries: {', '.join(missing)}")
        else:
            report_pass(group)
    except Exception as e:
        report_fail(group, f"Error reading source-map: {e}")

def check_reader_guide():
    group = "9. Reader-guide checks"
    guide_path = BASE_DIR / "publication" / "reader-guide.md"
    try:
        content = guide_path.read_text(encoding='utf-8')
        required = [
            "release/release-candidate-notes.md",
            "release/publication-readiness-summary.md",
            "release/post-publication-work.md",
            "release/pre-publication-sweep.md",
            "tools/README.md",
            "tools/check_consistency.py",
            "tools/test_check_consistency.py"
        ]

        # Check either 'publication/navigation-smoke-test.md' or 'navigation-smoke-test.md'
        if "publication/navigation-smoke-test.md" not in content and "navigation-smoke-test.md" not in content:
            missing = ["navigation-smoke-test.md"]
        else:
            missing = []

        missing.extend([r for r in required if r not in content])
        if missing:
            report_fail(group, f"Missing reader-guide references: {', '.join(missing)}")
        else:
            report_pass(group)
    except Exception as e:
        report_fail(group, f"Error reading reader-guide: {e}")

def check_publication_candidate_package():
    group = "Publication candidate package checks"
    manifest_file = "uuidv8-fid-v2/publication/publication-candidate-manifest.md"
    verification_file = "uuidv8-fid-v2/publication/publication-package-verification.md"

    errors = []

    # 1. Check existences
    manifest_path = REPO_ROOT / manifest_file
    verification_path = REPO_ROOT / verification_file

    if not manifest_path.exists():
        errors.append(f"Missing {manifest_file}")
    if not verification_path.exists():
        errors.append(f"Missing {verification_file}")

    if not errors:
        try:
            man_content = manifest_path.read_text(encoding='utf-8')
            ver_content = verification_path.read_text(encoding='utf-8')
            man_lower = man_content.lower()
            ver_lower = ver_content.lower()

            # 2. Both must contain 'non-normative'
            if "non-normative" not in man_lower:
                errors.append(f"{manifest_file} missing 'non-normative'")
            if "non-normative" not in ver_lower:
                errors.append(f"{verification_file} missing 'non-normative'")

            # 3. Both must state they do not declare a final release
            phrase = "does not declare a final release"
            if phrase not in man_lower:
                errors.append(f"{manifest_file} missing '{phrase}'")
            if phrase not in ver_lower:
                errors.append(f"{verification_file} missing '{phrase}'")

            # 4. Manifest must contain the three required checker commands
            cmd1 = "python uuidv8-fid-v2/tools/check_consistency.py"
            cmd_strict = "python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings"
            cmd2 = "python uuidv8-fid-v2/tools/test_check_consistency.py"

            if cmd_strict not in man_content:
                errors.append(f"{manifest_file} missing command: {cmd_strict}")

            # Check cmd1
            man_without_strict = man_content.replace(cmd_strict, "")
            if cmd1 not in man_without_strict:
                errors.append(f"{manifest_file} missing command: {cmd1}")

            if cmd2 not in man_content:
                errors.append(f"{manifest_file} missing command: {cmd2}")

            # 5. Manifest or verification document must contain the three required checker commands
            combined_content = man_content + ver_content
            if cmd_strict not in combined_content:
                errors.append(f"Neither document contains command: {cmd_strict}")

            combined_without_strict = combined_content.replace(cmd_strict, "")
            if cmd1 not in combined_without_strict:
                errors.append(f"Neither document contains command: {cmd1}")

            if cmd2 not in combined_content:
                errors.append(f"Neither document contains command: {cmd2}")

            # 6. Manifest references
            if "uuidv8-fid-v2.md" not in man_content:
                errors.append(f"{manifest_file} missing reference to uuidv8-fid-v2.md")
            if "uuidv8-fid-v2-registry.md" not in man_content:
                errors.append(f"{manifest_file} missing reference to uuidv8-fid-v2-registry.md")
            if "release-candidate-execution-record.md" not in man_content:
                errors.append(f"{manifest_file} missing reference to release-candidate-execution-record.md")
            if "check_consistency.py" not in man_content:
                errors.append(f"{manifest_file} missing reference to check_consistency.py")
            if "test_check_consistency.py" not in man_content:
                errors.append(f"{manifest_file} missing reference to test_check_consistency.py")

        except Exception as e:
            errors.append(f"Error reading package documents: {e}")

        # 7. Check references from other documents
        def check_ref(filepath, ref):
            try:
                c = (REPO_ROOT / filepath).read_text(encoding='utf-8')
                if ref not in c:
                    errors.append(f"{filepath} missing reference to {ref}")
            except Exception as e:
                errors.append(f"Error reading {filepath} for ref: {e}")

        check_ref("uuidv8-fid-v2/publication/00-index.md", "publication-candidate-manifest.md")
        check_ref("uuidv8-fid-v2/publication/00-index.md", "publication-package-verification.md")

        check_ref("uuidv8-fid-v2/publication/source-map.md", "publication-candidate-manifest.md")
        check_ref("uuidv8-fid-v2/publication/source-map.md", "publication-package-verification.md")

        check_ref("uuidv8-fid-v2/publication/reader-guide.md", "publication-candidate-manifest.md")
        check_ref("uuidv8-fid-v2/publication/reader-guide.md", "publication-package-verification.md")

        check_ref("uuidv8-fid-v2/publication/release-candidate-checklist.md", "publication-candidate-manifest.md")
        check_ref("uuidv8-fid-v2/publication/release-candidate-checklist.md", "publication-package-verification.md")

        check_ref("uuidv8-fid-v2/release/pre-publication-sweep.md", "publication-candidate-manifest.md")
        check_ref("uuidv8-fid-v2/release/pre-publication-sweep.md", "publication-package-verification.md")

        try:
            prs_content = (REPO_ROOT / "uuidv8-fid-v2/release/publication-readiness-summary.md").read_text(encoding='utf-8')
            if "manifest" not in prs_content.lower() and "verification" not in prs_content.lower() and "publication-candidate-manifest.md" not in prs_content and "publication-package-verification.md" not in prs_content:
                errors.append(f"publication-readiness-summary.md missing reference to manifest or verification document")
        except Exception as e:
            errors.append(f"Error reading publication-readiness-summary.md: {e}")

        # 8. Negative artifact checks
        # Only flag CI workflows that relate to uuidv8-fid-v2.
        ci_path = REPO_ROOT / ".github/workflows"
        if ci_path.exists() and ci_path.is_dir():
            for workflow_file in ci_path.glob("*.yml"):
                try:
                    wf_content = workflow_file.read_text(encoding='utf-8').lower()
                    if "uuidv8-fid" in wf_content or "uuidv8" in wf_content:
                        errors.append(f"UUIDv8-FID-v2 CI workflow exists: {workflow_file.name}")
                except Exception:
                    pass

        invalid_dirs = [
            "uuidv8-fid-v2/publication/html",
            "uuidv8-fid-v2/publication/rendered",
            "uuidv8-fid-v2/publication/dist",
            "uuidv8-fid-v2/dist",
            "uuidv8-fid-v2/build"
        ]
        for d in invalid_dirs:
            if (REPO_ROOT / d).exists():
                errors.append(f"Forbidden directory exists: {d}")

        # Check for committed HTML files under uuidv8-fid-v2
        html_files = list(BASE_DIR.rglob("*.html"))
        if html_files:
            for h in html_files:
                errors.append(f"Forbidden HTML artifact exists: {h.relative_to(REPO_ROOT)}")

    if errors:
        report_fail(group, "; ".join(errors))
    else:
        report_pass(group)

def check_reader_guide_heading_numbering():
    group = "Reader-guide heading numbering check"
    guide_path = BASE_DIR / "publication" / "reader-guide.md"
    expected = [
        "## 1. For public readers",
        "## 2. For specification readers",
        "## 3. For registry readers",
        "## 4. For implementers",
        "## 5. For reviewers",
        "## 6. For publication/package maintainers",
        "## 7. For release reviewers"
    ]
    try:
        content = guide_path.read_text(encoding='utf-8')
        headings = [line.strip() for line in content.splitlines() if line.strip().startswith("## ")]

        # Only take the expected ones from start to make sure order and contents match
        # Actually the spec has a ## Purpose before the numbered ones. Let's find numbered ones.
        numbered_headings = [h for h in headings if "## " in h and any(char.isdigit() for char in h)]

        if numbered_headings != expected:
            report_fail(group, f"Reader-guide numbered headings do not match expected sequential order. Found: {numbered_headings}")
        else:
            report_pass(group)
    except Exception as e:
        report_fail(group, f"Error reading reader-guide for heading check: {e}")

def check_release_candidate_execution_record():
    group = "Release candidate execution record checks"
    record_file = "uuidv8-fid-v2/release/release-candidate-execution-record.md"

    errors = []

    # file exists
    record_path = REPO_ROOT / record_file
    if not record_path.exists():
        errors.append(f"Execution record missing: {record_file}")
    else:
        try:
            content = record_path.read_text(encoding='utf-8')
            content_lower = content.lower()

            # contains non-normative
            if "non-normative" not in content_lower:
                errors.append(f"{record_file} missing 'non-normative'")

            # contains does not declare a final release
            if "does not declare a final release" not in content_lower:
                errors.append(f"{record_file} missing 'does not declare a final release'")

            # contains all three command names
            cmd1 = "python uuidv8-fid-v2/tools/check_consistency.py"
            cmd_strict = "python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings"
            cmd2 = "python uuidv8-fid-v2/tools/test_check_consistency.py"

            # Check strict command first so it doesn't just match the prefix
            if cmd_strict not in content:
                errors.append(f"{record_file} missing command: {cmd_strict}")

            # Remove cmd_strict from content so we can check if cmd1 exists separately
            content_without_strict = content.replace(cmd_strict, "")
            if cmd1 not in content_without_strict:
                errors.append(f"{record_file} missing command: {cmd1}")

            if cmd2 not in content:
                errors.append(f"{record_file} missing command: {cmd2}")

        except Exception as e:
            errors.append(f"Error reading {record_file}: {e}")

    # check references
    def check_ref(filepath, ref):
        try:
            c = (REPO_ROOT / filepath).read_text(encoding='utf-8')
            if ref not in c:
                errors.append(f"{filepath} missing reference to {ref}")
        except Exception as e:
            errors.append(f"Error reading {filepath} for ref: {e}")

    check_ref("uuidv8-fid-v2/release/00-index.md", "release-candidate-execution-record.md")
    check_ref("uuidv8-fid-v2/publication/source-map.md", "release-candidate-execution-record.md")
    check_ref("uuidv8-fid-v2/publication/reader-guide.md", "release-candidate-execution-record.md")
    check_ref("uuidv8-fid-v2/publication/release-candidate-checklist.md", "release-candidate-execution-record.md")
    check_ref("uuidv8-fid-v2/release/pre-publication-sweep.md", "release-candidate-execution-record.md")

    if errors:
        report_fail(group, "; ".join(errors))
    else:
        report_pass(group)

def check_release_candidate_freeze_gate():
    group = "Release candidate freeze gate checks"
    errors = []

    files = {
        "freeze": "uuidv8-fid-v2/release/release-candidate-freeze.md",
        "review": "uuidv8-fid-v2/release/human-review-record.md",
        "gate": "uuidv8-fid-v2/release/release-decision-gate.md"
    }

    # Existence and wording checks
    for name, filepath in files.items():
        p = REPO_ROOT / filepath
        if not p.exists():
            errors.append(f"Missing {filepath}")
        else:
            try:
                content = p.read_text(encoding='utf-8')
                content_lower = content.lower()
                if "non-normative" not in content_lower:
                    errors.append(f"{filepath} missing 'non-normative'")
                if "does not declare a final release" not in content_lower:
                    errors.append(f"{filepath} missing 'does not declare a final release'")
            except Exception as e:
                errors.append(f"Error reading {filepath}: {e}")

    # Specific human-review-record checks
    p_review = REPO_ROOT / files["review"]
    if p_review.exists():
        try:
            rev_content = p_review.read_text(encoding='utf-8')
            required_hex = ["0x10", "0x11..0xef", "0x00..0x0f", "0xf0..0xff", "0x7a"]
            for h in required_hex:
                if h not in rev_content:
                    errors.append(f"human-review-record.md missing invariant string: {h}")
        except Exception as e:
            pass

    # Specific release-decision-gate checks
    p_gate = REPO_ROOT / files["gate"]
    if p_gate.exists():
        try:
            gate_content = p_gate.read_text(encoding='utf-8')
            cmd1 = "python uuidv8-fid-v2/tools/check_consistency.py"
            cmd_strict = "python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings"
            cmd2 = "python uuidv8-fid-v2/tools/test_check_consistency.py"

            if cmd_strict not in gate_content:
                errors.append("release-decision-gate.md missing strict command")
            gate_without_strict = gate_content.replace(cmd_strict, "")
            if cmd1 not in gate_without_strict:
                errors.append("release-decision-gate.md missing default command")
            if cmd2 not in gate_content:
                errors.append("release-decision-gate.md missing test command")
            if "does not declare a final release" not in gate_content.lower():
                errors.append("release-decision-gate.md declaring a final release (missing non-declaration)")
        except Exception as e:
            pass

    # Check cross-references
    def check_ref(filepath, refs, req_all=True):
        p = REPO_ROOT / filepath
        if not p.exists():
            return
        try:
            c = p.read_text(encoding='utf-8')
            found = 0
            for r in refs:
                if r in c:
                    found += 1
                elif req_all:
                    errors.append(f"{filepath} missing reference to {r}")
            if not req_all and found == 0:
                errors.append(f"{filepath} missing at least one reference from {refs}")
        except Exception as e:
            errors.append(f"Error reading {filepath}: {e}")

    refs_all_three = ["release-candidate-freeze.md", "human-review-record.md", "release-decision-gate.md"]
    check_ref("uuidv8-fid-v2/release/00-index.md", refs_all_three)
    check_ref("uuidv8-fid-v2/publication/source-map.md", refs_all_three)
    check_ref("uuidv8-fid-v2/publication/reader-guide.md", refs_all_three)
    check_ref("uuidv8-fid-v2/publication/release-candidate-checklist.md", refs_all_three)
    check_ref("uuidv8-fid-v2/release/pre-publication-sweep.md", refs_all_three)
    check_ref("uuidv8-fid-v2/publication/publication-candidate-manifest.md", refs_all_three)

    # publication-readiness-summary.md checks for freeze/gate/review wording
    check_ref("uuidv8-fid-v2/release/publication-readiness-summary.md", ["freeze", "gate", "review"], req_all=False)

    # publication-package-verification.md checks for both human review record and release decision gate
    check_ref("uuidv8-fid-v2/publication/publication-package-verification.md", ["human-review-record.md", "release-decision-gate.md"], req_all=True)

    if errors:
        report_fail(group, "; ".join(errors))
    else:
        report_pass(group)

def check_release_non_final_guard():
    group = "10. Release non-final guard"
    release_files = [
        "uuidv8-fid-v2/release/00-index.md",
        "uuidv8-fid-v2/release/release-candidate-notes.md",
        "uuidv8-fid-v2/release/publication-readiness-summary.md",
        "uuidv8-fid-v2/release/pre-publication-sweep.md",
        "uuidv8-fid-v2/release/release-candidate-execution-record.md",
        "uuidv8-fid-v2/release/release-candidate-freeze.md",
        "uuidv8-fid-v2/release/human-review-record.md",
        "uuidv8-fid-v2/release/release-decision-gate.md",
        "uuidv8-fid-v2/release/single-file-assembly-dry-run-record.md",
        "uuidv8-fid-v2/publication/publication-candidate-manifest.md",
        "uuidv8-fid-v2/publication/publication-package-verification.md",
        "uuidv8-fid-v2/publication/single-file-assembly-dry-run.md",
        "uuidv8-fid-v2/publication/dual-form-publication-package.md",
        "uuidv8-fid-v2/release/dual-form-publication-verification-record.md",
        "uuidv8-fid-v2/release/final-publication-decision-gate.md",
        "uuidv8-fid-v2/release/final-publication-decision-checklist.md",
        "uuidv8-fid-v2/release/final-publication-preflight-record.md",
        "uuidv8-fid-v2/release/final-publication-decision-summary.md"
    ]

    required_phrases = [
        "non-normative",
        "does not declare a final release"
    ]
    forbidden_phrases = [
        "this is the final release",
        "final release is declared",
        "final release is approved",
        "publication is approved",
        "decision status: approved"
    ]

    errors = []
    for f in release_files:
        try:
            content = (REPO_ROOT / f).read_text(encoding='utf-8').lower()

            # Check required phrases
            for req in required_phrases:
                if req not in content:
                    errors.append(f"{f} missing required phrase: {req}")

            # Check forbidden phrase
            for forb in forbidden_phrases:
                if forb in content:
                    errors.append(f"{f} contains forbidden phrase: '{forb}'")

        except Exception as e:
            errors.append(f"Error reading {f}: {e}")

    if errors:
        report_fail(group, "; ".join(errors))
    else:
        report_pass(group)

def check_public_entry_points():
    group = "Public entry-point checks"
    errors = []

    # Check README.md
    try:
        readme_path = BASE_DIR / "README.md"
        content = readme_path.read_text(encoding='utf-8')
        content_lower = content.lower()

        required_paths_readme = [
            "00-index.md",
            "20-registry.md",
            "formats/10-time48-rand.md",
            "conformance/structural-test-vectors.md",
            "conformance/structural-test-vectors.json",
            "implementation/pseudocode.md",
            "publication/reader-guide.md",
            "release/pre-publication-sweep.md",
            "tools/README.md"
        ]

        for path in required_paths_readme:
            if path not in content:
                errors.append(f"uuidv8-fid-v2/README.md missing path: {path}")

        if "non-normative" not in content_lower:
            errors.append("uuidv8-fid-v2/README.md missing 'non-normative'")

    except Exception as e:
        errors.append(f"Error reading uuidv8-fid-v2/README.md: {e}")

    # Check uuidv8-fid-v2.md
    try:
        stub1_path = REPO_ROOT / "uuidv8-fid-v2.md"
        content = stub1_path.read_text(encoding='utf-8')
        content_lower = content.lower()

        required_paths_stub1 = [
            "uuidv8-fid-v2/README.md",
            "uuidv8-fid-v2/00-index.md"
        ]

        for path in required_paths_stub1:
            if path not in content:
                errors.append(f"uuidv8-fid-v2.md missing path: {path}")

        if "non-normative" not in content_lower:
            errors.append("uuidv8-fid-v2.md missing 'non-normative'")
        if "do not add normative requirements" not in content_lower:
            errors.append("uuidv8-fid-v2.md missing 'do not add normative requirements'")

    except Exception as e:
        errors.append(f"Error reading uuidv8-fid-v2.md: {e}")

    # Check uuidv8-fid-v2-registry.md
    try:
        stub2_path = REPO_ROOT / "uuidv8-fid-v2-registry.md"
        content = stub2_path.read_text(encoding='utf-8')
        content_lower = content.lower()

        required_paths_stub2 = [
            "uuidv8-fid-v2/README.md",
            "uuidv8-fid-v2/20-registry.md",
            "uuidv8-fid-v2/formats/10-time48-rand.md"
        ]

        for path in required_paths_stub2:
            if path not in content:
                errors.append(f"uuidv8-fid-v2-registry.md missing path: {path}")

        if "non-normative" not in content_lower:
            errors.append("uuidv8-fid-v2-registry.md missing 'non-normative'")
        if "do not add normative requirements" not in content_lower:
            errors.append("uuidv8-fid-v2-registry.md missing 'do not add normative requirements'")

    except Exception as e:
        errors.append(f"Error reading uuidv8-fid-v2-registry.md: {e}")

    if errors:
        report_fail(group, "; ".join(errors))
    else:
        report_pass(group)

def check_public_entry_point_non_final_guard():
    group = "Public entry-point non-final guard"
    files_to_check = [
        "uuidv8-fid-v2/README.md",
        "uuidv8-fid-v2.md",
        "uuidv8-fid-v2-registry.md"
    ]

    forbidden_phrases = [
        "this is the final release",
        "final release is declared"
    ]

    errors = []
    for f in files_to_check:
        try:
            content = (REPO_ROOT / f).read_text(encoding='utf-8').lower()
            for forb in forbidden_phrases:
                if forb in content:
                    errors.append(f"{f} contains forbidden phrase: '{forb}'")
        except Exception as e:
            errors.append(f"Error reading {f}: {e}")

    if errors:
        report_fail(group, "; ".join(errors))
    else:
        report_pass(group)

def check_index():
    group = "11. Index checks"
    idx_path = BASE_DIR / "00-index.md"
    try:
        content = idx_path.read_text(encoding='utf-8')
        required = [
            "formats/",
            "conformance/",
            "implementation/",
            "audit/",
            "publication/",
            "tools/",
            "release/"
        ]
        missing = [r for r in required if r not in content]
        if missing:
            report_fail(group, f"Missing index references: {', '.join(missing)}")
        else:
            report_pass(group)
    except Exception as e:
        report_fail(group, f"Error reading index: {e}")

def check_generated_single_file_guard():
    group = "12. Generated single-file guard"

    allowed_artifact = "uuidv8-fid-v2/publication/uuidv8-fid-v2-single-file.md"
    allowed_artifact_path = REPO_ROOT / allowed_artifact
    generated_notice = "This is generated dry-run output assembled from the split UUIDv8-FID-v2 source files"

    # 1. Scan for any unauthorized generated markdown files
    unauthorized_found = []
    for filepath in BASE_DIR.rglob("*.md"):
        rel_path = filepath.relative_to(REPO_ROOT).as_posix()
        if rel_path == allowed_artifact:
            continue

        try:
            content = filepath.read_text(encoding='utf-8')
            if generated_notice in content:
                unauthorized_found.append(rel_path)
        except Exception:
            pass

    if unauthorized_found:
        report_fail(group, f"Found unauthorized generated single-file artifacts: {', '.join(unauthorized_found)}")
    else:
        report_pass("No unauthorized generated markdown artifacts found")

    # 2. Check for legacy paths and rendered HTML or build artifacts
    forbidden = [
        "uuidv8-fid-v2/generated-single-file.md",
        "uuidv8-fid-v2/single-file.md",
        "uuidv8-fid-v2/uuidv8-fid-v2-single-file.md",
        "uuidv8-fid-v2/publication/generated-single-file.md",
        "uuidv8-fid-v2/publication/single-file.md",
        "uuidv8-fid-v2.html",
        "uuidv8-fid-v2/uuidv8-fid-v2.html",
        "uuidv8-fid-v2/publication/uuidv8-fid-v2.html",
        "dist/uuidv8-fid-v2.md",
        "build/uuidv8-fid-v2.md"
    ]

    found_build_artifacts = [f for f in forbidden if (REPO_ROOT / f).exists()]
    if found_build_artifacts:
        report_fail(group, f"Found forbidden build/HTML artifacts: {', '.join(found_build_artifacts)}")
    else:
        report_pass("No forbidden build/HTML artifacts found")

    # 3. Check the explicitly allowed artifact
    if not allowed_artifact_path.exists():
        report_fail(group, f"Allowed generated single-file artifact missing: {allowed_artifact}")
    else:
        report_pass(f"Allowed generated single-file artifact exists: {allowed_artifact}")

        try:
            content = allowed_artifact_path.read_text(encoding='utf-8')
            if generated_notice not in content:
                report_fail(group, f"Allowed generated artifact is missing generated-output notice: {allowed_artifact}")
            else:
                report_pass(f"Allowed generated artifact contains generated-output notice: {allowed_artifact}")

            invariant_strings = [
                "format_id = (format_type << 4) | format_subtype",
                "xxxxxxxx-xxxx-8T00-8S00-xxxxxxxxxxxx",
                "0x10",
                "0x7a"
            ]
            for inv in invariant_strings:
                if inv not in content:
                    report_fail(group, f"Allowed generated artifact is missing invariant string: {inv}")
                else:
                    report_pass(f"Allowed generated artifact contains invariant string: {inv}")

        except Exception as e:
            report_fail(group, f"Could not read allowed generated artifact {allowed_artifact}: {e}")

        try:
            import subprocess
            result = subprocess.run(
                [
                    sys.executable,
                    str(REPO_ROOT / "uuidv8-fid-v2" / "tools" / "assemble_single_file.py"),
                    "--repo-root",
                    str(REPO_ROOT),
                    "--verify-output",
                    allowed_artifact
                ],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                report_fail(group, f"Allowed generated artifact is stale or invalid: {allowed_artifact}\n{result.stderr.strip()}")
            else:
                report_pass(f"Allowed generated artifact matches regenerated output exactly: {allowed_artifact}")
        except Exception as e:
            report_fail(group, f"Could not run assemble_single_file.py --verify-output: {e}")

def check_relative_markdown_links():
    group = "Relative Markdown link check"

    files_to_check = list(BASE_DIR.rglob("*.md"))
    files_to_check.append(REPO_ROOT / "uuidv8-fid-v2.md")
    files_to_check.append(REPO_ROOT / "uuidv8-fid-v2-registry.md")

    link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')

    errors = []

    for filepath in files_to_check:
        if not filepath.is_file():
            continue

        try:
            content = filepath.read_text(encoding='utf-8')
            lines = content.splitlines()

            in_fenced_block = False
            for i, line in enumerate(lines):
                if line.strip().startswith('```'):
                    in_fenced_block = not in_fenced_block
                    continue

                if in_fenced_block:
                    continue

                # We want to ignore image links ![]().
                # The regex matches the [label](target). So if line contains ![label](target), we should ignore.
                # Actually let's just finditer and look at the character before the match.
                for match in link_pattern.finditer(line):
                    start_idx = match.start()
                    if start_idx > 0 and line[start_idx - 1] == '!':
                        continue # Image link

                    label = match.group(1)
                    target = match.group(2)

                    target = target.strip()

                    if not target:
                        continue

                    if target.startswith('#'):
                        continue

                    if target.startswith(('http://', 'https://')):
                        continue

                    if target.startswith('mailto:'):
                        continue

                    # Strip fragment
                    if '#' in target:
                        target = target.split('#')[0]

                    if not target:
                        continue

                    # Strip query string
                    if '?' in target:
                        target = target.split('?')[0]

                    if not target:
                        continue

                    target_path = urllib.parse.unquote(target)
                    resolved_path = (filepath.parent / target_path).resolve()

                    if not resolved_path.exists():
                        errors.append(f"{filepath.relative_to(REPO_ROOT)}:{i+1}: Link target missing: {target}")

        except Exception as e:
            errors.append(f"Error processing {filepath.relative_to(REPO_ROOT)}: {e}")

    if errors:
        report_fail(group, "\n" + "\n".join(errors))
    else:
        report_pass(group)

def check_stale_phrase_warnings():
    group = "13. Stale phrase warning checks"

    # We check all .md files under uuidv8-fid-v2 and the two top-level ones
    files_to_check = list(BASE_DIR.rglob("*.md"))
    files_to_check.append(REPO_ROOT / "uuidv8-fid-v2.md")
    files_to_check.append(REPO_ROOT / "uuidv8-fid-v2-registry.md")

    stale_phrases = [
        "No concrete payload format is assigned",
        "does not assign concrete values",
        "registry scaffold"
    ]

    allowlist = {
        "uuidv8-fid-v2/audit/release-readiness.md",
        "uuidv8-fid-v2/release/release-candidate-notes.md",
        "uuidv8-fid-v2/release/post-publication-work.md",
        "uuidv8-fid-v2/release/release-candidate-execution-record.md"
    }

    # Warning only, doesn't fail unless there's a script error
    # but we just report warnings.
    try:
        for filepath in files_to_check:
            if filepath.is_file():
                rel_path = filepath.relative_to(REPO_ROOT).as_posix()
                if rel_path in allowlist:
                    continue

                try:
                    lines = filepath.read_text(encoding='utf-8').splitlines()
                    for i, line in enumerate(lines):
                        for phrase in stale_phrases:
                            if phrase in line:
                                report_warn(rel_path, i+1, f"Found stale phrase '{phrase}'")
                except Exception as e:
                    # Ignore unreadable files or non-utf8 silently for warnings, or just warn
                    pass
        report_pass(group)
    except Exception as e:
        report_fail(group, f"Error processing warnings: {e}")

def check_single_file_assembly_dry_run():
    group = "Single-file assembly dry run checks"
    required_files = [
        "tools/assemble_single_file.py",
        "tools/test_assemble_single_file.py",
        "publication/single-file-assembly-dry-run.md",
        "release/single-file-assembly-dry-run-record.md"
    ]
    for rel in required_files:
        if not os.path.isfile(os.path.join(REPO_ROOT, "uuidv8-fid-v2", rel)):
            report_fail(group, f"Single-file assembly dry-run file missing: {rel}")
        else:
            report_pass(f"Single-file assembly dry-run file present: {rel}")

    def require_phrases(rel_path, phrases):
        path = os.path.join(REPO_ROOT, "uuidv8-fid-v2", rel_path)
        if not os.path.isfile(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().lower()
            for phrase in phrases:
                if phrase.lower() not in content:
                    report_fail(group, f"{rel_path} missing required phrase: {phrase}")
                else:
                    report_pass(f"{rel_path} contains required phrase: {phrase}")
        except Exception as e:
            report_fail(group, f"Could not read {rel_path}: {e}")

    phrases = [
        "non-normative",
        "does not declare a final release",
        "python uuidv8-fid-v2/tools/assemble_single_file.py --check",
        "python uuidv8-fid-v2/tools/assemble_single_file.py --stdout",
        "python uuidv8-fid-v2/tools/test_assemble_single_file.py"
    ]

    require_phrases("publication/single-file-assembly-dry-run.md", phrases)
    require_phrases("release/single-file-assembly-dry-run-record.md", phrases)

    def check_ref(filepath, ref):
        path = os.path.join(REPO_ROOT, "uuidv8-fid-v2", filepath)
        if not os.path.isfile(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if ref not in content:
                report_fail(group, f"{filepath} missing reference to {ref}")
            else:
                report_pass(f"{filepath} references {ref}")
        except Exception as e:
            report_fail(group, f"Could not read {filepath}: {e}")

    check_ref("tools/README.md", "assemble_single_file.py")
    check_ref("tools/README.md", "test_assemble_single_file.py")

    check_ref("publication/source-map.md", "single-file-assembly-dry-run.md")
    check_ref("publication/source-map.md", "single-file-assembly-dry-run-record.md")
    check_ref("publication/source-map.md", "assemble_single_file.py")
    check_ref("publication/source-map.md", "test_assemble_single_file.py")

    check_ref("publication/reader-guide.md", "single-file-assembly-dry-run.md")
    check_ref("publication/single-file-assembly-plan.md", "single-file-assembly-dry-run.md")
    check_ref("publication/publication-candidate-manifest.md", "single-file-assembly-dry-run.md")
    check_ref("publication/publication-candidate-manifest.md", "single-file-assembly-dry-run-record.md")
    check_ref("publication/publication-candidate-manifest.md", "assemble_single_file.py")
    check_ref("publication/publication-candidate-manifest.md", "test_assemble_single_file.py")

    check_ref("publication/publication-package-verification.md", "single-file-assembly-dry-run-record.md")

    # either record or check is acceptable in the decision gate but let's just check for tool check
    check_ref("release/release-decision-gate.md", "python uuidv8-fid-v2/tools/assemble_single_file.py --check")
    check_ref("release/release-decision-gate.md", "python uuidv8-fid-v2/tools/test_assemble_single_file.py")


def check_dual_form_publication_package():
    group = "Dual-form publication package checks"

    required_files = [
        "publication/dual-form-publication-package.md",
        "publication/uuidv8-fid-v2-single-file.md",
        "release/dual-form-publication-verification-record.md"
    ]
    for rel in required_files:
        if not os.path.isfile(os.path.join(REPO_ROOT, "uuidv8-fid-v2", rel)):
            report_fail(group, f"Dual-form file missing: {rel}")
        else:
            report_pass(f"Dual-form file present: {rel}")

    def require_phrases(rel_path, phrases):
        path = os.path.join(REPO_ROOT, "uuidv8-fid-v2", rel_path)
        if not os.path.isfile(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read().lower()
            for phrase in phrases:
                if phrase.lower() not in content:
                    report_fail(group, f"{rel_path} missing required phrase: {phrase}")
                else:
                    report_pass(f"{rel_path} contains required phrase: {phrase}")
        except Exception as e:
            report_fail(group, f"Could not read {rel_path}: {e}")

    require_phrases("publication/dual-form-publication-package.md", [
        "non-normative",
        "does not declare a final release",
        "the split files remain the canonical source; the committed single-file document is a generated derivative publication form."
    ])

    require_phrases("release/dual-form-publication-verification-record.md", [
        "non-normative",
        "does not declare a final release"
    ])

    def check_ref(filepath, ref):
        path = os.path.join(REPO_ROOT, "uuidv8-fid-v2", filepath)
        if not os.path.isfile(path):
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            if ref not in content:
                report_fail(group, f"{filepath} missing reference to {ref}")
            else:
                report_pass(f"{filepath} references {ref}")
        except Exception as e:
            report_fail(group, f"Could not read {filepath}: {e}")

    check_ref("publication/source-map.md", "dual-form-publication-package.md")
    check_ref("publication/source-map.md", "uuidv8-fid-v2-single-file.md")
    check_ref("publication/source-map.md", "dual-form-publication-verification-record.md")

    check_ref("publication/reader-guide.md", "dual-form-publication-package.md")

    check_ref("publication/publication-candidate-manifest.md", "dual-form-publication-package.md")
    check_ref("publication/publication-candidate-manifest.md", "uuidv8-fid-v2-single-file.md")
    check_ref("publication/publication-candidate-manifest.md", "dual-form-publication-verification-record.md")

    check_ref("publication/publication-package-verification.md", "uuidv8-fid-v2-single-file.md")
    check_ref("publication/publication-package-verification.md", "dual-form-publication-verification-record.md")

    check_ref("release/release-decision-gate.md", "dual-form-publication-verification-record.md")

    check_ref("tools/README.md", "python uuidv8-fid-v2/tools/assemble_single_file.py --output uuidv8-fid-v2/publication/uuidv8-fid-v2-single-file.md --force")
    check_ref("tools/README.md", "python uuidv8-fid-v2/tools/assemble_single_file.py --verify-output uuidv8-fid-v2/publication/uuidv8-fid-v2-single-file.md")


def check_final_publication_decision_gate():
    group = "11. Final Publication Decision Gate"
    gate_files = {
        "uuidv8-fid-v2/release/final-publication-decision-gate.md": ["this document prepares the final publication decision gate, but the final publication decision remains pending."],
        "uuidv8-fid-v2/release/final-publication-decision-summary.md": ["decision status: pending."],
        "uuidv8-fid-v2/release/final-publication-decision-checklist.md": ["- [ ] decide whether to prepare a future final release pr."],
        "uuidv8-fid-v2/release/final-publication-preflight-record.md": [
            "python uuidv8-fid-v2/tools/assemble_single_file.py --check",
            "python uuidv8-fid-v2/tools/assemble_single_file.py --verify-output uuidv8-fid-v2/publication/uuidv8-fid-v2-single-file.md",
            "python uuidv8-fid-v2/tools/test_assemble_single_file.py",
            "python uuidv8-fid-v2/tools/check_consistency.py",
            "python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings",
            "python uuidv8-fid-v2/tools/test_check_consistency.py"
        ]
    }

    errors = []
    for f, required_contents in gate_files.items():
        try:
            content = (REPO_ROOT / f).read_text(encoding='utf-8').lower()
            for req in required_contents:
                if req not in content:
                    errors.append(f"{f} missing specific final decision gate phrasing: {req}")
        except FileNotFoundError:
            errors.append(f"Missing expected final decision gate file: {f}")

    if errors:
        report_fail(group, errors)
    else:
        report_pass(group)

def main():
    parser = argparse.ArgumentParser(description="UUIDv8-FID-v2 local consistency checker.", allow_abbrev=False)
    parser.add_argument("--fail-on-warnings", action="store_true", help="Fail if any warnings are present.")

    try:
        args = parser.parse_args()
    except SystemExit as e:
        sys.exit(1)

    fail_on_warnings = args.fail_on_warnings

    print("Running UUIDv8-FID-v2 local consistency checks...\n")

    check_file_existence()
    data = check_json_validity()
    check_json_registry_state(data)
    check_json_vectors(data)
    check_markdown_conformance_vectors()
    check_registry_text()
    check_top_level_stubs()
    check_source_map()
    check_reader_guide()
    check_reader_guide_heading_numbering()
    check_publication_candidate_package()
    check_release_candidate_execution_record()
    check_release_candidate_freeze_gate()
    check_release_non_final_guard()
    check_final_publication_decision_gate()
    check_public_entry_points()
    check_public_entry_point_non_final_guard()
    check_index()
    check_generated_single_file_guard()
    check_relative_markdown_links()
    check_stale_phrase_warnings()
    check_single_file_assembly_dry_run()
    check_dual_form_publication_package()

    print()
    if has_failures:
        print("UUIDv8-FID-v2 consistency checks: FAIL")
        sys.exit(1)
    elif has_warnings:
        if fail_on_warnings:
            print("UUIDv8-FID-v2 consistency checks: FAIL (warnings present in strict mode)")
            sys.exit(1)
        else:
            print("UUIDv8-FID-v2 consistency checks: PASS with warnings")
            sys.exit(0)
    else:
        print("UUIDv8-FID-v2 consistency checks: PASS")
        sys.exit(0)

if __name__ == "__main__":
    main()
