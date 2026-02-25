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

        self._build_ui()
        self.refresh_inventory()
        self.perform_search()

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

        columns = (
            "item_type",
            "name",
            "path",
            "modified_at",
            "permissions",
            "size_bytes",
            "folder_total_size_bytes",
            "first_seen",
            "last_seen",
        )
        tree_frame = ttk.Frame(self.root, padding=(12, 0, 12, 12))
        tree_frame.pack(fill=tk.BOTH, expand=True)
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")

        headings = {
            "item_type": "Type",
            "name": "Name",
            "path": "Path",
            "modified_at": "Modified (UTC)",
            "permissions": "Perms",
            "size_bytes": "File Size",
            "folder_total_size_bytes": "Folder Size",
            "first_seen": "First Seen (UTC)",
            "last_seen": "Last Seen (UTC)",
        }
        widths = {
            "item_type": 80,
            "name": 220,
            "path": 420,
            "modified_at": 180,
            "permissions": 80,
            "size_bytes": 100,
            "folder_total_size_bytes": 100,
            "first_seen": 180,
            "last_seen": 180,
        }
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor=tk.W)

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

    def refresh_inventory(self) -> None:
        desktop_path, count = service.refresh_inventory(self.conn)
        self.status_var.set(f"Scanned {count} items from {desktop_path}")
        self.perform_search()

    def perform_search(self) -> None:
        rows = db.search_items(
            self.conn,
            query=self.query_var.get().strip(),
            item_type=self.type_var.get(),
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
        self.status_var.set(f"{len(rows)} result(s)")
