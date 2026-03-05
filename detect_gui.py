import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import os
import socket
import sys

VERSION = "0.1.0"
LOCK_PORT = 54321

class BranchDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Git Related Branch Detector v{VERSION}")
        self.root.geometry("900x600")

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

        columns = ("name", "shared", "relationship", "hash")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        
        self.tree.heading("name", text="Branch Name")
        self.tree.heading("shared", text="Shared History")
        self.tree.heading("relationship", text="Relationship")
        self.tree.heading("hash", text="Commit Hash")

        self.tree.column("name", width=300)
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
            # Might be detached HEAD
            current = self.git_cmd(["rev-parse", "--short", "HEAD"])
            self.current_branch_label.config(text=f"Current: DETACHED ({current})")
        else:
            self.current_branch_label.config(text=f"Current Branch: {current}")

        # List all branches
        branches_raw = self.git_cmd(["for-each-ref", "--format=%(refname:short) %(objectname)", "refs/heads", "refs/remotes"])
        if not branches_raw:
            return

        for line in branches_raw.split('\n'):
            if not line: continue
            name, b_hash = line.split()
            
            shared = "No"
            relationship = "Independent"
            tags = ()

            if name == current:
                shared = "Yes"
                relationship = "Current"
                tags = ('current',)
            else:
                # Check for shared history
                has_base = self.git_cmd(["merge-base", current, name])
                if has_base:
                    shared = "Yes"
                    # Determine Tip or Ancestor
                    is_ancestor = subprocess.call(["git", "merge-base", "--is-ancestor", name, current]) == 0
                    if is_ancestor:
                        # name is in current's history
                        # Double check if current is also ancestor of name (identical)
                        is_descendant = subprocess.call(["git", "merge-base", "--is-ancestor", current, name]) == 0
                        if is_descendant:
                            relationship = "Tip (Identical)"
                            tags = ('tip',)
                        else:
                            relationship = "Ancestor"
                            tags = ('ancestor',)
                    else:
                        # name is not ancestor of current, but shared base exists
                        # check if current is ancestor of name (then name is Tip)
                        is_tip = subprocess.call(["git", "merge-base", "--is-ancestor", current, name]) == 0
                        if is_tip:
                            relationship = "Tip (Ahead)"
                            tags = ('tip',)
                        else:
                            relationship = "Diverged"
                else:
                    tags = ('independent',)

            self.tree.insert("", tk.END, values=(name, shared, relationship, b_hash), tags=tags)

def ensure_single_instance():
    # Attempt to create a socket listener on a specific port
    try:
        # Use a global variable to keep the socket alive
        global lock_socket
        lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lock_socket.bind(('127.0.0.1', LOCK_PORT))
    except socket.error:
        # Port already in use
        return False
    return True

if __name__ == "__main__":
    if not ensure_single_instance():
        # Using a hidden root for the error message
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Instance Error", "Another instance of Git Related Branch Detector is already running.")
        sys.exit(1)

    root = tk.Tk()
    app = BranchDetectorApp(root)
    root.mainloop()
