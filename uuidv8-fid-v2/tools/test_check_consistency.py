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

    # Scenario F: generated single-file artifact fails
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
    with tempfile.TemporaryDirectory() as td:
        temp_dir = Path(td)
        setup_temp_repo(temp_dir)
        registry_path = temp_dir / "uuidv8-fid-v2" / "20-registry.md"
        with open(registry_path, 'a', encoding='utf-8') as f:
            f.write("\nregistry scaffold\n")
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
        result = run_checker(temp_dir, "--fail-on-warnings")
        if result.returncode != 0 and "FAIL (warnings present in strict mode)" in result.stdout:
            report_pass("injecting the same stale phrase into a temp copy causes --fail-on-warnings mode to exit nonzero")
        else:
            all_passed = report_fail("injecting the same stale phrase into a temp copy causes --fail-on-warnings mode to exit nonzero", "rc!=0, FAIL in strict mode stdout", result.returncode, result.stdout, result.stderr)

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

    print()
    if all_passed:
        print("UUIDv8-FID-v2 checker harness: PASS")
        sys.exit(0)
    else:
        print("UUIDv8-FID-v2 checker harness: FAIL")
        sys.exit(1)

if __name__ == "__main__":
    main()
