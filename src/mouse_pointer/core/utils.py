import sys
from pathlib import Path

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
