import io
import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from typing import TYPE_CHECKING, Any, Optional, Dict, List, Tuple
from PIL import Image, ImageTk
from mouse_pointer.generators.basic import create_cursor_image, render_svg_to_pil
from mouse_pointer.core.cursor import save_multi_cursor
from mouse_pointer.ui.components.preview_panel import PreviewPanel

if TYPE_CHECKING:
    from mouse_pointer.gui import CursorGeneratorGUI

def build_editor_tab(app: "CursorGeneratorGUI", parent: tk.Widget) -> ttk.Frame:
    """
    Builds the main cursor editor tab.
    'app' is the CursorGeneratorGUI instance (acts as the controller).
    """
    editor_frame = ttk.Frame(parent)
    editor_frame.pack(fill=tk.BOTH, expand=True)

    # Left Panel (Controls)
    controls_frame = ttk.LabelFrame(editor_frame, text="Settings", padding=10)
    controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    row = 0
    # Size
    ttk.Label(controls_frame, text=" Size (px):").grid(row=row, column=0, sticky=tk.W, pady=5)
    size_spin = ttk.Spinbox(controls_frame, from_=16, to=256, textvariable=app.var_size, width=5)
    size_spin.grid(row=row, column=1, sticky=tk.EW, pady=5)
    row += 1

    # Shape
    ttk.Label(controls_frame, text=" Shape:").grid(row=row, column=0, sticky=tk.W, pady=5)
    shape_cb = ttk.Combobox(controls_frame, textvariable=app.var_shape, values=["arrow", "triangle", "cross"], state="readonly", width=10)
    shape_cb.grid(row=row, column=1, sticky=tk.EW, pady=5)
    row += 1

    # Fill Color
    ttk.Label(controls_frame, text=" Fill Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
    def choose_color(target: str) -> None:
        v_map = {"fill": app.var_color, "border": app.var_border_color, "caption_text": app.var_caption_color, "caption_bg": app.var_caption_bg_color}
        var = v_map[target]
        color = colorchooser.askcolor(initialcolor=var.get(), title=f"Select {target.replace('_', ' ').capitalize()} Color")
        if color[1]:
            var.set(color[1])

    color_btn = ttk.Button(controls_frame, text="Choose...", command=lambda: choose_color("fill"))
    color_btn.grid(row=row, column=1, sticky=tk.EW, pady=5)
    color_preview = tk.Label(controls_frame, bg=app.var_color.get(), width=3)
    color_preview.grid(row=row, column=2, padx=5)
    app.var_color.trace_add("write", lambda *a: color_preview.config(bg=app.var_color.get()))
    row += 1

    # Border Color
    ttk.Label(controls_frame, text=" Border Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
    border_btn = ttk.Button(controls_frame, text="Choose...", command=lambda: choose_color("border"))
    border_btn.grid(row=row, column=1, sticky=tk.EW, pady=5)
    border_preview = tk.Label(controls_frame, bg=app.var_border_color.get(), width=3)
    border_preview.grid(row=row, column=2, padx=5)
    app.var_border_color.trace_add("write", lambda *a: border_preview.config(bg=app.var_border_color.get()))
    row += 1

    # --- Text Settings Helper ---
    def add_text_controls(parent, label_prefix, text_var, size_var, color_var, bg_var, alpha_var, aa_var, outline_var):
        nonlocal row
        ttk.Separator(parent, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
        row += 1
        
        ttk.Label(parent, text=f" {label_prefix} Text:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Entry(parent, textvariable=text_var, width=10).grid(row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        ttk.Label(parent, text=f" {label_prefix} Size:").grid(row=row, column=0, sticky=tk.W, pady=2)
        ttk.Spinbox(parent, from_=8, to=72, textvariable=size_var, width=5).grid(row=row, column=1, sticky=tk.EW, pady=2)
        row += 1
        
        # Color & BG
        color_frame = ttk.Frame(parent)
        color_frame.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=2)
        
        def pick_c(var, lbl):
            c = colorchooser.askcolor(initialcolor=var.get(), title=f"Select {lbl} Color")
            if c[1]: var.set(c[1])
            
        btn_c = ttk.Button(color_frame, text="Clr", width=4, command=lambda: pick_c(color_var, f"{label_prefix} Text"))
        btn_c.pack(side=tk.LEFT, padx=2)
        pre_c = tk.Label(color_frame, bg=color_var.get(), width=2)
        pre_c.pack(side=tk.LEFT, padx=2)
        color_var.trace_add("write", lambda *a: pre_c.config(bg=color_var.get()))
        
        btn_bg = ttk.Button(color_frame, text="BG", width=4, command=lambda: pick_c(bg_var, f"{label_prefix} BG"))
        btn_bg.pack(side=tk.LEFT, padx=2)
        pre_bg = tk.Label(color_frame, bg=bg_var.get(), width=2)
        pre_bg.pack(side=tk.LEFT, padx=2)
        bg_var.trace_add("write", lambda *a: pre_bg.config(bg=bg_var.get()))
        
        ttk.Label(color_frame, text=" α:").pack(side=tk.LEFT, padx=(5, 0))
        ttk.Spinbox(color_frame, from_=0, to=255, textvariable=alpha_var, width=4).pack(side=tk.LEFT, padx=2)
        row += 1
        
        # Options
        opt_frame = ttk.Frame(parent)
        opt_frame.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=2)
        ttk.Checkbutton(opt_frame, text="AA", variable=aa_var).pack(side=tk.LEFT, padx=2)
        ttk.Checkbutton(opt_frame, text="Out", variable=outline_var).pack(side=tk.LEFT, padx=2)
        row += 1

    # Apply Text controls
    add_text_controls(controls_frame, "TR", app.var_tr_text, app.var_tr_size, app.var_tr_color, app.var_tr_bg_color, app.var_tr_bg_alpha, app.var_tr_aa, app.var_tr_outline)
    add_text_controls(controls_frame, "MR", app.var_mr_text, app.var_mr_size, app.var_mr_color, app.var_mr_bg_color, app.var_mr_bg_alpha, app.var_mr_aa, app.var_mr_outline)
    add_text_controls(controls_frame, "Cap", app.var_caption_text, app.var_caption_size, app.var_caption_color, app.var_caption_bg_color, app.var_caption_bg_alpha, app.var_caption_aa, app.var_caption_outline)

    # Effects
    ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
    row += 1
    ttk.Checkbutton(controls_frame, text="Drop Shadow", variable=app.var_drop_shadow).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
    row += 1
    ttk.Checkbutton(controls_frame, text="Show Grid", variable=app.var_show_grid).grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
    row += 1

    # Right Panel (Preview & Action)
    right_panel = ttk.Frame(editor_frame)
    right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Reusable Preview Component
    preview = PreviewPanel(app, right_panel)


    # Save Action
    def generate_cur() -> None:
        if not preview.assets["preview_image"]:
            messagebox.showerror("Error", "No image to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".cur", filetypes=[("Cursor files", "*.cur"), ("All files", "*.*")], title="Save Cursor As")
        if file_path:
            try:
                fill_rgba, border_rgba = app.hex_to_rgba(app.var_color.get()), app.hex_to_rgba(app.var_border_color.get())
                
                def get_text_data(color_var, bg_var, alpha_var):
                    rgb = app.hex_to_rgba(color_var.get())[:3]
                    bg_rgb = app.hex_to_rgba(bg_var.get())[:3]
                    return (*rgb, 255), (*bg_rgb, alpha_var.get())

                tr_c, tr_bg = get_text_data(app.var_tr_color, app.var_tr_bg_color, app.var_tr_bg_alpha)
                mr_c, mr_bg = get_text_data(app.var_mr_color, app.var_mr_bg_color, app.var_mr_bg_alpha)
                cap_c, cap_bg = get_text_data(app.var_caption_color, app.var_caption_bg_color, app.var_caption_bg_alpha)

                try: tr_s = app.var_tr_size.get()
                except: tr_s = 12
                try: mr_s = app.var_mr_size.get()
                except: mr_s = 12
                try: cap_s = app.var_caption_size.get()
                except: cap_s = 12

                multi_image_data = []
                for s in [32, 48, 64]:
                    img, hotspot = create_cursor_image(
                        size=s, color=fill_rgba, shape=app.var_shape.get(), border_color=border_rgba, border_thickness=app.var_border_thickness.get(),
                        tr_text=app.var_tr_text.get(), tr_text_size=tr_s, tr_color=tr_c, tr_bg_color=tr_bg, tr_aa=app.var_tr_aa.get(), tr_outline=app.var_tr_outline.get(),
                        mr_text=app.var_mr_text.get(), mr_text_size=mr_s, mr_color=mr_c, mr_bg_color=mr_bg, mr_aa=app.var_mr_aa.get(), mr_outline=app.var_mr_outline.get(),
                        caption_text=app.var_caption_text.get(), caption_text_size=cap_s, caption_color=cap_c, caption_bg_color=cap_bg,
                        caption_aa=app.var_caption_aa.get(), caption_outline=app.var_caption_outline.get(), drop_shadow=app.var_drop_shadow.get(),
                        base_name=app.var_base_name.get(), badge1_name=app.var_badge1_name.get(), badge2_name=app.var_badge2_name.get(),
                        svg_aa=app.var_svg_aa.get()
                    )
                    multi_image_data.append((img, hotspot))
                save_multi_cursor(multi_image_data, file_path)
                messagebox.showinfo("Success", f"Saved successfully to:\n{file_path}")
            except Exception as e: messagebox.showerror("Error", f"Failed to save cursor:\n{str(e)}")

    gen_btn = ttk.Button(right_panel, text="Generate .cur (Multi-res)", command=generate_cur)
    gen_btn.pack(side=tk.RIGHT, pady=10)

    # Initial update
    preview.update_preview()
    
    return editor_frame
