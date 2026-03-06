import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import socket
import sys
import threading

VERSION = "0.2.14"
LOCK_PORT = 52941

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
        # Global System Information Section
        path_frame = ttk.LabelFrame(self.root, text="System Information", padding="5")
        path_frame.pack(fill=tk.X, padx=10, pady=(10, 0))

        # Working directory row
        cwd_frame = ttk.Frame(path_frame)
        cwd_frame.pack(fill=tk.X, pady=(2, 2))
        ttk.Label(cwd_frame, text="Working Dir:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.cwd_var = tk.StringVar(value=self.cwd)
        self.cwd_entry = ttk.Entry(cwd_frame, textvariable=self.cwd_var, state='readonly')
        self.cwd_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.btn_browse = ttk.Button(cwd_frame, text="Browse...", command=self.browse_dir)
        self.btn_browse.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_parent = ttk.Button(cwd_frame, text="⬆ Parent Dir", command=self.go_parent_dir)
        self.btn_parent.pack(side=tk.LEFT)

        # Git Repo row
        repo_frame = ttk.Frame(path_frame)
        repo_frame.pack(fill=tk.X, pady=(2, 2))
        ttk.Label(repo_frame, text="Git Repo:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.repo_var = tk.StringVar(value=self.repo_root)
        self.repo_label = ttk.Label(repo_frame, textvariable=self.repo_var, font=("Segoe UI", 9, "bold"))
        self.repo_label.pack(side=tk.LEFT)

        # Main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))

        # Tab 1: Related Branches
        self.tab_branches = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_branches, text="Related Branches")

        # Tab 2: Git Status
        self.tab_status = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_status, text="Git Status")

        # Tab 3: Remote Tracking
        self.tab_remote = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_remote, text="Remote Tracking")

        # Tab 4: Remotes List
        self.tab_remotes_list = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_remotes_list, text="Remotes List")

        self.setup_branches_tab()
        self.setup_status_tab()
        self.setup_remote_tab()
        self.setup_remotes_list_tab()

    def setup_branches_tab(self):
        # Main container for branches tab
        main_frame = ttk.Frame(self.tab_branches, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header Section
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        self.current_branch_label = ttk.Label(header_frame, text="Current Branch: Checking...", font=("Segoe UI", 10, "bold"))
        self.current_branch_label.pack(side=tk.LEFT)

        self.status_label = ttk.Label(header_frame, text="", font=("Segoe UI", 10, "bold"))
        self.status_label.pack(side=tk.LEFT, padx=(20, 0))

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
                is_on = True
                if opt in ["Tip (Identical)", "Ancestor"]:
                    is_on = False
                var = tk.BooleanVar(value=is_on)
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

    def setup_status_tab(self):
        status_frame = ttk.Frame(self.tab_status, padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)

        # Text area for git status
        self.status_text = tk.Text(status_frame, wrap=tk.NONE, font=("Consolas", 10))
        status_scroll_y = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        status_scroll_x = ttk.Scrollbar(status_frame, orient=tk.HORIZONTAL, command=self.status_text.xview)
        
        self.status_text.configure(yscrollcommand=status_scroll_y.set, xscrollcommand=status_scroll_x.set)
        
        self.status_text.grid(row=0, column=0, sticky="nsew")
        status_scroll_y.grid(row=0, column=1, sticky="ns")
        status_scroll_x.grid(row=1, column=0, sticky="ew")
        
        # Make the text area expand
        status_frame.grid_rowconfigure(0, weight=1)
        status_frame.grid_columnconfigure(0, weight=1)
        self.status_text.config(state=tk.DISABLED)

        # Refresh button for status tab
        btn_frame = ttk.Frame(status_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky=tk.E, pady=(10, 0))
        
        btn_refresh_status = ttk.Button(btn_frame, text="Refresh Status", command=self.refresh_status_tab)
        btn_refresh_status.pack(side=tk.RIGHT)

    def setup_remote_tab(self):
        remote_frame = ttk.Frame(self.tab_remote, padding="10")
        remote_frame.pack(fill=tk.BOTH, expand=True)

        # Header with Fetch button
        header = ttk.Frame(remote_frame)
        header.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(header, text="Local & Remote Synchronization Status", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        self.fetch_btn = ttk.Button(header, text="Fetch All", command=self.fetch_all_bg)
        self.fetch_btn.pack(side=tk.RIGHT)

        # Treeview for remote tracking
        tree_container = ttk.Frame(remote_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ("branch", "tracking", "status", "msg")
        self.remote_tree = ttk.Treeview(tree_container, columns=columns, show='headings')
        
        self.remote_tree.heading("branch", text="Branch")
        self.remote_tree.heading("tracking", text="Tracking Upstream")
        self.remote_tree.heading("status", text="Sync Status")
        self.remote_tree.heading("msg", text="Latest Commit Message")

        self.remote_tree.column("branch", width=150)
        self.remote_tree.column("tracking", width=200)
        self.remote_tree.column("status", width=150)
        self.remote_tree.column("msg", width=400)

        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.remote_tree.yview)
        self.remote_tree.configure(yscroll=scrollbar.set)
        
        self.remote_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Tags
        self.remote_tree.tag_configure('gone', foreground='#c62828')
        self.remote_tree.tag_configure('ahead', foreground='#2e7d32')
        self.remote_tree.tag_configure('behind', foreground='#e65100')
        self.remote_tree.tag_configure('remote_only', foreground='#9e9e9e')

    def setup_remotes_list_tab(self):
        remotes_frame = ttk.Frame(self.tab_remotes_list, padding="10")
        remotes_frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(remotes_frame)
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="Registered Remote Repositories", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        tree_container = ttk.Frame(remotes_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ("name", "url", "type")
        self.remotes_list_tree = ttk.Treeview(tree_container, columns=columns, show='headings')
        
        self.remotes_list_tree.heading("name", text="Name")
        self.remotes_list_tree.heading("url", text="URL")
        self.remotes_list_tree.heading("type", text="Type")

        self.remotes_list_tree.column("name", width=150)
        self.remotes_list_tree.column("url", width=500)
        self.remotes_list_tree.column("type", width=100, anchor=tk.CENTER)

        scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.remotes_list_tree.yview)
        self.remotes_list_tree.configure(yscroll=scrollbar.set)
        
        self.remotes_list_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _get_subprocess_kwargs(self):
        kwargs = {"stderr": subprocess.STDOUT, "text": True, "encoding": "utf-8", "errors": "replace"}
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

    def browse_dir(self):
        new_dir = filedialog.askdirectory(initialdir=self.cwd, title="Select Working Directory")
        if new_dir:
            self.change_dir(new_dir)

    def go_parent_dir(self):
        new_dir = os.path.dirname(self.cwd)
        if new_dir and new_dir != self.cwd:
            self.change_dir(new_dir)

    def change_dir(self, new_dir):
        try:
            os.chdir(new_dir)
            self.cwd = os.getcwd()
            self.cwd_var.set(self.cwd)
            self.repo_root = self.get_git_root()
            self.repo_var.set(self.repo_root)
            self.start_refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change directory:\n{e}")

    def start_refresh(self):
        self.refresh_branches_tab()
        self.refresh_status_tab()
        self.refresh_remote_tab()
        self.refresh_remotes_list_tab()

    def refresh_branches_tab(self):
        self.refresh_btn.config(state=tk.DISABLED)
        self.btn_browse.config(state=tk.DISABLED)
        self.btn_parent.config(state=tk.DISABLED)
        self.current_branch_label.config(text="Current Branch: Analyzing...", foreground="#e65100") # Deep Orange
        self.status_label.config(text="", foreground="black")
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

        # Check for dirty worktree
        status_raw = self.git_cmd(["status", "--porcelain"])
        is_dirty = bool(status_raw and status_raw.strip())

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
        self.root.after(0, self.store_and_apply_data, current_display, results, is_dirty)

    def store_and_apply_data(self, current_display, results, is_dirty):
        self.current_branch_label.config(text=current_display, foreground="black")
        
        if is_dirty:
            self.status_label.config(text="⚠️ Worktree Dirty (Uncommitted Changes)", foreground="#c62828") # Red-ish
        else:
            self.status_label.config(text="✓ Worktree Clean", foreground="#2e7d32") # Green-ish
            
        self.all_data = results
        self.apply_filters()
        self.refresh_btn.config(state=tk.NORMAL)
        self.btn_browse.config(state=tk.NORMAL)
        self.btn_parent.config(state=tk.NORMAL)

    def refresh_status_tab(self):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, "Loading git status...")
        self.status_text.config(state=tk.DISABLED)
        threading.Thread(target=self._refresh_status_bg, daemon=True).start()

    def _refresh_status_bg(self):
        # Use simple git status to get the verbose output and colors if we can? No, standard text output is fine.
        status_out = self.git_cmd(["status"])
        self.root.after(0, self._update_status_ui, status_out)

    def _update_status_ui(self, status_out):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        if status_out is not None:
            self.status_text.insert(tk.END, status_out)
        else:
            self.status_text.insert(tk.END, "Failed to execute 'git status'.")
        self.status_text.config(state=tk.DISABLED)

    def refresh_remote_tab(self):
        for item in self.remote_tree.get_children():
            self.remote_tree.delete(item)
        threading.Thread(target=self._refresh_remote_bg, daemon=True).start()

    def _refresh_remote_bg(self):
        results = []
        # 1. Get branch -vv for tracking info
        # Output format: * branch_name hash [upstream: ahead X, behind Y] commit_msg
        bv_raw = self.git_cmd(["branch", "-vv", "--color=never"])
        tracked_remotes = set()
        
        if bv_raw:
            import re
            for line in bv_raw.split('\n'):
                if not line.strip(): continue
                # Match: (optional *) branch_name hash [tracking_info] commit_msg
                # Tracking info pattern: [remote/branch: ahead X, behind Y]
                match = re.match(r'[* ]\s+(\S+)\s+\w+\s+(?:\[([^\]]+)\]\s+)?(.*)', line)
                if match:
                    b_name, tracking_raw, msg = match.groups()
                    status = "No Tracking"
                    upstream = ""
                    tags = ()
                    
                    if tracking_raw:
                        # tracking_raw can be "origin/main" or "origin/main: ahead 1" or "origin/main: gone"
                        if ':' in tracking_raw:
                            upstream, status_part = tracking_raw.split(':', 1)
                            status = status_part.strip()
                        else:
                            upstream = tracking_raw
                            status = "Synced"
                        
                        tracked_remotes.add(upstream)
                        if "gone" in status: tags = ('gone',)
                        elif "ahead" in status: tags = ('ahead',)
                        elif "behind" in status: tags = ('behind',)

                    results.append({"values": (b_name, upstream, status, msg), "tags": tags})

        # 2. Get remote branches (git branch -r) to find what's NOT tracked
        br_raw = self.git_cmd(["branch", "-r", "--color=never"])
        if br_raw:
            for line in br_raw.split('\n'):
                line = line.strip()
                if not line or " -> " in line: continue # Skip HEAD pointers
                r_name = line
                if r_name not in tracked_remotes:
                    # Get last commit message for this remote branch
                    r_msg = self.git_cmd(["log", "-1", "--format=%s", r_name]) or ""
                    results.append({"values": (f"({r_name})", r_name, "Remote Only", r_msg), "tags": ('remote_only',)})

        self.root.after(0, self._update_remote_ui, results)

    def _update_remote_ui(self, results):
        for res in results:
            self.remote_tree.insert("", tk.END, values=res["values"], tags=res["tags"])

    def fetch_all_bg(self):
        self.fetch_btn.config(state=tk.DISABLED, text="Fetching...")
        threading.Thread(target=self._fetch_all_worker, daemon=True).start()

    def _fetch_all_worker(self):
        self.git_call(["fetch", "--all"])
        self.root.after(0, self._fetch_complete)

    def _fetch_complete(self):
        self.fetch_btn.config(state=tk.NORMAL, text="Fetch All")
        self.start_refresh()

    def refresh_remotes_list_tab(self):
        for item in self.remotes_list_tree.get_children():
            self.remotes_list_tree.delete(item)
        threading.Thread(target=self._refresh_remotes_list_bg, daemon=True).start()

    def _refresh_remotes_list_bg(self):
        results = []
        rm_raw = self.git_cmd(["remote", "-v"])
        if rm_raw:
            for line in rm_raw.split('\n'):
                line = line.strip()
                if not line: continue
                # Example: github  git@github.com:TakashiSasaki/fido-uri.git (fetch)
                parts = line.split()
                if len(parts) >= 3:
                    name = parts[0]
                    url = parts[1]
                    # remove parentheses around type
                    rtype = parts[2].strip("()") if len(parts) > 2 else ""
                    results.append((name, url, rtype))
                elif len(parts) == 2: # Fallback if type is missing somehow
                    results.append((parts[0], parts[1], ""))

        self.root.after(0, self._update_remotes_list_ui, results)

    def _update_remotes_list_ui(self, results):
        for res in results:
            self.remotes_list_tree.insert("", tk.END, values=res)

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

def main():
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

if __name__ == "__main__":
    main()
