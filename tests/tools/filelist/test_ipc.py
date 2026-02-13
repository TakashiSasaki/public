import os
import json
import pytest
from unittest.mock import patch, MagicMock
from get_a_grip.tools.filelist.ipc import scan, save_to_json, main

# --- Unit Tests ---

@patch('get_a_grip.tools.filelist.ipc.scan_by_ipc')
def test_scan_directory_query_generation(mock_scan):
    """
    Verify that scan_directory_via_everything generates the correct Everything query
    (quoted path with trailing backslash).
    """
    # Simulate return
    mock_scan.return_value = {}
    
    # Test path
    test_path = os.path.abspath("C:/Data") # Normalized path
    scan("C:/Data")
    
    args, kwargs = mock_scan.call_args
    query = args[0]
    
    # The query should be f'"{search_path}"'
    # search_path should enforce trailing separator
    
    # Check quotes
    assert query.startswith('"')
    assert query.endswith('"')
    
    # Content inside quotes
    content = query.strip('"')
    # It should match abspath + separator
    expected_start = test_path
    assert content.startswith(expected_start)
    assert content.endswith(os.sep)

def test_save_to_json_structure(tmp_path):
    """
    Verify save_to_json writes a valid JSON-LD file with correct metadata.
    """
    output_file = tmp_path / "output.json"
    data = {
        "files": [{"Filename": "test.txt", "Size": 123}],
        "dirs": [{"Filename": "subdir"}]
    }
    
    # Mock user info functions to ensure stable output
    with patch('get_a_grip.tools.filelist.ipc.get_effective_user', return_value="mock_uid"), \
         patch('get_a_grip.tools.filelist.ipc.get_user_principal_name', return_value="mock_upn"):
        
        save_to_json(data, str(output_file))
        
    assert output_file.exists()
    
    with open(output_file, 'r', encoding='utf-8') as f:
        content = json.load(f)
        
    # Check JSON-LD context
    assert "@context" in content
    assert content["@type"] == "ItemList"
    
    # Check Metadata
    assert content["observer"]["uid"] == "mock_uid"
    assert content["observer"]["userPrincipalName"] == "mock_upn"
    assert "observedAtTime" in content
    
    # Check Payload
    assert len(content["files"]) == 1
    assert content["files"][0]["Filename"] == "test.txt"
    assert len(content["dirs"]) == 1

# --- Integration / Full Flow Tests ---

@patch('get_a_grip.tools.filelist.ipc.scan_by_ipc')
@patch('get_a_grip.tools.filelist.ipc.save_to_json')
def test_main_success(mock_save, mock_scan):
    """
    Test successful execution of main() flow.
    """
    # Setup mock data
    mock_scan.return_value = {"files": [], "dirs": []}
    
    # Mock sys.argv
    # Script name + Root Path + Output Path
    test_args = ["ipc.py", "C:\\Valid\\Path", "output.json"]
    
    with patch('sys.argv', test_args):
        # Mock os.path.isdir to return True for our fake path
        with patch('os.path.isdir', return_value=True):
            main()
            
    # Verify sequence
    mock_scan.assert_called_once()
    mock_save.assert_called_once()

@patch('get_a_grip.tools.filelist.ipc.scan_by_ipc')
def test_main_invalid_directory(mock_scan, caplog):
    """
    Test main() handles non-existent directory gracefully.
    """
    test_args = ["ipc.py", "InvalidPath", "output.json"]
    
    with patch('sys.argv', test_args):
        # Mock isdir to False
        with patch('os.path.isdir', return_value=False):
            # Expect exit code 1
            with pytest.raises(SystemExit) as e:
                main()
            assert e.value.code == 1
            
    assert "Directory not found" in caplog.text
    mock_scan.assert_not_called()

@patch('get_a_grip.tools.filelist.ipc.scan')
def test_main_exception_handling(mock_scan_dir, caplog):
    """
    Test main() handles exceptions during scanning.
    """
    mock_scan_dir.side_effect = Exception("IPC Error")
    
    test_args = ["ipc.py", "C:\\Path", "output.json"]
    
    with patch('sys.argv', test_args):
        with patch('os.path.isdir', return_value=True):
             with pytest.raises(SystemExit) as e:
                 main()
             assert e.value.code == 1
             
    assert "Error: IPC Error" in caplog.text

@patch('get_a_grip.tools.filelist.ipc.scan_by_ipc')
def test_scan_does_not_print(mock_scan):
    mock_scan.return_value = {"files": [], "dirs": []}

    with patch("builtins.print", side_effect=AssertionError("scan() must not print")):
        result = scan("C:/Data")

    assert result == {"files": [], "dirs": []}
