import os
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, ttk
from typing import TYPE_CHECKING, Any, Dict

from mouse_pointer.core.cursor import save_animated_cursor, save_multi_cursor
from mouse_pointer.generators.basic import create_animated_cursor_frames, create_cursor_image
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
            "Filename values are the conventional Windows cursor filenames used by the standard scheme "
            "(for example arrow.cur, help.cur, wait.cur, hand.cur). "
            "Text style follows your current editor and text settings, and role-specific text content is fixed per cursor role. "
            "Each export writes both .cur and .ani files using the current Animation tab settings."
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

    if not app.var_export_out_dir.get():
        app.var_export_out_dir.set(os.path.join(os.getcwd(), "cursor_set"))
    ttk.Entry(dir_frame, textvariable=app.var_export_out_dir, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def browse_dir() -> None:
        selected = filedialog.askdirectory(initialdir=app.var_export_out_dir.get() or os.getcwd(), title="Select output folder")
        if selected:
            app.var_export_out_dir.set(selected)

    ttk.Button(dir_frame, text="Browse...", command=browse_dir).pack(side=tk.LEFT, padx=(5, 0))

    ttk.Label(
        settings_frame,
        text=f"Generated sizes: {', '.join(f'{size}px' for size in EXPORT_SIZES)}",
        font=("Segoe UI", 8),
    ).pack(anchor=tk.W, pady=(8, 0))
    ttk.Label(
        settings_frame,
        text="ANI export uses the current Gradient / Scroll / Frames / Speed settings from the Animation tab.",
        font=("Segoe UI", 8),
        wraplength=760,
        justify=tk.LEFT,
    ).pack(anchor=tk.W, pady=(4, 0))

    table_frame = ttk.LabelFrame(export_frame, text="Cursor Roles", padding=10)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

    columns = ("name", "filename", "shape")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
    tree.heading("name", text="Role")
    tree.heading("filename", text="Filename")
    tree.heading("shape", text="Shape")

    tree.column("name", width=220, anchor=tk.W)
    tree.column("filename", width=150, anchor=tk.W)
    tree.column("shape", width=110, anchor=tk.CENTER)

    for role in CURSOR_ROLES:
        tree.insert(
            "",
            tk.END,
            iid=role["filename"],
            values=(
                role["name"],
                role["filename"],
                role["shape"],
            ),
        )

    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

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
            "gradient_intensity": max(0, safe_int(app.var_anim_gradient_intensity, 96)),
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

    def collect_animation_kwargs() -> Dict[str, Any]:
        return {
            "anim_gradient": app.var_anim_gradient.get(),
            "anim_scroll": app.var_anim_scroll.get(),
            "total_frames": max(2, safe_int(app.var_anim_frames, 15)),
            "jif_rate": max(1, safe_int(app.var_anim_speed, 10)),
        }

    def _run_export() -> None:
        out_dir = app.var_export_out_dir.get().strip()
        if not out_dir:
            messagebox.showerror("Export Error", "Output directory is required.")
            return

        output_path = Path(out_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        try:
            common_kwargs = collect_common_render_kwargs()
            animation_kwargs = collect_animation_kwargs()
            exported_cur = 0
            exported_ani = 0
            errors = []

            for item_id in tree.get_children():
                role = roles_by_filename[item_id]
                render_kwargs = dict(common_kwargs)
                render_kwargs.update(
                    {
                        "shape": role["shape"],
                        "tr_text": role["tr_text"],
                        "mr_text": role["mr_text"],
                        "caption_text": role["caption_text"],
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
                    exported_cur += 1

                    ani_frames = []
                    for export_size in EXPORT_SIZES:
                        frames = create_animated_cursor_frames(
                            size=export_size,
                            total_frames=animation_kwargs["total_frames"],
                            anim_gradient=animation_kwargs["anim_gradient"],
                            anim_scroll=animation_kwargs["anim_scroll"],
                            **render_kwargs,
                        )
                        if not ani_frames:
                            ani_frames = [[frame] for frame in frames]
                        else:
                            for frame_index, frame in enumerate(frames):
                                ani_frames[frame_index].append(frame)

                    ani_filename = Path(role["filename"]).with_suffix(".ani")
                    save_animated_cursor(ani_frames, output_path / ani_filename, jif_rate=animation_kwargs["jif_rate"])
                    exported_ani += 1
                except Exception as role_error:
                    errors.append(f"{role['filename']}: {role_error}")

            if errors:
                messagebox.showwarning(
                    "Export Finished with Errors",
                    f"{exported_cur} .cur files and {exported_ani} .ani files were generated out of {len(CURSOR_ROLES)} roles.\n\n" + "\n".join(errors),
                )
            else:
                messagebox.showinfo(
                    "Export Complete",
                    f"Generated {exported_cur} .cur files and {exported_ani} .ani files in:\n{output_path}",
                )
        except Exception as export_error:
            messagebox.showerror("Export Error", f"Failed to export cursor set:\n{export_error}")

    action_frame = ttk.Frame(export_frame)
    action_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
    ttk.Button(action_frame, text="Generate All Cursors", command=_run_export).pack(side=tk.RIGHT)

    return export_frame
