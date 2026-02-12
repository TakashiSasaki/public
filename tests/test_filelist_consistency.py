import os
import pytest
from pathlib import Path
from get_a_grip.tools.filelist import rglob, scandir, walk

def normalize_entries(entries):
    """
    Convert list of file/dir dicts to a dictionary keyed by filename.
    Resolves paths to absolute paths to handle potential slight differences in input handling.
    """
    normalized = {}
    for entry in entries:
        # Resolve to ensure consistent path string format (e.g. c:\\ vs C:\\)
        # Using strict resolve ensures realpath match
        p = Path(entry['Filename']).resolve()
        # Convert to string, ensuring lower case for Windows case-insensitivity consistency if needed
        # But let's try exact path match first as resolve() handles casing mostly.
        normalized[str(p)] = entry
    return normalized

def compare_results(result1, result2, mode1_name, mode2_name):
    """
    Compare two scan results for equality of filenames and metadata.
    """
    # Compare Files
    files1 = normalize_entries(result1.get('files', []))
    files2 = normalize_entries(result2.get('files', []))
    
    keys1 = set(files1.keys())
    keys2 = set(files2.keys())
    
    # Debug info on mismatch
    if keys1 != keys2:
        diff_1_minus_2 = keys1 - keys2
        diff_2_minus_1 = keys2 - keys1
        error_msg = f"File list mismatch between {mode1_name} and {mode2_name}.\n"
        if diff_1_minus_2:
            error_msg += f"In {mode1_name} only: {diff_1_minus_2}\n"
        if diff_2_minus_1:
            error_msg += f"In {mode2_name} only: {diff_2_minus_1}\n"
        pytest.fail(error_msg)
    
    # Compare Metadata (Attributes)
    for key in keys1:
        f1 = files1[key]
        f2 = files2[key]
        
        # Helper for error messages
        ctx = f"File: {key} ({mode1_name} vs {mode2_name})"
        
        assert f1['Size'] == f2['Size'], f"{ctx} Size mismatch: {f1['Size']} != {f2['Size']}"
        assert f1['Date Modified'] == f2['Date Modified'], f"{ctx} Date Modified mismatch"
        assert f1['Date Created'] == f2['Date Created'], f"{ctx} Date Created mismatch"
        assert f1['Attributes'] == f2['Attributes'], f"{ctx} Attributes mismatch"

    # Compare Directories
    dirs1 = normalize_entries(result1.get('dirs', []))
    dirs2 = normalize_entries(result2.get('dirs', []))
    
    dkeys1 = set(dirs1.keys())
    dkeys2 = set(dirs2.keys())
    
    if dkeys1 != dkeys2:
        diff_1_minus_2 = dkeys1 - dkeys2
        diff_2_minus_1 = dkeys2 - dkeys1
        error_msg = f"Directory list mismatch between {mode1_name} and {mode2_name}.\n"
        if diff_1_minus_2:
            error_msg += f"In {mode1_name} only: {diff_1_minus_2}\n"
        if diff_2_minus_1:
            error_msg += f"In {mode2_name} only: {diff_2_minus_1}\n"
        pytest.fail(error_msg)
    
    for key in dkeys1:
        d1 = dirs1[key]
        d2 = dirs2[key]
        
        ctx = f"Dir: {key} ({mode1_name} vs {mode2_name})"
        
        # Check basic attributes
        # Size for directories is technically 0 or block size, usually consistent but might vary by implementation method (stat vs scandir cached)
        # Let's focus on Attributes and Dates
        assert d1['Attributes'] == d2['Attributes'], f"{ctx} Attributes mismatch"
        assert d1['Date Modified'] == d2['Date Modified'], f"{ctx} Date Modified mismatch"


def test_consistency_scandir_rglob_walk(tmp_path):
    """
    Verify that rglob, scandir, and walk implementations produce identical results from a real filesystem scan.
    """
    # Setup robust test environment
    root = tmp_path / "consistency_root"
    root.mkdir()
    
    (root / "file1.txt").write_text("Hello World")
    
    subdir = root / "subdir"
    subdir.mkdir()
    (subdir / "file2.bin").write_bytes(b"\x00\x01\x02")
    
    # Nested deeply
    deep = subdir / "deep" / "structure"
    deep.mkdir(parents=True)
    (deep / "deep_file.log").write_text("Log")
    
    target_path = str(root.resolve())
    
    # Execute all scanning methods
    print(f"Scanning {target_path} with rglob...")
    res_rglob = rglob.scan_directory(target_path)
    
    print(f"Scanning {target_path} with scandir...")
    res_scandir = scandir.scan_directory(target_path)
    
    print(f"Scanning {target_path} with walk...")
    res_walk = walk.scan_directory(target_path)
    
    # Compare
    # scandir vs rglob
    compare_results(res_scandir, res_rglob, "scandir", "rglob")
    
    # scandir vs walk
    compare_results(res_scandir, res_walk, "scandir", "walk")
    
    # walk vs rglob (transitive, but good to check explicit edge cases if any)
    compare_results(res_walk, res_rglob, "walk", "rglob")
