
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import importlib.metadata
import threading
import re
from urllib.request import urlopen
from urllib.error import URLError

PYPROJECT_URL = "https://raw.githubusercontent.com/TakashiSasaki/get-a-grip/refs/heads/get-a-grip/pyproject.toml"

class LauncherApp:
    def __init__(self, root):
        try:
            self.current_version = importlib.metadata.version("get-a-grip")
        except importlib.metadata.PackageNotFoundError:
            self.current_version = "dev"

        self.root = root
        self.root.title(f"Get-a-Grip Launcher v{self.current_version}")
        self.root.geometry("350x380")
        
        # Track processes and buttons
        self.processes = {}
        self.buttons = {}

        lbl = ttk.Label(root, text="Select a tool to launch:", font=("Arial", 12))
        lbl.pack(pady=10)

        # Container for tool buttons (using tk.Button for background color support on Windows)
        tools_frame = ttk.Frame(root)
        tools_frame.pack(fill='both', expand=True, padx=20)

        self.add_tool_button(tools_frame, "EFU Tools (Update/Merge)", "get_a_grip.gui.efu_gui")
        self.add_tool_button(tools_frame, "Event Viewer", "get_a_grip.gui.event_viewer")
        self.add_tool_button(tools_frame, "Environment Viewer", "get_a_grip.gui.env_viewer")
        self.add_tool_button(tools_frame, "Shell Special Folders", "get_a_grip.gui.shell_folders_viewer")
        
        ttk.Separator(root, orient='horizontal').pack(fill='x', padx=10, pady=10)
        
        ttk.Button(root, text="Exit", command=self.on_close).pack(pady=5)
        
        # Version status label at the bottom
        self.version_label = ttk.Label(root, text="Checking for updates...", font=("Arial", 8), foreground="gray")
        self.version_label.pack(side="bottom", pady=5)
        
        # Handle window close
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        # Start monitoring process status
        self.monitor_processes()
        
        # Check for updates in the background
        threading.Thread(target=self.check_latest_version, daemon=True).start()

    def add_tool_button(self, parent, text, module_name):
        # Use standard tk.Button because ttk.Button background color is hard to change on Windows
        btn = tk.Button(parent, text=text, command=lambda: self.toggle_module(module_name))
        btn.pack(fill='x', pady=5)
        self.buttons[module_name] = btn

    def toggle_module(self, module_name):
        proc = self.processes.get(module_name)
        if proc and proc.poll() is None:
            # Running, so terminate
            proc.terminate()
            # We don't remove from self.processes yet, monitor_processes will handle it
        else:
            # Not running, so launch
            try:
                proc = subprocess.Popen([sys.executable, "-m", module_name])
                self.processes[module_name] = proc
                self.buttons[module_name].config(bg="#ffcccc", activebackground="#ff9999")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to launch {module_name}:\n{e}")

    def monitor_processes(self):
        for module_name, proc in list(self.processes.items()):
            if proc.poll() is not None:
                # Process finished
                self.buttons[module_name].config(bg="SystemButtonFace", activebackground="SystemButtonFace")
                del self.processes[module_name]
        
        # Update again in 1 second
        self.root.after(1000, self.monitor_processes)

    def check_latest_version(self):
        """Fetch the latest version from GitHub in a background thread."""
        try:
            with urlopen(PYPROJECT_URL, timeout=10) as response:
                content = response.read().decode("utf-8")
            match = re.search(r'^version\s*=\s*"([^"]+)"', content, re.MULTILINE)
            if match:
                latest_version = match.group(1)
                self.root.after(0, self.update_version_label, latest_version)
            else:
                self.root.after(0, self.set_version_label, "Could not parse remote version", "orange")
        except (URLError, OSError):
            self.root.after(0, self.set_version_label, "Update check failed (offline?)", "gray")

    def update_version_label(self, latest_version):
        """Compare versions and update the label on the main thread."""
        if self.current_version == "dev":
            self.set_version_label(f"Latest: v{latest_version} (dev mode)", "gray")
        elif self.current_version == latest_version:
            self.set_version_label(f"✓ Up to date (v{self.current_version})", "green")
        else:
            self.set_version_label(
                f"⚠ Update available: v{self.current_version} → v{latest_version}",
                "red"
            )

    def set_version_label(self, text, color):
        self.version_label.config(text=text, foreground=color)

    def on_close(self):
        # Kill all subprocesses before exiting
        for module_name, proc in self.processes.items():
            if proc.poll() is None:
                proc.terminate()
        self.root.destroy()

def main():
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()

