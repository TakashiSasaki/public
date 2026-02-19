import json
import os
from pathlib import Path
from platformdirs import user_config_dir

APP_NAME = "llama-cpp-tk"
APP_AUTHOR = "takas" # Optional, but good practice for platformdirs on Windows

def get_config_dir() -> Path:
    """Returns the platform-specific user configuration directory."""
    return Path(user_config_dir(APP_NAME, APP_AUTHOR))

def get_settings_path() -> Path:
    """Returns the full path to the settings.json file."""
    return get_config_dir() / "settings.json"

def get_default_models_dir() -> Path:
    """Returns the default models directory (relative to the app/script)."""
    # Default to a 'models' folder in the current working directory or 
    # relative to the package if installed globally (though this app seems local).
    # For now, let's keep it compatible with existing behavior: ./models
    return Path("models").absolute()

def load_settings() -> dict:
    """Loads settings from settings.json, returning defaults if not found."""
    settings_path = get_settings_path()
    defaults = {
        "_meta": {
            "app_name": APP_NAME,
            "description": "Configuration file for llama-cpp-tk application",
            "url": "https://github.com/TakashiSasaki/public/tree/llama-cpp-tk"
        },
        "general": {
            "models_path": str(get_default_models_dir()),
            "theme": "default"
        },
        "last_session": {
            "backend": "cuda",
            "model": ""
        },
        "parameters": {}
    }

    if not settings_path.exists():
        return defaults

    try:
        with open(settings_path, "r", encoding="utf-8") as f:
            user_settings = json.load(f)
            
        # Recursive merge/update defaults with user settings to handle missing keys
        _deep_update(defaults, user_settings)
        return defaults
    except Exception as e:
        print(f"Error loading settings: {e}")
        return defaults

def save_settings(settings: dict):
    """Saves the settings dictionary to settings.json."""
    settings_path = get_settings_path()
    
    # Ensure directory exists
    settings_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Error saving settings: {e}")

def _deep_update(base_dict, update_dict):
    """Recursively updates base_dict with values from update_dict."""
    for key, value in update_dict.items():
        if isinstance(value, dict) and key in base_dict and isinstance(base_dict[key], dict):
            _deep_update(base_dict[key], value)
        else:
            base_dict[key] = value

def get_models_path(settings: dict = None) -> Path:
    """Helper to get the Path object for models directory from settings."""
    if settings is None:
        settings = load_settings()
    
    path_str = settings.get("general", {}).get("models_path", "models")
    path = Path(path_str)
    
    # If path is relative, make it relative to CWD (or we could make it relative to config dir?)
    # Usually "models" implies ./models in the portable sense.
    # If the user sets an absolute path, Path(abs_path) works fine.
    if not path.is_absolute():
        path = Path.cwd() / path
        
    return path
