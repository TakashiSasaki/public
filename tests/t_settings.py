import sys
from pathlib import Path

# Add src to sys.path
sys.path.append(str(Path("src").absolute()))

from llama_cpp_sse import settings

def test_settings():
    print("Testing settings module...")
    
    # 1. Config Dir
    config_dir = settings.get_config_dir()
    print(f"Config Dir: {config_dir}")
    
    # 2. Settings Path
    settings_path = settings.get_settings_path()
    print(f"Settings Path: {settings_path}")
    
    # 3. Default Models Path
    default_models = settings.get_default_models_dir()
    print(f"Default Models Dir: {default_models}")
    
    # 4. Load Settings (should be defaults)
    s = settings.load_settings()
    print(f"Loaded Settings: {s}")
    
    # 5. Save Settings
    s["general"]["test_key"] = "test_value"
    settings.save_settings(s)
    print("Saved settings with test_key.")
    
    # 6. Reload and Verify
    s2 = settings.load_settings()
    if s2["general"].get("test_key") == "test_value":
        print("SUCCESS: Settings saved and reloaded correctly.")
    else:
        print("FAILURE: Settings persistence failed.")
        
    # 7. Get Models Path
    models_path = settings.get_models_path(s2)
    print(f"Resolved Models Path: {models_path}")
    
    # Clean up (optional, but maybe good to leave for user to see)
    # settings_path.unlink()

if __name__ == "__main__":
    test_settings()
