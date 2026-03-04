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

    # TR Text
    ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
    row += 1
    ttk.Label(controls_frame, text=" TR Text:").grid(row=row, column=0, sticky=tk.W, pady=5)
    tr_entry = ttk.Entry(controls_frame, textvariable=app.var_tr_text, width=10)
    tr_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
    row += 1

    ttk.Label(controls_frame, text=" TR Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
    tr_spin = ttk.Spinbox(controls_frame, from_=8, to=72, textvariable=app.var_tr_size, width=5)
    tr_spin.grid(row=row, column=1, sticky=tk.EW, pady=5)
    row += 1

    # MR Text
    ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=5)
    row += 1
    ttk.Label(controls_frame, text=" MR Text:").grid(row=row, column=0, sticky=tk.W, pady=5)
    mr_entry = ttk.Entry(controls_frame, textvariable=app.var_mr_text, width=10)
    mr_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
    row += 1

    ttk.Label(controls_frame, text=" MR Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
    mr_spin = ttk.Spinbox(controls_frame, from_=8, to=72, textvariable=app.var_mr_size, width=5)
    mr_spin.grid(row=row, column=1, sticky=tk.EW, pady=5)
    row += 1

    # Caption Text
    ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=5)
    row += 1
    ttk.Label(controls_frame, text=" Caption:").grid(row=row, column=0, sticky=tk.W, pady=5)
    caption_entry = ttk.Entry(controls_frame, textvariable=app.var_caption_text, width=10)
    caption_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
    row += 1

    ttk.Label(controls_frame, text=" Cap Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
    caption_spin = ttk.Spinbox(controls_frame, from_=8, to=72, textvariable=app.var_caption_size, width=5)
    caption_spin.grid(row=row, column=1, sticky=tk.EW, pady=5)
    row += 1

    ttk.Label(controls_frame, text=" Cap Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
    cap_color_btn = ttk.Button(controls_frame, text="Text Color", command=lambda: choose_color("caption_text"))
    cap_color_btn.grid(row=row, column=1, sticky=tk.EW, pady=5)
    cap_color_preview = tk.Label(controls_frame, bg=app.var_caption_color.get(), width=3)
    cap_color_preview.grid(row=row, column=2, padx=5)
    app.var_caption_color.trace_add("write", lambda *a: cap_color_preview.config(bg=app.var_caption_color.get()))
    row += 1

    ttk.Label(controls_frame, text=" Cap BG:").grid(row=row, column=0, sticky=tk.W, pady=5)
    cap_bg_btn = ttk.Button(controls_frame, text="BG Color", command=lambda: choose_color("caption_bg"))
    cap_bg_btn.grid(row=row, column=1, sticky=tk.EW, pady=5)
    cap_bg_preview = tk.Label(controls_frame, bg=app.var_caption_bg_color.get(), width=3)
    cap_bg_preview.grid(row=row, column=2, padx=5)
    app.var_caption_bg_color.trace_add("write", lambda *a: cap_bg_preview.config(bg=app.var_caption_bg_color.get()))
    row += 1

    # Caption Render Options
    cap_opt_frame = ttk.Frame(controls_frame)
    cap_opt_frame.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=2)
    ttk.Checkbutton(cap_opt_frame, text="Anti-alias", variable=app.var_caption_aa).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Checkbutton(cap_opt_frame, text="Outline", variable=app.var_caption_outline).pack(side=tk.LEFT)
    row += 1

    # --- SVG Overlays (Badges only) ---
    ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
    row += 1

    ttk.Label(controls_frame, text=" Badge 1 (MR):").grid(row=row, column=0, sticky=tk.W, pady=5)
    badge1_cb = ttk.Combobox(controls_frame, textvariable=app.var_badge1_name, values=[""] + list(app.pictograms_data.get("badges", {}).keys()), state="readonly", width=10)
    badge1_cb.grid(row=row, column=1, sticky=tk.EW, pady=5)
    row += 1
    
    ttk.Label(controls_frame, text=" Badge 2 (TR):").grid(row=row, column=0, sticky=tk.W, pady=5)
    badge2_cb = ttk.Combobox(controls_frame, textvariable=app.var_badge2_name, values=[""] + list(app.pictograms_data.get("badges", {}).keys()), state="readonly", width=10)
    badge2_cb.grid(row=row, column=1, sticky=tk.EW, pady=5)
    row += 1

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

    # Assets cache for thumbnails
    assets: Dict[str, Any] = {
        "thumb_cache": [],
    }

    def build_grid(parent, items, thumb_size, click_cb):
        if not items: return
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        inner = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfig(canvas_window, width=e.width))
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))
        
        stroke_color = app.var_color.get()
        for idx, (name, svg_data) in enumerate(items.items()):
            cell = ttk.Frame(inner, padding=4)
            cell.grid(row=idx // 6, column=idx % 6, padx=4, pady=4)
            pil_img = render_svg_to_pil(svg_data, target_size=thumb_size, color_hex=stroke_color, anti_alias=True)
            img_tk = ImageTk.PhotoImage(pil_img if pil_img else Image.new("RGBA", (thumb_size, thumb_size), (0, 0, 0, 0)))
            assets["thumb_cache"].append(img_tk)
            tk.Button(cell, image=img_tk, relief=tk.FLAT, bd=0, cursor="hand2", command=lambda n=name: click_cb(n)).pack()
            ttk.Label(cell, text=name, font=("Segoe UI", 7), wraplength=thumb_size + 16, justify=tk.CENTER).pack()

    # Badges Gallery
    picto_frame = ttk.LabelFrame(right_panel, text="Badges Pictograms")
    picto_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
    build_grid(picto_frame, app.pictograms_data.get("badges", {}), 40, lambda n: app.var_badge1_name.set(n))

    # Save Action
    def generate_cur() -> None:
        if not preview.assets["preview_image"]:
            messagebox.showerror("Error", "No image to save.")
            return
        file_path = filedialog.asksaveasfilename(defaultextension=".cur", filetypes=[("Cursor files", "*.cur"), ("All files", "*.*")], title="Save Cursor As")
        if file_path:
            try:
                fill_rgba, border_rgba = app.hex_to_rgba(app.var_color.get()), app.hex_to_rgba(app.var_border_color.get())
                cap_rgba, cap_bg_rgba = app.hex_to_rgba(app.var_caption_color.get()), app.hex_to_rgba(app.var_caption_bg_color.get())
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
                        tr_text=app.var_tr_text.get(), tr_text_size=tr_s, mr_text=app.var_mr_text.get(), mr_text_size=mr_s,
                        caption_text=app.var_caption_text.get(), caption_text_size=cap_s, caption_color=cap_rgba, caption_bg_color=cap_bg_rgba,
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
