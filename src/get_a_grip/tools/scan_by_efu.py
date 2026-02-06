import csv
import io
import json
import urllib.request
import urllib.parse
from typing import Dict, Any, List

def fetch_efu_from_everything(ip: str, port: int, query: str = "") -> str:
    """
    Fetches EFU (CSV) data from Everything HTTP server.
    """
    params = {
        's': query,
        'csv': 1,
        'encoding': 'UTF-8'
    }
    url = f"http://{ip}:{port}/?{urllib.parse.urlencode(params)}"
    
    with urllib.request.urlopen(url) as response:
        if response.status != 200:
            raise Exception(f"Failed to fetch data from Everything: HTTP {response.status}")
        return response.read().decode('utf-8')

def parse_efu_data(efu_content: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Parses EFU content (CSV) into a dictionary with 'files' and 'dirs' lists.
    """
    files = []
    dirs = []
    # Use io.StringIO to treat the string as a file for csv.DictReader
    f = io.StringIO(efu_content)
    reader = csv.DictReader(f)
    
    for row in reader:
        # Expected keys: Filename,Size,Date Modified,Date Created,Attributes
        attributes = int(row.get("Attributes", 0)) if row.get("Attributes") else 0
        
        file_info = {
            "Filename": row.get("Filename"),
            "Size": int(row.get("Size", 0)) if row.get("Size") else 0,
            "Date Modified": row.get("Date Modified"),
            "Date Created": row.get("Date Created"),
            "Attributes": attributes
        }
        
        # 0x10 is FILE_ATTRIBUTE_DIRECTORY
        if attributes & 0x10:
            dirs.append(file_info)
        else:
            files.append(file_info)
    
    return {"files": files, "dirs": dirs}

def scan_by_efu(ip: str = "127.160.164.78", port: int = 8000, query: str = "") -> Dict[str, Any]:
    """
    Scans by fetching EFU data from Everything and returns get-a-grip data structure.
    """
    efu_content = fetch_efu_from_everything(ip, port, query)
    return parse_efu_data(efu_content)
