import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import threading
import os

class GripLauncher:
    def __init__(self, root):
        self.root = root
        self.root.title("Get a Grip Launcher")
        self.root.geometry("600x450")

        # Configure style
        self.style = ttk.Style()
        # On Windows, 'vista' or 'xpnative' are usually good, 'default' often works well too.
        # We leave it to default 'native' behavior managed by ttk.

        # Header
        header_frame = ttk.Frame(root, padding="10")
        header_frame.pack(fill=tk.X)
        ttk.Label(header_frame, text="Get a Grip Legacy Launcher", font=("Segoe UI", 16, "bold")).pack()
        ttk.Label(header_frame, text="Lightweight GUI for CUI Tools", font=("Segoe UI", 9)).pack()

        # Build Buttons
        btn_frame = ttk.Frame(root, padding="10")
        btn_frame.pack(fill=tk.X)
        
        # Grid layout for buttons for better look
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        ttk.Button(btn_frame, text="Launch TUI (Textual)", command=self.run_tui).grid(row=0, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(btn_frame, text="Probe System Info", command=self.run_probe).grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        ttk.Button(btn_frame, text="Who Am I", command=self.run_whoami).grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        ttk.Button(btn_frame, text="Scan Directory...", command=self.scan_directory_dialog).grid(row=1, column=1, sticky="ew", padx=2, pady=2)
        
        # Windows-specific: Add Start Menu registration button
        if sys.platform == 'win32':
            ttk.Button(btn_frame, text="Register to Start Menu", command=self.register_to_start_menu).grid(row=2, column=0, columnspan=2, sticky="ew", padx=2, pady=5)
        
        # Separator
        ttk.Separator(root, orient='horizontal').pack(fill='x', padx=10, pady=5)

        # Output Area
        out_frame = ttk.Labelframe(root, text="Command Output", padding="5")
        out_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.log_text = tk.Text(out_frame, height=10, state='disabled', font=("Consolas", 9), wrap=tk.WORD)
        self.log_text.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        
        scrollbar = ttk.Scrollbar(out_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text['yscrollcommand'] = scrollbar.set

    def log(self, message):
        self.log_text.config(state='normal')
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state='disabled')

    def run_command(self, cmd_list):
        """Runs a command and captures its output to the log window."""
        def task():
            try:
                # Prepare creationflags for Windows to hide console window of the subprocess
                startupinfo = None
                creationflags = 0
                if sys.platform == 'win32':
                    creationflags = subprocess.CREATE_NO_WINDOW
                
                self.root.after(0, self.log, f"> {' '.join(cmd_list)}")
                
                process = subprocess.Popen(
                    cmd_list, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    text=True,
                    creationflags=creationflags
                )
                stdout, stderr = process.communicate()
                
                if stdout:
                    self.root.after(0, self.log, stdout.strip())
                if stderr:
                    self.root.after(0, self.log, f"[STDERR] {stderr.strip()}")
                
                self.root.after(0, self.log, f"Done. (Exit Code: {process.returncode})\n")
            except Exception as e:
                self.root.after(0, self.log, f"Error launching command: {e}\n")

        threading.Thread(target=task, daemon=True).start()

    def run_tui(self):
        """Launches the TUI in a new console window."""
        cmd = [sys.executable, "-m", "get_a_grip.cli", "tui"]
        try:
            self.log(f"> Launching TUI: {' '.join(cmd)}")
            if sys.platform == 'win32':
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                # Linux/Mac: Try to guess a terminal emulator or just run Popen roughly
                # Ideally we typically need x-terminal-emulator -e ...
                # For simplicity in this 'lightweight' approach, we try direct execution.
                # If command relies on TTY, this might fail if not launched from TTY.
                subprocess.Popen(cmd) 
            self.log("Launched TUI in separate console.")
        except Exception as e:
            self.log(f"Failed to launch TUI: {e}")

    def run_probe(self):
        self.run_command([sys.executable, "-m", "get_a_grip.cli", "probe"])

    def run_whoami(self):
        self.run_command([sys.executable, "-m", "get_a_grip.cli", "whoami"])

    def scan_directory_dialog(self):
        target_dir = filedialog.askdirectory(title="Select Directory to Scan")
        if target_dir:
            # We will use a default UUID output for now as per CLI default, 
            # effectively just: python -m get_a_grip.cli filelist <dir>
            # To avoid overwriting without asking, we might want to ensure unique name or use -f if we want simple behavior.
            # But the CLI asks for confirmation interactively which might block our captured process!
            # We should probably provide -f or handle input?
            # Our run_command implementation captures stdout/stderr but *not* stdin.
            # So if the CLI prompts, it will hang!
            
            # Let's add -f or generate a unique filename to avoid prompt.
            # Actually, let's explicitly specify output file to avoid collision prompt if possible.
            output_file = os.path.join(os.getcwd(), f"scan_result.json")
            
            # Since the CLI prompts confirmation if file exists, we should probably add -f if we want automation,
            # or better, use a unique name.
            import uuid
            unique_name = f"scan_{uuid.uuid4().hex[:8]}.json"
            
            cmd = [sys.executable, "-m", "get_a_grip.cli", "filelist", target_dir, "--output", unique_name]
            self.run_command(cmd)

    def register_to_start_menu(self):
        """Creates a Windows Start Menu shortcut for the GUI."""
        if sys.platform != 'win32':
            return

        try:
            # Attempt to find the full path of the 'gag-gui' entry point
            # This works if the path is in the environment variable PATH
            executable_name = "gag-gui.exe"
            try:
                exe_path = subprocess.check_output(["where", executable_name], text=True).splitlines()[0]
                args = ""
            except Exception:
                # Fallback to current pythonw (no console) + module if exe not in PATH
                # Replace python.exe with pythonw.exe if possible
                exe_path = sys.executable.replace("python.exe", "pythonw.exe")
                args = "-m get_a_grip.ttk"

            start_menu_path = os.path.join(
                os.environ["APPDATA"], 
                "Microsoft", "Windows", "Start Menu", "Programs", 
                "Get-A-Grip GUI.lnk"
            )

            # PowerShell script to create WScript.Shell COM shortcut
            ps_command = f"""
            $WshShell = New-Object -ComObject WScript.Shell
            $Shortcut = $WshShell.CreateShortcut("{start_menu_path}")
            $Shortcut.TargetPath = "{exe_path}"
            $Shortcut.Arguments = "{args}"
            $Shortcut.Description = "Get a Grip GUI Launcher"
            $Shortcut.WorkingDirectory = "{os.getcwd()}"
            $Shortcut.Save()
            """

            result = subprocess.run(
                ["powershell", "-Command", ps_command], 
                capture_output=True, 
                text=True
            )

            if result.returncode == 0:
                messagebox.showinfo("Success", f"Shortcut created in Start Menu:\n{start_menu_path}")
                self.log(f"Start Menu shortcut created at: {start_menu_path}")
            else:
                messagebox.showerror("Error", f"Failed to create shortcut:\n{result.stderr}")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

def main():
    root = tk.Tk()
    app = GripLauncher(root)
    root.mainloop()

if __name__ == "__main__":
    main()
