import sys
import os
import argparse
from typing import Dict, List, Any, Optional


# Add current directory to sys.path to ensure we can import the sibling module
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from everything_ipc import scan_by_ipc
except ImportError:
    try:
        # Fallback for package relative import if run as a module
        from .everything_ipc import scan_by_ipc
    except ImportError:
        from get_a_grip.core.everything_ipc import scan_by_ipc


# --- Search Presets Definition ---
# These queries use "Everything" search syntax.
# Reference: https://www.voidtools.com/support/everything/searching/
PRESETS = {
    "images": "ext:jpg;jpeg;png;gif;bmp;webp;svg",
    "videos": "ext:mp4;mkv;avi;mov;wmv;flv;webm",
    "audio": "ext:mp3;wav;flac;aac;ogg;m4a;wma",
    "documents": "ext:doc;docx;xls;xlsx;ppt;pptx;pdf;txt;md;rtf",
    "archives": "ext:zip;rar;7z;tar;gz;iso",
    "executables": "ext:exe;msi;bat;cmd;ps1;sh",
    "python_code": "ext:py;pyw",
    "recent_files": "dm:today",   # Modified today
    "large_files": "size:>100mb", # Larger than 100MB
    "empty_folders": "folder: empty:",
}

def run_preset_search(preset_name: str, count: int = 10):
    """Executes a search based on the provided preset name."""
    if preset_name not in PRESETS:
        print(f"Error: Preset '{preset_name}' is not defined.")
        print("Use --list to see available presets.")
        return

    query = PRESETS[preset_name]
    print(f"Running Preset: '{preset_name}'")
    print(f"Query: {query}")
    print(f"Max Results: {count}")
    print("-" * 40)

    try:
        results = scan_by_ipc(query, count)
        display_results(results)
    except Exception as e:
        print(f"Search failed: {e}")

def display_results(results: Dict[str, List[Dict[str, Any]]]):
    """Formats and prints the search results."""
    dirs = results.get("dirs", [])
    files = results.get("files", [])

    print(f"Found: {len(dirs)} folders, {len(files)} files.\n")

    if dirs:
        print("--- Folders ---")
        for d in dirs:
            print(f"[DIR]  {d['Filename']}")
    
    if files:
        print("--- Files ---")
        for f in files:
            # Format size to human readable
            size_bytes = f['Size']
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes/1024:.1f} KB"
            else:
                size_str = f"{size_bytes/(1024*1024):.1f} MB"
                
            print(f"[FILE] {f['Filename']} ({size_str})")

def run_search(query: str, count: int = 10):
    """Executes a search for a raw query string."""
    try:
        results = scan_by_ipc(query, count)
        display_results(results)
    except Exception as e:
        print(f"Search failed: {e}")

def interactive_mode(count: int):
    """Starts an interactive loop for testing Everything queries."""
    print("=== Everything IPC Interactive Test Mode ===")
    print(f"Results limit: {count}")
    print("Type 'exit' or 'quit' to stop, or press Ctrl+C.")
    print("-" * 40)
    
    while True:
        try:
            query = input("\nEverything Query > ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit"):
                break
            
            run_search(query, count)
        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

