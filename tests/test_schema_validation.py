import os
import json
import jsonschema
from jsonschema import validate
from get_a_grip.tools.scanner import scan_directory, save_to_json

def test_scanner_output_schema():
    # 1. Setup paths
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schema_path = os.path.join(root_dir, "schema", "filelist.json")
    output_path = os.path.join(root_dir, "test_scanner_output.json")
    
    # 2. Run scanner on a small known directory (the schemas directory itself)
    scan_target = os.path.join(root_dir, "schema")
    file_data = scan_directory(scan_target)
    save_to_json(file_data, output_path)
    
    try:
        # 3. Load the generated JSON
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # 4. Load the schema
        with open(schema_path, "r", encoding="utf-8") as f:
            schema = json.load(f)
            
        # 5. Validate
        print(f"Validating {output_path} against {schema_path}...")
        validate(instance=data, schema=schema)
        print("Validation successful! The scanner output matches the schema.")
        
    except jsonschema.exceptions.ValidationError as ve:
        print(f"Schema validation failed: {ve.message}")
        raise
    except Exception as e:
        print(f"An error occurred during testing: {e}")
        raise
    finally:
        # 6. Cleanup
        if os.path.exists(output_path):
            os.remove(output_path)

if __name__ == "__main__":
    test_scanner_output_schema()
