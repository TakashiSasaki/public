"""GUI viewer for platform directories using tkinter/ttk."""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys
import socket

from get_a_grip.core.inspect_platform_dirs import get_dir_data

# ── Directory descriptions ────────────────────────────────────────────────
# Based on platformdirs documentation and Windows conventions.
DIR_DESCRIPTIONS = {
    "User Data": (
        "ユーザー固有のアプリケーションデータを格納するディレクトリ。\n"
        "アプリケーションの設定ファイル、キャッシュ以外の永続データなどに使用します。\n\n"
        "【Windows の慣例】\n"
        "  %LOCALAPPDATA% (通常 C:\\Users\\<user>\\AppData\\Local)\n"
        "  roaming=True の場合は %APPDATA% (C:\\Users\\<user>\\AppData\\Roaming)\n"
        "  ドメイン環境ではローミングプロファイルとして別PCに同期されます。\n\n"
        "【platformdirs】 PlatformDirs.user_data_dir"
    ),
    "User Config": (
        "ユーザー固有の設定ファイルを格納するディレクトリ。\n"
        "JSON, TOML, INI 等の設定ファイルの保存先として最適です。\n\n"
        "【Windows の慣例】\n"
        "  Windows では User Data と同じパスになります。\n"
        "  Linux では $XDG_CONFIG_HOME (~/.config) が使われます。\n\n"
        "【platformdirs】 PlatformDirs.user_config_dir"
    ),
    "User Cache": (
        "ユーザー固有のキャッシュデータを格納するディレクトリ。\n"
        "再生成可能な一時的データ（ダウンロードキャッシュ、コンパイル済みファイル等）に使用します。\n"
        "このディレクトリは OS やクリーンアップツールによって削除される可能性があります。\n\n"
        "【Windows の慣例】\n"
        "  %LOCALAPPDATA%\\<app>\\Cache\n"
        "  ローミングされません（マシン固有のキャッシュのため）。\n\n"
        "【platformdirs】 PlatformDirs.user_cache_dir"
    ),
    "User State": (
        "ユーザー固有の状態データを格納するディレクトリ。\n"
        "ログファイル、バックアップ、最近使ったファイルのリストなど、\n"
        "キャッシュよりは重要だが設定ほど重要でないデータに使用します。\n\n"
        "【Windows の慣例】\n"
        "  Windows では User Data と同じパスになります。\n"
        "  Linux では $XDG_STATE_HOME (~/.local/state) が使われます。\n\n"
        "【platformdirs】 PlatformDirs.user_state_dir"
    ),
    "User Log": (
        "ユーザー固有のログファイルを格納するディレクトリ。\n"
        "アプリケーションのデバッグログや実行履歴の保存に適しています。\n\n"
        "【Windows の慣例】\n"
        "  %LOCALAPPDATA%\\<app>\\Logs\n"
        "  User Data の下に Logs サブディレクトリとして配置されます。\n\n"
        "【platformdirs】 PlatformDirs.user_log_dir"
    ),
    "User Documents": (
        "ユーザーのドキュメントフォルダ。\n"
        "ユーザーが直接アクセス・編集するファイル（エクスポートデータ等）の保存先です。\n\n"
        "【Windows の慣例】\n"
        "  %USERPROFILE%\\Documents (通常 C:\\Users\\<user>\\Documents)\n"
        "  OneDrive と同期されている場合があります。\n\n"
        "【platformdirs】 PlatformDirs.user_documents_dir"
    ),
    "User Runtime": (
        "ユーザー固有のランタイムデータを格納するディレクトリ。\n"
        "ソケットファイル、PIDファイル、一時的なIPC用ファイルなどに使用します。\n"
        "セッション終了時にクリアされることが期待されます。\n\n"
        "【Windows の慣例】\n"
        "  %LOCALAPPDATA%\\Temp\\<app>\n"
        "  一時ファイル領域の下に配置されます。\n\n"
        "【platformdirs】 PlatformDirs.user_runtime_dir"
    ),
    "Site Data": (
        "システム全体（全ユーザー共通）のアプリケーションデータを格納するディレクトリ。\n"
        "管理者がインストールした共有データ、全ユーザー向けの設定などに使用します。\n\n"
        "【Windows の慣例】\n"
        "  %PROGRAMDATA% (通常 C:\\ProgramData)\n"
        "  書き込みには管理者権限が必要な場合があります。\n\n"
        "【platformdirs】 PlatformDirs.site_data_dir"
    ),
    "Site Config": (
        "システム全体（全ユーザー共通）の設定ファイルを格納するディレクトリ。\n"
        "デフォルト設定やシステムポリシーの保存に適しています。\n\n"
        "【Windows の慣例】\n"
        "  Windows では Site Data と同じパスになります。\n"
        "  Linux では /etc/xdg が使われます。\n\n"
        "【platformdirs】 PlatformDirs.site_config_dir"
    ),
    "Site Cache": (
        "システム全体（全ユーザー共通）のキャッシュデータを格納するディレクトリ。\n"
        "全ユーザーで共有される再生成可能なデータに使用します。\n\n"
        "【Windows の慣例】\n"
        "  %PROGRAMDATA%\\<app>\\Cache\n"
        "  Site Data の下に Cache サブディレクトリとして配置されます。\n\n"
        "【platformdirs】 PlatformDirs.site_cache_dir"
    ),
}


