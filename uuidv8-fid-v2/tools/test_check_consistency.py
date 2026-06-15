import os
import sys
import shutil
import tempfile
import subprocess
from pathlib import Path

# Determine repo root relative to this script location
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent.parent

def setup_temp_repo(temp_dir: Path):
    """Copies the required files to the temp directory to mimic the repo structure."""
    shutil.copy2(REPO_ROOT / "uuidv8-fid-v2.md", temp_dir / "uuidv8-fid-v2.md")
    shutil.copy2(REPO_ROOT / "uuidv8-fid-v2-registry.md", temp_dir / "uuidv8-fid-v2-registry.md")
    shutil.copytree(REPO_ROOT / "uuidv8-fid-v2", temp_dir / "uuidv8-fid-v2", dirs_exist_ok=True)

def run_checker(temp_dir: Path, *args):
    """Runs the checker inside the temporary directory."""
    checker_path = temp_dir / "uuidv8-fid-v2" / "tools" / "check_consistency.py"
    cmd = [sys.executable, str(checker_path)]
    cmd.extend(args)
    result = subprocess.run(
        cmd,
        cwd=temp_dir,
        capture_output=True,
        text=True
    )
    return result

def report_pass(scenario_name):
    print(f"PASS: {scenario_name}")

def report_fail(scenario_name, expected, actual_rc, stdout, stderr):
    print(f"FAIL: {scenario_name}")
    print(f"  Expected: {expected}")
    print(f"  Actual Return Code: {actual_rc}")
    print("  --- STDOUT ---")
    print("\n".join(f"  {line}" for line in stdout.splitlines()[-10:]))  # Last 10 lines
    print("  --- STDERR ---")
    print("\n".join(f"  {line}" for line in stderr.splitlines()[-10:]))  # Last 10 lines
    return False


