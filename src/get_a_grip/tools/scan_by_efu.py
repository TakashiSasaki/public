import csv
import io
import json
import os
import urllib.request
import urllib.parse
from typing import Dict, Any, List

def fetch_json_from_everything(ip: str, port: int, query: str = "") -> Dict[str, Any]:
    """
    Fetches JSON data from Everything HTTP server using query parameters.
    """
    params = {
        's': query,
        'j': 1,               # JSON output
        'path_column': 1,     # Include full path
        'size_column': 1,     # Include size
        'date_modified_column': 1,
        'date_created_column': 1,
        'attributes_column': 1,
        'encoding': 'UTF-8'
    }
    url = f"http://{ip}:{port}/?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch data from Everything: HTTP {response.status}")
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        raise Exception(f"Connection error to Everything server at {ip}:{port}: {e}")

def scan_by_efu(ip: str = "127.160.164.78", port: int = 8000, query: str = "") -> Dict[str, List[Dict[str, Any]]]:
    """
    Scans by fetching JSON data from Everything and returns get-a-grip data structure.
    """
    data = fetch_json_from_everything(ip, port, query)
    
    files = []
    dirs = []
    
    # Everything returns results in the 'results' key
    results = data.get("results", [])
    
    for item in results:
        # Construct the filename: Everything usually returns 'name' and 'path'
        name = item.get("name", "")
        path = item.get("path", "")
        # Combine path and name if they are separate
        filename = os.path.join(path, name) if path else name
        
        # Everything HTTP API returns dates in various formats or as strings.
        # We'll keep them as they are or convert if needed to match scanner.py (FILETIME)
        # Note: If the user needs exact FILETIME matching, we might need further conversion.
        
        info = {
            "Filename": filename,
            "Size": int(item.get("size", 0)) if item.get("size") is not None else 0,
            "Date Modified": str(item.get("date_modified", "0")),
            "Date Created": str(item.get("date_created", "0")),
            "Attributes": int(item.get("attributes", 0)) if item.get("attributes") is not None else 0
        }
        
        if item.get("type") == "folder":
            dirs.append(info)
        else:
            files.append(info)
            
    return {"files": files, "dirs": dirs}
