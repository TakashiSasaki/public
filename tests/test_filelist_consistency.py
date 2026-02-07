import json
import tempfile
import pytest
import os
from pathlib import Path
from get_a_grip.tools import filelist_rglob, filelist_scandir

# Helper to normalize list of files/dirs for comparison
def normalize_entries(entries):
    """
    Convert list of file/dir dicts to a dictionary keyed by filename.
    Normalize paths if needed, but here we assume both tools produce absolute paths similarly.
    """
    normalized = {}
    for entry in entries:
        normalized[entry['Filename']] = entry
    return normalized

def compare_file_lists(data1, data2):
    files1 = normalize_entries(data1.get('files', []))
    dirs1 = normalize_entries(data1.get('dirs', []))
    files2 = normalize_entries(data2.get('files', []))
    dirs2 = normalize_entries(data2.get('dirs', []))

    # Check if keys (filenames) match exactly
    assert set(files1.keys()) == set(files2.keys()), "File list mismatch between implementations"
    assert set(dirs1.keys()) == set(dirs2.keys()), "Directory list mismatch between implementations"

    # Deep compare metadata for files
    for key in files1:
        entry1 = files1[key]
        entry2 = files2[key]
        
        # Compare critical fields
        logging_ctx = f"Mismatch in file: {key}"
        assert entry1['Size'] == entry2['Size'], f"{logging_ctx} (Size)"
        assert entry1['Date Modified'] == entry2['Date Modified'], f"{logging_ctx} (Date Modified)"
        assert entry1['Date Created'] == entry2['Date Created'], f"{logging_ctx} (Date Created)"
        # Attributes might be tricky if not consistently fetched, but let's assume they should match
        assert entry1['Attributes'] == entry2['Attributes'], f"{logging_ctx} (Attributes)"

def test_filelist_implementations_match(tmp_path):
    """
    Test that filelist.py (pathlib-based) and filelist_scandir.py (os.scandir-based)
    produce identical output for the current test directory.
    """
    # Create some dummy files/dirs to scan
    (tmp_path / "subdir").mkdir()
    (tmp_path / "file1.txt").write_text("content1")
    (tmp_path / "subdir" / "file2.txt").write_text("content2")

    # Run scans
    # We scan the tmp_path to ensure a controlled environment
    root_dir = str(tmp_path)
    
    data_legacy = filelist_rglob.scan_directory(root_dir)
    data_scandir = filelist_scandir.scan_directory(root_dir)

    # Compare results
    compare_file_lists(data_legacy, data_scandir)

if __name__ == "__main__":
    # If run directly, run scan on current directory and compare
    import sys
    
    print("Running ad-hoc comparison on current directory...")
    cwd = os.getcwd()
    
    try:
        data_legacy = filelist_rglob.scan_directory(cwd)
        data_scandir = filelist_scandir.scan_directory(cwd)
        compare_file_lists(data_legacy, data_scandir)
        print("SUCCESS: Both implementations match on current directory.")
    except AssertionError as e:
        print(f"FAILURE: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
