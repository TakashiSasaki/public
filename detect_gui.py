import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import socket
import sys

VERSION = "0.2.0"
LOCK_PORT = 54321

class BranchDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Git Related Branch Detector v{VERSION}")
        self.root.geometry("1000x600")

        # Paths
        self.cwd = os.getcwd()
        self.repo_root = self.get_git_root()

        self.setup_ui()
        self.refresh_data()

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

        self.refresh_btn = ttk.Button(header_frame, text="Refresh", command=self.refresh_data)
        self.refresh_btn.pack(side=tk.RIGHT)

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

    def git_cmd(self, args):
        try:
            return subprocess.check_output(["git"] + args, stderr=subprocess.STDOUT, text=True).strip()
        except subprocess.CalledProcessError:
            return None

    def refresh_data(self):
        # Clear tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        current = self.git_cmd(["branch", "--show-current"])
        if not current:
            current = self.git_cmd(["rev-parse", "--short", "HEAD"])
            self.current_branch_label.config(text=f"Current: DETACHED ({current})")
        else:
            self.current_branch_label.config(text=f"Current Branch: {current}")

        # Cache for hash evaluation to significantly speed up processing reflogs
        # Since many reflogs point to the same commit hash
        eval_cache = {}

        def evaluate_hash(target_name, target_hash):
            if target_hash in eval_cache:
                return eval_cache[target_hash]
            
            shared = "No"
            relationship = "Independent"
            tags = ()

            # Use the hash directly to prevent lookup issues with weird reflog names
            has_base = self.git_cmd(["merge-base", current, target_hash])
            if has_base:
                shared = "Yes"
                is_ancestor = subprocess.call(["git", "merge-base", "--is-ancestor", target_hash, current]) == 0
                if is_ancestor:
                    is_descendant = subprocess.call(["git", "merge-base", "--is-ancestor", current, target_hash]) == 0
                    if is_descendant:
                        relationship = "Tip (Identical)"
                        tags = ('tip',)
                    else:
                        relationship = "Ancestor"
                        tags = ('ancestor',)
                else:
                    is_tip = subprocess.call(["git", "merge-base", "--is-ancestor", current, target_hash]) == 0
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
                    self.tree.insert("", tk.END, values=(name, "Branch", "Yes", "Current", b_hash), tags=('current',))
                else:
                    shared, relationship, tags = evaluate_hash(name, b_hash)
                    self.tree.insert("", tk.END, values=(name, "Branch", shared, relationship, b_hash), tags=tags)

        # 2. Process Reflogs
        # Log all reflogs globally. %H is hash, %gd is selector (e.g., HEAD@{0})
        reflogs_raw = self.git_cmd(["log", "-g", "--all", "--format=%H %gd"])
        if reflogs_raw:
            for line in reflogs_raw.split('\n'):
                if not line: continue
                parts = line.split(maxsplit=1)
                if len(parts) == 2:
                    r_hash, name = parts
                    shared, relationship, tags = evaluate_hash(name, r_hash)
                    self.tree.insert("", tk.END, values=(name, "Reflog", shared, relationship, r_hash), tags=tags)


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
    root.mainloop()
