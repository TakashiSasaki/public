
import sys
import os
from pathlib import Path

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from get_a_grip.core import path_parser
    
    print("--- Testing find_command_in_path ---")
    
    # Try to find python (should exist)
    executable = "python"
    print(f"Searching for: {executable}")
    paths = path_parser.find_command_in_path(executable)
    if paths:
        for p in paths:
            print(f"  Found: {p}")
    else:
        print("  Not found.")

    # Try to find verify_path_parser.py (should exist in current dir if . is in PATH, or not)
    # Actually, current dir is not in PATH usually. 
    # Let's search for something common like cmd or notepad
    
    executable = "cmd"
    print(f"\nSearching for: {executable}")
    paths = path_parser.find_command_in_path(executable)
    if paths:
        for p in paths:
            print(f"  Found: {p}")
    else:
        print("  Not found.")

    executable = "notepad.exe"
    print(f"\nSearching for: {executable}")
    paths = path_parser.find_command_in_path(executable)
    if paths:
        for p in paths:
            print(f"  Found: {p}")
    else:
        print("  Not found.")

except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
