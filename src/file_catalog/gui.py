from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, ttk
import sqlite3

from . import db, service
from .filetime import filetime_to_iso8601
from .paths import resolve_desktop_path

VISIBLE_COLUMNS_SETTING_KEY = "ui.visible_columns"
COLUMN_WIDTHS_SETTING_KEY = "ui.column_widths"


class DesktopSearchApp:
    def __init__(self, root: tk.Tk, conn: sqlite3.Connection) -> None:
        self.root = root
        self.conn = conn
        self.root.title("Desktop Seiri")
        self.root.geometry("1100x650")

        self.query_var = tk.StringVar()
        self.scan_root_var = tk.StringVar(value=str(resolve_desktop_path()))
        self.type_var = tk.StringVar(value="all")
        self.status_var = tk.StringVar(value="Ready")
        self.page_size = 200
        self.current_page = 0
        self.total_rows = 0
        self.columns = (
            "item_type",
            "name",
            "root",
            "path",
            "target",
            "modified_filetime",
            "permissions",
            "size_bytes",
            "folder_total_size_bytes",
            "first_seen_filetime",
            "last_seen_filetime",
        )
        self.column_headings = {
            "item_type": "Type",
            "name": "Name",
            "root": "Root",
            "path": "Path",
            "target": "Target",
            "modified_filetime": "Modified (UTC)",
            "permissions": "Perms",
            "size_bytes": "File Size",
            "folder_total_size_bytes": "Folder Size",
            "first_seen_filetime": "First Seen (UTC)",
            "last_seen_filetime": "Last Seen (UTC)",
        }
        self.column_widths = {
            "item_type": 80,
            "name": 220,
            "root": 150,
            "path": 360,
            "target": 360,
            "modified_filetime": 180,
            "permissions": 80,
            "size_bytes": 100,
            "folder_total_size_bytes": 100,
            "first_seen_filetime": 180,
            "last_seen_filetime": 180,
        }
        self.column_visibility: dict[str, tk.BooleanVar] = {}
        self._visible_column_defaults: dict[str, bool] = {column: True for column in self.columns}

        self._load_ui_preferences()

        self._build_ui()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self.perform_search()

    def _build_ui(self) -> None:
        controls = ttk.Frame(self.root, padding=12)
        controls.pack(fill=tk.X)

        ttk.Label(controls, text="Scan Root").pack(side=tk.LEFT)
        scan_root_entry = ttk.Entry(controls, textvariable=self.scan_root_var, width=42)
        scan_root_entry.pack(side=tk.LEFT, padx=(8, 8))
        ttk.Button(controls, text="Browse...", command=self.browse_scan_root).pack(
            side=tk.LEFT, padx=(0, 12)
        )

        ttk.Label(controls, text="Search").pack(side=tk.LEFT)
        search_entry = ttk.Entry(controls, textvariable=self.query_var, width=28)
        search_entry.pack(side=tk.LEFT, padx=(8, 12))
        search_entry.bind("<Return>", lambda _e: self.perform_search())

        ttk.Label(controls, text="Type").pack(side=tk.LEFT)
        type_box = ttk.Combobox(
            controls,
            textvariable=self.type_var,
            values=["all", "file", "folder"],
            state="readonly",
            width=10,
        )
        type_box.pack(side=tk.LEFT, padx=(8, 12))
        type_box.bind("<<ComboboxSelected>>", lambda _e: self.perform_search())

        ttk.Button(controls, text="Search", command=self.perform_search).pack(side=tk.LEFT)
        ttk.Button(controls, text="Start Scan", command=self.refresh_inventory).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        ttk.Button(controls, text="Open Data Folder", command=self.open_data_folder).pack(
            side=tk.LEFT, padx=(8, 0)
        )

        column_controls = ttk.Frame(self.root, padding=(12, 0, 12, 8))
        column_controls.pack(fill=tk.X)
        ttk.Label(column_controls, text="Visible Columns").pack(side=tk.LEFT, padx=(0, 8))
        for column in self.columns:
            var = tk.BooleanVar(value=self._visible_column_defaults.get(column, True))
            self.column_visibility[column] = var
            ttk.Checkbutton(
                column_controls,
                text=self.column_headings[column],
                variable=var,
                command=lambda c=column: self.toggle_column(c),
            ).pack(side=tk.LEFT, padx=(0, 6))

        tree_frame = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        tree_frame.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=self.column_headings[col])
            self.tree.column(col, width=self.column_widths[col], anchor=tk.W)
        self._apply_display_columns()

        y_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        x_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)
        self.tree.bind("<ButtonRelease-1>", self._on_tree_mouse_release, add="+")

        pager = ttk.Frame(self.root, padding=(12, 0, 12, 6))
        pager.pack(fill=tk.X)
        ttk.Button(pager, text="Next", command=self.next_page).pack(side=tk.RIGHT)
        ttk.Button(pager, text="Prev", command=self.prev_page).pack(side=tk.RIGHT, padx=(0, 8))

        status = ttk.Label(self.root, textvariable=self.status_var, anchor=tk.W, padding=(12, 6))
        status.pack(fill=tk.X)

    def toggle_column(self, column: str) -> None:
        if self.column_visibility[column].get():
            self._apply_display_columns()
            self._save_ui_preferences()
            return
        visible_count = sum(1 for v in self.column_visibility.values() if v.get())
        if visible_count == 0:
            self.column_visibility[column].set(True)
            return
        self._apply_display_columns()
        self._save_ui_preferences()

    def _apply_display_columns(self) -> None:
        display_columns = tuple(
            column for column in self.columns if self.column_visibility[column].get()
        )
        if not display_columns:
            display_columns = (self.columns[0],)
            self.column_visibility[self.columns[0]].set(True)
        self.tree["displaycolumns"] = display_columns

    def _load_ui_preferences(self) -> None:
        visible_columns_json = db.get_setting(self.conn, VISIBLE_COLUMNS_SETTING_KEY)
        if visible_columns_json:
            try:
                visible_columns = json.loads(visible_columns_json)
            except json.JSONDecodeError:
                visible_columns = None
            if isinstance(visible_columns, list):
                visible_set = {str(column) for column in visible_columns if column in self.columns}
                if visible_set:
                    self._visible_column_defaults = {
                        column: column in visible_set for column in self.columns
                    }

        column_widths_json = db.get_setting(self.conn, COLUMN_WIDTHS_SETTING_KEY)
        if column_widths_json:
            try:
                loaded_widths = json.loads(column_widths_json)
            except json.JSONDecodeError:
                loaded_widths = None
            if isinstance(loaded_widths, dict):
                for column, width in loaded_widths.items():
                    if column not in self.column_widths:
                        continue
                    if isinstance(width, int) and width > 0:
                        self.column_widths[column] = width

    def _save_ui_preferences(self) -> None:
        visible_columns = [
            column
            for column in self.columns
            if column in self.column_visibility and self.column_visibility[column].get()
        ]
        current_widths = {
            column: int(self.tree.column(column, "width")) for column in self.columns
        }
        db.set_setting(
            self.conn,
            VISIBLE_COLUMNS_SETTING_KEY,
            json.dumps(visible_columns, ensure_ascii=True),
        )
        db.set_setting(
            self.conn,
            COLUMN_WIDTHS_SETTING_KEY,
            json.dumps(current_widths, ensure_ascii=True),
        )

    def _on_tree_mouse_release(self, event: tk.Event[tk.Widget]) -> None:
        region = self.tree.identify_region(event.x, event.y)
        if region == "separator":
            self._save_ui_preferences()

    def _on_close(self) -> None:
        self._save_ui_preferences()
        self.root.destroy()

    def refresh_inventory(self) -> None:
        raw_scan_root = self.scan_root_var.get().strip()
        scan_root = Path(raw_scan_root).expanduser() if raw_scan_root else None
        try:
            target, count, skipped = service.refresh_inventory(self.conn, scan_root=scan_root)
        except ValueError as exc:
            self.status_var.set(str(exc))
            return
        self.current_page = 0
        if skipped:
            self.status_var.set(
                f"Skipped rescan for {target} (latest Last Seen is within 1 hour)"
            )
        else:
            self.status_var.set(f"Scanned {count} items from {target}")
        self.perform_search()

    def browse_scan_root(self) -> None:
        initial_dir = self.scan_root_var.get().strip() or str(resolve_desktop_path())
        selected = filedialog.askdirectory(
            parent=self.root,
            title="Select scan root folder",
            initialdir=initial_dir,
            mustexist=True,
        )
        if selected:
            self.scan_root_var.set(selected)

    def open_data_folder(self) -> None:
        data_dir = db.db_path().parent
        try:
            if sys.platform.startswith("win"):
                os.startfile(str(data_dir))
            elif sys.platform == "darwin":
                subprocess.run(["open", str(data_dir)], check=False)
            else:
                subprocess.run(["xdg-open", str(data_dir)], check=False)
            self.status_var.set(f"Opened data folder: {data_dir}")
        except OSError as exc:
            self.status_var.set(f"Failed to open data folder: {exc}")

    def perform_search(self) -> None:
        self.current_page = 0
        self._load_page()

    def prev_page(self) -> None:
        if self.current_page == 0:
            return
        self.current_page -= 1
        self._load_page()

    def next_page(self) -> None:
        max_page = (self.total_rows - 1) // self.page_size if self.total_rows else 0
        if self.current_page >= max_page:
            return
        self.current_page += 1
        self._load_page()

    def _load_page(self) -> None:
        query = self.query_var.get().strip()
        item_type = self.type_var.get()
        self.total_rows = db.count_items(self.conn, query=query, item_type=item_type)
        offset = self.current_page * self.page_size
        rows = db.search_items(
            self.conn,
            query=query,
            item_type=item_type,
            limit=self.page_size,
            offset=offset,
        )
        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert(
                "",
                tk.END,
                values=(
                    row["item_type"],
                    row["name"],
                    row["root"],
                    row["path"],
                    row["target"] if row["target"] is not None else "",
                    filetime_to_iso8601(row["modified_filetime"]),
                    row["permissions"],
                    row["size_bytes"] if row["size_bytes"] is not None else "",
                    row["folder_total_size_bytes"]
                    if row["folder_total_size_bytes"] is not None
                    else "",
                    filetime_to_iso8601(row["first_seen_filetime"]),
                    filetime_to_iso8601(row["last_seen_filetime"]),
                ),
            )
        start = offset + 1 if self.total_rows else 0
        end = min(offset + len(rows), self.total_rows)
        self.status_var.set(
            f"Showing {start}-{end} of {self.total_rows} result(s), page {self.current_page + 1}"
        )
