import os
import sys
import json
import re
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
            "uuidv8-fid-v2/20-registry.md",
            "uuidv8-fid-v2/formats/10-time48-rand.md",
            "uuidv8-fid-v2/conformance/structural-test-vectors.json",
            "uuidv8-fid-v2/implementation/pseudocode.md",
            "uuidv8-fid-v2/audit/consistency-checklist.md",
            "uuidv8-fid-v2/publication/release-candidate-checklist.md",
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

def check_index():
    group = "9. Index checks"
    idx_path = BASE_DIR / "00-index.md"
    try:
        content = idx_path.read_text(encoding='utf-8')
        required = [
            "formats/",
            "conformance/",
            "implementation/",
            "audit/",
            "publication/",
            "tools/"
        ]
        missing = [r for r in required if r not in content]
        if missing:
            report_fail(group, f"Missing index references: {', '.join(missing)}")
        else:
            report_pass(group)
    except Exception as e:
        report_fail(group, f"Error reading index: {e}")

def check_generated_single_file_guard():
    group = "10. Generated single-file guard"
    forbidden = [
        "uuidv8-fid-v2/generated-single-file.md",
        "uuidv8-fid-v2/single-file.md",
        "uuidv8-fid-v2/uuidv8-fid-v2-single-file.md"
    ]

    found = [f for f in forbidden if (REPO_ROOT / f).exists()]
    if found:
        report_fail(group, f"Found generated single-file artifacts: {', '.join(found)}")
    else:
        report_pass(group)

def check_stale_phrase_warnings():
    group = "11. Stale phrase warning checks"

    # We check all .md files under uuidv8-fid-v2 and the two top-level ones
    files_to_check = list(BASE_DIR.rglob("*.md"))
    files_to_check.append(REPO_ROOT / "uuidv8-fid-v2.md")
    files_to_check.append(REPO_ROOT / "uuidv8-fid-v2-registry.md")

    stale_phrases = [
        "No concrete payload format is assigned",
        "does not assign concrete values",
        "registry scaffold"
    ]

    # Warning only, doesn't fail unless there's a script error
    # but we just report warnings.
    try:
        for filepath in files_to_check:
            if filepath.is_file():
                try:
                    lines = filepath.read_text(encoding='utf-8').splitlines()
                    for i, line in enumerate(lines):
                        for phrase in stale_phrases:
                            if phrase in line:
                                rel_path = filepath.relative_to(REPO_ROOT)
                                report_warn(rel_path, i+1, f"Found stale phrase '{phrase}'")
                except Exception as e:
                    # Ignore unreadable files or non-utf8 silently for warnings, or just warn
                    pass
        report_pass(group)
    except Exception as e:
        report_fail(group, f"Error processing warnings: {e}")

def main():
    print("Running UUIDv8-FID-v2 local consistency checks...\n")

    check_file_existence()
    data = check_json_validity()
    check_json_registry_state(data)
    check_json_vectors(data)
    check_markdown_conformance_vectors()
    check_registry_text()
    check_top_level_stubs()
    check_source_map()
    check_index()
    check_generated_single_file_guard()
    check_stale_phrase_warnings()

    print()
    if has_failures:
        print("UUIDv8-FID-v2 consistency checks: FAIL")
        sys.exit(1)
    elif has_warnings:
        print("UUIDv8-FID-v2 consistency checks: PASS with warnings")
        sys.exit(0)
    else:
        print("UUIDv8-FID-v2 consistency checks: PASS")
        sys.exit(0)

if __name__ == "__main__":
    main()
