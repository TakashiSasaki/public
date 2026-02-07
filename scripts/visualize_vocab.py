
import sys
from pathlib import Path
from rdflib import Graph
from rdflib.tools.rdf2dot import rdf2dot

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/visualize_vocab.py <path_to_jsonld_file>", file=sys.stderr)
        return

    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"File not found: {file_path}", file=sys.stderr)
        return
    
    try:
        g = Graph()
        # Parse JSON-LD file
        # Note: top-level @id in flattened JSON-LD can cause triples to be loaded into a Named Graph,
        # leaving the default graph empty. Ensure the file structure is compatible.
        g.parse(str(file_path), format="json-ld")
        
        # Warn if no triples found
        if len(g) == 0:
            print(f"Warning: No triples found in {file_path}. The graph might be empty or loaded into a Named Graph.", file=sys.stderr)
        else:
            print(f"// Extracted {len(g)} triples from {file_path.name}", file=sys.stderr)

        # Output DOT format to stdout
        rdf2dot(g, sys.stdout)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
