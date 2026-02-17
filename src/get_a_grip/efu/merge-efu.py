
import os
import csv
import argparse
from pathlib import Path
from datetime import datetime

def parse_last_seen(iso_str: str) -> datetime:
    """Parses ISO8601 string to datetime. Returns min datetime if invalid/empty."""
    if not iso_str:
        return datetime.min
    try:
        return datetime.fromisoformat(iso_str)
    except ValueError:
        return datetime.min

def merge_efu_files(start_dir: Path, uuid: str, output_file: Path):
    target_filename = f"{uuid}.efu"
    merged_entries = {}
    
    # 1. Discover and Read
    efu_files = []
    for root, dirs, files in os.walk(start_dir):
        if target_filename in files:
            efu_files.append(Path(root) / target_filename)

    print(f"Found {len(efu_files)} EFU files.")

    for efu_path in efu_files:
        try:
            # Skip if this is the output file (to avoid self-inclusion if output is in start_dir)
            if efu_path.resolve() == output_file.resolve():
                continue

            with open(efu_path, "r", encoding="utf-8-sig", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    filename = row.get("Filename")
                    if not filename:
                        continue
                    
                    if filename in merged_entries:
                        # Conflict resolution: Latest Last Seen wins
                        existing_row = merged_entries[filename]
                        old_time = parse_last_seen(existing_row.get("Last Seen"))
                        new_time = parse_last_seen(row.get("Last Seen"))
                        
                        if new_time > old_time:
                            merged_entries[filename] = row
                    else:
                        merged_entries[filename] = row
        except Exception as e:
            print(f"Warning: Failed to read {efu_path}: {e}")

    # 2. Write Output
    fieldnames = ["Filename", "Size", "Date Modified", "Date Created", "Attributes", "Last Seen"]
    
    # Sort by Filename
    sorted_rows = sorted(merged_entries.values(), key=lambda x: x["Filename"])
    
    # Ensure directory exists
    if output_file.parent:
        output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted_rows)

    print(f"Merged {len(sorted_rows)} entries into {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Merge multiple EFU files into one.")
    parser.add_argument("--uuid", required=True, help="UUID used to identify EFU files (<uuid>.efu)")
    parser.add_argument("--start-dir", required=True, help="Directory to start searching for EFU files")
    parser.add_argument("--output", required=True, help="Path to the output merged EFU file")
    
    args = parser.parse_args()
    
    start_dir = Path(args.start_dir)
    output_file = Path(args.output)
    
    if not start_dir.exists():
        print(f"Error: Start directory {start_dir} does not exist.")
        return

    merge_efu_files(start_dir, args.uuid, output_file)

if __name__ == "__main__":
    main()
