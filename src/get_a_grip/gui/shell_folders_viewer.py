"""GUI viewer for Windows Shell Special Folders."""

import os
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox

from get_a_grip.core.shell_folders import get_shell_folders


class ShellFoldersViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("get-a-grip: Shell Special Folders")
        self.root.geometry("900x600")

        self.setup_ui()

    def setup_ui(self):
        # Header
        header = ttk.Label(
            self.root,
            text="Windows Shell Special Folders",
            font=("Arial", 14, "bold"),
        )
        header.pack(pady=(10, 5))

        desc = ttk.Label(
            self.root,
            text="Double-click a row to open the folder in Explorer. Right-click to copy the path.",
            font=("Arial", 9),
        )
        desc.pack(pady=(0, 10))

        # Treeview
        columns = ("name", "path")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings")

        self.tree.heading("name", text="Name", anchor="w")
        self.tree.heading("path", text="Path", anchor="w")

        self.tree.column("name", width=250, minwidth=150)
        self.tree.column("path", width=600, minwidth=300)

        # Scrollbars
        vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.root, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Layout
        self.tree.pack(side="top", expand=True, fill="both", padx=(10, 0), pady=(0, 0))
        vsb.pack(side="right", fill="y", pady=(0, 0))
        hsb.pack(side="bottom", fill="x", padx=(10, 0))

        # Populate data
        self.populate()

        # Bindings
        self.tree.bind("<Double-1>", self.on_double_click)
        self.tree.bind("<Button-3>", self.on_right_click)

        # Context menu
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy Path", command=self.copy_selected_path)
        self.context_menu.add_command(label="Open in Explorer", command=self.open_selected_folder)

    def populate(self):
        folders = get_shell_folders()
        for name, path in folders:
            exists = os.path.exists(path)
            tag = "exists" if exists else "missing"
            self.tree.insert("", "end", values=(name, path), tags=(tag,))

        # Style missing folders with a subtle color
        self.tree.tag_configure("missing", foreground="#999999")

    def on_double_click(self, event):
        self.open_selected_folder()

    def on_right_click(self, event):
        # Select the row under cursor
        row_id = self.tree.identify_row(event.y)
        if row_id:
            self.tree.selection_set(row_id)
            self.context_menu.post(event.x_root, event.y_root)

    def open_selected_folder(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        path = item["values"][1]
        if os.path.exists(path):
            os.startfile(path)
        else:
            messagebox.showwarning(
                "Not Found",
                f"The folder does not exist:\n{path}"
            )

    def copy_selected_path(self):
        selection = self.tree.selection()
        if not selection:
            return
        item = self.tree.item(selection[0])
        path = item["values"][1]
        self.root.clipboard_clear()
        self.root.clipboard_append(path)


def main():
    root = tk.Tk()
    app = ShellFoldersViewerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
