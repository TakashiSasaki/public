import json
import os
import logging
from datetime import datetime
from typing import List, Dict
from get_a_grip.tools.whoami import get_effective_user, get_user_principal_name
from get_a_grip.tools.filelist.types import FileList, FileItem

logger = logging.getLogger(__name__)

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
    Recursively scans a directory and returns detailed information for all files and directories.
    Includes the root directory itself in the output.
    Uses os.scandir for better performance on Windows.
    """
    root_abs = os.path.abspath(root_path)
    files: List[FileItem] = []
    directories: List[FileItem] = []

    # Include the root directory itself
    try:
        stat_root = os.stat(root_abs)
        attributes = getattr(stat_root, "st_file_attributes", 0)
        directories.append({
            "Filename": root_abs,
            "Size": stat_root.st_size,
            "Date Modified": unix_to_filetime(stat_root.st_mtime),
            "Date Created": unix_to_filetime(stat_root.st_ctime),
            "Attributes": attributes
        })
    except (OSError, PermissionError) as e:
        logger.warning("Could not access root directory %s: %s", root_abs, e)

    # Recursive scan using os.scandir
    # We use a stack to avoid recursion limit and to control flow easier
    stack = [root_abs]
    while stack:
        current_path = stack.pop()
        try:
            with os.scandir(current_path) as it:
                for entry in it:
                    try:
                        # entry.stat() is cached from the directory listing on Windows
                        stat = entry.stat()
                        attributes = getattr(stat, "st_file_attributes", 0)
                        
                        item_info = {
                            "Filename": entry.path,
                            "Size": stat.st_size,
                            "Date Modified": unix_to_filetime(stat.st_mtime),
                            "Date Created": unix_to_filetime(stat.st_ctime),
                            "Attributes": attributes
                        }

                        if entry.is_file():
                            files.append(item_info)
                        elif entry.is_dir():
                            directories.append(item_info)
                            stack.append(entry.path)
                    except (OSError, PermissionError) as e:
                        logger.warning("Could not access %s: %s", entry.path, e)
        except (OSError, PermissionError) as e:
             # This usually happens if we don't have permission to list the directory
             # or if the directory vanished.
             pass

    return FileList(files=files, dirs=directories)

def save_to_json(data: FileList, output_path: str) -> None:
    """
    Saves the scanned data to a JSON-LD file with an external context.
    """
    output_data = {
        "@context": [
            "https://purl.org/gag/schema/filelist.jsonld"
        ],
        "@type": "ItemList",
        "observedAtTime": datetime.now().isoformat(),
        "observer": {
            "uid": get_effective_user(),
            "userPrincipalName": get_user_principal_name()
        },
        "files": data.get("files", []),
        "dirs": data.get("dirs", [])
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) > 2:
        root = sys.argv[1]
        out = sys.argv[2]
        logger.info("Scanning %s with os.scandir...", root)
        data = scan(root)
        save_to_json(data, out)
        logger.info("Saved results to %s", out)
    else:
        logger.info("Usage: filelist_scandir.py <dir> <output.json>")
