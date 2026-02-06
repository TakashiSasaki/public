import os
import sys
import time
import argparse

def scan_dirs_benchmark(root_path):
    root_abs = os.path.abspath(root_path)
    if not os.path.exists(root_abs):
        print(f"Error: Directory not found: {root_abs}")
        sys.exit(1)

    print(f"Benchmarking directory-only scan on: {root_abs}")
    print("Press Ctrl+C to abort.")
    print("-" * 40)

    start_time = time.time()
    dir_count = 0
    
    # We'll use a stack for iterative traversal (Depth First Search)
    stack = [root_abs]
    
    # Progress tracking
    last_print_time = start_time
    print_interval = 0.1  # Update display every 0.1 seconds

    try:
        while stack:
            # Pop a directory from the stack
            current_path = stack.pop()
            dir_count += 1

            # Progress display
            current_time = time.time()
            if current_time - last_print_time > print_interval:
                elapsed = current_time - start_time
                rate = dir_count / elapsed if elapsed > 0 else 0
                sys.stdout.write(f"\rDirs found: {dir_count:,} | Time: {elapsed:.1f}s | Rate: {rate:,.0f} dirs/s")
                sys.stdout.flush()
                last_print_time = current_time

            # Scan the directory
            try:
                with os.scandir(current_path) as it:
                    for entry in it:
                        # Only interested in directories
                        if entry.is_dir():
                            stack.append(entry.path)
                        # We specifically ignore files and do NOT call entry.stat()
                        # to measure pure structure traversald speed.
            except (OSError, PermissionError):
                # Ignore permission errors for consistency with typical benchmarks
                pass

    except KeyboardInterrupt:
        print("\n\nScan aborted by user.")

    end_time = time.time()
    duration = end_time - start_time
    
    # Final output
    sys.stdout.write(f"\rDirs found: {dir_count:,} | Time: {duration:.2f}s | Rate: {dir_count / duration if duration else 0:,.0f} dirs/s     \n")
    print("-" * 40)
    print("Done.")

def main():
    parser = argparse.ArgumentParser(description="Benchmark pure directory scanning speed using os.scandir.")
    parser.add_argument("directory", nargs="?", default=".", help="The root directory to start scanning from (default: current directory)")
    
    args = parser.parse_args()
    
    scan_dirs_benchmark(args.directory)

if __name__ == "__main__":
    main()
