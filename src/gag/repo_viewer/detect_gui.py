import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import socket
import sys
import threading
import re
import platform
from . import app_config

import importlib.metadata

from .git_core import GitRepository

try:
    VERSION = importlib.metadata.version("gag-repo-viewer")
except importlib.metadata.PackageNotFoundError:
    VERSION = "dev"

LOCK_PORT = 52941


class BranchDetectorApp:
    def __init__(self, root):
        self.root = root
        self.root.title(f"Git Related Branch Detector v{VERSION}")
        self.root.geometry("1100x700")

        self.cwd = os.getcwd()
        self.repo = GitRepository(self.cwd)
        self.initial_filters = app_config.load_filters()

        try:
            icon_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app_icon.png")
            if os.path.exists(icon_path):
                img = tk.PhotoImage(file=icon_path)
                self.root.tk.call('wm', 'iconphoto', self.root._w, img)
        except Exception:
            pass

        self.filter_vars = {}
        self.all_data = []

        self.setup_ui()
        self.root.after(100, self.start_refresh)

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
        self.btn_terminal.pack(side=tk.LEFT, padx=(0, 5))

        self.btn_appdata = ttk.Button(cwd_frame, text="📂 App Data", command=self._open_app_data_dir)
        self.btn_appdata.pack(side=tk.LEFT)

        # Git Repo row
        repo_frame = ttk.Frame(path_frame)
        repo_frame.pack(fill=tk.X, pady=(2, 2))
        ttk.Label(repo_frame, text="Git Repo:").pack(side=tk.LEFT, padx=(0, 5))

        self.repo_text = tk.Text(repo_frame, height=1, font=("Segoe UI", 9), padx=5, pady=2,
                                bg=self.root.cget('bg'), relief=tk.FLAT, state=tk.DISABLED)
        self.repo_text.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.repo_text.tag_configure("highlight", foreground="#1565c0", font=("Segoe UI", 9, "bold"))

        # Current Branch & Status row
        branch_info_frame = ttk.Frame(path_frame)
        branch_info_frame.pack(fill=tk.X, pady=(2, 2))

        ttk.Label(branch_info_frame, text="Current Branch:").pack(side=tk.LEFT, padx=(0, 5))
        self.current_branch_label = ttk.Label(branch_info_frame, text="Analyzing...", font=("Segoe UI", 9, "bold"))
        self.current_branch_label.pack(side=tk.LEFT, padx=(0, 15))

        ttk.Label(branch_info_frame, text="Worktree:").pack(side=tk.LEFT, padx=(0, 5))
        self.status_label = ttk.Label(branch_info_frame, text="", font=("Segoe UI", 9))
        self.status_label.pack(side=tk.LEFT)

        # Main notebook
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 10))

        # Tabs
        self.tab_branches = ttk.Frame(self.notebook)
        self.tab_status = ttk.Frame(self.notebook)
        self.tab_remote = ttk.Frame(self.notebook)
        self.tab_remotes_list = ttk.Frame(self.notebook)
        self.tab_submodules = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_branches, text="Related Branches")
        self.notebook.add(self.tab_status, text="Git Status")
        self.notebook.add(self.tab_remote, text="Remote Tracking")
        self.notebook.add(self.tab_remotes_list, text="Remotes List")
        self.notebook.add(self.tab_submodules, text="Submodules")

        self.setup_branches_tab()
        self.setup_status_tab()
        self.setup_remote_tab()
        self.setup_remotes_list_tab()
        self.setup_submodules_tab()

    def setup_branches_tab(self):
        main_frame = ttk.Frame(self.tab_branches, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        filter_frame = ttk.LabelFrame(header_frame, text="Filters", padding="5")
        filter_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        row1 = ttk.Frame(filter_frame)
        row1.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))
        row2 = ttk.Frame(filter_frame)
        row2.pack(side=tk.TOP, fill=tk.X, pady=(2, 2))

        def create_filter_group(parent, group_name, options):
            group = ttk.Frame(parent)
            group.pack(side=tk.LEFT, padx=(0, 15))
            ttk.Label(group, text=group_name + ":", font=("Segoe UI", 9, "bold"), width=12).pack(side=tk.LEFT, padx=(5, 5))
            for opt in options:
                # Load persisted state or default to True
                val = self.initial_filters.get(opt, True)
                var = tk.BooleanVar(value=val)
                self.filter_vars[opt] = var
                cb = ttk.Checkbutton(group, text=opt, variable=var, command=self.apply_filters)
                cb.pack(side=tk.LEFT)

        create_filter_group(row1, "Type", ["Local", "Remote", "Reflog"])
        create_filter_group(row1, "Shared Node", ["Shared", "Unique"])
        create_filter_group(row2, "Relationship", ["Current", "Tip (Identical)", "Tip (Ahead)", "Ancestor", "Diverged", "Independent"])

        btn_frame = ttk.Frame(header_frame)
        btn_frame.pack(side=tk.RIGHT, fill=tk.Y)
        self.refresh_btn = ttk.Button(btn_frame, text="Refresh", command=self.start_refresh)
        self.refresh_btn.pack(side=tk.TOP, pady=2)

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

        self.tree.bind("<Button-3>", lambda e: self._show_tree_context_menu(e, self.tree, "branch"))

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

        self.remote_tree.bind("<Button-3>", lambda e: self._show_tree_context_menu(e, self.remote_tree, "remote"))

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
        self.remotes_data = []
        self.remotes_list_text.bind("<Button-1>", self._on_remote_list_click)

        controls_frame = ttk.Frame(remotes_frame)
        controls_frame.pack(fill=tk.X, pady=(10, 0))
        ttk.Label(controls_frame, text="Rename Selected Remote to:").pack(side=tk.LEFT, padx=(0, 5))
        self.new_remote_name_var = tk.StringVar()
        ttk.Entry(controls_frame, textvariable=self.new_remote_name_var, width=30).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(controls_frame, text="Rename", command=self.rename_selected_remote).pack(side=tk.LEFT)

    def setup_submodules_tab(self):
        sm_frame = ttk.Frame(self.tab_submodules, padding="10")
        sm_frame.pack(fill=tk.BOTH, expand=True)

        header = ttk.Frame(sm_frame)
        header.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(header, text="Git Submodule Overview", font=("Segoe UI", 10, "bold")).pack(side=tk.LEFT)

        btn_group = ttk.Frame(header)
        btn_group.pack(side=tk.RIGHT)
        self.sm_update_btn = ttk.Button(btn_group, text="Update", command=lambda: self.submodule_action("update"))
        self.sm_update_btn.pack(side=tk.LEFT, padx=2)
        self.sm_update_remote_btn = ttk.Button(btn_group, text="Update (Remote)", command=lambda: self.submodule_action("update_remote"))
        self.sm_update_remote_btn.pack(side=tk.LEFT, padx=2)
        self.sm_sync_btn = ttk.Button(btn_group, text="Sync", command=lambda: self.submodule_action("sync"))
        self.sm_sync_btn.pack(side=tk.LEFT, padx=2)
        self.sm_fetch_btn = ttk.Button(btn_group, text="Fetch", command=lambda: self.submodule_action("fetch"))
        self.sm_fetch_btn.pack(side=tk.LEFT, padx=2)
        self.sm_open_btn = ttk.Button(btn_group, text="Open", command=self.submodule_open)
        self.sm_open_btn.pack(side=tk.LEFT, padx=2)

        tree_container = ttk.Frame(sm_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)

        columns = ("path", "name", "branch", "status", "upstream", "recorded", "actual")
        self.sm_tree = ttk.Treeview(tree_container, columns=columns, show='headings')
        self.sm_tree.heading("path", text="Path")
        self.sm_tree.heading("name", text="Name")
        self.sm_tree.heading("branch", text="In-Submodule Branch")
        self.sm_tree.heading("status", text="Sync Status")
        self.sm_tree.heading("upstream", text="Upstream Status")
        self.sm_tree.heading("recorded", text="Recorded Commit")
        self.sm_tree.heading("actual", text="Actual Commit")
        self.sm_tree.column("path", width=150)
        self.sm_tree.column("name", width=100)
        self.sm_tree.column("branch", width=150)
        self.sm_tree.column("status", width=120)
        self.sm_tree.column("upstream", width=150)
        self.sm_tree.column("recorded", width=100)
        self.sm_tree.column("actual", width=100)

        v_scroll = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.sm_tree.yview)
        h_scroll = ttk.Scrollbar(sm_frame, orient=tk.HORIZONTAL, command=self.sm_tree.xview)
        self.sm_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        self.sm_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(fill=tk.X)

        self.sm_tree.tag_configure('dirty', foreground='#c62828')
        self.sm_tree.tag_configure('behind', foreground='#e65100')
        self.sm_tree.tag_configure('clean', foreground='#2e7d32')
        self.sm_tree.tag_configure('detached', foreground='#9e9e9e')

        self.sm_tree.bind("<Button-3>", lambda e: self._show_tree_context_menu(e, self.sm_tree, "submodule"))

    # ------------------------------------------------------------------
    # Navigation / directory change
    # ------------------------------------------------------------------

    def browse_dir(self):
        new_dir = filedialog.askdirectory(initialdir=self.cwd)
        if new_dir:
            self.change_dir(new_dir)

    def go_parent_dir(self):
        parent = os.path.dirname(self.cwd)
        if parent and parent != self.cwd:
            self.change_dir(parent)

    def change_dir(self, new_dir):
        try:
            os.chdir(new_dir)
            self.cwd = os.getcwd()
            self.repo = GitRepository(self.cwd)
            self.start_refresh()
        except Exception as e:
            messagebox.showerror("Error", f"Failed:\n{e}")

    def open_terminal(self):
        try:
            self.repo.open_terminal(self.cwd)
        except RuntimeError as e:
            messagebox.showerror("Error", str(e))

    # ------------------------------------------------------------------
    # Path display helpers
    # ------------------------------------------------------------------

    def update_path_displays(self):
        proj_name = os.path.basename(self.repo.repo_root) if self.repo.repo_root and self.repo.repo_root != "Not a Git Repository" else None
        self._render_path_with_highlight(self.cwd_text, self.cwd, proj_name)
        self._render_path_with_highlight(self.repo_text, self.repo.repo_root, proj_name)

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

    # ------------------------------------------------------------------
    # Refresh orchestration
    # ------------------------------------------------------------------

    def start_refresh(self):
        self.update_path_displays()
        self.refresh_branches_tab()
        self.refresh_status_tab()
        self.refresh_remote_tab()
        self.refresh_remotes_list_tab()
        self.refresh_submodules_tab()

    # ------------------------------------------------------------------
    # Branches tab
    # ------------------------------------------------------------------

    def refresh_branches_tab(self):
        self.refresh_btn.config(state=tk.DISABLED)
        self.btn_browse.config(state=tk.DISABLED)
        self.btn_parent.config(state=tk.DISABLED)
        self.btn_terminal.config(state=tk.DISABLED)
        self.current_branch_label.config(text="Current Branch: Analyzing...", foreground="#e65100")
        self.status_label.config(text="")
        for item in self.tree.get_children():
            self.tree.delete(item)
        threading.Thread(target=self._refresh_branches_bg, daemon=True).start()

    def _refresh_branches_bg(self):
        results, current, is_dirty = self.repo.fetch_branches()
        self.root.after(0, self._update_branches_ui, results, current, is_dirty)

    def _update_branches_ui(self, results, current_name, is_dirty):
        self.current_branch_label.config(text=f"{current_name}", foreground="black")
        if is_dirty:
            self.status_label.config(text="⚠️ Dirty", foreground="#c62828")
        else:
            self.status_label.config(text="✓ Clean", foreground="#2e7d32")
        self.all_data = results
        self.apply_filters()
        self.refresh_btn.config(state=tk.NORMAL)
        self.btn_browse.config(state=tk.NORMAL)
        self.btn_parent.config(state=tk.NORMAL)
        self.btn_terminal.config(state=tk.NORMAL)

    def apply_filters(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Save filter state to config
        current_state = {k: v.get() for k, v in self.filter_vars.items()}
        app_config.save_filters(current_state)

        for res in self.all_data:
            _, v_type, v_shared, v_rel, _ = res["values"]
            if v_rel == "Current":
                continue
            if v_type in self.filter_vars and not self.filter_vars[v_type].get():
                continue
            if v_shared in self.filter_vars and not self.filter_vars[v_shared].get():
                continue
            if v_rel in self.filter_vars and not self.filter_vars[v_rel].get():
                continue
            self.tree.insert("", tk.END, values=res["values"], tags=res["tags"])

    # ------------------------------------------------------------------
    # Status tab
    # ------------------------------------------------------------------

    def refresh_status_tab(self):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, "Loading...")
        self.status_text.config(state=tk.DISABLED)
        threading.Thread(target=self._refresh_status_bg, daemon=True).start()

    def _refresh_status_bg(self):
        out = self.repo.fetch_status()
        self.root.after(0, lambda: self._update_status_ui(out))

    def _update_status_ui(self, out):
        self.status_text.config(state=tk.NORMAL)
        self.status_text.delete(1.0, tk.END)
        self.status_text.insert(tk.END, out if out else "Failed")
        self.status_text.config(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # Remote Tracking tab
    # ------------------------------------------------------------------

    def refresh_remote_tab(self):
        for item in self.remote_tree.get_children():
            self.remote_tree.delete(item)
        threading.Thread(target=self._refresh_remote_bg, daemon=True).start()

    def _refresh_remote_bg(self):
        results = self.repo.fetch_remote_tracking()
        self.root.after(0, lambda: self._update_remote_ui(results))

    def _update_remote_ui(self, results):
        for res in results:
            self.remote_tree.insert("", tk.END, values=res["values"], tags=res["tags"])

    def fetch_all_bg(self):
        self.fetch_btn.config(state=tk.DISABLED, text="Fetching...")
        threading.Thread(target=self._fetch_all_worker, daemon=True).start()

    def _fetch_all_worker(self):
        self.repo.git_call(["fetch", "--all"])
        self.root.after(0, self._fetch_complete)

    def _fetch_complete(self):
        self.fetch_btn.config(state=tk.NORMAL, text="Fetch All")
        self.start_refresh()

    # ------------------------------------------------------------------
    # Remotes List tab
    # ------------------------------------------------------------------

    def refresh_remotes_list_tab(self):
        threading.Thread(target=self._refresh_remotes_list_bg, daemon=True).start()

    def _refresh_remotes_list_bg(self):
        results = self.repo.fetch_remotes_list()
        self.root.after(0, lambda: self._update_remotes_list_ui(results))

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
        if not new_name or old_name == new_name:
            return
        if self.repo.rename_remote(old_name, new_name):
            self.new_remote_name_var.set("")
            self.start_refresh()
        else:
            messagebox.showerror("Git Error", "Failed to rename remote.")

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
            else:
                self._update_remotes_selection_ui()
        self.remotes_list_text.config(state=tk.DISABLED)

    # ------------------------------------------------------------------
    # Submodules tab
    # ------------------------------------------------------------------

    def refresh_submodules_tab(self):
        for item in self.sm_tree.get_children():
            self.sm_tree.delete(item)
        threading.Thread(target=self._refresh_submodules_bg, daemon=True).start()

    def _refresh_submodules_bg(self):
        results = self.repo.fetch_submodules()
        self.root.after(0, self._update_submodules_ui, results)

    def _update_submodules_ui(self, results):
        for res in results:
            self.sm_tree.insert("", tk.END, values=res["values"], tags=res["tags"])

    def submodule_action(self, action_type):
        selection = self.sm_tree.selection()
        paths = [self.sm_tree.item(item)['values'][0] for item in selection]

        def worker():
            if action_type == "update":
                self.repo.git_call(["submodule", "update", "--init", "--recursive"] + paths)
            elif action_type == "update_remote":
                self.repo.git_call(["submodule", "update", "--remote", "--recursive"] + paths)
            elif action_type == "sync":
                self.repo.git_call(["submodule", "sync", "--recursive"] + paths)
            elif action_type == "fetch":
                if paths:
                    for p in paths:
                        import subprocess
                        sm_path = os.path.join(self.repo.repo_root, p)
                        subprocess.run(["git", "fetch"], cwd=sm_path, **self.repo._get_subprocess_kwargs())
                else:
                    self.repo.git_call(["submodule", "foreach", "--recursive", "git fetch"])
            self.root.after(0, self.start_refresh)

        threading.Thread(target=worker, daemon=True).start()

    def submodule_open(self):
        selection = self.sm_tree.selection()
        if not selection:
            return
        path = self.sm_tree.item(selection[0])['values'][0]
        sm_abs_path = os.path.join(self.repo.repo_root, path)
        if os.path.isdir(sm_abs_path):
            self.change_dir(sm_abs_path)

    # ------------------------------------------------------------------
    # Context menus and clipboard
    # ------------------------------------------------------------------

    def _show_tree_context_menu(self, event, tree, menu_type):
        item = tree.identify_row(event.y)
        if not item:
            return
        tree.selection_set(item)
        values = tree.item(item)['values']
        menu = tk.Menu(self.root, tearoff=0)

        if menu_type == "branch":
            full_name = str(values[0])
            menu.add_command(label=f"Copy Branch Name: {full_name}", command=lambda: self.copy_to_clip(full_name))
            if full_name.startswith("remotes/"):
                parts = full_name.split('/')
                if len(parts) >= 3:
                    remote_name = parts[1]
                    inner_branch = "/".join(parts[2:])
                    menu.add_separator()
                    menu.add_command(label=f"Copy Remote: {remote_name}", command=lambda: self.copy_to_clip(remote_name))
                    menu.add_command(label=f"Copy Branch: {inner_branch}", command=lambda: self.copy_to_clip(inner_branch))

        elif menu_type == "remote":
            local_name = str(values[0])
            upstream = str(values[1]) if values[1] else ""
            menu.add_command(label=f"Copy Local Name: {local_name}", command=lambda: self.copy_to_clip(local_name))
            if upstream:
                menu.add_separator()
                menu.add_command(label=f"Copy Upstream (Full): {upstream}", command=lambda: self.copy_to_clip(upstream))
                if '/' in upstream:
                    parts = upstream.split('/', 1)
                    menu.add_command(label=f"Copy Remote: {parts[0]}", command=lambda: self.copy_to_clip(parts[0]))
                    menu.add_command(label=f"Copy Branch: {parts[1]}", command=lambda: self.copy_to_clip(parts[1]))

        elif menu_type == "submodule":
            menu.add_command(label=f"Copy Path: {values[0]}", command=lambda: self.copy_to_clip(values[0]))
            menu.add_command(label=f"Copy Name: {values[1]}", command=lambda: self.copy_to_clip(values[1]))
            menu.add_command(label=f"Copy Actual Hash: {values[6]}", command=lambda: self.copy_to_clip(values[6]))

        menu.post(event.x_root, event.y_root)

    def copy_to_clip(self, text):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()

    def _open_app_data_dir(self):
        import subprocess, os
        path = str(app_config.get_config_dir())
        try:
            if os.name == "nt":
                subprocess.Popen(["explorer", path])
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open app data dir: {e}")


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
        messagebox.showerror('Instance Error', 'Already running.')
        sys.exit(1)
    root = tk.Tk()
    BranchDetectorApp(root)
    try:
        root.mainloop()
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
