import json
import os
from pathlib import Path
from typing import List, Optional

def scan_directory(root_path: str) -> List[str]:
    """
    Recursively scans a directory and returns a list of all file paths.

    Args:
        root_path (str): The directory path to scan.

    Returns:
        List[str]: A list of absolute file paths found under the root_path.
    """
    root = Path(root_path).resolve()
    file_list = []

    for path in root.rglob("*"):
        if path.is_file():
            file_list.append(str(path))

    return file_list

def save_to_json(data: List[str], output_path: str) -> None:
    """
    Saves a list of strings to a JSON file.

    Args:
        data (List[str]): The data to save.
        output_path (str): The destination file path.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def run_scanner(directory: str, output: Optional[str] = None) -> str:
    """
    Main execution logic for scanning a directory and saving the results.

    Args:
        directory (str): The directory to scan.
        output (Optional[str]): The output file path. Defaults to a specific UUID-based filename.

    Returns:
        str: The path of the created JSON file.
    """
    if not output:
        output = "fbd0009d-e91b-414f-9f4f-db3fbd3a16ee.json"

    print(f"Scanning directory: {directory}...")
    files = scan_directory(directory)
    
    print(f"Found {len(files)} files. Saving to {output}...")
    save_to_json(files, output)
    
    return output
