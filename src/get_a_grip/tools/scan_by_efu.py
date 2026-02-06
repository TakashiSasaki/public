import csv
import io
import json
import os
import urllib.request
import urllib.parse
from typing import Dict, Any, List

def fetch_raw_from_everything(ip: str, port: int, query: str = "", format: str = "json") -> str:
    """
    Fetches the raw response from Everything HTTP server as a string.
    """
    params = {
        's': query,
        'encoding': 'UTF-8'
    }
    
    if format == "json":
        params.update({
            'j': 1,
            'path_column': 1,
            'size_column': 1,
            'date_modified_column': 1,
            'date_created_column': 1,
            'attributes_column': 1,
        })
    elif format == "csv":
        params['csv'] = 1

    url = f"http://{ip}:{port}/?{urllib.parse.urlencode(params)}"
    
    try:
        with urllib.request.urlopen(url) as response:
            if response.status != 200:
                raise Exception(f"Failed to fetch data from Everything: HTTP {response.status}")
            return response.read().decode('utf-8')
    except Exception as e:
        raise Exception(f"Connection error to Everything server at {ip}:{port}: {e}")

def fetch_json_from_everything(ip: str, port: int, query: str = "") -> Dict[str, Any]:
    """
    Fetches JSON data from Everything HTTP server.
    """
    raw_data = fetch_raw_from_everything(ip, port, query, format="json")
    return json.loads(raw_data)

def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely converts a value to an integer, returning default if conversion fails or value is empty.
    """
    if value is None or value == "":
        return default
    try:
        return int(value)
    except (ValueError, TypeError):
        return default

def scan_by_efu(ip: str = "127.160.164.78", port: int = 8000, query: str = "") -> Dict[str, List[Dict[str, Any]]]:
    """
    Scans by fetching JSON data from Everything and returns get-a-grip data structure.
    """
    data = fetch_json_from_everything(ip, port, query)
    
    files = []
    dirs = []
    
    results = data.get("results", [])
    
    for item in results:
        name = item.get("name", "")
        path = item.get("path", "")
        filename = os.path.join(path, name) if path else name
        
        info = {
            "Filename": filename,
            "Size": safe_int(item.get("size")),
            "Date Modified": str(item.get("date_modified", "0")),
            "Date Created": str(item.get("date_created", "0")),
            "Attributes": safe_int(item.get("attributes"))
        }
        
        if item.get("type") == "folder":
            dirs.append(info)
        else:
            files.append(info)
            
    return {"files": files, "dirs": dirs}
