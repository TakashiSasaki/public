import argparse
import sys
import os
from get_a_grip.tools.scanner import scan_directory, save_to_json
from get_a_grip.tools.efu_converter import json_to_efu, efu_to_json
from get_a_grip.tools.whoami import print_whoami
from get_a_grip.tools.probe import print_probe_data, save_probe_data
from get_a_grip.tools.scan_by_efu import scan_by_efu, fetch_raw_from_everything

def main():
    parser = argparse.ArgumentParser(description="get-a-grip: A collection of tools.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scanner subcommand
    scanner_parser = subparsers.add_parser("scanner", help="Scan directory structures")
    scanner_parser.add_argument("directory", help="The directory path to scan.")
    scanner_parser.add_argument("-o", "--output", help="The output JSON file path. Defaults to fbd0009d-e91b-414f-9f4f-db3fbd3a16ee.json")
    scanner_parser.add_argument("-f", "--force", action="store_true", help="Overwrite the output file if it exists without asking.")

    # jsonld2efu subcommand
    j2e_parser = subparsers.add_parser("jsonld2efu", help="Convert JSON-LD to EFU")
    j2e_parser.add_argument("input", help="Input JSON-LD file")
    j2e_parser.add_argument("output", help="Output EFU file")

    # efu2jsonld subcommand
    e2j_parser = subparsers.add_parser("efu2jsonld", help="Convert EFU to JSON-LD")
    e2j_parser.add_argument("input", help="Input EFU file")
    e2j_parser.add_argument("output", help="Output JSON-LD file")

    # whoami subcommand
    subparsers.add_parser("whoami", help="Print effective user")

    # probe subcommand
    probe_parser = subparsers.add_parser("probe", help="Collect environmental data")
    probe_parser.add_argument("-o", "--output", help="The output JSON file path.")
    
    # scan-by-efu subcommand
    sbe_parser = subparsers.add_parser("scan-by-efu", help="Scan using Everything HTTP server")
    sbe_parser.add_argument("directory", nargs="?", default=".", help="The directory path to scan (default: current directory)")
    sbe_parser.add_argument("--ip", default="127.160.164.78", help="Everything HTTP server IP")
    sbe_parser.add_argument("--port", type=int, default=8000, help="Everything HTTP server port")
    sbe_parser.add_argument("-q", "--query", default="", help="Search query")
    sbe_parser.add_argument("-o", "--output", help="The output JSON file path.")
    sbe_parser.add_argument("-f", "--force", action="store_true", help="Overwrite output if exists")
    sbe_parser.add_argument("--raw", action="store_true", help="Show raw response from Everything server")
    sbe_parser.add_argument("-c", "--count", type=int, default=10, help="Maximum number of results to fetch (default: 10)")

    args = parser.parse_args()

    if args.command == "scanner":
        try:
            output_file = args.output if args.output else "fbd0009d-e91b-414f-9f4f-db3fbd3a16ee.json"
            
            if not args.force and os.path.exists(output_file):
                response = input(f"File '{output_file}' already exists. Overwrite? [y/N]: ")
                if response.lower() != 'y':
                    print("Aborted.")
                    return

            print(f"Scanning directory: {args.directory}...")
            scan_data = scan_directory(args.directory)
            
            num_files = len(scan_data.get("files", []))
            num_dirs = len(scan_data.get("dirs", []))
            print(f"Found {num_files} files and {num_dirs} directories. Saving to {output_file} in detailed format...")
            
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
        try:
            print_whoami()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "probe":
        try:
            if args.output:
                save_probe_data(args.output)
                print(f"Environmental data saved to {args.output}")
            else:
                print_probe_data()
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "scan-by-efu":
        try:
            # Resolve directory and combine it into Everything search query
            target_dir = os.path.abspath(args.directory)
            combined_query = f'"{target_dir}"'
            if args.query:
                combined_query += f" {args.query}"

            if args.raw:
                print(f"Fetching {args.count} raw results from {args.ip}:{args.port} (Query: '{combined_query}')...")
                raw_response = fetch_raw_from_everything(args.ip, args.port, combined_query, count=args.count)
                print("-" * 40)
                print(raw_response)
                print("-" * 40)
                return

            output_file = args.output if args.output else "everything-scan.json"
            
            if not args.force and os.path.exists(output_file):
                response = input(f"File '{output_file}' already exists. Overwrite? [y/N]: ")
                if response.lower() != 'y':
                    print("Aborted.")
                    return

            print(f"Scanning via Everything HTTP: {args.ip}:{args.port} (Path: '{target_dir}', Query: '{args.query}', Count: {args.count})...")
            scan_data = scan_by_efu(args.ip, args.port, combined_query, count=args.count)
            
            num_files = len(scan_data.get("files", []))
            num_dirs = len(scan_data.get("dirs", []))
            print(f"Found {num_files} files and {num_dirs} directories. Saving to {output_file}...")
            
            save_to_json(scan_data, output_file)
            print(f"Scan complete. Results saved in {output_file}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
