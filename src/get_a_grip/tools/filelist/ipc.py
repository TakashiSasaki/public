import sys
import os
import argparse
import json
from datetime import datetime
from typing import Dict, List

# Try to import everything_ipc
try:
    from get_a_grip.tools.everything_ipc import scan_by_ipc
except ImportError:
    try:
        from ..everything_ipc import scan_by_ipc
    except ImportError:
         # Fallback
         from everything_ipc import scan_by_ipc

from get_a_grip.tools.whoami import get_effective_user, get_user_principal_name

def scan_directory_via_everything(root_path: str) -> Dict[str, List[dict]]:
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
    
    print(f"Querying Everything with: {query}")
    # count=0 means unlimited results
    return scan_by_ipc(query, count=0)

def save_to_json(data: Dict[str, List[dict]], output_path: str) -> None:
    """
    Saves the scanned data to a JSON-LD file.
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

def main():
    parser = argparse.ArgumentParser(description="Recursively list files in a directory using Everything IPC.")
    parser.add_argument("root_path", help="Root directory to scan")
    parser.add_argument("output_path", help="Output JSON file path")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.root_path):
        print(f"Error: Directory not found: {args.root_path}")
        sys.exit(1)

    try:
        data = scan_directory_via_everything(args.root_path)
        save_to_json(data, args.output_path)
        print(f"Scan complete. Found {len(data['files'])} files and {len(data['dirs'])} dirs.")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
