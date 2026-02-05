import argparse
import sys
from get_a_grip.tools.scanner import scan_directory, save_to_json

def main():
    parser = argparse.ArgumentParser(description="get-a-grip: A collection of tools.")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Scanner subcommand
    scanner_parser = subparsers.add_parser("scanner", help="Scan directory structures")
    scanner_parser.add_argument("directory", help="The directory path to scan.")
    scanner_parser.add_argument("-o", "--output", help="The output JSON file path. Defaults to fbd0009d-e91b-414f-9f4f-db3fbd3a16ee.json")

    args = parser.parse_args()

    if args.command == "scanner":
        try:
            print(f"Scanning directory: {args.directory}...")
            file_data = scan_directory(args.directory)
            
            output_file = args.output if args.output else "fbd0009d-e91b-414f-9f4f-db3fbd3a16ee.json"
            print(f"Found {len(file_data)} files. Saving to {output_file} in detailed format...")
            
            save_to_json(file_data, output_file)
            print(f"Scan complete. Results saved in {output_file}")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
