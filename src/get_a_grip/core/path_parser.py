import os
import sys
import winreg
from typing import List

if sys.platform != "win32":
    raise OSError("This module is only supported on Windows.")

def get_system_path() -> List[str]:
    """
    Retrieves the system PATH environment variable and returns it as a list of paths.
    """
    path_env = os.environ.get("PATH", "")
    # os.pathsep is ';' on Windows and ':' on Unix-like systems
    return [p for p in path_env.split(os.pathsep) if p]

def get_system_path_from_registry() -> str:
    """
    Retrieves the system PATH environment variable directly from the Windows Registry.
    Key: HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment
    """
    key_path = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
    try:
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path) as key:
            value, _ = winreg.QueryValueEx(key, "Path")
            return value
    except FileNotFoundError:
        return ""

def get_user_path_from_registry() -> str:
    """
    Retrieves the user PATH environment variable directly from the Windows Registry.
    Key: HKEY_CURRENT_USER\\Environment
    """
    key_path = r"Environment"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path) as key:
            value, _ = winreg.QueryValueEx(key, "Path")
            return value
    except FileNotFoundError:
        return ""
