"""
This module serves as the default entry point for file scanning operations.
It wraps the fastest available implementation (excluding external tools like Everything/IPC).
Currently, it delegates to filelist_scandir (os.scandir based) which is significantly
faster than the previous pathlib based implementation (now in filelist_rglob.py).
"""

from .filelist_scandir import scan_directory, save_to_json, unix_to_filetime

__all__ = ["scan_directory", "save_to_json", "unix_to_filetime"]
