"""Retrieve Windows Shell Special Folders from the registry."""

import os
import winreg


def get_shell_folders() -> list[tuple[str, str]]:
    """Return a sorted list of (name, path) tuples for Windows shell special folders.

    Reads from both 'Shell Folders' and 'User Shell Folders' under
    HKEY_CURRENT_USER\\Software\\Microsoft\\Windows\\CurrentVersion\\Explorer.
    Paths containing unexpanded environment variables (e.g. %USERPROFILE%)
    are expanded automatically.
    """
    folders: dict[str, str] = {}

    reg_keys = [
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders",
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders",
    ]

    for reg_key in reg_keys:
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_key) as key:
                i = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(key, i)
                        if isinstance(value, str) and value and not name.startswith("!"):
                            expanded = os.path.expandvars(value)
                            folders[name] = expanded
                        i += 1
                    except OSError:
                        break
        except OSError:
            continue

    return sorted(folders.items(), key=lambda x: x[0].lower())