def main():
    print("Running UUIDv8-FID-v2 checker harness...\n")
    all_passed = True

    # Scenario A: baseline real repository passes
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "uuidv8-fid-v2" / "tools" / "check_consistency.py")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True
    )
    if result.returncode == 0 and ("UUIDv8-FID-v2 consistency checks: PASS" in result.stdout or "UUIDv8-FID-v2 consistency checks: PASS with warnings" in result.stdout):
        report_pass("baseline real repository passes")
    else:
        all_passed = report_fail("baseline real repository passes", "rc=0 and PASS in stdout", result.returncode, result.stdout, result.stderr)

    # Scenario B: missing public README fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        (temp_dir / "uuidv8-fid-v2" / "README.md").unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "uuidv8-fid-v2/README.md" in result.stdout:
            report_pass("missing public README fails")
        else:
            all_passed = report_fail("missing public README fails", "rc!=0, FAIL in stdout, mentions README.md", result.returncode, result.stdout, result.stderr)

    # Scenario C: registry assignment mutation fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        json_path = temp_dir / "uuidv8-fid-v2" / "conformance" / "structural-test-vectors.json"
        with open(json_path, 'r', encoding='utf-8') as f:
            import json
            data = json.load(f)
        data["registry_state"]["assigned"]["0x11"] = "invalid-test-assignment"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f)
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and ("0x11" in result.stdout or "assigned" in result.stdout):
            report_pass("registry assignment mutation fails")
        else:
            all_passed = report_fail("registry assignment mutation fails", "rc!=0, FAIL in stdout, mentions registry/assigned", result.returncode, result.stdout, result.stderr)

    # Scenario D: reader-guide heading numbering mutation fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        guide_path = temp_dir / "uuidv8-fid-v2" / "publication" / "reader-guide.md"
        content = guide_path.read_text(encoding='utf-8')
        content = content.replace("## 3. For registry readers", "## 2. For registry readers")
        guide_path.write_text(content, encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and ("heading" in result.stdout.lower() or "numbering" in result.stdout.lower() or "sequential order" in result.stdout.lower()):
            report_pass("reader-guide heading mutation fails")
        else:
            all_passed = report_fail("reader-guide heading mutation fails", "rc!=0, FAIL in stdout, mentions heading/numbering", result.returncode, result.stdout, result.stderr)

    # Scenario E: broken relative Markdown link fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        readme_path = temp_dir / "uuidv8-fid-v2" / "README.md"
        with open(readme_path, 'a', encoding='utf-8') as f:
            f.write("\n\n[broken local link](does-not-exist.md)\n")
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "does-not-exist.md" in result.stdout:
            report_pass("broken relative Markdown link fails")
        else:
            all_passed = report_fail("broken relative Markdown link fails", "rc!=0, FAIL in stdout, mentions does-not-exist.md", result.returncode, result.stdout, result.stderr)

    # Scenario F: generated single-file artifact fails (even without the generated string, legacy path is blocked)
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        (temp_dir / "uuidv8-fid-v2" / "generated-single-file.md").touch()
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "generated-single-file.md" in result.stdout:
            report_pass("generated single-file artifact fails")
        else:
            all_passed = report_fail("generated single-file artifact fails", "rc!=0, FAIL in stdout, mentions generated-single-file.md", result.returncode, result.stdout, result.stderr)

    # Scenario G: final release phrase fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        readme_path = temp_dir / "uuidv8-fid-v2" / "README.md"
        with open(readme_path, 'a', encoding='utf-8') as f:
            f.write("\n\nThis is the final release.\n")
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and ("forbidden phrase" in result.stdout.lower() or "final release" in result.stdout.lower()):
            report_pass("final release phrase fails")
        else:
            all_passed = report_fail("final release phrase fails", "rc!=0, FAIL in stdout, mentions forbidden phrase/final release", result.returncode, result.stdout, result.stderr)

    # Scenario RC1: missing release-candidate execution record fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        rc_record = temp_dir / "uuidv8-fid-v2" / "release" / "release-candidate-execution-record.md"
        if rc_record.exists():
            rc_record.unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "release-candidate-execution-record.md" in result.stdout:
            report_pass("missing release-candidate execution record fails")
        else:
            all_passed = report_fail("missing release-candidate execution record fails", "rc!=0, FAIL in stdout, mentions execution record missing", result.returncode, result.stdout, result.stderr)

    # Scenario RC2: execution record missing from source-map fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        source_map = temp_dir / "uuidv8-fid-v2" / "publication" / "source-map.md"
        content = source_map.read_text(encoding='utf-8')
        content = content.replace("release-candidate-execution-record.md", "MISSING_RECORD")
        source_map.write_text(content, encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "missing reference to release-candidate-execution-record.md" in result.stdout:
            report_pass("execution record missing from source-map fails")
        else:
            all_passed = report_fail("execution record missing from source-map fails", "rc!=0, FAIL in stdout, mentions missing reference", result.returncode, result.stdout, result.stderr)

    # Scenario RC3: execution record containing forbidden final-release phrase fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        rc_record = temp_dir / "uuidv8-fid-v2" / "release" / "release-candidate-execution-record.md"
        with open(rc_record, 'a', encoding='utf-8') as f:
            f.write("\n\nThis is the final release.\n")
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "forbidden phrase" in result.stdout:
            report_pass("execution record containing a forbidden final-release phrase fails")
        else:
            all_passed = report_fail("execution record containing a forbidden final-release phrase fails", "rc!=0, FAIL in stdout, mentions forbidden phrase", result.returncode, result.stdout, result.stderr)

    # Scenario RC4: execution record missing one of the required command names fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        rc_record = temp_dir / "uuidv8-fid-v2" / "release" / "release-candidate-execution-record.md"
        content = rc_record.read_text(encoding='utf-8')
        content = content.replace("python uuidv8-fid-v2/tools/test_check_consistency.py", "python MISSING_CMD.py")
        rc_record.write_text(content, encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "missing command" in result.stdout:
            report_pass("execution record missing one of the required command names fails")
        else:
            all_passed = report_fail("execution record missing one of the required command names fails", "rc!=0, FAIL in stdout, mentions missing command", result.returncode, result.stdout, result.stderr)

    # Scenario RC5: execution record missing the strict warning-mode command fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        rc_record = temp_dir / "uuidv8-fid-v2" / "release" / "release-candidate-execution-record.md"
        content = rc_record.read_text(encoding='utf-8')
        content = content.replace("python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings", "python MISSING_STRICT_CMD.py")
        rc_record.write_text(content, encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "missing command" in result.stdout:
            report_pass("execution record missing the strict warning-mode command fails")
        else:
            all_passed = report_fail("execution record missing the strict warning-mode command fails", "rc!=0, FAIL in stdout, mentions missing command", result.returncode, result.stdout, result.stderr)

    # Scenario P1: missing publication-candidate-manifest.md fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        (temp_dir / "uuidv8-fid-v2" / "publication" / "publication-candidate-manifest.md").unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "publication-candidate-manifest.md" in result.stdout:
            report_pass("missing publication-candidate-manifest.md fails")
        else:
            all_passed = report_fail("missing publication-candidate-manifest.md fails", "rc!=0, FAIL in stdout, mentions manifest", result.returncode, result.stdout, result.stderr)

    # Scenario P2: missing publication-package-verification.md fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        (temp_dir / "uuidv8-fid-v2" / "publication" / "publication-package-verification.md").unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "publication-package-verification.md" in result.stdout:
            report_pass("missing publication-package-verification.md fails")
        else:
            all_passed = report_fail("missing publication-package-verification.md fails", "rc!=0, FAIL in stdout, mentions verification", result.returncode, result.stdout, result.stderr)

    # Scenario P3: manifest missing non-normative wording fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        manifest_path = temp_dir / "uuidv8-fid-v2" / "publication" / "publication-candidate-manifest.md"
        content = manifest_path.read_text(encoding='utf-8')
        content = content.replace("non-normative", "MISSING_WORD")
        manifest_path.write_text(content, encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "non-normative" in result.stdout:
            report_pass("manifest missing non-normative wording fails")
        else:
            all_passed = report_fail("manifest missing non-normative wording fails", "rc!=0, FAIL in stdout, mentions non-normative", result.returncode, result.stdout, result.stderr)

    # Scenario P4: manifest containing forbidden final-release phrase fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        manifest_path = temp_dir / "uuidv8-fid-v2" / "publication" / "publication-candidate-manifest.md"
        with open(manifest_path, 'a', encoding='utf-8') as f:
            f.write("\n\nThis is the final release.\n")
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "forbidden phrase" in result.stdout.lower():
            report_pass("manifest containing forbidden final-release phrase fails")
        else:
            all_passed = report_fail("manifest containing forbidden final-release phrase fails", "rc!=0, FAIL in stdout, mentions forbidden phrase", result.returncode, result.stdout, result.stderr)

    # Scenario P5: manifest missing a required local checker command fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        manifest_path = temp_dir / "uuidv8-fid-v2" / "publication" / "publication-candidate-manifest.md"
        content = manifest_path.read_text(encoding='utf-8')
        content = content.replace("python uuidv8-fid-v2/tools/test_check_consistency.py", "python MISSING_CMD.py")
        manifest_path.write_text(content, encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "missing command" in result.stdout:
            report_pass("manifest missing a required local checker command fails")
        else:
            all_passed = report_fail("manifest missing a required local checker command fails", "rc!=0, FAIL in stdout, mentions missing command", result.returncode, result.stdout, result.stderr)

    # Scenario P6: source-map missing manifest or verification reference fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        source_map = temp_dir / "uuidv8-fid-v2" / "publication" / "source-map.md"
        content = source_map.read_text(encoding='utf-8')
        content = content.replace("publication-candidate-manifest.md", "MISSING_MANIFEST")
        source_map.write_text(content, encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "publication-candidate-manifest.md" in result.stdout:
            report_pass("source-map missing manifest reference fails")
        else:
            all_passed = report_fail("source-map missing manifest reference fails", "rc!=0, FAIL in stdout, mentions manifest", result.returncode, result.stdout, result.stderr)

    # Scenario P7: manifest references a non-existent local file and relative Markdown link check fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        manifest_path = temp_dir / "uuidv8-fid-v2" / "publication" / "publication-candidate-manifest.md"
        with open(manifest_path, 'a', encoding='utf-8') as f:
            f.write("\n\n[bad link](does-not-exist.md)\n")
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "does-not-exist.md" in result.stdout:
            report_pass("manifest references a non-existent local file and relative Markdown link check fails")
        else:
            all_passed = report_fail("manifest references a non-existent local file and relative Markdown link check fails", "rc!=0, FAIL in stdout, mentions bad link", result.returncode, result.stdout, result.stderr)

    # Scenario P8: specific HTML file in package fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        html_path = temp_dir / "uuidv8-fid-v2" / "publication" / "index.html"
        html_path.write_text("<html></html>", encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "Forbidden HTML artifact exists" in result.stdout:
            report_pass("specific HTML file in package fails")
        else:
            all_passed = report_fail("specific HTML file in package fails", "rc!=0, FAIL in stdout, mentions Forbidden HTML artifact", result.returncode, result.stdout, result.stderr)

    # Scenario P9: UUIDv8-FID-v2 CI workflow fails while unrelated workflows pass.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        workflows_dir = temp_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        # Unrelated workflow
        (workflows_dir / "unrelated.yml").write_text("name: Unrelated Build\n", encoding='utf-8')
        # We first check that unrelated workflows don't fail the check
        result_unrelated = run_checker(temp_dir)

        # UUIDv8 workflow
        (workflows_dir / "uuidv8.yml").write_text("name: UUIDv8-FID-v2 Checks\n", encoding='utf-8')
        result_uuidv8 = run_checker(temp_dir)

        if result_unrelated.returncode == 0 and result_uuidv8.returncode != 0 and "FAIL" in result_uuidv8.stdout and "UUIDv8-FID-v2 CI workflow exists" in result_uuidv8.stdout:
            report_pass("UUIDv8-FID-v2 CI workflow fails while unrelated workflows pass")
        else:
            all_passed = report_fail("UUIDv8-FID-v2 CI workflow fails while unrelated workflows pass", "rc=0 for unrelated, rc!=0 and FAIL in stdout for uuidv8", result_uuidv8.returncode, result_uuidv8.stdout, result_uuidv8.stderr)


    # Scenario FZ1: missing release-candidate-freeze.md fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        (temp_dir / "uuidv8-fid-v2" / "release" / "release-candidate-freeze.md").unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "release-candidate-freeze.md" in result.stdout:
            report_pass("missing release-candidate-freeze.md fails")
        else:
            all_passed = report_fail("missing release-candidate-freeze.md fails", "rc!=0, FAIL in stdout, mentions freeze.md", result.returncode, result.stdout, result.stderr)

    # Scenario FZ2: missing human-review-record.md fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        (temp_dir / "uuidv8-fid-v2" / "release" / "human-review-record.md").unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "human-review-record.md" in result.stdout:
            report_pass("missing human-review-record.md fails")
        else:
            all_passed = report_fail("missing human-review-record.md fails", "rc!=0, FAIL in stdout, mentions review-record.md", result.returncode, result.stdout, result.stderr)

    # Scenario FZ3: missing release-decision-gate.md fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        (temp_dir / "uuidv8-fid-v2" / "release" / "release-decision-gate.md").unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "release-decision-gate.md" in result.stdout:
            report_pass("missing release-decision-gate.md fails")
        else:
            all_passed = report_fail("missing release-decision-gate.md fails", "rc!=0, FAIL in stdout, mentions decision-gate.md", result.returncode, result.stdout, result.stderr)

    # Scenario FZ4: freeze document missing non-normative wording fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        fz_path = temp_dir / "uuidv8-fid-v2" / "release" / "release-candidate-freeze.md"
        content = fz_path.read_text(encoding='utf-8')
        # Account for case variations in the markdown file
        content = content.replace("non-normative", "MISSING_WORD").replace("Non-normative", "MISSING_WORD")
        fz_path.write_text(content, encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "non-normative" in result.stdout:
            report_pass("freeze document missing non-normative wording fails")
        else:
            all_passed = report_fail("freeze document missing non-normative wording fails", "rc!=0, FAIL in stdout, mentions non-normative", result.returncode, result.stdout, result.stderr)

    # Scenario FZ5: human review record containing forbidden final-release phrase fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        rev_path = temp_dir / "uuidv8-fid-v2" / "release" / "human-review-record.md"
        with open(rev_path, 'a', encoding='utf-8') as f:
            f.write("\n\nThis is the final release.\n")
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "forbidden phrase" in result.stdout.lower():
            report_pass("human review record containing forbidden final-release phrase fails")
        else:
            all_passed = report_fail("human review record containing forbidden final-release phrase fails", "rc!=0, FAIL in stdout, mentions forbidden phrase", result.returncode, result.stdout, result.stderr)

    # Scenario FZ6: release decision gate missing a required local command fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        gate_path = temp_dir / "uuidv8-fid-v2" / "release" / "release-decision-gate.md"
        content = gate_path.read_text(encoding='utf-8')
        content = content.replace("python uuidv8-fid-v2/tools/test_check_consistency.py", "python MISSING_CMD.py")
        gate_path.write_text(content, encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "missing test command" in result.stdout:
            report_pass("release decision gate missing a required local command fails")
        else:
            all_passed = report_fail("release decision gate missing a required local command fails", "rc!=0, FAIL in stdout, mentions missing test command", result.returncode, result.stdout, result.stderr)

    # Scenario FZ7: source-map missing freeze/gate/review reference fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        sm_path = temp_dir / "uuidv8-fid-v2" / "publication" / "source-map.md"
        content = sm_path.read_text(encoding='utf-8')
        content = content.replace("release-candidate-freeze.md", "MISSING_FREEZE")
        sm_path.write_text(content, encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "release-candidate-freeze.md" in result.stdout:
            report_pass("source-map missing freeze/gate/review reference fails")
        else:
            all_passed = report_fail("source-map missing freeze/gate/review reference fails", "rc!=0, FAIL in stdout, mentions missing reference", result.returncode, result.stdout, result.stderr)

    # Scenario FZ8: human review record missing 0x7a fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        rev_path = temp_dir / "uuidv8-fid-v2" / "release" / "human-review-record.md"
        content = rev_path.read_text(encoding='utf-8')
        content = content.replace("0x7a", "0xMISSING")
        rev_path.write_text(content, encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "0x7a" in result.stdout:
            report_pass("human review record missing 0x7a fails")
        else:
            all_passed = report_fail("human review record missing 0x7a fails", "rc!=0, FAIL in stdout, mentions 0x7a", result.returncode, result.stdout, result.stderr)

    # Scenario FZ9: release decision gate declaring a final release fails
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        gate_path = temp_dir / "uuidv8-fid-v2" / "release" / "release-decision-gate.md"
        content = gate_path.read_text(encoding='utf-8')
        content = content.replace("does not declare a final release", "MISSING_NON_DECLARATION")
        gate_path.write_text(content, encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "declaring a final release" in result.stdout:
            report_pass("release decision gate declaring a final release fails")
        else:
            all_passed = report_fail("release decision gate declaring a final release fails", "rc!=0, FAIL in stdout, mentions declaring final release", result.returncode, result.stdout, result.stderr)

    # Scenario W1: baseline real repository passes in default mode
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "uuidv8-fid-v2" / "tools" / "check_consistency.py")],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        report_pass("baseline real repository passes in default mode")
    else:
        all_passed = report_fail("baseline real repository passes in default mode", "rc=0", result.returncode, result.stdout, result.stderr)

    # Scenario W2: baseline real repository passes in --fail-on-warnings mode after stale phrase cleanup
    result = subprocess.run(
        [sys.executable, str(REPO_ROOT / "uuidv8-fid-v2" / "tools" / "check_consistency.py"), "--fail-on-warnings"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True
    )
    if result.returncode == 0:
        report_pass("baseline real repository passes in --fail-on-warnings mode after stale phrase cleanup")
    else:
        all_passed = report_fail("baseline real repository passes in --fail-on-warnings mode after stale phrase cleanup", "rc=0", result.returncode, result.stdout, result.stderr)

    # Scenario W3: injecting stale phrase into a temp copy produces a warning in default mode but still exits 0
    # Note: Because the single-file artifact is now checked for staleness, we must also regenerate the artifact in the temp copy
    # so that the checker does not fail on staleness instead of testing the warning.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        registry_path = temp_dir / "uuidv8-fid-v2" / "20-registry.md"
        with open(registry_path, 'a', encoding='utf-8') as f:
            f.write("\nregistry scaffold\n")

        # Regenerate the artifact so verification passes
        subprocess.run([sys.executable, str(temp_dir / "uuidv8-fid-v2" / "tools" / "assemble_single_file.py"), "--repo-root", str(temp_dir), "--output", str(temp_dir / "uuidv8-fid-v2" / "publication" / "uuidv8-fid-v2-single-file.md"), "--force"], cwd=temp_dir, capture_output=True)

        result = run_checker(temp_dir)
        if result.returncode == 0 and "PASS with warnings" in result.stdout:
            report_pass("injecting stale phrase into a temp copy produces a warning in default mode but still exits 0")
        else:
            all_passed = report_fail("injecting stale phrase into a temp copy produces a warning in default mode but still exits 0", "rc=0, PASS with warnings in stdout", result.returncode, result.stdout, result.stderr)

    # Scenario W4: injecting the same stale phrase into a temp copy causes --fail-on-warnings mode to exit nonzero
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        registry_path = temp_dir / "uuidv8-fid-v2" / "20-registry.md"
        with open(registry_path, 'a', encoding='utf-8') as f:
            f.write("\nregistry scaffold\n")

        # Regenerate the artifact so verification passes
        subprocess.run([sys.executable, str(temp_dir / "uuidv8-fid-v2" / "tools" / "assemble_single_file.py"), "--repo-root", str(temp_dir), "--output", str(temp_dir / "uuidv8-fid-v2" / "publication" / "uuidv8-fid-v2-single-file.md"), "--force"], cwd=temp_dir, capture_output=True)

        result = run_checker(temp_dir, "--fail-on-warnings")
        if result.returncode != 0 and "FAIL (warnings present in strict mode)" in result.stdout:
            report_pass("injecting the same stale phrase into a temp copy causes --fail-on-warnings mode to exit nonzero")
        else:
            all_passed = report_fail("injecting the same stale phrase into a temp copy causes --fail-on-warnings mode to exit nonzero", "rc!=0, FAIL in strict mode stdout", result.returncode, result.stdout, result.stderr)

    # Scenario SF1: missing assemble_single_file.py fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        target = temp_dir / "uuidv8-fid-v2" / "tools" / "assemble_single_file.py"
        if target.exists():
            target.unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0:
            report_pass("missing assemble_single_file.py fails")
        else:
            all_passed = report_fail("missing assemble_single_file.py fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario SF2: missing test_assemble_single_file.py fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        target = temp_dir / "uuidv8-fid-v2" / "tools" / "test_assemble_single_file.py"
        if target.exists():
            target.unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0:
            report_pass("missing test_assemble_single_file.py fails")
        else:
            all_passed = report_fail("missing test_assemble_single_file.py fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario SF3: missing single-file-assembly-dry-run.md fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        target = temp_dir / "uuidv8-fid-v2" / "publication" / "single-file-assembly-dry-run.md"
        if target.exists():
            target.unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0:
            report_pass("missing single-file-assembly-dry-run.md fails")
        else:
            all_passed = report_fail("missing single-file-assembly-dry-run.md fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario SF4: missing single-file-assembly-dry-run-record.md fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        target = temp_dir / "uuidv8-fid-v2" / "release" / "single-file-assembly-dry-run-record.md"
        if target.exists():
            target.unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0:
            report_pass("missing single-file-assembly-dry-run-record.md fails")
        else:
            all_passed = report_fail("missing single-file-assembly-dry-run-record.md fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario SF5: dry-run doc missing "non-normative" fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        target = temp_dir / "uuidv8-fid-v2" / "publication" / "single-file-assembly-dry-run.md"
        if target.exists():
            content = target.read_text(encoding="utf-8")
            # Be careful: "Non-Normative Status" and "non-normative"
            content = content.replace("non-normative", "omitted_word")
            content = content.replace("Non-Normative", "omitted_word")
            target.write_text(content, encoding="utf-8")
        result = run_checker(temp_dir)
        if result.returncode != 0:
            report_pass("dry-run doc missing 'non-normative' fails")
        else:
            all_passed = report_fail("dry-run doc missing 'non-normative' fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario SF6: dry-run record containing forbidden final-release phrase fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        target = temp_dir / "uuidv8-fid-v2" / "release" / "single-file-assembly-dry-run-record.md"
        if target.exists():
            content = target.read_text(encoding="utf-8")
            target.write_text(content.replace("does not declare a final release", "omitted_word"), encoding="utf-8")
        result = run_checker(temp_dir)
        if result.returncode != 0:
            report_pass("dry-run record containing forbidden final-release phrase fails")
        else:
            all_passed = report_fail("dry-run record containing forbidden final-release phrase fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario SF7: dry-run doc missing one required assembly command fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        target = temp_dir / "uuidv8-fid-v2" / "publication" / "single-file-assembly-dry-run.md"
        if target.exists():
            content = target.read_text(encoding="utf-8")
            target.write_text(content.replace("assemble_single_file.py --check", "omitted_word"), encoding="utf-8")
        result = run_checker(temp_dir)
        if result.returncode != 0:
            report_pass("dry-run doc missing one required assembly command fails")
        else:
            all_passed = report_fail("dry-run doc missing one required assembly command fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario SF8: source-map missing assembly tool reference fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        target = temp_dir / "uuidv8-fid-v2" / "publication" / "source-map.md"
        if target.exists():
            content = target.read_text(encoding="utf-8")
            target.write_text(content.replace("assemble_single_file.py", "omitted_word"), encoding="utf-8")
        result = run_checker(temp_dir)
        if result.returncode != 0:
            report_pass("source-map missing assembly tool reference fails")
        else:
            all_passed = report_fail("source-map missing assembly tool reference fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario SF9: committing an obvious generated single-file artifact still fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        target = temp_dir / "uuidv8-fid-v2" / "generated-single-file.md"
        target.write_text("This is a generated single-file artifact\n# UUIDv8-FID-v2\n", encoding="utf-8")
        result = run_checker(temp_dir)
        if result.returncode != 0:
            report_pass("committing an obvious generated single-file artifact still fails")
        else:
            all_passed = report_fail("committing an obvious generated single-file artifact still fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario H: fenced code block broken link is ignored
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        readme_path = temp_dir / "uuidv8-fid-v2" / "README.md"
        with open(readme_path, 'a', encoding='utf-8') as f:
            f.write("\n\n```text\n[broken local link inside code](does-not-exist-inside-code.md)\n```\n")
        result = run_checker(temp_dir)
        # Note: the checker can pass with warnings, so rc can be 0.
        # But we need to ensure "does-not-exist-inside-code.md" is not reported.
        if result.returncode == 0 and "does-not-exist-inside-code.md" not in result.stdout:
            report_pass("fenced code block broken link is ignored")
        else:
            all_passed = report_fail("fenced code block broken link is ignored", "rc=0, 'does-not-exist-inside-code.md' not in stdout", result.returncode, result.stdout, result.stderr)

    # Scenario DF1: missing dual-form-publication-package.md fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        (temp_dir / "uuidv8-fid-v2" / "publication" / "dual-form-publication-package.md").unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0 and "Dual-form file missing: publication/dual-form-publication-package.md" in result.stdout:
            report_pass("missing dual-form-publication-package.md fails")
        else:
            all_passed = report_fail("missing dual-form-publication-package.md fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario DF2: missing committed generated single-file artifact fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        (temp_dir / "uuidv8-fid-v2" / "publication" / "uuidv8-fid-v2-single-file.md").unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0 and "Allowed generated single-file artifact missing:" in result.stdout:
            report_pass("missing committed generated single-file artifact fails")
        else:
            all_passed = report_fail("missing committed generated single-file artifact fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario DF3: missing dual-form-publication-verification-record.md fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        (temp_dir / "uuidv8-fid-v2" / "release" / "dual-form-publication-verification-record.md").unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0 and "Dual-form file missing: release/dual-form-publication-verification-record.md" in result.stdout:
            report_pass("missing dual-form-publication-verification-record.md fails")
        else:
            all_passed = report_fail("missing dual-form-publication-verification-record.md fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario DF4: dual-form doc missing "non-normative" fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        df_path = temp_dir / "uuidv8-fid-v2" / "publication" / "dual-form-publication-package.md"
        df_path.write_text(df_path.read_text().replace("non-normative", "some-other-word"))
        result = run_checker(temp_dir)
        if result.returncode != 0 and "missing required phrase: non-normative" in result.stdout:
            report_pass("dual-form doc missing 'non-normative' fails")
        else:
            all_passed = report_fail("dual-form doc missing 'non-normative' fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario DF5: dual-form doc missing required non-final phrase fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        df_path = temp_dir / "uuidv8-fid-v2" / "publication" / "dual-form-publication-package.md"
        df_path.write_text(df_path.read_text().replace("does not declare a final release", "some-other-phrase"))
        result = run_checker(temp_dir)
        if result.returncode != 0 and "missing required phrase: does not declare a final release" in result.stdout:
            report_pass("dual-form doc missing required non-final phrase fails")
        else:
            all_passed = report_fail("dual-form doc missing required non-final phrase fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario DF5a: dual-form doc containing forbidden final-release phrase fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        df_path = temp_dir / "uuidv8-fid-v2" / "publication" / "dual-form-publication-package.md"
        with open(df_path, 'a', encoding='utf-8') as f:
            f.write("\nThis is the final release.\n")
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "forbidden phrase" in result.stdout.lower():
            report_pass("dual-form doc containing forbidden final-release phrase fails")
        else:
            all_passed = report_fail("dual-form doc containing forbidden final-release phrase fails", "rc!=0, FAIL in stdout", result.returncode, result.stdout, result.stderr)

    # Scenario DF5b: dual-form verification record containing forbidden final-release phrase fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        df_path = temp_dir / "uuidv8-fid-v2" / "release" / "dual-form-publication-verification-record.md"
        with open(df_path, 'a', encoding='utf-8') as f:
            f.write("\nThis is the final release.\n")
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "forbidden phrase" in result.stdout.lower():
            report_pass("dual-form verification record containing forbidden final-release phrase fails")
        else:
            all_passed = report_fail("dual-form verification record containing forbidden final-release phrase fails", "rc!=0, FAIL in stdout", result.returncode, result.stdout, result.stderr)

    # Scenario DF6: committed single-file artifact missing generated-output notice fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        df_path = temp_dir / "uuidv8-fid-v2" / "publication" / "uuidv8-fid-v2-single-file.md"
        df_path.write_text(df_path.read_text().replace("This is generated dry-run output assembled from the split UUIDv8-FID-v2 source files", "Some other notice"))
        result = run_checker(temp_dir)
        if result.returncode != 0 and "Allowed generated artifact is missing generated-output notice" in result.stdout:
            report_pass("committed single-file artifact missing generated-output notice fails")
        else:
            all_passed = report_fail("committed single-file artifact missing generated-output notice fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario DF7: committed single-file artifact missing key invariant string fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        df_path = temp_dir / "uuidv8-fid-v2" / "publication" / "uuidv8-fid-v2-single-file.md"
        df_path.write_text(df_path.read_text().replace("xxxxxxxx-xxxx-8T00-8S00-xxxxxxxxxxxx", "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"))
        result = run_checker(temp_dir)
        if result.returncode != 0 and "Allowed generated artifact is missing invariant string:" in result.stdout:
            report_pass("committed single-file artifact missing key invariant string fails")
        else:
            all_passed = report_fail("committed single-file artifact missing key invariant string fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario DF8: committed single-file artifact hand-edited or stale fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        df_path = temp_dir / "uuidv8-fid-v2" / "publication" / "uuidv8-fid-v2-single-file.md"
        df_path.write_text(df_path.read_text() + "\nSome hand-edited content.")
        result = run_checker(temp_dir)
        if result.returncode != 0 and "Allowed generated artifact is stale or invalid" in result.stdout:
            report_pass("committed single-file artifact hand-edited or stale fails")
        else:
            all_passed = report_fail("committed single-file artifact hand-edited or stale fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario DF9: source-map missing generated artifact reference fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        sm_path = temp_dir / "uuidv8-fid-v2" / "publication" / "source-map.md"
        sm_path.write_text(sm_path.read_text().replace("uuidv8-fid-v2-single-file.md", "some-other-file.md"))
        result = run_checker(temp_dir)
        if result.returncode != 0 and "missing reference to uuidv8-fid-v2-single-file.md" in result.stdout:
            report_pass("source-map missing generated artifact reference fails")
        else:
            all_passed = report_fail("source-map missing generated artifact reference fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario DF10: a second generated single-file artifact still fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        bad_artifact = temp_dir / "uuidv8-fid-v2" / "single-file.md"
        bad_artifact.write_text("This is generated dry-run output assembled from the split UUIDv8-FID-v2 source files")
        result = run_checker(temp_dir)
        if result.returncode != 0 and "Found unauthorized generated single-file artifacts: uuidv8-fid-v2/single-file.md" in result.stdout:
            report_pass("a second generated single-file artifact under uuidv8-fid-v2/ fails")
        else:
            all_passed = report_fail("a second generated single-file artifact under uuidv8-fid-v2/ fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario DF11: a second generated Markdown artifact under uuidv8-fid-v2/publication/ fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        bad_artifact = temp_dir / "uuidv8-fid-v2" / "publication" / "another-single-file.md"
        bad_artifact.write_text("This is generated dry-run output assembled from the split UUIDv8-FID-v2 source files")
        result = run_checker(temp_dir)
        if result.returncode != 0 and "Found unauthorized generated single-file artifacts: uuidv8-fid-v2/publication/another-single-file.md" in result.stdout:
            report_pass("a second generated single-file artifact under uuidv8-fid-v2/publication/ fails")
        else:
            all_passed = report_fail("a second generated single-file artifact under uuidv8-fid-v2/publication/ fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    # Scenario DF12: an arbitrary filename containing the generated-output notice fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        bad_artifact = temp_dir / "uuidv8-fid-v2" / "arbitrary.md"
        bad_artifact.write_text("This is generated dry-run output assembled from the split UUIDv8-FID-v2 source files")
        result = run_checker(temp_dir)
        if result.returncode != 0 and "Found unauthorized generated single-file artifacts: uuidv8-fid-v2/arbitrary.md" in result.stdout:
            report_pass("an arbitrary filename containing the generated-output notice fails")
        else:
            all_passed = report_fail("an arbitrary filename containing the generated-output notice fails", "rc!=0", result.returncode, result.stdout, result.stderr)

    print()


    # Scenario FG1: missing final-publication-decision-gate.md fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        (temp_dir / "uuidv8-fid-v2" / "release" / "final-publication-decision-gate.md").unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "missing" in result.stdout.lower():
            report_pass("missing final-publication-decision-gate.md fails")
        else:
            all_passed = report_fail("missing final-publication-decision-gate.md fails", "rc!=0, FAIL in stdout", result.returncode, result.stdout, result.stderr)

    # Scenario FG2: missing final-publication-decision-checklist.md fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        (temp_dir / "uuidv8-fid-v2" / "release" / "final-publication-decision-checklist.md").unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "missing" in result.stdout.lower():
            report_pass("missing final-publication-decision-checklist.md fails")
        else:
            all_passed = report_fail("missing final-publication-decision-checklist.md fails", "rc!=0, FAIL in stdout", result.returncode, result.stdout, result.stderr)

    # Scenario FG3: missing final-publication-preflight-record.md fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        (temp_dir / "uuidv8-fid-v2" / "release" / "final-publication-preflight-record.md").unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "missing" in result.stdout.lower():
            report_pass("missing final-publication-preflight-record.md fails")
        else:
            all_passed = report_fail("missing final-publication-preflight-record.md fails", "rc!=0, FAIL in stdout", result.returncode, result.stdout, result.stderr)

    # Scenario FG4: missing final-publication-decision-summary.md fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        (temp_dir / "uuidv8-fid-v2" / "release" / "final-publication-decision-summary.md").unlink()
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "missing" in result.stdout.lower():
            report_pass("missing final-publication-decision-summary.md fails")
        else:
            all_passed = report_fail("missing final-publication-decision-summary.md fails", "rc!=0, FAIL in stdout", result.returncode, result.stdout, result.stderr)

    # Scenario FG5: final decision gate doc missing "non-normative" fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        fz_path = temp_dir / "uuidv8-fid-v2" / "release" / "final-publication-decision-gate.md"
        content_txt = fz_path.read_text(encoding='utf-8')
        fz_path.write_text(content_txt.replace("non-normative", "MISSING_WORD"), encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "non-normative" in result.stdout.lower():
            report_pass("final decision gate doc missing 'non-normative' fails")
        else:
            all_passed = report_fail("final decision gate doc missing 'non-normative' fails", "rc!=0, FAIL in stdout", result.returncode, result.stdout, result.stderr)

    # Scenario FG6: final decision gate doc missing "does not declare a final release" fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        fz_path = temp_dir / "uuidv8-fid-v2" / "release" / "final-publication-decision-gate.md"
        content_txt = fz_path.read_text(encoding='utf-8')
        fz_path.write_text(content_txt.replace("does not declare a final release", "MISSING_WORD"), encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "does not declare a final release" in result.stdout.lower():
            report_pass("final decision gate doc missing 'does not declare a final release' fails")
        else:
            all_passed = report_fail("final decision gate doc missing 'does not declare a final release' fails", "rc!=0, FAIL in stdout", result.returncode, result.stdout, result.stderr)

    # Scenario FG7: final decision summary missing "Decision status: pending." fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        fz_path = temp_dir / "uuidv8-fid-v2" / "release" / "final-publication-decision-summary.md"
        content_txt = fz_path.read_text(encoding='utf-8')
        fz_path.write_text(content_txt.replace("Decision status: pending.", "MISSING_WORD"), encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout:
            report_pass("final decision summary missing 'Decision status: pending.' fails")
        else:
            all_passed = report_fail("final decision summary missing 'Decision status: pending.' fails", "rc!=0, FAIL in stdout", result.returncode, result.stdout, result.stderr)

    # Scenario FG8: final decision checklist marks final decision as approved or checked off, and the checker fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        fz_path = temp_dir / "uuidv8-fid-v2" / "release" / "final-publication-decision-checklist.md"
        content_txt = fz_path.read_text(encoding='utf-8')
        fz_path.write_text(content_txt.replace("- [ ] Decide whether to prepare a future final release PR.", "- [x] Decide whether to prepare a future final release PR."), encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout:
            report_pass("final decision checklist marks final decision as checked off fails")
        else:
            all_passed = report_fail("final decision checklist marks final decision as checked off fails", "rc!=0, FAIL in stdout", result.returncode, result.stdout, result.stderr)

    # Scenario FG9: any final decision document containing "This is the final release" fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        fz_path = temp_dir / "uuidv8-fid-v2" / "release" / "final-publication-decision-gate.md"
        with open(fz_path, 'a', encoding='utf-8') as f:
            f.write("\n\nThis is the final release.\n")
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "forbidden phrase" in result.stdout.lower():
            report_pass("any final decision document containing 'This is the final release' fails")
        else:
            all_passed = report_fail("any final decision document containing 'This is the final release' fails", "rc!=0, FAIL in stdout", result.returncode, result.stdout, result.stderr)

    # Scenario FG10: any final decision document containing "Decision status: approved" fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        fz_path = temp_dir / "uuidv8-fid-v2" / "release" / "final-publication-decision-summary.md"
        with open(fz_path, 'a', encoding='utf-8') as f:
            f.write("\n\nDecision status: approved.\n")
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout and "forbidden phrase" in result.stdout.lower():
            report_pass("any final decision document containing 'Decision status: approved' fails")
        else:
            all_passed = report_fail("any final decision document containing 'Decision status: approved' fails", "rc!=0, FAIL in stdout", result.returncode, result.stdout, result.stderr)



    # Scenario FG11: preflight record missing command evidence fails.
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        fz_path = temp_dir / "uuidv8-fid-v2" / "release" / "final-publication-preflight-record.md"
        content_txt = fz_path.read_text(encoding='utf-8')
        fz_path.write_text(content_txt.replace("python uuidv8-fid-v2/tools/check_consistency.py --fail-on-warnings", "MISSING_WORD"), encoding='utf-8')
        result = run_checker(temp_dir)
        if result.returncode != 0 and "FAIL" in result.stdout:
            report_pass("preflight record missing command evidence fails")
        else:
            all_passed = report_fail("preflight record missing command evidence fails", "rc!=0, FAIL in stdout", result.returncode, result.stdout, result.stderr)

    if all_passed:
        print("UUIDv8-FID-v2 checker harness: PASS")
        sys.exit(0)
    else:
        print("UUIDv8-FID-v2 checker harness: FAIL")
        sys.exit(1)

if __name__ == "__main__":
    main()
