import json
from datetime import datetime
from pathlib import Path
from collections import Counter
from typing import Dict, Tuple
from get_a_grip.tools.whoami import get_effective_user, get_user_principal_name
from get_a_grip.tools.filelist.types import FileList, FileItem

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

def normalize_filelist(entries: list[FileItem]) -> Tuple[Dict[str, FileItem], Counter[str]]:
    """
    Convert list of file/dir dicts to a dictionary keyed by absolute filename.
    Also returns a counter for duplicate path detection.
    """
    normalized: Dict[str, FileItem] = {}
    counts: Counter[str] = Counter()
    for entry in entries:
        p = Path(entry['Filename']).resolve()
        key = str(p)
        counts[key] += 1
        normalized[key] = entry
    return normalized, counts

def compare_filelists(result1: FileList, result2: FileList, name1: str, name2: str) -> None:
    """
    Compare two scan results for equality. Raises RuntimeError if they mismatch.
    """
    for section in ["files", "dirs"]:
        norm1, counts1 = normalize_filelist(result1.get(section, []))
        norm2, counts2 = normalize_filelist(result2.get(section, []))

        dup1 = [path for path, count in counts1.items() if count > 1]
        dup2 = [path for path, count in counts2.items() if count > 1]
        if dup1 or dup2:
            msg = f"Duplicate entries detected in {section} list between {name1} and {name2}.\n"
            if dup1:
                msg += f"Duplicates in {name1}: {dup1[:5]}\n"
            if dup2:
                msg += f"Duplicates in {name2}: {dup2[:5]}\n"
            raise RuntimeError(msg)
        
        keys1 = set(norm1.keys())
        keys2 = set(norm2.keys())
        
        if keys1 != keys2:
            diff1 = keys1 - keys2
            diff2 = keys2 - keys1
            msg = f"{section.capitalize()} list mismatch between {name1} and {name2}.\n"
            if diff1: msg += f"Only in {name1}: {list(diff1)[:5]}\n"
            if diff2: msg += f"Only in {name2}: {list(diff2)[:5]}\n"
            raise RuntimeError(msg)
        
        # Metadata check
        for key in keys1:
            item1 = norm1[key]
            item2 = norm2[key]
            for field in ["Size", "Date Modified", "Date Created", "Attributes"]:
                # Directory size can be inconsistent between different stat calls on Windows
                if section == "dirs" and field == "Size":
                    continue
                    
                if item1.get(field) != item2.get(field):
                    raise RuntimeError(
                        f"Metadata mismatch for {key} ({field}): "
                        f"{name1}={item1.get(field)}, {name2}={item2.get(field)}"
                    )
