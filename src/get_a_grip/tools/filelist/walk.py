import json
import os
from datetime import datetime
from typing import List, Dict
from get_a_grip.tools.whoami import get_effective_user, get_user_principal_name
from get_a_grip.tools.filelist.types import FileList, FileItem

def unix_to_filetime(unix_timestamp: float) -> str:
    """
    Converts a Unix timestamp to a Windows FILETIME 64-bit value string.
    FILETIME is the number of 100-nanosecond intervals since January 1, 1601.
    """
    # Unix epoch is 1970-01-01. Offset is 11,644,473,600 seconds.
    # Convert to 100-nanosecond intervals.
    filetime = int((unix_timestamp + 11644473600) * 10_000_000)
    return str(filetime)

def scan(root_path: str) -> FileList:
    """
    Recursively scans a directory using os.walk and returns detailed information for all files and directories.
    Includes the root directory itself in the output.
    """
    root_abs = os.path.abspath(root_path)
    files_list: List[FileItem] = []
    dirs_list: List[FileItem] = []

    # Include the root directory itself
    try:
        stat = os.stat(root_abs)
        # On Windows, st_file_attributes is available in Python
        attributes = getattr(stat, "st_file_attributes", 0)
        dirs_list.append({
            "Filename": root_abs,
            "Size": stat.st_size,
            "Date Modified": unix_to_filetime(stat.st_mtime),
            "Date Created": unix_to_filetime(stat.st_ctime),
            "Attributes": attributes
        })
    except OSError as e:
        print(f"Warning: Could not access root directory {root_abs}: {e}")

    # Use os.walk to verify subdirectories and files
    for dirpath, dirnames, filenames in os.walk(root_abs):
        # Process directories
        for d in dirnames:
            full_path = os.path.join(dirpath, d)
            try:
                stat = os.stat(full_path)
                attributes = getattr(stat, "st_file_attributes", 0)
                dirs_list.append({
                    "Filename": full_path,
                    "Size": stat.st_size,
                    "Date Modified": unix_to_filetime(stat.st_mtime),
                    "Date Created": unix_to_filetime(stat.st_ctime),
                    "Attributes": attributes
                })
            except OSError as e:
                print(f"Warning: Could not access {full_path}: {e}")

        # Process files
        for f in filenames:
            full_path = os.path.join(dirpath, f)
            try:
                stat = os.stat(full_path)
                attributes = getattr(stat, "st_file_attributes", 0)
                files_list.append({
                    "Filename": full_path,
                    "Size": stat.st_size,
                    "Date Modified": unix_to_filetime(stat.st_mtime),
                    "Date Created": unix_to_filetime(stat.st_ctime),
                    "Attributes": attributes
                })
            except OSError as e:
                print(f"Warning: Could not access {full_path}: {e}")

    return FileList(files=files_list, dirs=dirs_list)

def save_to_json(data: FileList, output_path: str) -> None:
    """
    Saves the scanned data to a JSON-LD file with an external context.
    """
    output_data = {
        "@context": [
            "https://purl.org/gag/schema/filelist.jsonld"
        ],
        "@type": "ItemList",
        "observedAt": datetime.now().isoformat(),
        "observer": {
            "uid": get_effective_user(),
            "userPrincipalName": get_user_principal_name()
        },
        "files": data.get("files", []),
        "dirs": data.get("dirs", [])
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
