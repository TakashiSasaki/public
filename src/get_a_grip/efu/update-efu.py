import os
import csv
import argparse
from pathlib import Path
from datetime import datetime

def to_filetime(unix_timestamp: float) -> int:
    """
    Converts a Unix timestamp (seconds since 1970-01-01) 
    to Windows FILETIME (100-nanosecond intervals since 1601-01-01).
    """
    # Seconds between 1601-01-01 and 1970-01-01
    EPOCH_DIFF = 11644473600
    return int((unix_timestamp + EPOCH_DIFF) * 10000000)

def get_efu_row(path: Path) -> dict:
    """Returns a dictionary representing an EFU row for the given path."""
    try:
        stat = path.stat()
        is_dir = path.is_dir()
        return {
            "Filename": str(path.absolute()),
            "Size": stat.st_size if not is_dir else "",
            "Date Modified": to_filetime(stat.st_mtime),
            "Date Created": to_filetime(stat.st_ctime),
            "Attributes": 16 if is_dir else 32  # 16 = Directory, 32 = Archive (typical for files)
        }
    except Exception:
        # Skip files that can't be accessed
        return None

def update_efu_file(efu_root: Path, uuid: str):
    """
    Traverses efu_root and records entries into <uuid>.efu.
    Stops at subdirectories that contain their own <uuid>.efu.
    Existing entries in <uuid>.efu are preserved if not found in current scan (monotonic increase).
    """
    efu_filename = f"{uuid}.efu"
    efu_path = efu_root / efu_filename
    last_seen = datetime.now().isoformat()
    
    # Dictionary to store entries keyed by Filename
    # This allows us to merge existing data with new data
    entries = {}

    # Load existing EFU if it exists
    fieldnames = ["Filename", "Size", "Date Modified", "Date Created", "Attributes", "Last Seen"]
    if efu_path.exists():
        try:
            with open(efu_path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if row.get("Filename"):
                        entries[row["Filename"]] = row
        except Exception as e:
            print(f"Warning: Failed to read existing EFU {efu_path}: {e}")

    # Collect current files
    current_scan_rows = []
    
    # We use os.walk but manually handle pruning
    # Actually, a simple recursive function is easier for pruning
    
    def collect(current_dir: Path):
        try:
            for item in current_dir.iterdir():
                # Skip the EFU file we are writing to initially? 
                # Spec says to record found files. Example says A records root/my-uuid.efu.
                
                row = get_efu_row(item)
                if row:
                    row["Last Seen"] = last_seen
                    current_scan_rows.append(row)
                
                if item.is_dir():
                    # Check if this subdirectory has its own <uuid>.efu
                    if (item / efu_filename).exists():
                        # Record the EFU file itself (already done by the loop above)
                        # but STOP traversing deeper
                        continue
                    else:
                        collect(item)
        except PermissionError:
            pass # Skip inaccessible directories

    # Record the root itself?
    root_row = get_efu_row(efu_root)
    if root_row:
        root_row["Last Seen"] = last_seen
        current_scan_rows.append(root_row)
        
    collect(efu_root)
    
    # Merge current scan into entries (overwrite existing)
    for row in current_scan_rows:
        entries[row["Filename"]] = row

    # Convert back to list and sort
    sorted_rows = sorted(entries.values(), key=lambda x: x["Filename"])

    # Write to CSV with BOM
    with open(efu_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)
    
    print(f"Updated {efu_path} with {len(sorted_rows)} entries (scanned: {len(current_scan_rows)}).")

def main():
    parser = argparse.ArgumentParser(description="Update Everything EFU files based on UUID.")
    parser.add_argument("uuid", help="UUID used for the EFU filename (<uuid>.efu)")
    parser.add_argument("start_dir", help="Directory to start searching for EFU files")
    
    args = parser.parse_args()
    start_path = Path(args.start_dir)
    efu_filename = f"{args.uuid}.efu"
    
    if not start_path.exists():
        print(f"Error: Directory {args.start_dir} does not exist.")
        return

    # Phase 1: Discover all EFU roots
    # EFU root is any directory containing <uuid>.efu
    efu_roots = []
    for root, dirs, files in os.walk(start_path):
        if efu_filename in files:
            efu_roots.append(Path(root))
            
    if not efu_roots:
        print(f"No {efu_filename} files found under {args.start_dir}")
        return

    print(f"Found {len(efu_roots)} EFU file(s). Starting update...")
    
    # Phase 2: Update each found EFU file
    for root in efu_roots:
        update_efu_file(root, args.uuid)

if __name__ == "__main__":
    main()
