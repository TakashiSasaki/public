import sys
from pathlib import Path
import tkinter as tk
from tkinter import ttk, messagebox
import argparse

try:
    import platformdirs
    from platformdirs import PlatformDirs
except ImportError:
    print("Error: 'platformdirs' library is not installed.")
    print("Please install it using: pip install platformdirs")
    sys.exit(1)

def get_dir_data(app_name, app_author):
    """
    platformdirs から各種ディレクトリ情報を取得し、リスト形式で返します。
    """
    dirs = PlatformDirs(app_name, app_author, roaming=True)
    
    data = [
        ("User Data", dirs.user_data_dir),
        ("User Config", dirs.user_config_dir),
        ("User Cache", dirs.user_cache_dir),
        ("User State", dirs.user_state_dir),
        ("User Log", dirs.user_log_dir),
        ("User Documents", dirs.user_documents_dir),
        ("User Runtime", dirs.user_runtime_dir),
        ("Site Data", dirs.site_data_dir),
        ("Site Config", dirs.site_config_dir),
        ("Site Cache", dirs.site_cache_dir),
    ]
    return data

def run_gui(app_name, app_author):
    """
    ttk を使用してディレクトリ情報を表示するウィンドウを起動します。
    """
    root = tk.Tk()
    root.title(f"Platform Dirs Explorer - {app_name}")
    root.geometry("800x400")

    # メインフレーム
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # ヘッダー
    header = ttk.Label(main_frame, text=f"Platform Directories for '{app_name}'", font=("Segoe UI", 12, "bold"))
    header.pack(pady=(0, 10))

    # ツリービュー (表)
    columns = ("Type", "Path")
    tree = ttk.Treeview(main_frame, columns=columns, show="headings")
    tree.heading("Type", text="Directory Type")
    tree.heading("Path", text="Path")
    tree.column("Type", width=150, stretch=tk.NO)
    tree.column("Path", width=600)

    # データ挿入
    data = get_dir_data(app_name, app_author)
    for dtype, path in data:
        tree.insert("", tk.END, values=(dtype, path))

    # スクロールバー
    scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    # コピー機能用のボタンフレーム
    btn_frame = ttk.Frame(root, padding="5")
    btn_frame.pack(fill=tk.X)

    def copy_to_clipboard():
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showwarning("Warning", "Please select a row to copy.")
            return
        
        values = tree.item(selected_item[0], "values")
        path = values[1]
        root.clipboard_clear()
        root.clipboard_append(path)
        messagebox.showinfo("Copied", f"Path copied to clipboard:\n{path}")

    copy_btn = ttk.Button(btn_frame, text="Copy Selected Path", command=copy_to_clipboard)
    copy_btn.pack(side=tk.RIGHT, padx=5)

    root.mainloop()

def run_cli(app_name, app_author):
    """
    コンソールにディレクトリ情報を表示します。
    """
    data = get_dir_data(app_name, app_author)
    
    print(f"--- platformdirs information for '{app_name}' (Author: '{app_author}') ---")
    print(f"OS Platform: {sys.platform}")
    print("-" * 70)
    
    for dtype, path in data:
        print(f"{dtype:15}: {path}")
    
    print("-" * 70)
    
    # 実用例: pathlib との組み合わせ
    dirs = PlatformDirs(app_name, app_author, roaming=True)
    config_dir = Path(dirs.user_config_dir)
    print(f"[Pathlib Integration Example]")
    print(f"  Potential config file: {config_dir / 'settings.json'}")
    print(f"  Directory exists?      {config_dir.exists()}")

