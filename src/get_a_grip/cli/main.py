
import argparse
import sys
import os
from pathlib import Path

# Core tool imports
from get_a_grip.core.filelist import scan, save_to_json
from get_a_grip.core.filelist.http import scan as scan_http, fetch_raw_from_everything
from get_a_grip.core.everything_ipc import scan_by_ipc
from get_a_grip.core.efu_converter import json_to_efu, efu_to_json
from get_a_grip.core.whoami import print_whoami
from get_a_grip.core.probe import print_probe_data, save_probe_data

# Sub-tool main imports
# These tools must be importable. 
# Depending on how they are written, importing might trigger code if not guarded.
# We verified guards in previous steps.

try:
    from get_a_grip.cli.efu.update_efu import main as update_efu_main
except ImportError:
    update_efu_main = None

try:
    from get_a_grip.cli.efu.merge_efu import main as merge_efu_main
except ImportError:
    merge_efu_main = None

try:
    from get_a_grip.gui.efu_gui import main as efu_gui_main
except ImportError:
    efu_gui_main = None

try:
    from get_a_grip.gui.env_viewer import main as env_viewer_main
except ImportError:
    env_viewer_main = None

try:
    from get_a_grip.cli.path_viewer import main as path_viewer_main
except ImportError:
    path_viewer_main = None

# Git tools - checking locations
# Based on pyproject.toml: get_a_grip.tools.git.find_github_dir
try:
    from get_a_grip.tools.git.find_github_dir import main as find_github_dir_main
except ImportError:
    find_github_dir_main = None

try:
    from get_a_grip.tools.git.find_git_worktree import main as find_git_worktree_main
except ImportError:
    find_git_worktree_main = None

try:
    from get_a_grip.tools.git.find_git_repo import main as find_git_repo_main
except ImportError:
    find_git_repo_main = None

try:
    from get_a_grip.tools.inspect_platform_dirs import main as inspect_platform_dirs_main
except ImportError:
    inspect_platform_dirs_main = None

try:
    from get_a_grip.tui import main as tui_main
except ImportError:
    tui_main = None

try:
    from get_a_grip.gui.launcher import main as launcher_main
except ImportError:
    launcher_main = None

try:
    from get_a_grip.gui.shortcut_manager import main as shortcut_manager_main
except ImportError:
    shortcut_manager_main = None


