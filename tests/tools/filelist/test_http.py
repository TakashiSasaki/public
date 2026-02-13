import pytest
import json
import os
from unittest.mock import patch, MagicMock

# Import the module under test
# Assuming the package is installed in editable mode or PYTHONPATH is set correctly by test runner
from get_a_grip.tools.filelist.http import scan, safe_filetime, fetch_raw_from_everything

# --- Unit Tests for Utility Functions ---

def test_safe_filetime_basic():
    # Should strip non-digits
    assert safe_filetime("2023-01-01 12:00:00") == "20230101120000"
    assert safe_filetime("123abc456") == "123456"

def test_safe_filetime_empty():
    assert safe_filetime(None) == "0"
    assert safe_filetime("") == "0"

def test_safe_filetime_int():
    assert safe_filetime(12345) == "12345"

# --- Integration Tests using Mocks (Simulated Network) ---

@patch('urllib.request.urlopen')
def test_scan_success(mock_urlopen):
    """
    Test successful execution of scan with mocked HTTP response.
    """
    # 1. Setup Mock Response
    mock_response = MagicMock()
    mock_response.status = 200
    
    # Simulate JSON data returned by Everything HTTP API
    example_data = {
        "totalResults": 2,
        "results": [
            {
                "name": "file.txt",
                "path": "C:\\Data",
                "size": 1024,
                "date_modified": "2023-01-01 12:00:00",
                "type": "file",
                "attributes": 32
            },
             {
                "name": "SubDir",
                "path": "C:\\Data",
                "size": 0,
                "date_modified": "2023-01-02 12:00:00",
                "type": "folder",
                "attributes": 16
            }
        ]
    }
    
    # Simulate read() returning bytes
    # The actual implementation calls response.read().decode('utf-8')
    mock_response.read.return_value = json.dumps(example_data).encode('utf-8')
    
    # Context manager support
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = None
    
    mock_urlopen.return_value = mock_response
    
    # 2. Execute
    result = scan("test", ip="127.0.0.1", port=80, count=10)
    
    # 3. Verify Structure
    assert "files" in result
    assert "dirs" in result
    assert len(result["files"]) == 1
    assert len(result["dirs"]) == 1
    
    # Verify Content
    # File check
    file_info = result["files"][0]
    expected_path = os.path.join("C:\\Data", "file.txt")
    assert file_info["Filename"] == expected_path
    assert file_info["Size"] == 1024
    assert file_info["Date Modified"] == "20230101120000"
    assert file_info["Attributes"] == 32
    
    # Dir check
    dir_info = result["dirs"][0]
    expected_dir = os.path.join("C:\\Data", "SubDir")
    assert dir_info["Filename"] == expected_dir
    assert dir_info["Attributes"] == 16

@patch('urllib.request.urlopen')
def test_fetch_raw_http_error(mock_urlopen):
    """
    Test handling of HTTP error codes.
    """
    mock_response = MagicMock()
    mock_response.status = 500
    mock_response.__enter__.return_value = mock_response
    mock_response.__exit__.return_value = None
    
    mock_urlopen.return_value = mock_response
    
    with pytest.raises(Exception) as excinfo:
        fetch_raw_from_everything("127.0.0.1", 80)
    
    assert "HTTP 500" in str(excinfo.value)

@patch('urllib.request.urlopen')
def test_fetch_raw_connection_error(mock_urlopen):
    """
    Test handling of network exceptions (e.g. connection refused).
    """
    mock_urlopen.side_effect = Exception("Connection refused")
    
    with pytest.raises(Exception) as excinfo:
        fetch_raw_from_everything("127.0.0.1", 80)
    
    assert "Connection error" in str(excinfo.value)
    assert "Connection refused" in str(excinfo.value)
