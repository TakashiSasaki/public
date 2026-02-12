import os
import json
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
from get_a_grip.tools.filelist.rglob import unix_to_filetime, scan_directory, save_to_json

# --- Unit Tests ---

def test_unix_to_filetime():
    # 1970-01-01 00:00:00 UTC -> 116444736000000000 (Windows FileTime)
    # The constants in the file are:
    # (unix_timestamp + 11644473600) * 10_000_000
    expected_epoch = str(int(11644473600 * 10_000_000))
    assert unix_to_filetime(0) == expected_epoch
    
    # 1 second after epoch
    expected_1s = str(int((1 + 11644473600) * 10_000_000))
    assert unix_to_filetime(1) == expected_1s

# --- Integration / Functional Tests ---

def test_scan_directory_integration(tmp_path):
    """
    Test scanning a real directory structure created in tmp_path.
    """
    # Setup test directory structure
    # tmp_path/
    #   root/
    #     file1.txt
    #     subdir/
    #       file2.txt
    
    root = tmp_path / "root"
    root.mkdir()
    
    file1 = root / "file1.txt"
    file1.write_text("content1")
    
    subdir = root / "subdir"
    subdir.mkdir()
    
    file2 = subdir / "file2.txt"
    file2.write_text("content2")
    
    # Execute scan
    result = scan_directory(str(root))
    
    # Verify Structure
    assert "files" in result
    assert "dirs" in result
    
    files = result["files"]
    dirs = result["dirs"]
    
    # Check count
    # Files: file1.txt, file2.txt
    assert len(files) == 2
    
    # Dirs: root (included by implementation), subdir
    assert len(dirs) == 2 
    
    # Verify contents using resolved paths for robust comparison
    filenames = [str(Path(f["Filename"]).resolve()) for f in files]
    assert str(file1.resolve()) in filenames
    assert str(file2.resolve()) in filenames
    
    dirnames = [str(Path(d["Filename"]).resolve()) for d in dirs]
    assert str(root.resolve()) in dirnames
    assert str(subdir.resolve()) in dirnames
    
    # Check metadata
    f1_data = next(f for f in files if Path(f["Filename"]).name == "file1.txt")
    assert f1_data["Size"] == len("content1")
    assert "Date Modified" in f1_data
    assert "Date Created" in f1_data

def test_save_to_json(tmp_path):
    output_file = tmp_path / "output.json"
    data = {
        "files": [{"Filename": "a.txt", "Size": 10}],
        "dirs": []
    }
    
    # Mock user info functions
    with patch('get_a_grip.tools.filelist.rglob.get_effective_user', return_value="mock_user"), \
         patch('get_a_grip.tools.filelist.rglob.get_user_principal_name', return_value="mock_upn"):
        
        save_to_json(data, str(output_file))
        
    assert output_file.exists()
    content = json.loads(output_file.read_text(encoding="utf-8"))
    
    assert content["@type"] == "ItemList"
    assert len(content["files"]) == 1
    assert content["observer"]["uid"] == "mock_user"
    assert "observedAt" in content
