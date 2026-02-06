import json
import sys

try:
    from jsonschema import validate, ValidationError
except ImportError:
    print("Error: jsonschema library not found. Install with: pip install jsonschema")
    sys.exit(1)

def validate_filelist(data_file, schema_file):
    """Validate a filelist JSON file against the schema."""
    
    # Load schema
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    # Load data
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Validate
    try:
        validate(instance=data, schema=schema)
        print(f"[OK] Validation successful: {data_file} conforms to {schema_file}")
        return True
    except ValidationError as e:
        print(f"[FAIL] Validation failed: {data_file} does NOT conform to {schema_file}")
        print(f"\nError: {e.message}")
        print(f"Path: {' -> '.join(str(p) for p in e.path)}")
        print(f"Schema path: {' -> '.join(str(p) for p in e.schema_path)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: validate_filelist.py <data.json> <schema.json>")
        sys.exit(1)
    
    data_file = sys.argv[1]
    schema_file = sys.argv[2]
    
    success = validate_filelist(data_file, schema_file)
    sys.exit(0 if success else 1)
