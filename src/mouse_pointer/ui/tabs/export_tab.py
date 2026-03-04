import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import io
from pathlib import Path
from PIL import Image
from mouse_pointer.generators.basic import create_cursor_image
from mouse_pointer.core.cursor import save_multi_cursor

def build_export_tab(app, parent):
    """
    Builds the Export Set tab.
    'app' is the CursorGeneratorGUI instance.
    """
    export_frame = ttk.Frame(parent)
    export_frame.pack(fill=tk.BOTH, expand=True)
    
    # Description
    desc = ttk.Label(export_frame, text="Generate a full set of 17 standard Windows cursors based on your current settings.")
    desc.pack(pady=10, padx=10, anchor=tk.W)
    
    # Settings Container
    settings_frame = ttk.LabelFrame(export_frame, text="Export Settings", padding=10)
    settings_frame.pack(fill=tk.X, padx=10, pady=5)
    
    # Directory Selector
    dir_frame = ttk.Frame(settings_frame)
    dir_frame.pack(fill=tk.X, pady=5)
    ttk.Label(dir_frame, text="Output Directory:").pack(side=tk.LEFT, padx=5)
    
    out_dir_var = tk.StringVar(value=os.path.join(os.getcwd(), "my_cursors"))
    dir_entry = ttk.Entry(dir_frame, textvariable=out_dir_var, width=50)
    dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
    
    def browse_dir():
        d = filedialog.askdirectory(initialdir=out_dir_var.get())
        if d:
            out_dir_var.set(d)
            
    ttk.Button(dir_frame, text="Browse...", command=browse_dir).pack(side=tk.LEFT, padx=5)
    
    # Quick text overrides table
    table_frame = ttk.LabelFrame(export_frame, text="Text Overrides (Optional)", padding=10)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
    
    columns = ("role", "tr_text", "mr_text", "caption")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
    tree.heading("role", text="Cursor Role")
    tree.heading("tr_text", text="TR Text (Override)")
    tree.heading("mr_text", text="MR Text (Override)")
    tree.heading("caption", text="Caption (Override)")
    
    tree.column("role", width=150, anchor=tk.W)
    tree.column("tr_text", width=120, anchor=tk.CENTER)
    tree.column("mr_text", width=120, anchor=tk.CENTER)
    tree.column("caption", width=120, anchor=tk.CENTER)
    
    # Predefined roles logic
    try:
        from mouse_pointer.generators.cursor_roles import CURSOR_ROLES
    except ImportError:
        CURSOR_ROLES = []

    # Populate tree
    for role in CURSOR_ROLES:
        _id = role.get("filename", "")
        _name = role.get("name", "")
        _label_mr = role.get("label_mr", "")
        
        # Default text logic... just examples
        tr, mr, cap = "", _label_mr, ""
        if "link" in _name or "hand" in _id: cap = "Link"
        elif "help" in _name: tr = "?"
        elif "wait" in _id or "starting" in _id: cap = "Wait"
        elif "cross" in _id: cap = "Cross"
        elif "text" in _name or "ibeam" in _id: cap = "Text"
        elif "move" in _name or "sizeall" in _id: cap = "Move"
        
        tree.insert("", tk.END, iid=_id, values=(_name, tr, mr, cap))
        
    tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
    
    # Scrollbar
    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscroll=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Editing frame below tree
    edit_frame = ttk.Frame(table_frame)
    edit_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(edit_frame, text="Edit selected MR Text:").pack(side=tk.LEFT, padx=5)
    edit_mr_var = tk.StringVar()
    edit_entry = ttk.Entry(edit_frame, textvariable=edit_mr_var, width=10)
    edit_entry.pack(side=tk.LEFT, padx=5)
    
    def _apply_mr_edit():
        selected = tree.selection()
        if not selected: return
        new_val = edit_mr_var.get()
        for item in selected:
            vals = list(tree.item(item, "values"))
            vals[2] = new_val # Update MR text column
            tree.item(item, values=vals)
            
    ttk.Button(edit_frame, text="Apply", command=_apply_mr_edit).pack(side=tk.LEFT, padx=5)
    
    def _on_select(event):
        selected = tree.selection()
        if selected:
            vals = tree.item(selected[0], "values")
            edit_mr_var.set(vals[2])

    tree.bind("<<TreeviewSelect>>", _on_select)
    
    # Action
    btn_frame = ttk.Frame(export_frame)
    btn_frame.pack(fill=tk.X, pady=10)
    
    # Store tree and out dir in app so it can be accessed by the export function
    app.export_tree = tree
    app.out_dir_var = out_dir_var
    
    def _run_export():
        out_dir = fd.askdirectory(title="出力フォルダを選択")
        if not out_dir:
            return

        try:
            fill_rgba   = app.hex_to_rgba(app.var_color.get())
            border_rgba = app.hex_to_rgba(app.var_border_color.get())
            cap_rgba    = app.hex_to_rgba(app.var_caption_color.get())
            cap_bg_rgba = app.hex_to_rgba(app.var_caption_bg_color.get())
            try:    tr_s = app.var_tr_size.get()
            except tk.TclError: tr_s = 12
            try:    cap_s = app.var_caption_size.get()
            except tk.TclError: cap_s = 12
            shape       = app.var_shape.get()
            tr_text     = app.var_tr_text.get()
            cap_text    = app.var_caption_text.get()
            border_th   = app.var_border_thickness.get()
            drop_shadow = app.var_drop_shadow.get()
            base_name   = app.var_base_name.get()
            badge1_name = app.var_badge1_name.get()
            badge2_name = app.var_badge2_name.get()

            sizes = [32, 48, 64]
            errors = []

            # Treeview から現在のロール設定を取得
            rows = []
            for iid in tree.get_children():
                vals = tree.item(iid, "values")
                rows.append({"name": vals[0], "filename": iid, "label_mr": vals[2]})

            for role in rows:
                mr_text = role["label_mr"]
                filename = role["filename"]
                out_path = str(Path(out_dir) / filename)
                try:
                    multi_image_data = []
                    for s in sizes:
                        img, hotspot = create_cursor_image(
                            size=s,
                            color=fill_rgba,
                            shape=shape,
                            border_color=border_rgba,
                            border_thickness=border_th,
                            tr_text=tr_text,
                            tr_text_size=tr_s,
                            mr_text=mr_text,
                            mr_text_size=max(8, s // 4),
                            caption_text=cap_text,
                            caption_text_size=cap_s,
                            caption_color=cap_rgba,
                            caption_bg_color=cap_bg_rgba,
                            drop_shadow=drop_shadow,
                            base_name=base_name,
                            badge1_name=badge1_name,
                            badge2_name=badge2_name,
                        )
                        multi_image_data.append((img, hotspot))
                    save_multi_cursor(multi_image_data, out_path)
                except Exception as e:
                    errors.append(f"{filename}: {e}")

            if errors:
                messagebox.showwarning("一部エラー", f"{len(rows) - len(errors)} 個成功、{len(errors)} 個失敗:\n" + "\n".join(errors))
            else:
                messagebox.showinfo("完了", f"17 種類のカーソルを以下に出力しました:\n{out_dir}")
        except Exception as e:
            import traceback
            messagebox.showerror("Error", f"一括出力に失敗しました:\n{traceback.format_exc()}")

    ttk.Button(btn_frame, text="Generate All Cursors", command=_run_export).pack(side=tk.RIGHT, padx=10)
