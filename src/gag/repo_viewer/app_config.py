import json
import os
from pathlib import Path
from platformdirs import user_data_dir

APP_NAME = "work.moukaeritai.gag/repo_viewer"
APP_AUTHOR = False
CONFIG_FILE = "filters.json"

def get_config_dir() -> Path:
    """Returns the app's data directory, creating it if it doesn't exist."""
    path = Path(user_data_dir(appname=APP_NAME, appauthor=APP_AUTHOR))
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_config_path() -> Path:
    """Returns the full path to the filters config file."""
    return get_config_dir() / CONFIG_FILE

def load_filters() -> dict:
    """Loads the filter states from the config file."""
    path = get_config_path()
    if not path.exists():
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_filters(state: dict):
    """Saves the filter states to the config file."""
    path = get_config_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(state, f, indent=4)
    except Exception:
        pass
