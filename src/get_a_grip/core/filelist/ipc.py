import sys
import os
import argparse
import json
import logging
from datetime import datetime
from typing import Dict, List
from get_a_grip.contracts.filelist import FileList, FileItem

# Try to import everything_ipc
try:
    from get_a_grip.core.everything_ipc import scan_by_ipc
except ImportError:
    try:
        from ..everything_ipc import scan_by_ipc
    except ImportError:
         # Fallback
         from everything_ipc import scan_by_ipc

from get_a_grip.core.whoami import get_effective_user, get_user_principal_name

logger = logging.getLogger(__name__)

def scan(root_path: str) -> FileList:
    """
    Recursively list all files and directories under root_path using Everything IPC.
    Query used: "<root_path>\"
    """
    root_abs = os.path.abspath(root_path)
    
    # Everything query syntax for recursive directory search: "C:\Path\"
    # We must ensure it ends with a backslash and is quoted.
    if not root_abs.endswith(os.sep):
        search_path = root_abs + os.sep
    else:
        search_path = root_abs
        
    query = f'"{search_path}"'
    
    # count=0 means unlimited results
    return FileList(scan_by_ipc(query, count=0))

def save_to_json(data: FileList, output_path: str) -> None:
    """
    Saves the scanned data to a JSON-LD file.
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

