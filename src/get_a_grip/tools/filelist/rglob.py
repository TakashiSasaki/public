import json
import logging
from datetime import datetime
from pathlib import Path
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
    """
    root = Path(root_path).resolve()
    files: List[FileItem] = []
    directories: List[FileItem] = []

    # Include the root directory itself
    try:
        stat = root.stat()
        attributes = getattr(stat, "st_file_attributes", 0)
        directories.append({
            "Filename": str(root),
            "Size": stat.st_size,
            "Date Modified": unix_to_filetime(stat.st_mtime),
            "Date Created": unix_to_filetime(stat.st_ctime),
            "Attributes": attributes
        })
    except (OSError, PermissionError) as e:
        logger.warning("Could not access root directory %s: %s", root, e)

    for path in root.rglob("*"):
        try:
            stat = path.stat()
            # On Windows, st_file_attributes is available in Python 3.12+
            attributes = getattr(stat, "st_file_attributes", 0)
            
            item_info = {
                "Filename": str(path),
                "Size": stat.st_size,
                "Date Modified": unix_to_filetime(stat.st_mtime),
                "Date Created": unix_to_filetime(stat.st_ctime),
                "Attributes": attributes
            }

            if path.is_file():
                files.append(item_info)
            elif path.is_dir():
                directories.append(item_info)
        except (OSError, PermissionError) as e:
            logger.warning("Could not access %s: %s", path, e)

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


