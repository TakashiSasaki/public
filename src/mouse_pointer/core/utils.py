import sys
from pathlib import Path

def get_app_asset_path(*parts: str) -> Path:
    """
    Returns the path to app-specific assets for both development and
    PyInstaller one-file execution.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return Path(sys._MEIPASS) / "app_assets" / Path(*parts)

    return Path(__file__).parent.parent.parent.parent / "assets" / Path(*parts)

def get_assets_dir() -> Path:
    """
    Returns the path to the assets directory, handling both standard execution
    and PyInstaller's one-file bundle environment.
    """
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller bundled path
        return Path(sys._MEIPASS) / "assets"
    
    # Standard development path
    # src/mouse_pointer/core/utils.py -> pictogram/src/assets
    return Path(__file__).parent.parent.parent.parent / "pictogram" / "src" / "assets"
