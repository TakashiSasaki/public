import argparse
import json
import sys
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from get_a_grip.core.path_parser import (
    get_system_path,
    get_system_path_from_registry,
    get_user_path_from_registry
)

def main():
    parser = argparse.ArgumentParser(description="Display Windows PATH environment variable.")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    # Get active PATH
    active_paths = get_system_path()

    # Get registry PATHs to determine source
    # These are now List[Path]
    system_registry_paths_list = get_system_path_from_registry()
    user_registry_paths_list = get_user_path_from_registry()

    # Normalize paths for comparison (lower case, resolve symlinks might be too much, just basic normcase)
    # We use a set for faster lookup. 
    # Since we are comparing against what's in PATH (which might be mixed case),
    # converting to string and normcase is the safest common denominator.
    system_registry_paths = set(os.path.normcase(str(p)) for p in system_registry_paths_list)
    user_registry_paths = set(os.path.normcase(str(p)) for p in user_registry_paths_list)

    path_data = []
    
    for p in active_paths:
        # p is a Path object
        norm_p = os.path.normcase(str(p))
        is_system = norm_p in system_registry_paths
        is_user = norm_p in user_registry_paths
        
        source = "Unknown"
        style = "dim"
        
        if is_system and is_user:
            source = "System & User"
            style = "bold yellow"
        elif is_system:
            source = "System"
            style = "blue"
        elif is_user:
            source = "User"
            style = "green"
        else:
            source = "Session/Other"
            style = "white"
            
        path_data.append({
            "path": p,
            "source": source,
            "style": style
        })

    if args.json:
        # Include source in JSON output
        print(json.dumps(path_data, indent=4))
    else:
        console = Console()
        
        table = Table(title="PATH Environment Variable", show_header=True, header_style="bold magenta", expand=True)
        table.add_column("Order", style="cyan", justify="right", width=6)
        table.add_column("Source", width=15)
        table.add_column("Path", style="white", no_wrap=False)

        for idx, item in enumerate(path_data, 1):
            source_text = Text(item["source"], style=item["style"])
            table.add_row(str(idx), source_text, str(item["path"]))
        
        console.print(Panel(table, title="get-a-grip PATH Viewer", subtitle=f"Total entries: {len(active_paths)}"))

if __name__ == "__main__":
    main()
