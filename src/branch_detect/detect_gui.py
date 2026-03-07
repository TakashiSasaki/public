import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import subprocess
import os
import socket
import sys
import threading
import platform
import re

VERSION = "0.2.19"
LOCK_PORT = 52941

class BranchDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Git Related Branch Detector v{VERSION}")
        self.root.geometry("1100x700")

        self.cwd = os.getcwd()
        self.repo_root = self.get_git_root()

        self.filter_vars = {}
        self.all_data = []

        self.setup_ui()
        self.start_refresh()

    def get_git_root(self):
        try:
            kwargs = self._get_subprocess_kwargs()
            result = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                                    capture_output=True, check=True, **kwargs)
            return result.stdout.strip()
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
        
        self.cwd_text = tk.Text(cwd_frame, height=1, font=("Segoe UI", 9), padx=5, pady=2,
                               bg=self.root.cget('bg'), relief=tk.FLAT, state=tk.DISABLED)
        self.cwd_text.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        self.cwd_text.tag_configure("highlight", foreground="#1565c0", font=("Segoe UI", 9, "bold"))

        self.btn_browse = ttk.Button(cwd_frame, text="Browse...", command=self.browse_dir)
        self.btn_browse.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_parent = ttk.Button(cwd_frame, text="⬆ Parent Dir", command=self.go_parent_dir)
        self.btn_parent.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_terminal = ttk.Button(cwd_frame, text="💻 Terminal", command=self.open_terminal)
        self.btn_terminal.pack(side=tk.LEFT)

        # Git Repo row
        repo_frame = ttk.Frame(path_frame)
        repo_frame.pack(fill=tk.X, pady=(2, 2))
        ttk.Label(repo_frame, text="Git Repo:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.repo_text = tk.Text(repo_frame, height=1, font=("Segoe UI", 9), padx=5, pady=2,
                                bg=self.root.cget('bg'), relief=tk.FLAT, state=tk.DISABLED)
        self.repo_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.repo_text.tag_configure("highlight", foreground="#1565c0", font=("Segoe UI", 9, "bold"))

        # Main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))

        # Tabs
        self.tab_branches = ttk.Frame(self.notebook)
        self.tab_status = ttk.Frame(self.notebook)
        self.tab_remote = ttk.Frame(self.notebook)
        self.tab_remotes_list = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_branches, text="Related Branches")
        self.notebook.add(self.tab_status, text="Git Status")
        self.notebook.add(self.tab_remote, text="Remote Tracking")
        self.notebook.add(self.tab_remotes_list, text="Remotes List")

        self.setup_branches_tab()
        self.setup_status_tab()
        self.setup_remote_tab()
        self.setup_remotes_list_tab()

    def setup_branches_tab(self):
        main_frame = ttk.Frame(self.tab_branches, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        filter_frame = ttk.LabelFrame(header_frame, text="Filters", padding="5")
        filter_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        filter_groups = {
            "Type": ["Local", "Remote", "Reflog"],
            "Shared Node": ["Shared", "Unique"],
            "Relationship": ["Current", "Tip (Identical)", "Ancestor", "Independent"]
        }

        for group_name, options in filter_groups.items():
            group = ttk.Frame(filter_frame)
            group.pack(side=tk.LEFT, padx=(0, 15))
            ttk.Label(group, text=group_name + ":", font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT, padx=(0, 5))
            
            for opt in options:
                var = tk.BooleanVar(value=True)
                self.filter_vars[opt] = var
                cb = ttk.Checkbutton(group, text=opt, variable=var, command=self.apply_filters)
                cb.pack(side=tk.LEFT)

        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y)

        self.refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self.start_refresh)
        self.refresh_btn.pack(side=tk.TOP, pady=2)

        info_frame = ttk.Frame(main_frame)
        info_frame.pack(fill=tk.X, pady=(0, 5))
        self.current_branch_label = ttk.Label(info_frame, text="Current Branch: Unknown", font=("Segoe UI", 10, "bold"))
        self.current_branch_label.pack(side=tk.LEFT)
        self.status_label = ttk.Label(info_frame, text="", font=("Segoe UI", 9))
        self.status_label.pack(side=tk.RIGHT)

        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("branch", "type", "shared", "relationship", "msg")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')
        self.tree.heading("branch", text="Branch")
        self.tree.heading("type", text="Type")
        self.tree.heading("shared", text="Shared Node")
        self.tree.heading("relationship", text="Relationship")
        self.tree.heading("msg", text="Latest Commit Message")

        self.tree.column("branch", width=250)
        self.tree.column("type", width=80)
        self.tree.column("shared", width=80)
        self.tree.column("relationship", width=120)
        self.tree.column("msg", width=400)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.tag_configure('current', font=('Segoe UI', 9, 'bold'), background='#e3f2fd')
        self.tree.tag_configure('tip', foreground='#2e7d32')
        self.tree.tag_configure('ancestor', foreground='#1565c0')
        self.tree.tag_configure('independent', foreground='#c62828')
        self.tree.tag_configure('reflog', foreground='#9e9e9e')

    def setup_status_tab(self):
        status_frame = ttk.Frame(self.tab_status, padding="10")
        status_frame.pack(fill=tk.BOTH, expand=True)

        self.status_text = tk.Text(status_frame, wrap=tk.WORD, font=("Consolas", 10))
        h_scroll = ttk.Scrollbar(status_frame, orient=tk.HORIZONTAL, command=self.status_text.xview)
        v_scroll = ttk.Scrollbar(status_frame, orient=tk.VERTICAL, command=self.status_text.yview)
        self.status_text.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        self.status_text.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        status_frame.grid_rowconfigure(0, weight=1)
        status_frame.grid_columnconfigure(0, weight=1)
        self.status_text.config(state=tk.DISABLED)

        btn_frame = ttk.Frame(status_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, sticky=tk.E, pady=(10, 0))
        ttk.Button(btn_frame, text="Refresh Status", command=self.refresh_status_tab).pack(side=tk.RIGHT)

    def setup_remote_tab(self):
        remote_frame = ttk.Frame(self.tab_remote, padding="10")
        remote_frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(remote_frame)
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="Local & Remote Synchronization Status", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)
        self.fetch_btn = ttk.Button(header, text="Fetch All", command=self.fetch_all_bg)
        self.fetch_btn.pack(side=tk.RIGHT)

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

        text_container = ttk.Frame(remotes_frame)
        text_container.pack(fill=tk.BOTH, expand=True)

        self.remotes_list_text = tk.Text(text_container, font=("Segoe UI", 9), padx=5, pady=5,
                                        tabs=(150, tk.LEFT, 700, tk.LEFT), cursor="arrow",
                                        state=tk.DISABLED, undo=False)
        self.remotes_list_text.tag_configure("header", font=("Segoe UI", 9, "bold"))
        self.remotes_list_text.tag_configure("highlight", foreground="#1565c0", font=("Segoe UI", 9, "bold"))
        self.remotes_list_text.tag_configure("selection", background="#0078d7", foreground="white")

        scrollbar = ttk.Scrollbar(text_container, orient=tk.VERTICAL, command=self.remotes_list_text.yview)
        self.remotes_list_text.configure(yscroll=scrollbar.set)
        self.remotes_list_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.selected_remote_index = None
        self.remotes_data = [] # (name, url, type)
        self.remotes_list_text.bind("<Button-1>", self._on_remote_list_click)

        controls_frame = ttk.Frame(remotes_frame)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(controls_frame, text="Rename Selected Remote to:").pack(side=tk.LEFT, padx=(0, 5))
        self.new_remote_name_var = tk.StringVar()
        ttk.Entry(controls_frame, textvariable=self.new_remote_name_var, width=30).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="Rename", command=self.rename_selected_remote).pack(side=tk.LEFT)

    def _on_remote_list_click(self, event):
        index = self.remotes_list_text.index(f"@{event.x},{event.y}")
        line_num = int(index.split('.')[0])
        data_index = line_num - 2
        if 0 <= data_index < len(self.remotes_data):
            self.selected_remote_index = data_index
            self.new_remote_name_var.set(self.remotes_data[data_index][0])
            self._update_remotes_selection_ui()

    def _update_remotes_selection_ui(self):
        self.remotes_list_text.tag_remove("selection", "1.0", tk.END)
        if self.selected_remote_index is not None:
            line_num = self.selected_remote_index + 2
            self.remotes_list_text.tag_add("selection", f"{line_num}.0", f"{line_num}.end+1c")

    def rename_selected_remote(self):
        if self.selected_remote_index is None:
            messagebox.showwarning("Warning", "Please select a remote.")
            return
        old_name = self.remotes_data[self.selected_remote_index][0]
        new_name = self.new_remote_name_var.get().strip()
        if not new_name or old_name == new_name: return
        try:
            kwargs = self._get_subprocess_kwargs()
            kwargs['stdout'] = subprocess.PIPE
            subprocess.run(["git", "remote", "rename", old_name, new_name], check=True, **kwargs)
            self.new_remote_name_var.set("")
            self.start_refresh()
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Git Error", f"Failed:\n{e.output}")

    def browse_dir(self):
        new_dir = filedialog.askdirectory(initialdir=self.cwd)
        if new_dir: self.change_dir(new_dir)

    def go_parent_dir(self):
        parent = os.path.dirname(self.cwd)
        if parent and parent != self.cwd: self.change_dir(parent)

    def change_dir(self, new_dir):
        try:
            os.chdir(new_dir)
            self.cwd = os.getcwd()
            self.repo_root = self.get_git_root()
            self.start_refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Failed:\n{e}")

    def open_terminal(self):
        try:
            if os.name == 'nt':
                try: subprocess.Popen(["wt.exe", "-d", self.cwd])
                except FileNotFoundError: subprocess.Popen(["powershell.exe"], cwd=self.cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:
                if platform.system() == 'Darwin': subprocess.Popen(['open', '-a', 'Terminal', self.cwd])
                else: subprocess.Popen(['x-terminal-emulator'], cwd=self.cwd)
        except Exception as e:
            messagebox.showerror("Error", f"Failed:\n{e}")

    def update_path_displays(self):
        proj_name = os.path.basename(self.repo_root) if self.repo_root and self.repo_root != "Not a Git Repository" else None
        self._render_path_with_highlight(self.cwd_text, self.cwd, proj_name)
        self._render_path_with_highlight(self.repo_text, self.repo_root, proj_name)

    def _render_path_with_highlight(self, text_widget, path_str, highlight_str):
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        if not path_str:
            text_widget.config(state=tk.DISABLED)
            return
        text_widget.insert(tk.END, path_str)
        if highlight_str:
            for m in re.finditer(re.escape(highlight_str), path_str):
                text_widget.tag_add("highlight", f"1.{m.start()}", f"1.{m.end()}")
        text_widget.config(state=tk.DISABLED)

    def start_refresh(self):
        self.update_path_displays()
        self.refresh_branches_tab()
        self.refresh_status_tab()
        self.refresh_remote_tab()
        self.refresh_remotes_list_tab()

    def refresh_branches_tab(self):
        self.refresh_btn.config(state=tk.DISABLED)
        self.btn_browse.config(state=tk.DISABLED)
        self.btn_parent.config(state=tk.DISABLED)
        self.btn_terminal.config(state=tk.DISABLED)
        self.current_branch_label.config(text="Current Branch: Analyzing...", foreground="#e65100")
        self.status_label.config(text="")
        for item in self.tree.get_children(): self.tree.delete(item)
        threading.Thread(target=self._refresh_branches_bg, daemon=True).start()

    def _refresh_branches_bg(self):
        if self.repo_root == "Not a Git Repository":
            self.root.after(0, self._update_branches_ui, [], "Unknown", False)
            return

        is_dirty = bool(self.git_cmd(["status", "--porcelain"]))
        current = self.git_cmd(["branch", "--show-current"])
        if not current:
            # Maybe it's a detached HEAD, try to get a hash or short name
            current = self.git_cmd(["rev-parse", "--short", "HEAD"]) or "Unknown"

        raw_refs = self.git_cmd(["for-each-ref", "--format=%(refname:short)|%(objectname)"])
        reflog_raw = self.git_cmd(["log", "-g", "--all", "--format=%H %gd %s"])
        
        # Track which hashes we've already matched to a named branch
        named_hashes = {} # hash -> list of names
        if raw_refs:
            for line in raw_refs.split('\n'):
                if not line.strip(): continue
                b_name, b_hash = line.split('|')
                if b_hash not in named_hashes: named_hashes[b_hash] = []
                named_hashes[b_hash].append(b_name)

        current_hash = self.git_cmd(["rev-parse", "HEAD"])
        
        rel_cache = {}
        def get_relationship(c1, c2):
            if not c1 or not c2: return "Independent"
            if c1 == c2: return "Tip (Identical)"
            if (c1, c2) in rel_cache: return rel_cache[(c1, c2)]
            base = self.git_cmd(["merge-base", c1, c2])
            if base == c2: res = "Ancestor"
            else: res = "Independent"
            rel_cache[(c1, c2)] = res
            return res

        results = []
        seen_hashes = set()

        # 1. Process named references (Branches/Remotes)
        if raw_refs:
            for line in raw_refs.split('\n'):
                if not line.strip(): continue
                b_name, b_hash = line.split('|')
                
                b_type = "Remote" if b_name.startswith("origin/") or "/" in b_name else "Local"
                shared = "Shared" # Named branches are usually considered shared/tracked
                
                if b_name == current:
                    rel = "Current"
                    tags = ('current',)
                else:
                    rel = get_relationship(current_hash, b_hash)
                    if rel == "Tip (Identical)": tags = ('tip',)
                    elif rel == "Ancestor": tags = ('ancestor',)
                    else: tags = ('independent',)
                    
                msg = self.git_cmd(["log", "-1", "--format=%s", b_name])
                results.append({"values": (b_name, b_type, shared, rel, msg), "tags": tags})
                seen_hashes.add(b_hash)

        # 2. Process reflog entries (only those not already seen as branches, or all?)
        # Let's include unique hashes from reflog as "Reflog" type.
        if reflog_raw:
            for line in reflog_raw.split('\n'):
                if not line.strip(): continue
                parts = line.split(' ', 2)
                if len(parts) < 2: continue
                r_hash, r_selector = parts[0], parts[1]
                r_msg = parts[2] if len(parts) > 2 else ""

                if r_hash in seen_hashes: continue # Avoid noise if it's already a branch head

                rel = get_relationship(current_hash, r_hash)
                tags = ('reflog',)
                if rel == "Tip (Identical)": tags += ('tip',)
                elif rel == "Ancestor": tags += ('ancestor',)
                else: tags += ('independent',)

                results.append({"values": (r_selector, "Reflog", "Shared", rel, r_msg), "tags": tags})
                seen_hashes.add(r_hash)

        self.root.after(0, self._update_branches_ui, results, current, is_dirty)

    def _update_branches_ui(self, results, current_name, is_dirty):
        self.current_branch_label.config(text=f"Current Branch: {current_name}", foreground="black")
        if is_dirty: self.status_label.config(text="⚠️ Worktree Dirty", foreground="#c62828")
        else: self.status_label.config(text="✓ Worktree Clean", foreground="#2e7d32")
            
        self.all_data = results
        self.apply_filters()
        
        self.refresh_btn.config(state=tk.NORMAL)
        self.btn_browse.config(state=tk.NORMAL)
        self.btn_parent.config(state=tk.NORMAL)
        self.btn_terminal.config(state=tk.NORMAL)

    def refresh_status_tab(self):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, "Loading...")
        self.status_text.config(state=tk.DISABLED)
        threading.Thread(target=self._refresh_status_bg, daemon=True).start()

    def _refresh_status_bg(self):
        out = self.git_cmd(["status"])
        self.root.after(0, lambda: self._update_status_ui(out))

    def _update_status_ui(self, out):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, out if out else "Failed")
        self.status_text.config(state=tk.DISABLED)

    def refresh_remote_tab(self):
        for item in self.remote_tree.get_children(): self.remote_tree.delete(item)
        threading.Thread(target=self._refresh_remote_bg, daemon=True).start()

    def _refresh_remote_bg(self):
        results = []
        bv_raw = self.git_cmd(["branch", "-vv", "--color=never"])
        tracked = set()
        if bv_raw:
            for line in bv_raw.split('\n'):
                if not line.strip(): continue
                match = re.match(r'[* ]\s+(\S+)\s+\w+\s+(?:\[([^\]]+)\]\s+)?(.*)', line)
                if match:
                    b_name, track_raw, msg = match.groups()
                    status, up = "No Tracking", ""
                    tags = ()
                    if track_raw:
                        if ':' in track_raw: up, status = map(str.strip, track_raw.split(':', 1))
                        else: up, status = track_raw, "Synced"
                        tracked.add(up)
                        if "gone" in status: tags = ('gone',)
                        elif "ahead" in status: tags = ('ahead',)
                        elif "behind" in status: tags = ('behind',)
                    results.append({"values": (b_name, up, status, msg), "tags": tags})

        br_raw = self.git_cmd(["branch", "-r", "--color=never"])
        if br_raw:
            for line in br_raw.split('\n'):
                line = line.strip()
                if not line or " -> " in line: continue
                if line not in tracked:
                    msg = self.git_cmd(["log", "-1", "--format=%s", line]) or ""
                    results.append({"values": (f"({line})", line, "Remote Only", msg), "tags": ('remote_only',)})

        self.root.after(0, lambda: self._update_remote_ui(results))

    def _update_remote_ui(self, results):
        for res in results: self.remote_tree.insert("", tk.END, values=res["values"], tags=res["tags"])

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
        threading.Thread(target=self._refresh_remotes_list_bg, daemon=True).start()

    def _refresh_remotes_list_bg(self):
        results = []
        rm_raw = self.git_cmd(["remote", "-v"])
        if rm_raw:
            for line in rm_raw.split('\n'):
                parts = line.strip().split()
                if len(parts) >= 2:
                    rtype = parts[2].strip("()") if len(parts)>2 else ""
                    results.append((parts[0], parts[1], rtype))
        self.root.after(0, lambda: self._update_remotes_list_ui(results))

    def _update_remotes_list_ui(self, results):
        self.remotes_data = results
        self.remotes_list_text.config(state=tk.NORMAL)
        self.remotes_list_text.delete(1.0, tk.END)
        self.remotes_list_text.insert(tk.END, "Name\tURL\tType\n", "header")
        for rname, rurl, rtype in results:
            self.remotes_list_text.insert(tk.END, rname, "highlight")
            self.remotes_list_text.insert(tk.END, "\t")
            u_start = self.remotes_list_text.index("insert")
            self.remotes_list_text.insert(tk.END, rurl)
            if rname:
                for m in re.finditer(re.escape(rname), rurl):
                    l, c = map(int, u_start.split('.'))
                    self.remotes_list_text.tag_add("highlight", f"{l}.{c+m.start()}", f"{l}.{c+m.end()}")
            self.remotes_list_text.insert(tk.END, f"\t{rtype}\n")
        
        if self.selected_remote_index is not None:
            if self.selected_remote_index >= len(results):
                self.selected_remote_index = None
                self.new_remote_name_var.set("")
            else: self._update_remotes_selection_ui()
        self.remotes_list_text.config(state=tk.DISABLED)

    def apply_filters(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for res in self.all_data:
            if res["values"][3] == "Current":
                self.tree.insert("", tk.END, values=res["values"], tags=res["tags"])
                break
        for res in self.all_data:
            _, v_type, v_shared, v_rel, _ = res["values"]
            if v_rel == "Current": continue
            if v_type in self.filter_vars and not self.filter_vars[v_type].get(): continue
            if v_shared in self.filter_vars and not self.filter_vars[v_shared].get(): continue
            if v_rel in self.filter_vars and not self.filter_vars[v_rel].get(): continue
            self.tree.insert("", tk.END, values=res["values"], tags=res["tags"])

    def git_cmd(self, args):
        kwargs = self._get_subprocess_kwargs()
        try:
            return subprocess.run(["git"] + args, capture_output=True, check=True, **kwargs).stdout.strip()
        except Exception: return ""

    def git_call(self, args):
        kwargs = self._get_subprocess_kwargs()
        try: return subprocess.run(["git"] + args, capture_output=True, check=True, **kwargs).returncode == 0
        except Exception: return False

    def _get_subprocess_kwargs(self):
        kwargs = {"text": True, "encoding": "utf-8", "errors": "replace"}
        if os.name == 'nt':
            si = subprocess.STARTUPINFO()
            si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            kwargs["startupinfo"] = si
        return kwargs

def ensure_single_instance():
    try:
        global lock_socket
        lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        lock_socket.bind(('127.0.0.1', LOCK_PORT))
    except socket.error: return False
    return True

def main():
    if not ensure_single_instance():
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror('Instance Error', 'Already running.')
        sys.exit(1)
    root = tk.Tk()
    BranchDetectorApp(root)
    try: root.mainloop()
    except KeyboardInterrupt: sys.exit(0)

if __name__ == "__main__":
    main()
