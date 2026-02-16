import os
import sys
import winreg
from typing import List
from pathlib import Path

if sys.platform != "win32":
    raise OSError("This module is only supported on Windows.")

def get_path_from_environment() -> List[Path]:
    """
    Retrieves the system PATH environment variable and returns it as a list of Path objects.
    """
    path_env = os.environ.get("PATH", "")
    # os.pathsep is ';' on Windows and ':' on Unix-like systems
    return [Path(p) for p in path_env.split(os.pathsep) if p]

def get_system_path_from_registry() -> List[Path]:
    """
    Retrieves the system PATH environment variable directly from the Windows Registry.
    Key: HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment
    """
    key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            value, _ = winreg.QueryValueEx(key, "Path")
            # os.pathsep is ';' on Windows
            return [Path(p) for p in value.split(os.pathsep) if p]
    except FileNotFoundError:
        return []

def get_user_path_from_registry() -> List[Path]:
    """
    Retrieves the user PATH environment variable directly from the Windows Registry.
    Key: HKEY_CURRENT_USER\\Environment
    """
    key_path = r"Environment"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            value, _ = winreg.QueryValueEx(key, "Path")
            return [Path(p) for p in value.split(os.pathsep) if p]
    except FileNotFoundError:
        return []

def find_command_in_path(command_name: str) -> List[Path]:
    """
    Searches for an executable command in the directories listed in the PATH environment variable.
    Returns a list of all matching paths, similar to the Windows 'where' command.
    
    If the command_name includes an extension, searches for that exact file.
    If no extension is provided, appends extensions from PATHEXT (e.g., .EXE, .BAT) to search.
    
    The search is case-insensitive on Windows.
    """
    found_paths = []
    search_dirs = get_path_from_environment()
    
    # Check if command_name has an extension
    has_extension = os.path.splitext(command_name)[1] != ""
    
    extensions = [""]
    if not has_extension:
        # Get PATHEXT, default to .COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC
        pathext = os.environ.get("PATHEXT", ".COM;.EXE;.BAT;.CMD;.VBS;.VBE;.JS;.JSE;.WSF;.WSH;.MSC")
        extensions = [ext.lower() for ext in pathext.split(os.pathsep) if ext]
        # Also ensure we search for the name as-is (though on Windows usually extension is needed for execution)
        # But 'where' command logic tries extensions.

    for directory in search_dirs:
        if not directory.exists() or not directory.is_dir():
            continue
            
        for ext in extensions:
            # Construct the full path
            # Case-insensitive check is handled by filesystem on Windows.
            
            candidate_name = command_name + ext if not has_extension else command_name
            candidate_path = directory / candidate_name
            
            if candidate_path.exists() and candidate_path.is_file():
                # On Windows, we might want to return the path with the correct case from filesystem.
                # Path.resolve() does this but resolves symlinks too.
                # For now, return as is or resolve if needed. 
                # Let's use resolve to get absolute path and correct casing.
                try:
                    found_paths.append(candidate_path.resolve())
                except OSError:
                    # Fallback if resolve fails (e.g. permission issues)
                    found_paths.append(candidate_path)
                    
    return found_paths
