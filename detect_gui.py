import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import socket
import sys
import threading

VERSION = "0.2.3"
LOCK_PORT = 54321

class BranchDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Git Related Branch Detector v{VERSION}")
        self.root.geometry("1000x600")

        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.png")
            if os.path.exists(icon_path):
                img = tk.PhotoImage(file=icon_path)
                self.root.tk.call('wm', 'iconphoto', self.root._w, img)
        except Exception:
            pass

        # Paths
        self.cwd = os.getcwd()
        self.repo_root = self.get_git_root()

        self.all_data = []  # Store raw data for filtering
        self.filter_vars = {} # Store Tkinter variables for filters

        self.setup_ui()
        # Start initial load asynchronously
        self.root.after(100, self.start_refresh)

    def get_git_root(self):
        try:
            return subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"], 
                stderr=subprocess.STDOUT, text=True
            ).strip()
        except subprocess.CalledProcessError:
            return "Not a Git Repository"

    def setup_ui(self):
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Path Info Section
        path_frame = ttk.LabelFrame(main_frame, text="System Information", padding="5")
        path_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(path_frame, text=f"Working Dir: {self.cwd}").pack(anchor=tk.W)
        ttk.Label(path_frame, text=f"Git Repo: {self.repo_root}").pack(anchor=tk.W)

        # Header Section
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        self.current_branch_label = ttk.Label(header_frame, text="Current Branch: Checking...", font=("Segoe UI", 10, "bold"))
        self.current_branch_label.pack(side=tk.LEFT)

        self.refresh_btn = ttk.Button(header_frame, text="Refresh", command=self.start_refresh)
        self.refresh_btn.pack(side=tk.RIGHT)

        # Filters Section
        filter_frame = ttk.LabelFrame(main_frame, text="Filters", padding="5")
        filter_frame.pack(fill=tk.X, pady=(0, 10))

        row1 = ttk.Frame(filter_frame)
        row1.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))
        
        row2 = ttk.Frame(filter_frame)
        row2.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))

        def create_filter_group(parent, title, options):
            group = ttk.Frame(parent)
            group.pack(side=tk.LEFT, padx=(0, 20))
            
            # Use a fixed width label for alignment
            label = ttk.Label(group, text=f"{title}:", width=15, font=("Segoe UI", 9, "bold"))
            label.pack(side=tk.LEFT, padx=(5, 10))
            
            for opt in options:
                var = tk.BooleanVar(value=True)
                self.filter_vars[opt] = var
                cb = ttk.Checkbutton(group, text=opt, variable=var, command=self.apply_filters)
                cb.pack(side=tk.LEFT, padx=(0, 15))

        create_filter_group(row1, "Type", ["Branch", "Reflog"])
        create_filter_group(row1, "Shared History", ["Yes", "No"])
        create_filter_group(row2, "Relationship", [
            "Tip (Identical)", "Tip (Ahead)", "Ancestor", "Diverged", "Independent"
        ])

        # List Section (Treeview)
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "type", "shared", "relationship", "hash")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        self.tree.heading("name", text="Reference Name")
        self.tree.heading("type", text="Type")
        self.tree.heading("shared", text="Shared History")
        self.tree.heading("relationship", text="Relationship")
        self.tree.heading("hash", text="Commit Hash")

        self.tree.column("name", width=250)
        self.tree.column("type", width=80, anchor=tk.CENTER)
        self.tree.column("shared", width=100, anchor=tk.CENTER)
        self.tree.column("relationship", width=120, anchor=tk.CENTER)
        self.tree.column("hash", width=350)

        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tags for coloring
        self.tree.tag_configure('current', background='#e1f5fe', font=("Segoe UI", 9, "bold"))
        self.tree.tag_configure('tip', foreground='#2e7d32') # Green-ish
        self.tree.tag_configure('ancestor', foreground='#1565c0') # Blue-ish
        self.tree.tag_configure('independent', foreground='#9e9e9e') # Gray-ish

    def _get_subprocess_kwargs(self):
        kwargs = {"stderr": subprocess.STDOUT, "text": True}
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs["startupinfo"] = startupinfo
        return kwargs

    def git_cmd(self, args):
        try:
            return subprocess.check_output(["git"] + args, **self._get_subprocess_kwargs()).strip()
        except subprocess.CalledProcessError:
            return None

    def git_call(self, args):
        kwargs = {"stdout": subprocess.DEVNULL}
        if os.name == 'nt':
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs["startupinfo"] = startupinfo
        return subprocess.call(["git"] + args, **kwargs)

    def start_refresh(self):
        self.refresh_btn.config(state=tk.DISABLED)
        self.current_branch_label.config(text="Current Branch: Analyzing...")
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        threading.Thread(target=self.refresh_data_bg, daemon=True).start()

    def refresh_data_bg(self):
        results = []
        
        current = self.git_cmd(["branch", "--show-current"])
        current_display = ""
        if not current:
            current = self.git_cmd(["rev-parse", "--short", "HEAD"])
            current_display = f"Current: DETACHED ({current})"
        else:
            current_display = f"Current Branch: {current}"

        eval_cache = {}

        def evaluate_hash(target_name, target_hash):
            if target_hash in eval_cache:
                return eval_cache[target_hash]
            
            shared = "No"
            relationship = "Independent"
            tags = ()

            has_base = self.git_cmd(["merge-base", current, target_hash])
            if has_base:
                shared = "Yes"
                is_ancestor = self.git_call(["merge-base", "--is-ancestor", target_hash, current]) == 0
                if is_ancestor:
                    is_descendant = self.git_call(["merge-base", "--is-ancestor", current, target_hash]) == 0
                    if is_descendant:
                        relationship = "Tip (Identical)"
                        tags = ('tip',)
                    else:
                        relationship = "Ancestor"
                        tags = ('ancestor',)
                else:
                    is_tip = self.git_call(["merge-base", "--is-ancestor", current, target_hash]) == 0
                    if is_tip:
                        relationship = "Tip (Ahead)"
                        tags = ('tip',)
                    else:
                        relationship = "Diverged"
            else:
                tags = ('independent',)
            
            result = (shared, relationship, tags)
            eval_cache[target_hash] = result
            return result

        # 1. Process Branches
        branches_raw = self.git_cmd(["for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads", "refs/remotes"])
        if branches_raw:
            for line in branches_raw.split('\n'):
                if not line: continue
                name, b_hash = line.split()
                
                if name == current:
                    results.append({"values": (name, "Branch", "Yes", "Current", b_hash), "tags": ('current',)})
                else:
                    shared, relationship, tags = evaluate_hash(name, b_hash)
                    results.append({"values": (name, "Branch", shared, relationship, b_hash), "tags": tags})

        # 2. Process Reflogs
        reflogs_raw = self.git_cmd(["log", "-g", "--all", "--format=%H %gd"])
        if reflogs_raw:
            for line in reflogs_raw.split('\n'):
                if not line: continue
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    r_hash, name = parts
                    shared, relationship, tags = evaluate_hash(name, r_hash)
                    results.append({"values": (name, "Reflog", shared, relationship, r_hash), "tags": tags})
                    
        # Update UI safely from main thread
        self.root.after(0, self.store_and_apply_data, current_display, results)

    def store_and_apply_data(self, current_display, results):
        self.current_branch_label.config(text=current_display)
        self.all_data = results
        self.apply_filters()
        self.refresh_btn.config(state=tk.NORMAL)

    def apply_filters(self):
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # 1. Always insert Current first
        for res in self.all_data:
            _, _, _, relationship, _ = res["values"]
            if relationship == "Current":
                self.tree.insert("", tk.END, values=res["values"], tags=res["tags"])
                break

        # 2. Apply filters to the rest
        for res in self.all_data:
            _, v_type, v_shared, v_rel, _ = res["values"]
            
            if v_rel == "Current":
                continue # Already handled

            # Check logic: if any associated filter var exists and is False, skip
            if v_type in self.filter_vars and not self.filter_vars[v_type].get():
                continue
            if v_shared in self.filter_vars and not self.filter_vars[v_shared].get():
                continue
            if v_rel in self.filter_vars and not self.filter_vars[v_rel].get():
                continue

            self.tree.insert("", tk.END, values=res["values"], tags=res["tags"])


def ensure_single_instance():
    try:
        global lock_socket
        lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lock_socket.bind(('127.0.0.1', LOCK_PORT))
    except socket.error:
        return False
    return True

if __name__ == "__main__":
    if not ensure_single_instance():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Instance Error", "Another instance of Git Related Branch Detector is already running.")
        sys.exit(1)

    root = tk.Tk()
    app = BranchDetectorApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        root.destroy()
        sys.exit(0)