class PlatformDirsViewerApp:
    def __init__(self, root, app_name="get-a-grip", app_author="takas"):
        self.root = root
        self.root.title(f"Platform Dirs Explorer - {app_name}")
        self.root.geometry("850x550")

        # メインフレーム
        main_frame = ttk.Frame(root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ヘッダー
        header = ttk.Label(
            main_frame,
            text=f"Platform Directories for '{app_name}'",
            font=("Segoe UI", 12, "bold"),
        )
        header.pack(pady=(0, 5))

        # ユーザー情報
        try:
            username = os.getlogin()
        except OSError:
            username = os.environ.get("USERNAME", os.environ.get("USER", "unknown"))
        hostname = socket.gethostname()
        user_label = ttk.Label(
            main_frame,
            text=f"User: {username}  |  Host: {hostname}",
            font=("Segoe UI", 10),
        )
        user_label.pack(pady=(0, 10))

        # ── ツリービュー（上部） ──
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("Type", "Path")
        self.tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        self.tree.heading("Type", text="Directory Type")
        self.tree.heading("Path", text="Path")
        self.tree.column("Type", width=150, stretch=tk.NO)
        self.tree.column("Path", width=650)

        # データ挿入
        data = get_dir_data(app_name, app_author)
        for dtype, path in data:
            self.tree.insert("", tk.END, values=(dtype, path))

        # スクロールバー
        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # ── 説明パネル（下部・選択時のみ表示） ──
        self.desc_frame = ttk.LabelFrame(main_frame, text="📖 ディレクトリの説明", padding="10")
        # pack() はまだ呼ばない（選択時に表示する）

        self.desc_label = tk.Text(
            self.desc_frame,
            wrap=tk.WORD,
            height=8,
            font=("Segoe UI", 9),
            bg="#f5f5f5",
            relief=tk.FLAT,
            padx=8,
            pady=8,
            cursor="arrow",
        )
        self.desc_label.pack(fill=tk.BOTH, expand=True)
        self.desc_label.configure(state=tk.DISABLED)

        # ── イベントバインド ──
        self.tree.bind("<<TreeviewSelect>>", self.on_select)
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

    def on_select(self, event):
        """ツリービューの行が選択されたときに説明パネルを表示・更新する。"""
        selected = self.tree.selection()
        if not selected:
            self.desc_frame.pack_forget()
            return

        values = self.tree.item(selected[0], "values")
        dir_type = values[0] if values else None

        desc = DIR_DESCRIPTIONS.get(dir_type)
        if desc:
            # 説明パネルを表示
            self.desc_frame.pack(fill=tk.X, pady=(10, 0))
            self.desc_frame.configure(text=f"📖 {dir_type}")
            self.desc_label.configure(state=tk.NORMAL)
            self.desc_label.delete("1.0", tk.END)
            self.desc_label.insert("1.0", desc)
            self.desc_label.configure(state=tk.DISABLED)
        else:
            self.desc_frame.pack_forget()

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
