from __future__ import annotations

import tkinter as tk
from tkinter import ttk
import sqlite3

from . import db, service


class DesktopSearchApp:
    def __init__(self, root: tk.Tk, conn: sqlite3.Connection) -> None:
        self.root = root
        self.conn = conn
        self.root.title("Desktop Seiri")
        self.root.geometry("1100x650")

        self.query_var = tk.StringVar()
        self.type_var = tk.StringVar(value="all")
        self.status_var = tk.StringVar(value="Ready")
        self.page_size = 200
        self.current_page = 0
        self.total_rows = 0
        self.columns = (
            "item_type",
            "name",
            "path",
            "target_path",
            "modified_at",
            "permissions",
            "size_bytes",
            "folder_total_size_bytes",
            "first_seen",
            "last_seen",
        )
        self.column_headings = {
            "item_type": "Type",
            "name": "Name",
            "path": "Path",
            "target_path": "Target Path",
            "modified_at": "Modified (UTC)",
            "permissions": "Perms",
            "size_bytes": "File Size",
            "folder_total_size_bytes": "Folder Size",
            "first_seen": "First Seen (UTC)",
            "last_seen": "Last Seen (UTC)",
        }
        self.column_widths = {
            "item_type": 80,
            "name": 220,
            "path": 360,
            "target_path": 360,
            "modified_at": 180,
            "permissions": 80,
            "size_bytes": 100,
            "folder_total_size_bytes": 100,
            "first_seen": 180,
            "last_seen": 180,
        }
        self.column_visibility: dict[str, tk.BooleanVar] = {}

        self._build_ui()
        self.refresh_inventory()

    def _build_ui(self) -> None:
        controls = ttk.Frame(self.root, padding=12)
        controls.pack(fill=tk.X)

        ttk.Label(controls, text="Search").pack(side=tk.LEFT)
        search_entry = ttk.Entry(controls, textvariable=self.query_var, width=40)
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
        ttk.Button(controls, text="Refresh Desktop Scan", command=self.refresh_inventory).pack(
            side=tk.LEFT, padx=(8, 0)
        )
        ttk.Button(controls, text="Prev", command=self.prev_page).pack(side=tk.LEFT, padx=(16, 0))
        ttk.Button(controls, text="Next", command=self.next_page).pack(side=tk.LEFT, padx=(8, 0))

        column_controls = ttk.Frame(self.root, padding=(12, 0, 12, 8))
        column_controls.pack(fill=tk.X)
        ttk.Label(column_controls, text="Visible Columns").pack(side=tk.LEFT, padx=(0, 8))
        for column in self.columns:
            var = tk.BooleanVar(value=True)
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

        status = ttk.Label(self.root, textvariable=self.status_var, anchor=tk.W, padding=(12, 6))
        status.pack(fill=tk.X)

    def toggle_column(self, column: str) -> None:
        if self.column_visibility[column].get():
            self._apply_display_columns()
            return
        visible_count = sum(1 for v in self.column_visibility.values() if v.get())
        if visible_count == 0:
            self.column_visibility[column].set(True)
            return
        self._apply_display_columns()

    def _apply_display_columns(self) -> None:
        display_columns = tuple(
            column for column in self.columns if self.column_visibility[column].get()
        )
        if not display_columns:
            display_columns = (self.columns[0],)
            self.column_visibility[self.columns[0]].set(True)
        self.tree["displaycolumns"] = display_columns

    def refresh_inventory(self) -> None:
        desktop_path, count, skipped = service.refresh_inventory(self.conn)
        self.current_page = 0
        if skipped:
            self.status_var.set(
                f"Skipped rescan for {desktop_path} (latest Last Seen is within 1 hour)"
            )
        else:
            self.status_var.set(f"Scanned {count} items from {desktop_path}")
        self.perform_search()

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
                    row["path"],
                    row["target_path"] if row["target_path"] is not None else "",
                    row["modified_at"],
                    row["permissions"],
                    row["size_bytes"] if row["size_bytes"] is not None else "",
                    row["folder_total_size_bytes"]
                    if row["folder_total_size_bytes"] is not None
                    else "",
                    row["first_seen"],
                    row["last_seen"],
                ),
            )
        start = offset + 1 if self.total_rows else 0
        end = min(offset + len(rows), self.total_rows)
        self.status_var.set(
            f"Showing {start}-{end} of {self.total_rows} result(s), page {self.current_page + 1}"
        )
