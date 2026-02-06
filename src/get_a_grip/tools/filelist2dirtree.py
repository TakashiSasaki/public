"""
Convert filelist JSON output to directory tree structure.

This script reads a filelist JSON file (conforming to schema/filelist.json)
and extracts the directory entries to build a hierarchical tree structure
conforming to schema/dirtree.json.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Union, Optional

# Type alias for the tree structure
TreeNode = Union[None, Dict[str, "TreeNode"]]


def build_tree_from_paths(paths: List[str]) -> Dict[str, TreeNode]:
    """
    Build a directory tree from a list of absolute paths.
    
    Args:
        paths: List of absolute directory paths.
        
    Returns:
        A dictionary representing the tree structure conforming to dirtree.json schema.
    """
    # Find common root(s)
    roots: Dict[str, TreeNode] = {}
    
    for path in paths:
        # Normalize and split path
        # On Windows, this handles both forward and back slashes
        parts = []
        # Split by both types of separators
        for sep in ['\\', '/']:
            if sep in path:
                parts = path.split(sep)
                break
        
        # Filter out empty strings
        parts = [p for p in parts if p]
        
        if not parts:
            continue
        
        # First part is the root (e.g., "C:" or "D:")
        root = parts[0]
        
        # Initialize root if not exists
        if root not in roots:
            roots[root] = {}
        
        # Navigate/create the tree structure
        current = roots[root]
        
        # Process remaining parts (skip root)
        for part in parts[1:]:
            if current is None:
                # This shouldn't happen in well-formed data
                break
            
            if not isinstance(current, dict):
                # Current is None, need to convert to dict
                current = {}
            
            if part not in current:
                current[part] = {}
            
            # Move deeper
            next_node = current[part]
            if next_node is None:
                # Leaf node, convert to dict to add children
                current[part] = {}
                current = current[part]
            else:
                current = next_node
    
    # Convert empty dicts to None (leaf nodes)
    def simplify_tree(node: TreeNode) -> TreeNode:
        """Convert empty dictionaries to None."""
        if node is None:
            return None
        if isinstance(node, dict):
            if not node:
                # Empty dict = leaf directory with no subdirectories
                return None
            simplified = {}
            for key, value in node.items():
                simplified[key] = simplify_tree(value)
            # Keep the dict even if children are None
            # This represents a directory with subdirectories
            return simplified
        return node
    
    # Simplify each root
    for root_key in roots:
        roots[root_key] = simplify_tree(roots[root_key])
    
    return {
        "@context": "https://purl.org/gag/schema/dirtree.jsonld",
        "dirtree": roots
    }


def convert_filelist_to_dirtree(filelist_path: str, output_path: Optional[str] = None) -> Dict[str, TreeNode]:
    """
    Convert a filelist JSON file to a directory tree structure.
    
    Args:
        filelist_path: Path to the filelist JSON file.
        output_path: Optional path to save the output JSON file.
        
    Returns:
        The directory tree structure.
    """
    # Load filelist
    with open(filelist_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Extract directory paths
    dirs = data.get('dirs', [])
    dir_paths = [d['Filename'] for d in dirs if 'Filename' in d]
    
    print(f"Found {len(dir_paths)} directories in {filelist_path}")
    
    # Build tree
    tree = build_tree_from_paths(dir_paths)
    
    # Save if output path specified
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(tree, f, ensure_ascii=False, indent=2)
        print(f"Directory tree saved to {output_path}")
    
    return tree


def main():
    parser = argparse.ArgumentParser(
        description="Convert filelist JSON to directory tree structure."
    )
    parser.add_argument("input", help="Input filelist JSON file")
    parser.add_argument("-o", "--output", help="Output dirtree JSON file (default: print to stdout)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input):
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)
    
    tree = convert_filelist_to_dirtree(args.input, args.output)
    
    if not args.output:
        # Print to stdout
        print(json.dumps(tree, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
