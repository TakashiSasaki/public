import json
import os
from pathlib import Path
from typing import List, Optional

def unix_to_filetime(unix_timestamp: float) -> str:
    """
    Converts a Unix timestamp to a Windows FILETIME 64-bit value string.
    FILETIME is the number of 100-nanosecond intervals since January 1, 1601.
    """
    # Unix epoch is 1970-01-01. Offset is 11,644,473,600 seconds.
    # Convert to 100-nanosecond intervals.
    filetime = int((unix_timestamp + 11644473600) * 10_000_000)
    return str(filetime)

def scan_directory(root_path: str) -> List[dict]:
    """
    Recursively scans a directory and returns detailed information for all files.
    """
    root = Path(root_path).resolve()
    file_info_list = []

    for path in root.rglob("*"):
        if path.is_file():
            try:
                stat = path.stat()
                # On Windows, st_file_attributes is available in Python 3.12+
                attributes = getattr(stat, "st_file_attributes", 0)
                
                file_info = {
                    "Filename": str(path),
                    "Size": stat.st_size,
                    "Date Modified": unix_to_filetime(stat.st_mtime),
                    "Date Created": unix_to_filetime(stat.st_ctime),
                    "Attributes": attributes
                }
                file_info_list.append(file_info)
            except (OSError, PermissionError) as e:
                print(f"Warning: Could not access {path}: {e}")

    return file_info_list

def save_to_json(data: List[dict], output_path: str) -> None:
    """
    Saves the scanned data to a JSON-LD file with an external context.
    """
    uuid_urn = "urn:uuid:fbd0009d-e91b-414f-9f4f-db3fbd3a16ee"
    
    output_data = {
        "@context": [
            uuid_urn,
            "src/get_a_grip/context.json"
        ],
        "@type": "ItemList",
        "files": data
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

def run_scanner(directory: str, output: Optional[str] = None) -> str:
    """
    Main execution logic for scanning a directory and saving the results in the new format.
    """
    if not output:
        output = "fbd0009d-e91b-414f-9f4f-db3fbd3a16ee.json"

    print(f"Scanning directory: {directory}...")
    file_data = scan_directory(directory)
    
    print(f"Found {len(file_data)} files. Saving to {output} in detailed format...")
    save_to_json(file_data, output)
    
    return output
