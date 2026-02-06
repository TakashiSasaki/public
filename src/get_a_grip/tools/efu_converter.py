import csv
import json
import os
from typing import List, Dict, Any

def json_to_efu(input_path: str, output_path: str) -> None:
    """
    Converts a JSON-LD file (get-a-grip format) to an Everything File List (EFU) file.
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    files = data.get("files", [])
    
    # EFU Header
    header = ["Filename", "Size", "Date Modified", "Date Created", "Attributes"]

    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        # Use simple quoting for header so it looks like standard EFU (no quotes usually)
        writer_header = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer_header.writerow(header)

        # Use QUOTE_NONNUMERIC for content so filenames are quoted but numbers are not
        writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)

        for item in files:
            # Extract fields. JSON keys match EFU headers
            filename = item.get("Filename", "")
            size = int(item.get("Size", 0))
            # JSON-LD uses strings for large integers usually, but we convert to int for EFU writing validation
            date_modified = int(item.get("Date Modified", "0"))
            date_created = int(item.get("Date Created", "0"))
            attributes = int(item.get("Attributes", 0))

            row = [filename, size, date_modified, date_created, attributes]
            
            writer.writerow(row)

def efu_to_json(input_path: str, output_path: str) -> None:
    """
    Converts an Everything File List (EFU) file to a JSON-LD file (get-a-grip format).
    """
    files_list = []
    
    with open(input_path, 'r', encoding='utf-8', newline='') as f:
        # EFU is a CSV.
        reader = csv.DictReader(f)
        
        # Verify header? DictReader uses first row.
        # Expected keys: Filename,Size,Date Modified,Date Created,Attributes
        
        for row in reader:
            # We need to construct the dict matching schema
            # CSV values are strings. We should convert to appropriate types for JSON.
            # Schema: Size (int), Attributes (int), Dates (str or int? scanner uses str for dates, int for Size/Attr)
            
            file_info = {
                "Filename": row.get("Filename"),
                "Size": int(row.get("Size", 0)),
                "Date Modified": row.get("Date Modified"),
                "Date Created": row.get("Date Created"),
                "Attributes": int(row.get("Attributes", 0))
            }
            files_list.append(file_info)

    # Wrap in JSON-LD structure
    output_data = {
        "@context": [
            "https://purl.org/gag/schema/filelist.jsonld"
        ],
        "@type": "ItemList",
        "files": files_list
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
