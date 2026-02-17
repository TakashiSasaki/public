
import os
import sys
from pathlib import Path
import win32com.client

def get_shortcut_path():
    """Returns the path to the shortcut file in the Start Menu."""
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise EnvironmentError("APPDATA environment variable not found.")
    
    start_menu = Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
    return start_menu / "Get-a-Grip.lnk"

def create_shortcut():
    """Creates a shortcut to the GUI launcher in the Start Menu."""
    shortcut_path = get_shortcut_path()
    
    # Target: pythonw.exe (no console) or python.exe
    # We want to launch the module `get_a_grip.gui.launcher`
    
    # python_exe = sys.executable
    # Better to use pythonw.exe if available to avoid console window for GUI
    python_dir = Path(sys.executable).parent
    pythonw = python_dir / "pythonw.exe"
    
    target_exe = str(pythonw) if pythonw.exists() else sys.executable
    
    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(shortcut_path))
    shortcut.TargetPath = target_exe
    shortcut.Arguments = "-m get_a_grip.gui.launcher"
    shortcut.Description = "Get-a-Grip GUI Launcher"
    shortcut.IconLocation = target_exe # Use python icon for now
    shortcut.WorkingDirectory = str(Path.cwd()) # Or maybe user home?
    shortcut.Save()
    
    print(f"Shortcut created at: {shortcut_path}")

def remove_shortcut():
    """Removes the shortcut from the Start Menu."""
    shortcut_path = get_shortcut_path()
    
    if shortcut_path.exists():
        os.remove(shortcut_path)
        print(f"Shortcut removed: {shortcut_path}")
    else:
        print(f"Shortcut not found at: {shortcut_path}")

def main():
    # Simple CLI for testing or standalone usage
    import argparse
    parser = argparse.ArgumentParser(description="Manage Get-a-Grip Start Menu Shortcut")
    parser.add_argument("action", choices=["install", "uninstall"], help="Action to perform")
    
    args = parser.parse_args()
    
    try:
        if args.action == "install":
            create_shortcut()
        elif args.action == "uninstall":
            remove_shortcut()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
