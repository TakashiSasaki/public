import tkinter as tk
from tkinter import ttk, messagebox
import json
from datetime import datetime
from get_a_grip.storage import AppDataStorage

class AppDataViewer(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Get-A-Grip AppData Viewer")
        self.geometry("900x600")
        
        # Initialize storage
        try:
            self.storage = AppDataStorage.get_instance()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize AppDataStorage:\n{e}")
            self.destroy()
            return

        self._create_ui()
        self._load_data()

    def _create_ui(self):
        # Tools / Action Bar
        toolbar = ttk.Frame(self, padding="5")
        toolbar.pack(fill=tk.X)
        
        ttk.Button(toolbar, text="Refresh", command=self._load_data).pack(side=tk.LEFT)
        ttk.Button(toolbar, text="Close", command=self.destroy).pack(side=tk.RIGHT)

        # Tab Control
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Tab 1: Database Info
        self.frame_info = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.frame_info, text="Database Info")
        
        # Tab 2: Settings
        self.frame_settings = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_settings, text="Settings")
        self.tree_settings = self._create_treeview(self.frame_settings, ["Key", "Value", "Updated At"])

        # Tab 3: Cache
        self.frame_cache = ttk.Frame(self.notebook)
        self.notebook.add(self.frame_cache, text="Cache")
        self.tree_cache = self._create_treeview(self.frame_cache, ["Key", "Value", "Expires At", "Created At"])

    def _create_treeview(self, parent, columns):
        """Helper to create a standard treeview with scrollbars"""
        frame = ttk.Frame(parent)
        frame.pack(fill=tk.BOTH, expand=True)

        tree = ttk.Treeview(frame, columns=columns, show="headings")
        
        for col in columns:
            tree.heading(col, text=col)
            # Adjust column width logic optionally
            width = 150 if col in ["Updated At", "Expires At", "Created At", "Key"] else 400
            tree.column(col, width=width)

        v_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=tree.yview)
        h_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=tree.xview)
        
        tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

        v_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        h_scroll.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        return tree

    def _load_data(self):
        self._load_info()
        self._load_settings()
        self._load_cache()

    def _load_info(self):
        # Clear existing widgets
        for widget in self.frame_info.winfo_children():
            widget.destroy()

        # Database Meta Info
        conn = self.storage.conn
        try:
            db_path = self.storage.db_path
            
            cur = conn.execute("PRAGMA application_id")
            app_id = cur.fetchone()[0]
            
            cur = conn.execute("PRAGMA user_version")
            user_ver = cur.fetchone()[0]
            
            cur = conn.execute("PRAGMA page_count")
            page_count = cur.fetchone()[0]
            
            cur = conn.execute("PRAGMA page_size")
            page_size = cur.fetchone()[0]
            
            db_size = page_count * page_size
            
            info = [
                ("Database Path", str(db_path)),
                ("Application ID", f"{app_id} (0x{app_id & 0xFFFFFFFF:08x})"),
                ("User Version (Schema)", str(user_ver)),
                ("File Size", f"{db_size / 1024:.2f} KB"),
            ]
            
            row = 0
            for label, value in info:
                ttk.Label(self.frame_info, text=label + ":", font=("Segoe UI", 9, "bold")).grid(row=row, column=0, sticky="w", padx=5, pady=2)
                ttk.Label(self.frame_info, text=value).grid(row=row, column=1, sticky="w", padx=5, pady=2)
                row += 1

        except Exception as e:
            ttk.Label(self.frame_info, text=f"Error loading info: {e}", foreground="red").pack()

    def _load_settings(self):
        self._clear_tree(self.tree_settings)
        conn = self.storage.conn
        try:
            cursor = conn.execute("SELECT key, value, updated_at FROM settings ORDER BY key")
            for row in cursor:
                # Pretty print JSON value if possible, else raw string
                val_str = row["value"]
                try:
                    # Compact JSON representation
                    val_obj = json.loads(val_str)
                    val_display = json.dumps(val_obj, ensure_ascii=False)
                except:
                    val_display = str(val_str)
                
                self.tree_settings.insert("", tk.END, values=(row["key"], val_display, row["updated_at"]))
        except Exception as e:
            print(f"Error loading settings: {e}")

    def _load_cache(self):
        self._clear_tree(self.tree_cache)
        conn = self.storage.conn
        try:
            cursor = conn.execute("SELECT key, value, expires_at, created_at FROM cache ORDER BY key")
            for row in cursor:
                val_str = row["value"]
                try:
                    val_obj = json.loads(val_str)
                    val_display = json.dumps(val_obj, ensure_ascii=False)
                except:
                    val_display = str(val_str)
                
                self.tree_cache.insert("", tk.END, values=(row["key"], val_display, row["expires_at"], row["created_at"]))
        except Exception as e:
            print(f"Error loading cache: {e}")

    def _clear_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)

