import argparse
import json
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from get_a_grip.core.env_internal import get_python_env_info

def print_env_info():
    parser = argparse.ArgumentParser(description="Display Python execution environment information.")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    parser.add_argument("--gui", action="store_true", help="Launch GUI viewer")
    args = parser.parse_args()

    if args.gui:
        from get_a_grip.gui.env_viewer import main as gui_main
        gui_main()
        return

    info = get_python_env_info()

    if args.json:
        print(json.dumps(info, indent=4))
    else:
        console = Console()
        
        table = Table(title="Python Environment Information")
        
        table.add_column("Key", style="cyan", no_wrap=True)
        table.add_column("Value", style="magenta")
        
        table.add_row("Python Executable", info["python_executable"])
        table.add_row("Python Version", info["python_version"])
        table.add_row("Platform", info["platform"])
        table.add_row("System", info["system"])
        table.add_row("Release", info["release"])
        table.add_row("Current Working Directory", info["cwd"])
        
        console.print(Panel(table, title="get-a-grip Environment Info", subtitle="Powered by Rich"))

if __name__ == "__main__":
    print_env_info()
