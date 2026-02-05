import argparse
import sys
from get_a_grip.scanner import run_scanner

def main():
    parser = argparse.ArgumentParser(description="get-a-grip: A tool to scan directory structures.")
    parser.add_argument("directory", help="The directory path to scan.")
    parser.add_argument("-o", "--output", help="The output JSON file path. Defaults to fbd0009d-e91b-414f-9f4f-db3fbd3a16ee.json")

    args = parser.parse_args()

    try:
        output_file = run_scanner(args.directory, args.output)
        print(f"Scan complete. Results saved in {output_file}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