def main():
    parser = argparse.ArgumentParser(description="get-a-grip: A collection of tools.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- Launcher ---
    subparsers.add_parser("launch", help="Launch GUI Launcher")

    # --- EFU Tools ---
    efu_parser = subparsers.add_parser("efu", help="Everything File Utility tools")
    efu_subparsers = efu_parser.add_subparsers(dest="efu_command", help="EFU subcommands")
    
    efu_subparsers.add_parser("update", help="Update EFU files", add_help=False)
    efu_subparsers.add_parser("merge", help="Merge EFU files", add_help=False)
    efu_subparsers.add_parser("gui", help="Launch EFU GUI")

    # --- Env/Path Tools ---
    subparsers.add_parser("env", help="Environment Viewer GUI")
    subparsers.add_parser("path", help="Path Viewer CLI")

    # --- Shortcut Management ---
    shortcut_parser = subparsers.add_parser("shortcut", help="Manage Start Menu shortcut")
    shortcut_parser.add_argument("action", choices=["install", "uninstall"], help="Action to perform")

    # --- Git/Tools ---
    tools_parser = subparsers.add_parser("tools", help="Miscellaneous tools")
    tools_subparsers = tools_parser.add_subparsers(dest="tools_command")
    
    tools_subparsers.add_parser("find-github-dir", help="Find GitHub directory")
    tools_subparsers.add_parser("find-git-worktree", help="Find Git worktree")
    tools_subparsers.add_parser("find-git-repo", help="Find Git repo")
    tools_subparsers.add_parser("inspect-dirs", help="Inspect platform dirs")
    
    # --- Legacy Commands (retained for backward compatibility logic inside gag) ---
    subparsers.add_parser("tui", help="Launch TUI")
    
    # filelist and others need full argument definition if we want to parse them here.
    # To avoid duplication, we can treat them like 'efu update' and pass raw args if we want,
    # OR we can keep the full definition here. Since they were in the original __init__.py,
    # let's keep the definitions to maintain the 'filelist' command behavior exactly as before within 'gag'.

    # filelist
    fl_parser = subparsers.add_parser("filelist", help="Scan directory structures")
    fl_parser.add_argument("directory", help="The directory path to scan.")
    fl_parser.add_argument("-o", "--output", help="The output JSON file path.")
    fl_parser.add_argument("--uuid", default="2e985654-ccc3-4141-979b-58d014133d56", help="The UUID for the output file")
    fl_parser.add_argument("-f", "--force", action="store_true", help="Overwrite the output file if it exists without asking.")
    
    # jsonld2efu
    j2e_parser = subparsers.add_parser("jsonld2efu", help="Convert JSON-LD to EFU")
    j2e_parser.add_argument("input", help="Input JSON-LD file")
    j2e_parser.add_argument("output", help="Output EFU file")

    # efu2jsonld
    e2j_parser = subparsers.add_parser("efu2jsonld", help="Convert EFU to JSON-LD")
    e2j_parser.add_argument("input", help="Input EFU file")
    e2j_parser.add_argument("output", help="Output JSON-LD file")

    # whoami
    subparsers.add_parser("whoami", help="Print effective user")

    # probe
    probe_parser = subparsers.add_parser("probe", help="Collect environmental data")
    probe_parser.add_argument("-o", "--output", help="The output JSON file path.")

    # filelist-http
    flh_parser = subparsers.add_parser("filelist-http", help="Scan using Everything HTTP server")
    flh_parser.add_argument("directory", nargs="?", default=".", help="The directory path to scan (default: current directory)")
    flh_parser.add_argument("--ip", default="127.160.164.78", help="Everything HTTP server IP")
    flh_parser.add_argument("--port", type=int, default=8000, help="Everything HTTP server port")
    flh_parser.add_argument("-q", "--query", default="", help="Search query")
    flh_parser.add_argument("-o", "--output", help="The output JSON file path.")
    flh_parser.add_argument("--uuid", default="2e985654-ccc3-4141-979b-58d014133d56", help="The UUID for the output file")
    flh_parser.add_argument("-f", "--force", action="store_true", help="Overwrite output if exists")
    flh_parser.add_argument("--raw", action="store_true", help="Show raw response from Everything server")
    flh_parser.add_argument("-c", "--count", type=int, default=0, help="Maximum number of results to fetch")

    # filelist-ipc
    fli_parser = subparsers.add_parser("filelist-ipc", help="Scan using Everything IPC (DLL)")
    fli_parser.add_argument("directory", nargs="?", default=".", help="The directory path to scan (default: current directory)")
    fli_parser.add_argument("-q", "--query", default="", help="Search query")
    fli_parser.add_argument("-o", "--output", help="The output JSON file path.")
    fli_parser.add_argument("--uuid", default="2e985654-ccc3-4141-979b-58d014133d56", help="The UUID for the output file")
    fli_parser.add_argument("-f", "--force", action="store_true", help="Overwrite output if exists")
    fli_parser.add_argument("-c", "--count", type=int, default=0, help="Maximum number of results to fetch")

    # Parse args. 
    # For commands that we want to pass-through (efu update/merge, tools), we typically peek sys.argv using parse_known_args
    # but that might consume flags meant for the subcommand if they match top-level flags (none here).
    
    # Strategy: Use parse_known_args.
    args, remaining_argv = parser.parse_known_args()

    if args.command == "efu":
        if not hasattr(args, 'efu_command') or not args.efu_command:
            parser.parse_args(['efu', '--help']) # show help
            return

        if args.efu_command == "update":
            # Pass remaining args to update_efu
            if update_efu_main:
                # We need to reconstruct argv for the called script
                # It expects [script_name, --arg, val...]
                sys.argv = ["gag-efu-update"] + remaining_argv
                update_efu_main()
            else:
                print("Error: update-efu not found.")
                
        elif args.efu_command == "merge":
            if merge_efu_main:
                sys.argv = ["gag-efu-merge"] + remaining_argv
                merge_efu_main()
            else:
                print("Error: merge-efu not found.")
                
        elif args.efu_command == "gui":
            if efu_gui_main:
                efu_gui_main()
            else:
                print("Error: efu-gui not found.")

    elif args.command == "env":
        if env_viewer_main:
            env_viewer_main()
        else:
             print("Error: env-viewer not found.")

    elif args.command == "path":
        if path_viewer_main:
            # path-viewer might use argparse, pass args
            sys.argv = ["gag-path"] + remaining_argv
            path_viewer_main()
        else:
             print("Error: path-viewer not found.")

    elif args.command == "tools":
        if not hasattr(args, 'tools_command') or not args.tools_command:
            parser.parse_args(['tools', '--help'])
            return
            
        tool = args.tools_command
        # Tools might use argparse.
        # But wait, we defined them as subparsers above without add_help=False?
        # If we defined them as subparsers, parse_known_args might have already consumed prompt-like args?
        # Actually our tool definitions above have no arguments defined, so any arguments passed 
        # would end up in remaining_argv IF they look like flags. 
        # But if they look like positionals (e.g. `gag tools find-github-dir .`), `.` would be consumed/error if not defined?
        # Actually, since we defined no args for them, any positional would be an error during parse_known_args?
        # parse_known_args only ignores UNKNOWN flags. Extra positionals cause error if not defined.
        
        # FIX: We should probably use `add_help=False` and disable intermixed args for tools too if they accept args.
        # Checking existing tools usage:
        # find-github-dir [path]
        # find-git-worktree [path]
        # find-git-repo [path]
        # inspect-dirs (no args?)
        
        # So we should treat them like efu update/merge.
        
        # To fix this cleanly without redefining their args:
        # We need to execute them manually if we want to pass control.
        # But we already parsed `tools` and `tools_command`.
        
        # If we re-run logic:
        # If we want to use argparse for dispatch only, we can use `nargs=argparse.REMAINDER`?
        pass # dispatched below
        
        sys.argv = [f"gag-tools-{tool}"] + remaining_argv
        if tool == "find-github-dir" and find_github_dir_main: find_github_dir_main()
        elif tool == "find-git-worktree" and find_git_worktree_main: find_git_worktree_main()
        elif tool == "find-git-repo" and find_git_repo_main: find_git_repo_main()
        elif tool == "inspect-dirs" and inspect_platform_dirs_main: inspect_platform_dirs_main()
        else:
            print(f"Tool {tool} not found or implementation missing.")

    elif args.command == "tui":
        if tui_main: tui_main()
        else: print("Textual not installed.")

    elif args.command == "shortcut":
        if shortcut_manager_main:
            # Reconstruct args for the shortcut manager or just call functions?
            # shortcut_manager.main uses argparse on sys.argv or we can pass args?
            # It uses parser.parse_args().
            # So we set sys.argv.
            sys.argv = ["gag-shortcut", args.action]
            shortcut_manager_main()
        else:
            print("Error: shortcut manager not found (pywin32 might be missing).")

    # --- Core Commands (Fully implemented here) ---
    elif args.command == "filelist":
        try:
            output_file = args.output if args.output else f"{args.uuid}.json"
            if not args.force and os.path.exists(output_file):
                response = input(f"File '{output_file}' already exists. Overwrite? [y/N]: ")
                if response.lower() != 'y':
                    print("Aborted.")
                    return
            print(f"Scanning directory: {args.directory}...")
            scan_data = scan(args.directory)
            num_files = len(scan_data.get("files", []))
            num_dirs = len(scan_data.get("dirs", []))
            print(f"Found {num_files} files and {num_dirs} directories. Saving to {output_file}...")
            save_to_json(scan_data, output_file)
            print(f"Scan complete. Results saved in {output_file}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "jsonld2efu":
        try:
            json_to_efu(args.input, args.output)
            print(f"Converted {args.input} to {args.output}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "efu2jsonld":
        try:
            efu_to_json(args.input, args.output)
            print(f"Converted {args.input} to {args.output}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "whoami":
        print_whoami()

    elif args.command == "probe":
        if args.output:
            save_probe_data(args.output)
            print(f"Environmental data saved to {args.output}")
        else:
            print_probe_data()

    elif args.command == "filelist-http":
         try:
            target_dir = os.path.abspath(args.directory)
            combined_query = f'"{target_dir}"'
            if args.query: combined_query += f" {args.query}"

            if args.raw:
                print(f"Fetching raw results...")
                raw_response = fetch_raw_from_everything(args.ip, args.port, combined_query, count=args.count)
                print(raw_response)
                return

            output_file = args.output if args.output else f"{args.uuid}.json"
            if not args.force and os.path.exists(output_file):
                 if input(f"File '{output_file}' exists. Overwrite? [y/N]: ").lower() != 'y': return

            print(f"Scanning via Everything HTTP...")
            scan_data = scan_http(target=combined_query, ip=args.ip, port=args.port, count=args.count)
            save_to_json(scan_data, output_file)
            print(f"Scan complete. Saved to {output_file}")
         except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "filelist-ipc":
        try:
            target_dir = os.path.abspath(args.directory)
            combined_query = f'"{target_dir}"'
            if args.query: combined_query += f" {args.query}"

            output_file = args.output if args.output else f"{args.uuid}.json"
            if not args.force and os.path.exists(output_file):
                 if input(f"File '{output_file}' exists. Overwrite? [y/N]: ").lower() != 'y': return

            print(f"Scanning via Everything IPC...")
            scan_data = scan_by_ipc(combined_query, count=args.count)
            save_to_json(scan_data, output_file)
            print(f"Scan complete. Saved to {output_file}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "launch":
        if launcher_main:
            launcher_main()
        else:
            print("Error: launcher not found (tk/tcl might be missing).")
    
    else:
        # Fallback if command is not matched but no error raised?
        if args.command is None:
            parser.print_help()

if __name__ == "__main__":
    main()
