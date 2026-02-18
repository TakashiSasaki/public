"""GUI viewer for platform directories using tkinter/ttk."""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

from get_a_grip.core.inspect_platform_dirs import get_dir_data


class PlatformDirsViewerApp:
    def __init__(self, root, app_name="get-a-grip", app_author="takas"):
        self.root = root
        self.root.title(f"Platform Dirs Explorer - {app_name}")
        self.root.geometry("800x400")

        # メインフレーム
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ヘッダー
        header = ttk.Label(
            main_frame,
            text=f"Platform Directories for '{app_name}'",
            font=("Segoe UI", 12, "bold"),
        )
        header.pack(pady=(0, 10))

        # ツリービュー
        columns = ("Type", "Path")
        self.tree = ttk.Treeview(main_frame, columns=columns, show="headings")
        self.tree.heading("Type", text="Directory Type")
        self.tree.heading("Path", text="Path")
        self.tree.column("Type", width=150, stretch=tk.NO)
        self.tree.column("Path", width=600)

        # データ挿入
        data = get_dir_data(app_name, app_author)
        for dtype, path in data:
            self.tree.insert("", tk.END, values=(dtype, path))

        # スクロールバー
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ダブルクリックでフォルダを開く
        self.tree.bind("<Double-1>", self.on_double_click)

        # 右クリックメニュー
        self.context_menu = tk.Menu(root, tearoff=0)
        self.context_menu.add_command(label="Copy Path", command=self.copy_path)
        self.context_menu.add_command(label="Open Folder", command=self.open_folder)
        self.tree.bind("<Button-3>", self.on_right_click)

        # ボタンフレーム
        btn_frame = ttk.Frame(root, padding="5")
        btn_frame.pack(fill=tk.X)

        copy_btn = ttk.Button(btn_frame, text="Copy Selected Path", command=self.copy_path)
        copy_btn.pack(side=tk.RIGHT, padx=5)

    def get_selected_path(self):
        selected = self.tree.selection()
        if not selected:
            return None
        values = self.tree.item(selected[0], "values")
        return values[1] if values else None

    def copy_path(self):
        path = self.get_selected_path()
        if not path:
            messagebox.showwarning("Warning", "Please select a row to copy.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(path)
        messagebox.showinfo("Copied", f"Path copied to clipboard:\n{path}")

    def open_folder(self):
        path = self.get_selected_path()
        if path and os.path.isdir(path):
            os.startfile(path)

    def on_double_click(self, event):
        self.open_folder()

    def on_right_click(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)


def main():
    root = tk.Tk()
    app = PlatformDirsViewerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
