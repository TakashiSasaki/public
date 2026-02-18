
import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import sys
import os
import importlib.metadata

class LauncherApp:
    def __init__(self, root):
        try:
            version = importlib.metadata.version("get-a-grip")
        except importlib.metadata.PackageNotFoundError:
            version = "dev"

        self.root = root
        self.root.title(f"Get-a-Grip Launcher v{version}")
        self.root.geometry("300x250")

        lbl = ttk.Label(root, text="Select a tool to launch:", font=("Arial", 12))
        lbl.pack(pady=10)

        # Buttons
        ttk.Button(root, text="EFU Tools (Update/Merge)", command=self.launch_efu).pack(fill='x', padx=20, pady=5)
        ttk.Button(root, text="Event Viewer", command=self.launch_event_viewer).pack(fill='x', padx=20, pady=5)
        ttk.Button(root, text="Environment Viewer", command=self.launch_env_viewer).pack(fill='x', padx=20, pady=5)
        
        ttk.Separator(root, orient='horizontal').pack(fill='x', padx=10, pady=10)
        
        ttk.Button(root, text="Exit", command=root.quit).pack(pady=5)

    def launch_module(self, module_name):
        try:
            # Launch as a separate process
            subprocess.Popen([sys.executable, "-m", module_name])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to launch {module_name}:\n{e}")

    def launch_efu(self):
        self.launch_module("get_a_grip.gui.efu_gui")

    def launch_event_viewer(self):
        self.launch_module("get_a_grip.gui.event_viewer")

    def launch_env_viewer(self):
        self.launch_module("get_a_grip.gui.env_viewer")

def main():
    root = tk.Tk()
    app = LauncherApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
