
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import threading
import sys
from pathlib import Path

class EfuGuiApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EFU Tools GUI")
        self.root.geometry("600x500")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=5, pady=5)

        self.create_update_tab()
        self.create_merge_tab()

    def get_available_drives(self):
        import string
        import os
        drives = []
        for d in string.ascii_uppercase:
            drive_path = f"{d}:/"
            if os.path.exists(drive_path):
                drives.append(drive_path)
        return drives

    def create_drive_buttons(self, parent, string_var):
        frame = ttk.Frame(parent)
        frame.pack(fill='x', padx=5, pady=2)
        ttk.Label(frame, text="Drives:").pack(side='left')
        
        drives = self.get_available_drives()
        for drive in drives:
            btn = ttk.Button(frame, text=drive, width=4, 
                             command=lambda d=drive: string_var.set(d))
            btn.pack(side='left', padx=2)

    def check_dir_for_uuid(self, dir_var, uuid_var):
        path_str = dir_var.get().strip()
        if not path_str:
            return
        
        path = Path(path_str)
        if not path.exists() or not path.is_dir():
            return
            
        # Find valid UUIDs (files looking like <uuid>.efu)
        # We assume UUID doesn't contain '.' ? Actually filename is <uuid>.efu.
        # Let's list all .efu files.
        try:
            efu_files = list(path.glob('*.efu'))
            if len(efu_files) == 1:
                # Auto-fill
                uuid = efu_files[0].stem
                uuid_var.set(uuid)
        except Exception as e:
            print(f"Error scanning dir: {e}")

    def create_update_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Update EFU")

        # Start Dir (Moved up)
        frame_dir = ttk.Frame(tab)
        frame_dir.pack(fill='x', padx=5, pady=5)
        ttk.Label(frame_dir, text="Start Directory:").pack(side='left')
        self.update_dir_var = tk.StringVar()
        self.update_dir_var.trace_add("write", lambda *args: self.check_dir_for_uuid(self.update_dir_var, self.update_uuid_var))
        ttk.Entry(frame_dir, textvariable=self.update_dir_var).pack(side='left', expand=True, fill='x', padx=5)
        ttk.Button(frame_dir, text="Browse...", command=lambda: self.browse_dir(self.update_dir_var)).pack(side='left')
        
        # Drive Buttons
        self.create_drive_buttons(tab, self.update_dir_var)

        # UUID (Moved down)
        frame_uuid = ttk.Frame(tab)
        frame_uuid.pack(fill='x', padx=5, pady=5)
        ttk.Label(frame_uuid, text="UUID:").pack(side='left')
        self.update_uuid_var = tk.StringVar()
        ttk.Entry(frame_uuid, textvariable=self.update_uuid_var).pack(side='left', expand=True, fill='x', padx=5)

        # Execute Button
        ttk.Button(tab, text="Run Update", command=self.run_update).pack(pady=10)

        # Log Area
        self.update_log = tk.Text(tab, state='disabled', height=15)
        self.update_log.pack(expand=True, fill='both', padx=5, pady=5)

    def create_merge_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="Merge EFU")

        # Start Dir (Moved up)
        frame_dir = ttk.Frame(tab)
        frame_dir.pack(fill='x', padx=5, pady=5)
        ttk.Label(frame_dir, text="Start Directory:").pack(side='left')
        self.merge_dir_var = tk.StringVar()
        self.merge_dir_var.trace_add("write", lambda *args: self.check_dir_for_uuid(self.merge_dir_var, self.merge_uuid_var))
        ttk.Entry(frame_dir, textvariable=self.merge_dir_var).pack(side='left', expand=True, fill='x', padx=5)
        ttk.Button(frame_dir, text="Browse...", command=lambda: self.browse_dir(self.merge_dir_var)).pack(side='left')

        # Drive Buttons
        self.create_drive_buttons(tab, self.merge_dir_var)

        # UUID (Moved down)
        frame_uuid = ttk.Frame(tab)
        frame_uuid.pack(fill='x', padx=5, pady=5)
        ttk.Label(frame_uuid, text="UUID:").pack(side='left')
        self.merge_uuid_var = tk.StringVar()
        ttk.Entry(frame_uuid, textvariable=self.merge_uuid_var).pack(side='left', expand=True, fill='x', padx=5)

        # Output File
        frame_out = ttk.Frame(tab)
        frame_out.pack(fill='x', padx=5, pady=5)
        ttk.Label(frame_out, text="Output File:").pack(side='left')
        self.merge_out_var = tk.StringVar()
        ttk.Entry(frame_out, textvariable=self.merge_out_var).pack(side='left', expand=True, fill='x', padx=5)
        ttk.Button(frame_out, text="Save As...", command=lambda: self.browse_save(self.merge_out_var)).pack(side='left')

        # Execute Button
        ttk.Button(tab, text="Run Merge", command=self.run_merge).pack(pady=10)

        # Log Area
        self.merge_log = tk.Text(tab, state='disabled', height=15)
        self.merge_log.pack(expand=True, fill='both', padx=5, pady=5)

    def browse_dir(self, var):
        d = filedialog.askdirectory()
        if d:
            var.set(d)

    def browse_save(self, var):
        f = filedialog.asksaveasfilename(defaultextension=".efu", filetypes=[("EFU Files", "*.efu"), ("All Files", "*.*")])
        if f:
            var.set(f)

    def log(self, text_widget, message):
        text_widget.config(state='normal')
        text_widget.insert('end', message + "\n")
        text_widget.see('end')
        text_widget.config(state='disabled')

    def run_command_in_thread(self, command, log_widget):
        def task():
            self.log(log_widget, f"Running: {' '.join(command)}")
            try:
                # Need to find the script paths relative to this gui script or project root
                # Assuming running from project root or src
                # We can construct absolute paths.
                
                process = subprocess.Popen(
                    command,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    cwd=Path.cwd() # Run in current working directory
                )
                
                for line in process.stdout:
                    self.root.after(0, self.log, log_widget, line.strip())
                
                process.wait()
                self.root.after(0, self.log, log_widget, f"Process finished with exit code {process.returncode}")
                if process.returncode == 0:
                     self.root.after(0, messagebox.showinfo, "Success", "Operation completed successfully.")
                else:
                     self.root.after(0, messagebox.showerror, "Error", "Operation failed.")

            except Exception as e:
                self.root.after(0, self.log, log_widget, f"Error: {e}")
                self.root.after(0, messagebox.showerror, "Error", f"An error occurred: {e}")

        threading.Thread(target=task, daemon=True).start()

    def get_script_path(self, script_name):
        # Assumes directory structure:
        # src/get_a_grip/gui/efu_gui.py
        # src/get_a_grip/cli/efu/update-efu.py
        # We are here:
        current_file = Path(__file__).resolve()
        # Go up to get_a_grip
        base_dir = current_file.parent.parent
        script_path = base_dir / "cli" / "efu" / script_name
        return str(script_path)

    def run_update(self):
        uuid = self.update_uuid_var.get().strip()
        start_dir = self.update_dir_var.get().strip()
        
        if not uuid or not start_dir:
            messagebox.showwarning("Validation", "Please fill in UUID and Start Directory")
            return

        script = self.get_script_path("update-efu.py")
        cmd = [sys.executable, script, "--uuid", uuid, "--start-dir", start_dir]
        self.update_log.config(state='normal')
        self.update_log.delete(1.0, 'end')
        self.update_log.config(state='disabled')
        self.run_command_in_thread(cmd, self.update_log)

    def run_merge(self):
        uuid = self.merge_uuid_var.get().strip()
        start_dir = self.merge_dir_var.get().strip()
        output = self.merge_out_var.get().strip()

        if not uuid or not start_dir or not output:
            messagebox.showwarning("Validation", "Please fill in all fields")
            return

        script = self.get_script_path("merge-efu.py")
        cmd = [sys.executable, script, "--uuid", uuid, "--start-dir", start_dir, "--output", output]
        self.merge_log.config(state='normal')
        self.merge_log.delete(1.0, 'end')
        self.merge_log.config(state='disabled')
        self.run_command_in_thread(cmd, self.merge_log)

if __name__ == "__main__":
    root = tk.Tk()
    app = EfuGuiApp(root)
    root.mainloop()
