import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import List, Dict, Any
from get_a_grip.core.event_log import EventLogCore
from get_a_grip.storage import AppDataStorage

class EventLogViewer(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.storage = AppDataStorage.get_instance()
        self.available_logs = EventLogCore.get_available_logs()
        self.fetched_logs: List[Dict[str, Any]] = []
        
        self._create_widgets()

    def _create_widgets(self):
        # Notebook for Tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Retrieve (取得) & Tab 2: Save (保存) combined into one interaction flow or separated?
        # User requested: "取得する機能とデータベースに保存する機能を別々に実装してください... 取得と保存と閲覧のためのタブを実装してください"
        # So I will create 3 tabs: Retrieve, Save, View.
        
        self.tab_retrieve = ttk.Frame(self.notebook)
        self.tab_save = ttk.Frame(self.notebook)
        self.tab_view = ttk.Frame(self.notebook)
        
        self.notebook.add(self.tab_retrieve, text="取得 (Retrieve)")
        self.notebook.add(self.tab_save, text="保存 (Save)")
        self.notebook.add(self.tab_view, text="閲覧 (View)")
        
        self._build_retrieve_tab()
        self._build_save_tab()
        self._build_view_tab()

    def _build_retrieve_tab(self):
        # Controls
        controls = ttk.Frame(self.tab_retrieve, padding=5)
        controls.pack(fill=tk.X)
        
        ttk.Label(controls, text="ログの種類:").pack(side=tk.LEFT, padx=5)
        self.log_type_var = tk.StringVar(value="System")
        self.log_combo = ttk.Combobox(controls, textvariable=self.log_type_var, values=self.available_logs)
        self.log_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls, text="取得開始", command=self.fetch_logs).pack(side=tk.LEFT, padx=5)
        
        # Preview Area
        self.retrieve_tree = self._create_treeview(self.tab_retrieve)
        
    def _build_save_tab(self):
        # Controls
        controls = ttk.Frame(self.tab_save, padding=5)
        controls.pack(fill=tk.X)
        
        self.save_btn = ttk.Button(controls, text="DBに保存", command=self.save_logs, state=tk.DISABLED)
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        self.save_status_lbl = ttk.Label(controls, text="未取得")
        self.save_status_lbl.pack(side=tk.LEFT, padx=5)

        # Content Area (Shows what will be saved)
        ttk.Label(self.tab_save, text="保存対象のログプレビュー:", padding=5).pack(anchor=tk.W)
        self.save_tree = self._create_treeview(self.tab_save)
        
    def _build_view_tab(self):
        # Controls
        controls = ttk.Frame(self.tab_view, padding=5)
        controls.pack(fill=tk.X)
        
        ttk.Label(controls, text="表示するログ:").pack(side=tk.LEFT, padx=5)
        self.view_log_type_var = tk.StringVar(value="System")
        self.view_log_combo = ttk.Combobox(controls, textvariable=self.view_log_type_var, values=self.available_logs)
        self.view_log_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(controls, text="読み込み (DB)", command=self.load_from_db).pack(side=tk.LEFT, padx=5)
        
        # Treeview
        self.view_tree = self._create_treeview(self.tab_view)

    def _create_treeview(self, parent):
        columns = ("time", "id", "level", "source", "message")
        tree = ttk.Treeview(parent, columns=columns, show="headings")
        
        tree.heading("time", text="日時")
        tree.heading("id", text="ID")
        tree.heading("level", text="レベル")
        tree.heading("source", text="ソース")
        tree.heading("message", text="メッセージ")
        
        tree.column("time", width=150, stretch=False)
        tree.column("id", width=60, stretch=False)
        tree.column("level", width=100, stretch=False)
        tree.column("source", width=150, stretch=False)
        tree.column("message", width=400)
        
        # Scrollbars
        container = ttk.Frame(parent)
        container.pack(fill=tk.BOTH, expand=True)
        
        tree.pack(in_=container, side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        tree.configure(yscrollcommand=vsb.set)
        
        return tree

    def fetch_logs(self):
        log_name = self.log_type_var.get()
        
        def task():
            try:
                logs = EventLogCore.fetch_logs(log_name, limit=100)
                self.after(0, lambda: self._on_fetch_success(logs))
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("エラー", f"ログ取得失敗: {e}"))
                
        threading.Thread(target=task, daemon=True).start()

    def _on_fetch_success(self, logs):
        self.fetched_logs = logs
        
        # Update Retrieve Tab
        self._update_tree(self.retrieve_tree, logs)
        
        # Update Save Tab Preview
        self._update_tree(self.save_tree, logs)
        
        # Enable Save Button and update status
        self.save_btn.config(state=tk.NORMAL)
        self.save_status_lbl.config(text=f"{len(logs)} 件のログが保存可能です")
        
        messagebox.showinfo("完了", f"{len(logs)} 件取得しました。")

    def save_logs(self):
        if not self.fetched_logs:
            return

        log_name = self.log_type_var.get()
        try:
            EventLogCore.save_logs(log_name, self.fetched_logs)
            messagebox.showinfo("完了", "データベースに保存しました。")
            self.save_status_lbl.config(text="保存完了")
        except Exception as e:
            messagebox.showerror("エラー", f"保存失敗: {e}")

    def load_from_db(self):
        log_name = self.view_log_type_var.get()
        # Storageから取得するロジックはStorageクラスにあるが、
        # ここでは直接呼ぶか、Core経由にするか。
        # Coreには `save_logs` しかないので、直でStorageを呼ぶか、Coreに追加するか。
        # 設計としてはCoreに集約したほうがいいが、Planでは `save_logs` だけだった。
        # 既存の `storage.get_cached_event_logs` を使う。
        
        logs = self.storage.get_cached_event_logs(log_name, limit=200)
        self._update_tree(self.view_tree, logs)

    def _update_tree(self, tree, logs):
        for item in tree.get_children():
            tree.delete(item)
            
        for log in logs:
            # 辞書キーが storage.py の戻り値と fetch_logs の戻り値で微妙に違う可能性があるか確認。
            # storage.py: record_number, event_id, event_type, source_name, time_generated, message
            # fetch_logs: record_number, event_id, event_type, source_name, time_generated, message
            # 同じキーを使っているので大丈夫。
            
            tree.insert("", tk.END, values=(
                log.get('time_generated', ''),
                log.get('event_id', ''),
                log.get('event_type', ''),
                log.get('source_name', ''),
                log.get('message', '').replace("\n", " ").strip()
            ))

def main():
    root = tk.Tk()
    root.title("Windows Event Log Viewer (Refactored)")
    root.geometry("1000x600")
    
    viewer = EventLogViewer(root)
    viewer.pack(fill=tk.BOTH, expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    main()
