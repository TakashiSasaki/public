import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import TYPE_CHECKING, Any, Dict

from mouse_pointer.core.cursor import save_multi_cursor
from mouse_pointer.generators.basic import create_cursor_image
from mouse_pointer.generators.cursor_roles import CURSOR_ROLES

if TYPE_CHECKING:
    from mouse_pointer.gui import CursorGeneratorGUI


EXPORT_SIZES = [32, 48, 64, 96, 128]


def build_export_tab(app: "CursorGeneratorGUI", parent: tk.Widget) -> ttk.Frame:
    export_frame = ttk.Frame(parent)
    export_frame.pack(fill=tk.BOTH, expand=True)

    roles_by_filename = {role["filename"]: role for role in CURSOR_ROLES}

    desc = ttk.Label(
        export_frame,
        text=(
            "Generate a Windows cursor set into one folder. "
            "Color, border, shadow, and text styling follow your current editor settings, "
            "while each role uses its own recognisable cursor shape."
        ),
        wraplength=760,
        justify=tk.LEFT,
    )
    desc.pack(padx=10, pady=10, anchor=tk.W)

    settings_frame = ttk.LabelFrame(export_frame, text="Export Settings", padding=10)
    settings_frame.pack(fill=tk.X, padx=10, pady=5)

    dir_frame = ttk.Frame(settings_frame)
    dir_frame.pack(fill=tk.X)
    ttk.Label(dir_frame, text="Output Directory:").pack(side=tk.LEFT, padx=(0, 5))

    out_dir_var = tk.StringVar(value=os.path.join(os.getcwd(), "cursor_set"))
    ttk.Entry(dir_frame, textvariable=out_dir_var, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def browse_dir() -> None:
        selected = filedialog.askdirectory(initialdir=out_dir_var.get() or os.getcwd(), title="Select output folder")
        if selected:
            out_dir_var.set(selected)

    ttk.Button(dir_frame, text="Browse...", command=browse_dir).pack(side=tk.LEFT, padx=(5, 0))

    ttk.Label(
        settings_frame,
        text=f"Generated sizes: {', '.join(f'{size}px' for size in EXPORT_SIZES)}",
        font=("Segoe UI", 8),
    ).pack(anchor=tk.W, pady=(8, 0))

    table_frame = ttk.LabelFrame(export_frame, text="Cursor Roles", padding=10)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    columns = ("name", "filename", "shape", "tr_text", "mr_text", "caption_text")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
    tree.heading("name", text="Role")
    tree.heading("filename", text="Filename")
    tree.heading("shape", text="Shape")
    tree.heading("tr_text", text="TR")
    tree.heading("mr_text", text="MR")
    tree.heading("caption_text", text="Caption")

    tree.column("name", width=170, anchor=tk.W)
    tree.column("filename", width=110, anchor=tk.W)
    tree.column("shape", width=90, anchor=tk.CENTER)
    tree.column("tr_text", width=80, anchor=tk.CENTER)
    tree.column("mr_text", width=100, anchor=tk.CENTER)
    tree.column("caption_text", width=160, anchor=tk.W)

    for role in CURSOR_ROLES:
        tree.insert(
            "",
            tk.END,
            iid=role["filename"],
            values=(
                role["name"],
                role["filename"],
                role["shape"],
                role["tr_text"],
                role["mr_text"],
                role["caption_text"],
            ),
        )

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    edit_frame = ttk.LabelFrame(export_frame, text="Selected Role Override", padding=10)
    edit_frame.pack(fill=tk.X, padx=10, pady=(0, 10))

    selected_role_var = tk.StringVar(value="Select a row to edit text overrides.")
    ttk.Label(edit_frame, textvariable=selected_role_var).grid(row=0, column=0, columnspan=6, sticky=tk.W, pady=(0, 8))

    edit_tr_var = tk.StringVar()
    edit_mr_var = tk.StringVar()
    edit_caption_var = tk.StringVar()

    ttk.Label(edit_frame, text="TR Text:").grid(row=1, column=0, sticky=tk.W, padx=(0, 5))
    ttk.Entry(edit_frame, textvariable=edit_tr_var, width=10).grid(row=1, column=1, sticky=tk.W, padx=(0, 12))
    ttk.Label(edit_frame, text="MR Text:").grid(row=1, column=2, sticky=tk.W, padx=(0, 5))
    ttk.Entry(edit_frame, textvariable=edit_mr_var, width=12).grid(row=1, column=3, sticky=tk.W, padx=(0, 12))
    ttk.Label(edit_frame, text="Caption:").grid(row=1, column=4, sticky=tk.W, padx=(0, 5))
    ttk.Entry(edit_frame, textvariable=edit_caption_var, width=24).grid(row=1, column=5, sticky=tk.EW)
    edit_frame.columnconfigure(5, weight=1)

    def sync_editor_from_selection(*_args: Any) -> None:
        selected = tree.selection()
        if not selected:
            return

        item_id = selected[0]
        role = roles_by_filename[item_id]
        values = tree.item(item_id, "values")
        selected_role_var.set(f"{role['name']} ({role['shape']})")
        edit_tr_var.set(values[3])
        edit_mr_var.set(values[4])
        edit_caption_var.set(values[5])

    def apply_selected_override() -> None:
        selected = tree.selection()
        if not selected:
            return

        item_id = selected[0]
        values = list(tree.item(item_id, "values"))
        values[3] = edit_tr_var.get()
        values[4] = edit_mr_var.get()
        values[5] = edit_caption_var.get()
        tree.item(item_id, values=values)

    def reset_selected_override() -> None:
        selected = tree.selection()
        if not selected:
            return

        item_id = selected[0]
        role = roles_by_filename[item_id]
        tree.item(
            item_id,
            values=(
                role["name"],
                role["filename"],
                role["shape"],
                role["tr_text"],
                role["mr_text"],
                role["caption_text"],
            ),
        )
        sync_editor_from_selection()

    tree.bind("<<TreeviewSelect>>", sync_editor_from_selection)

    button_row = ttk.Frame(edit_frame)
    button_row.grid(row=2, column=0, columnspan=6, sticky=tk.W, pady=(8, 0))
    ttk.Button(button_row, text="Apply to Selected", command=apply_selected_override).pack(side=tk.LEFT)
    ttk.Button(button_row, text="Reset Selected", command=reset_selected_override).pack(side=tk.LEFT, padx=(8, 0))

    def safe_int(var: tk.Variable, default: int) -> int:
        try:
            value = var.get()
            return int(value) if value != "" else default
        except (ValueError, tk.TclError):
            return default

    def get_text_data(color_var: tk.StringVar, bg_var: tk.StringVar, alpha_var: tk.IntVar) -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]]:
        text_rgb = app.hex_to_rgba(color_var.get())[:3]
        bg_rgb = app.hex_to_rgba(bg_var.get())[:3]
        return (*text_rgb, 255), (*bg_rgb, alpha_var.get())

    def collect_common_render_kwargs() -> Dict[str, Any]:
        tr_color, tr_bg = get_text_data(app.var_tr_color, app.var_tr_bg_color, app.var_tr_bg_alpha)
        mr_color, mr_bg = get_text_data(app.var_mr_color, app.var_mr_bg_color, app.var_mr_bg_alpha)
        caption_color, caption_bg = get_text_data(app.var_caption_color, app.var_caption_bg_color, app.var_caption_bg_alpha)

        return {
            "color": app.hex_to_rgba(app.var_color.get()),
            "border_color": app.hex_to_rgba(app.var_border_color.get()),
            "border_thickness": app.var_border_thickness.get(),
            "tr_text_size": safe_int(app.var_tr_size, 12),
            "tr_color": tr_color,
            "tr_bg_color": tr_bg,
            "tr_aa": app.var_tr_aa.get(),
            "tr_outline": app.var_tr_outline.get(),
            "mr_text_size": safe_int(app.var_mr_size, 12),
            "mr_color": mr_color,
            "mr_bg_color": mr_bg,
            "mr_aa": app.var_mr_aa.get(),
            "mr_outline": app.var_mr_outline.get(),
            "caption_text_size": safe_int(app.var_caption_size, 12),
            "caption_color": caption_color,
            "caption_bg_color": caption_bg,
            "caption_aa": app.var_caption_aa.get(),
            "caption_outline": app.var_caption_outline.get(),
            "drop_shadow": app.var_drop_shadow.get(),
            "base_name": app.var_base_name.get(),
            "badge1_name": app.var_badge1_name.get(),
            "badge2_name": app.var_badge2_name.get(),
            "svg_aa": app.var_svg_aa.get(),
        }

    def _run_export() -> None:
        out_dir = out_dir_var.get().strip()
        if not out_dir:
            messagebox.showerror("Export Error", "Output directory is required.")
            return

        output_path = Path(out_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        try:
            common_kwargs = collect_common_render_kwargs()
            exported = 0
            errors = []

            for item_id in tree.get_children():
                role = roles_by_filename[item_id]
                values = tree.item(item_id, "values")
                render_kwargs = dict(common_kwargs)
                render_kwargs.update(
                    {
                        "shape": role["shape"],
                        "tr_text": values[3],
                        "mr_text": values[4],
                        "caption_text": values[5],
                    }
                )
                if not role.get("use_overlays", True):
                    render_kwargs["base_name"] = ""
                    render_kwargs["badge1_name"] = ""
                    render_kwargs["badge2_name"] = ""

                try:
                    multi_image_data = []
                    for export_size in EXPORT_SIZES:
                        image, hotspot = create_cursor_image(size=export_size, **render_kwargs)
                        multi_image_data.append((image, hotspot))
                    save_multi_cursor(multi_image_data, output_path / role["filename"])
                    exported += 1
                except Exception as role_error:
                    errors.append(f"{role['filename']}: {role_error}")

            if errors:
                messagebox.showwarning(
                    "Export Finished with Errors",
                    f"{exported} of {len(CURSOR_ROLES)} cursors were generated.\n\n" + "\n".join(errors),
                )
            else:
                messagebox.showinfo(
                    "Export Complete",
                    f"Generated {exported} cursors in:\n{output_path}",
                )
        except Exception as export_error:
            messagebox.showerror("Export Error", f"Failed to export cursor set:\n{export_error}")

    action_frame = ttk.Frame(export_frame)
    action_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    ttk.Button(action_frame, text="Generate All Cursors", command=_run_export).pack(side=tk.RIGHT)

    return export_frame
