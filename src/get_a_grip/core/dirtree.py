"""
Directory tree scanner that outputs a recursive JSON structure.
Output conforms to schema/dirtree.json where:
- Object keys are path segments (directory/file names)
- Object values are either null (leaf/file) or nested objects (directories)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from typing import Dict, Optional, Union
from get_a_grip.core.whoami import get_effective_user, get_user_principal_name

# Type alias for the tree structure
TreeNode = Union[None, Dict[str, "TreeNode"]]


class ProgressTracker:
    """Tracks and displays scan progress."""
    
    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.dir_count = 0
        self.start_time = time.time()
        self.last_print_time = self.start_time
        self.print_interval = 0.1  # Update display every 0.1 seconds
    
    def increment(self) -> None:
        """Increment directory count and update display if needed."""
        self.dir_count += 1
        
        if not self.enabled:
            return
        
        current_time = time.time()
        if current_time - self.last_print_time > self.print_interval:
            elapsed = current_time - self.start_time
            rate = self.dir_count / elapsed if elapsed > 0 else 0
            sys.stdout.write(f"\rDirs found: {self.dir_count:,} | Time: {elapsed:.1f}s | Rate: {rate:,.0f} dirs/s")
            sys.stdout.flush()
            self.last_print_time = current_time
    
    def finish(self) -> None:
        """Print final statistics."""
        if not self.enabled:
            return
        
        duration = time.time() - self.start_time
        rate = self.dir_count / duration if duration > 0 else 0
        sys.stdout.write(f"\rDirs found: {self.dir_count:,} | Time: {duration:.2f}s | Rate: {rate:,.0f} dirs/s     \n")
        sys.stdout.flush()


# Global progress tracker (set during scan)
_progress: Optional[ProgressTracker] = None


def scan_directory_tree(root_path: str, progress: bool = False) -> Dict[str, TreeNode]:
    """
    Recursively scans a directory and builds a tree structure.
    
    Args:
        root_path: The root directory path to scan.
        progress: Whether to display progress during scan.
        
    Returns:
        A dictionary where keys are the root directory name(s) and values
        are nested tree structures conforming to dirtree.json schema.
    """
    global _progress
    _progress = ProgressTracker(enabled=progress)
    
    root_abs = os.path.abspath(root_path)
    root_name = os.path.basename(root_abs)
    
    # Handle drive roots on Windows (e.g., "C:\\")
    if not root_name:
        # This is a drive root like "C:\\"
        root_name = root_abs.rstrip(os.sep)
    
    tree = _build_tree(root_abs)
    
    _progress.finish()
    
    return {
        "@context": "https://purl.org/gag/schema/dirtree.jsonld",
        "observedAtTime": datetime.now().isoformat(),
        "observer": {
            "uid": get_effective_user(),
            "userPrincipalName": get_user_principal_name()
        },
        "dirtree": {root_name: tree}
    }


def _build_tree(path: str) -> TreeNode:
    """
    Recursively builds a tree node for the given path.
    
    Args:
        path: The absolute path to scan.
        
    Returns:
        None if the path is a file or empty directory,
        otherwise a dictionary of child nodes.
    """
    global _progress
    
    if not os.path.isdir(path):
        return None
    
    if _progress:
        _progress.increment()
    
    children: Dict[str, TreeNode] = {}
    
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_dir():
                    # Recursively build subtree for directories
                    children[entry.name] = _build_tree(entry.path)
                # Note: We only include directories in the tree.
                # Files are not included in this directory-only tree.
    except (OSError, PermissionError):
        # Return empty dict if we can't access the directory
        pass
    
    # Return None for empty directories (leaf nodes)
    # or the children dict for directories with contents
    if not children:
        return None
    
    return children


def save_to_json(tree: Dict[str, TreeNode], output_path: str) -> None:
    """
    Saves the tree structure to a JSON file.
    
    Args:
        tree: The tree structure to save.
        output_path: The path to the output JSON file.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=2)


