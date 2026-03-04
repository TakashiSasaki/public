import io
import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from typing import TYPE_CHECKING, Any, Optional, Dict, List, Tuple
from PIL import Image, ImageTk
from mouse_pointer.generators.basic import create_cursor_image
from mouse_pointer.core.cursor import save_multi_cursor

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
    def on_change(event: Any = None) -> None:
        update_preview()

    # Size
    ttk.Label(controls_frame, text=" Size (px):").grid(row=row, column=0, sticky=tk.W, pady=5)
    size_spin = ttk.Spinbox(controls_frame, from_=16, to=256, textvariable=app.var_size, width=5)
    size_spin.grid(row=row, column=1, sticky=tk.EW, pady=5)
    size_spin.bind("<FocusOut>", on_change)
    row += 1

    # Shape
    ttk.Label(controls_frame, text=" Shape:").grid(row=row, column=0, sticky=tk.W, pady=5)
    shape_cb = ttk.Combobox(controls_frame, textvariable=app.var_shape, values=["arrow", "triangle", "cross"], state="readonly", width=10)
    shape_cb.grid(row=row, column=1, sticky=tk.EW, pady=5)
    shape_cb.bind("<<ComboboxSelected>>", on_change)
    row += 1

    # Fill Color
    ttk.Label(controls_frame, text=" Fill Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
    color_btn = ttk.Button(controls_frame, text="Choose...", command=lambda: choose_color("fill"))
    color_btn.grid(row=row, column=1, sticky=tk.EW, pady=5)
    color_preview = tk.Label(controls_frame, bg=app.var_color.get(), width=3)
    color_preview.grid(row=row, column=2, padx=5)
    row += 1

    # Border Color
    ttk.Label(controls_frame, text=" Border Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
    border_btn = ttk.Button(controls_frame, text="Choose...", command=lambda: choose_color("border"))
    border_btn.grid(row=row, column=1, sticky=tk.EW, pady=5)
    border_preview = tk.Label(controls_frame, bg=app.var_border_color.get(), width=3)
    border_preview.grid(row=row, column=2, padx=5)
    row += 1

    # TR Text
    ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
    row += 1
    ttk.Label(controls_frame, text=" TR Text:").grid(row=row, column=0, sticky=tk.W, pady=5)
    tr_entry = ttk.Entry(controls_frame, textvariable=app.var_tr_text, width=10)
    tr_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
    tr_entry.bind("<KeyRelease>", on_change)
    row += 1

    ttk.Label(controls_frame, text=" TR Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
    tr_spin = ttk.Spinbox(controls_frame, from_=8, to=72, textvariable=app.var_tr_size, width=5)
    tr_spin.grid(row=row, column=1, sticky=tk.EW, pady=5)
    tr_spin.bind("<FocusOut>", on_change)
    row += 1

    # MR Text
    ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=5)
    row += 1
    ttk.Label(controls_frame, text=" MR Text:").grid(row=row, column=0, sticky=tk.W, pady=5)
    mr_entry = ttk.Entry(controls_frame, textvariable=app.var_mr_text, width=10)
    mr_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
    mr_entry.bind("<KeyRelease>", on_change)
    row += 1

    ttk.Label(controls_frame, text=" MR Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
    mr_spin = ttk.Spinbox(controls_frame, from_=8, to=72, textvariable=app.var_mr_size, width=5)
    mr_spin.grid(row=row, column=1, sticky=tk.EW, pady=5)
    mr_spin.bind("<FocusOut>", on_change)
    row += 1

    # Caption Text
    ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=5)
    row += 1
    ttk.Label(controls_frame, text=" Caption:").grid(row=row, column=0, sticky=tk.W, pady=5)
    caption_entry = ttk.Entry(controls_frame, textvariable=app.var_caption_text, width=10)
    caption_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
    caption_entry.bind("<KeyRelease>", on_change)
    row += 1

    ttk.Label(controls_frame, text=" Cap Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
    caption_spin = ttk.Spinbox(controls_frame, from_=8, to=72, textvariable=app.var_caption_size, width=5)
    caption_spin.grid(row=row, column=1, sticky=tk.EW, pady=5)
    caption_spin.bind("<FocusOut>", on_change)
    row += 1

    ttk.Label(controls_frame, text=" Cap Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
    cap_color_btn = ttk.Button(controls_frame, text="Text Color", command=lambda: choose_color("caption_text"))
    cap_color_btn.grid(row=row, column=1, sticky=tk.EW, pady=5)
    cap_color_preview = tk.Label(controls_frame, bg=app.var_caption_color.get(), width=3)
    cap_color_preview.grid(row=row, column=2, padx=5)
    row += 1

    ttk.Label(controls_frame, text=" Cap BG:").grid(row=row, column=0, sticky=tk.W, pady=5)
    cap_bg_btn = ttk.Button(controls_frame, text="BG Color", command=lambda: choose_color("caption_bg"))
    cap_bg_btn.grid(row=row, column=1, sticky=tk.EW, pady=5)
    cap_bg_preview = tk.Label(controls_frame, bg=app.var_caption_bg_color.get(), width=3)
    cap_bg_preview.grid(row=row, column=2, padx=5)
    row += 1

    # Caption Render Options
    cap_opt_frame = ttk.Frame(controls_frame)
    cap_opt_frame.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=2)
    ttk.Checkbutton(cap_opt_frame, text="Anti-alias", variable=app.var_caption_aa, command=on_change).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Checkbutton(cap_opt_frame, text="Outline", variable=app.var_caption_outline, command=on_change).pack(side=tk.LEFT)
    row += 1

    # --- SVG Overlays ---
    ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
    row += 1
    ttk.Label(controls_frame, text=" SVG Base:").grid(row=row, column=0, sticky=tk.W, pady=5)
    base_cb = ttk.Combobox(controls_frame, textvariable=app.var_base_name, values=[""] + list(app.pictograms_data.get("bases", {}).keys()), state="readonly", width=10)
    base_cb.grid(row=row, column=1, sticky=tk.EW, pady=5)
    base_cb.bind("<<ComboboxSelected>>", on_change)
    row += 1

    ttk.Label(controls_frame, text=" Badge 1 (MR):").grid(row=row, column=0, sticky=tk.W, pady=5)
    badge1_cb = ttk.Combobox(controls_frame, textvariable=app.var_badge1_name, values=[""] + list(app.pictograms_data.get("badges", {}).keys()), state="readonly", width=10)
    badge1_cb.grid(row=row, column=1, sticky=tk.EW, pady=5)
    badge1_cb.bind("<<ComboboxSelected>>", on_change)
    row += 1
    
    ttk.Label(controls_frame, text=" Badge 2 (TR):").grid(row=row, column=0, sticky=tk.W, pady=5)
    badge2_cb = ttk.Combobox(controls_frame, textvariable=app.var_badge2_name, values=[""] + list(app.pictograms_data.get("badges", {}).keys()), state="readonly", width=10)
    badge2_cb.grid(row=row, column=1, sticky=tk.EW, pady=5)
    badge2_cb.bind("<<ComboboxSelected>>", on_change)
    row += 1

    # Effects
    ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
    row += 1
    drop_shadow_chk = ttk.Checkbutton(controls_frame, text="Drop Shadow", variable=app.var_drop_shadow, command=on_change)
    drop_shadow_chk.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
    row += 1
    show_grid_chk = ttk.Checkbutton(controls_frame, text="Show Grid", variable=app.var_show_grid, command=on_change)
    show_grid_chk.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
    row += 1

    # Add empty label for spacing
    ttk.Label(controls_frame, text="").grid(row=row, column=0, pady=5)
    row += 1

    # Right Panel (Preview & Action)
    preview_frame = ttk.Frame(editor_frame)
    preview_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Add traces to all relevant variables for real-time Live Preview updates
    def _on_var_changed(*args: Any) -> None:
        on_change()

    app.var_size.trace_add("write", _on_var_changed)
    app.var_tr_text.trace_add("write", _on_var_changed)
    app.var_mr_text.trace_add("write", _on_var_changed)
    app.var_caption_text.trace_add("write", _on_var_changed)
    app.var_tr_size.trace_add("write", _on_var_changed)
    app.var_mr_size.trace_add("write", _on_var_changed)
    app.var_caption_size.trace_add("write", _on_var_changed)
    
    # --- Container for Top row (Preview Canvas & Pictograms) ---
    top_preview_container = ttk.Frame(preview_frame)
    top_preview_container.pack(fill=tk.BOTH, expand=True)
    
    # プレビュー表示用キャンバス（左側）
    canvas_frame = ttk.LabelFrame(top_preview_container, text="Live Preview")
    canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
    
    preview_canvas = tk.Canvas(canvas_frame, width=256, height=256, bg="#f0f0f0", relief=tk.SUNKEN, borderwidth=1)
    preview_canvas.pack(padx=10, pady=10, anchor=tk.CENTER)

    info_frame = ttk.Frame(canvas_frame)
    info_frame.pack(pady=(0, 10))

    hotspot_label = ttk.Label(info_frame, text="Hotspot: (0, 0)")
    hotspot_label.pack(side=tk.LEFT, padx=10)

    coordinate_label = ttk.Label(info_frame, text="Coord: -")
    coordinate_label.pack(side=tk.LEFT, padx=10)

    # プレビューロジックで使用する変数を外部スコープから維持するためのアセット
    # (GC対策も兼ねる)
    assets: Dict[str, Any] = {
        "preview_image": None,
        "img_tk": None,
        "current_hotspot": (0, 0),
        "_unscaled_preview_cache": [],
        "_thumb_cache": [],
    }

    def render_svg_thumbnail(svg_data: Dict[str, Any], size: int = 48, stroke_color: str = "#800080") -> Optional[Image.Image]:
        """SVGデータをPIL Imageとしてレンダリングして返す（透明背景）。失敗時はNone。"""
        try:
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPM

            content: str = svg_data.get("content", "")
            viewBox: str = svg_data.get("viewBox", "0 0 32 32")
            stroke_w = 1.5 if viewBox == "0 0 16 16" else 2

            full_svg = f'''<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewBox}" width="{size}" height="{size}" fill="none" stroke="{stroke_color}" stroke-width="{stroke_w}" stroke-linecap="round" stroke-linejoin="round">
    {content}
</svg>'''
            drawing = svg2rlg(io.BytesIO(full_svg.encode('utf-8')))
            factor = size / float(drawing.width)
            drawing.scale(factor, factor)
            drawing.width = size
            drawing.height = size

            buf_w = io.BytesIO()
            renderPM.drawToFile(drawing, buf_w, fmt="PNG", bg=0xFFFFFF)
            buf_w.seek(0)
            img_w = Image.open(buf_w).convert("RGB")

            buf_b = io.BytesIO()
            renderPM.drawToFile(drawing, buf_b, fmt="PNG", bg=0x000000)
            buf_b.seek(0)
            img_b = Image.open(buf_b).convert("RGB")

            pw = list(img_w.getdata())
            pb = list(img_b.getdata())
            out: List[Tuple[int, int, int, int]] = []
            for (rw, gw, bw), (rb, gb, bb) in zip(pw, pb):
                a = max(1.0 - (rw - rb) / 255.0, 1.0 - (gw - gb) / 255.0, 1.0 - (bw - bb) / 255.0, 0.0)
                a = min(a, 1.0)
                if a > 0:
                    r, g, b = min(int(rb / a), 255), min(int(gb / a), 255), min(int(bb / a), 255)
                else:
                    r, g, b = 0, 0, 0
                out.append((r, g, b, int(a * 255)))

            result = Image.new("RGBA", (size, size))
            result.putdata(out)
            return result
        except Exception: return None

    def update_preview() -> None:
        try:
            size_val = app.var_size.get()
            color_hex = app.var_color.get()
            fill_rgba = app.hex_to_rgba(color_hex)
            border_rgba = app.hex_to_rgba(app.var_border_color.get())
            cap_rgba = app.hex_to_rgba(app.var_caption_color.get())
            cap_bg_rgba = app.hex_to_rgba(app.var_caption_bg_color.get())
            
            try: tr_s = app.var_tr_size.get()
            except: tr_s = 12
            try: mr_s = app.var_mr_size.get()
            except: mr_s = 12
            try: cap_s = app.var_caption_size.get()
            except: cap_s = 12

            img, hotspot = create_cursor_image(
                size=size_val, color=fill_rgba, shape=app.var_shape.get(),
                border_color=border_rgba, border_thickness=app.var_border_thickness.get(),
                tr_text=app.var_tr_text.get(), tr_text_size=tr_s,
                mr_text=app.var_mr_text.get(), mr_text_size=mr_s,
                caption_text=app.var_caption_text.get(), caption_text_size=cap_s,
                caption_color=cap_rgba, caption_bg_color=cap_bg_rgba,
                caption_aa=app.var_caption_aa.get(), caption_outline=app.var_caption_outline.get(),
                drop_shadow=app.var_drop_shadow.get(), base_name=app.var_base_name.get(),
                badge1_name=app.var_badge1_name.get(), badge2_name=app.var_badge2_name.get()
            )
            assets["preview_image"] = img
            assets["current_hotspot"] = hotspot

            hotspot_label.config(text=f"Hotspot: {hotspot}")
            preview_scaled = img.resize((128, 128), Image.Resampling.NEAREST)
            assets["img_tk"] = ImageTk.PhotoImage(preview_scaled)
            preview_canvas.delete("all")
            
            cw, ch = 256, 256
            offset_x, offset_y = (cw - 128) // 2, (ch - 128) // 2
            for i in range(0, 128, 10):
                for j in range(0, 128, 10):
                    c = "#ffffff" if (i//10 + j//10) % 2 == 0 else "#cccccc"
                    preview_canvas.create_rectangle(offset_x + i, offset_y + j, min(offset_x + i + 10, offset_x + 128), min(offset_y + j + 10, offset_y + 128), fill=c, outline=c, tags="bg")
            
            preview_canvas.create_rectangle(offset_x - 1, offset_y - 1, offset_x + 128, offset_y + 128, outline="#ff4444", width=1, tags="border")
            preview_canvas.create_image(cw//2, ch//2, image=assets["img_tk"], anchor=tk.CENTER, tags="cursor")

            if app.var_show_grid.get():
                grid_scale = 128 / size_val
                for i in range(size_val + 1):
                    pos = i * grid_scale
                    preview_canvas.create_line(offset_x + pos, offset_y, offset_x + pos, offset_y + 128, fill="#888888", dash=(1, 3), tags="grid")
                    preview_canvas.create_line(offset_x, offset_y + pos, offset_x + 128, offset_y + pos, fill="#888888", dash=(1, 3), tags="grid")

            scale = 128 / size_val
            hx, hy = offset_x + hotspot[0] * scale, offset_y + hotspot[1] * scale
            preview_canvas.create_line(hx - 7, hy, hx + 7, hy, fill="white", width=3, tags="hotspot")
            preview_canvas.create_line(hx, hy - 7, hx, hy + 7, fill="white", width=3, tags="hotspot")
            preview_canvas.create_line(hx - 6, hy, hx + 6, hy, fill="#ff2222", width=1, tags="hotspot")
            preview_canvas.create_line(hx, hy - 6, hx, hy + 6, fill="#ff2222", width=1, tags="hotspot")
            preview_canvas.create_oval(hx - 1.5, hy - 1.5, hx + 1.5, hy + 1.5, fill="#ff2222", outline="white", tags="hotspot")

            if hasattr(app, 'unscaled_preview_labels'):
                assets["_unscaled_preview_cache"] = []
                for s in [32, 48, 64, 96, 128]:
                    if s in app.unscaled_preview_labels:
                        native_img, _ = create_cursor_image(
                            size=s, color=fill_rgba, shape=app.var_shape.get(),
                            border_color=border_rgba, border_thickness=app.var_border_thickness.get(),
                            tr_text=app.var_tr_text.get(), tr_text_size=tr_s,
                            mr_text=app.var_mr_text.get(), mr_text_size=mr_s,
                            caption_text=app.var_caption_text.get(), caption_text_size=cap_s,
                            caption_color=cap_rgba, caption_bg_color=cap_bg_rgba,
                            caption_aa=app.var_caption_aa.get(), caption_outline=app.var_caption_outline.get(),
                            drop_shadow=app.var_drop_shadow.get(), base_name=app.var_base_name.get(),
                            badge1_name=app.var_badge1_name.get(), badge2_name=app.var_badge2_name.get()
                        )
                        tk_native = ImageTk.PhotoImage(native_img)
                        assets["_unscaled_preview_cache"].append(tk_native)
                        app.unscaled_preview_labels[s].config(image=tk_native)
        except Exception as e: print(f"Preview update error: {e}")

    def _on_mouse_move(event: Any) -> None:
        size_val = app.var_size.get()
        cw, ch = 256, 256
        img_w, img_h = 128, 128
        offset_x, offset_y = (cw - img_w) // 2, (ch - img_h) // 2
        rel_x, rel_y = event.x - offset_x, event.y - offset_y
        if 0 <= rel_x < img_w and 0 <= rel_y < img_h:
            scale = 128 / size_val
            px, py = min(max(int(rel_x / scale), 0), size_val - 1), min(max(int(rel_y / scale), 0), size_val - 1)
            coordinate_label.config(text=f"Coord: ({px}, {py})")
        else: coordinate_label.config(text="Coord: -")

    def _on_mouse_leave(event: Any) -> None:
        coordinate_label.config(text="Coord: -")

    preview_canvas.bind("<Motion>", _on_mouse_move)
    preview_canvas.bind("<Leave>", _on_mouse_leave)

    def choose_color(target: str) -> None:
        v_map = {"fill": app.var_color, "border": app.var_border_color, "caption_text": app.var_caption_color, "caption_bg": app.var_caption_bg_color}
        p_map = {"fill": color_preview, "border": border_preview, "caption_text": cap_color_preview, "caption_bg": cap_bg_preview}
        var, prev = v_map[target], p_map[target]
        color = colorchooser.askcolor(initialcolor=var.get(), title=f"Select {target.replace('_', ' ').capitalize()} Color")
        if color[1]:
            var.set(color[1])
            prev.config(bg=color[1])
            update_preview()

    def generate_cur() -> None:
        if not assets["preview_image"]:
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
                        base_name=app.var_base_name.get(), badge1_name=app.var_badge1_name.get(), badge2_name=app.var_badge2_name.get()
                    )
                    multi_image_data.append((img, hotspot))
                save_multi_cursor(multi_image_data, file_path)
                messagebox.showinfo("Success", f"Saved successfully to:\n{file_path}")
            except Exception as e: messagebox.showerror("Error", f"Failed to save cursor:\n{str(e)}")

    def _build_pictogram_list(parent: tk.Widget, items: dict, thumb_size: int = 48) -> None:
        if not items:
            ttk.Label(parent, text="No data found.").pack(padx=20, pady=20)
            return
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
            pil_img = render_svg_thumbnail(svg_data, size=thumb_size, stroke_color=stroke_color)
            img_tk = ImageTk.PhotoImage(pil_img if pil_img else Image.new("RGBA", (thumb_size, thumb_size), (0, 0, 0, 0)))
            assets["_thumb_cache"].append(img_tk)
            
            def cb(n=name):
                # We need to determine if it's base or badge. Actually let's just use closures.
                pass # logic will be injected via direct callbacks below

            btn = tk.Button(cell, image=img_tk, relief=tk.FLAT, bd=0, cursor="hand2", activebackground="#d0e8ff")
            btn.pack()
            # Callback injection based on context would be better but for now let's use the old approach
            # inside _build_pictogram_list we'll pass the callback
            
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
            pil_img = render_svg_thumbnail(svg_data, size=thumb_size, stroke_color=stroke_color)
            img_tk = ImageTk.PhotoImage(pil_img if pil_img else Image.new("RGBA", (thumb_size, thumb_size), (0, 0, 0, 0)))
            assets["_thumb_cache"].append(img_tk)
            tk.Button(cell, image=img_tk, relief=tk.FLAT, bd=0, cursor="hand2", command=lambda n=name: click_cb(n)).pack()
            ttk.Label(cell, text=name, font=("Segoe UI", 7), wraplength=thumb_size + 16, justify=tk.CENTER).pack()

    # ピクトグラムビュアー（右側）枠
    picto_frame = ttk.LabelFrame(top_preview_container, text="Pictograms (Bases & Badges)")
    picto_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
    
    # Notebook for Bases vs Badges
    picto_notebook = ttk.Notebook(picto_frame)
    picto_notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    tab_bases = ttk.Frame(picto_notebook)
    tab_badges = ttk.Frame(picto_notebook)
    picto_notebook.add(tab_bases, text="Bases")
    picto_notebook.add(tab_badges, text="Badges")
    
    def on_base_selected(name: str):
        app.var_base_name.set(name)
        update_preview()
    def on_badge_selected(name: str):
        app.var_badge1_name.set(name)
        update_preview()

    build_grid(tab_bases, app.pictograms_data.get("bases", {}), 48, on_base_selected)
    build_grid(tab_badges, app.pictograms_data.get("badges", {}), 40, on_badge_selected)

    # --- Unscaled Native Sizes Preview (Bottom row) ---
    native_preview_frame = ttk.LabelFrame(preview_frame, text="Native Sizes Preview (Unscaled 1:1)")
    native_preview_frame.pack(fill=tk.X, pady=(10, 0))

    preview_container = ttk.Frame(native_preview_frame, padding=5)
    preview_container.pack(fill=tk.X)

    app.unscaled_preview_labels = {}
    preview_sizes = [32, 48, 64, 96, 128]
    for s in preview_sizes:
        cell = ttk.Frame(preview_container)
        cell.pack(side=tk.LEFT, padx=10, fill=tk.Y)
        ttk.Label(cell, text=f"{s}px", font=("Segoe UI", 8)).pack()
        lbl = tk.Label(cell, bg="#cccccc", width=0, height=0, bd=1, relief=tk.SOLID)
        lbl.pack(pady=2)
        app.unscaled_preview_labels[s] = lbl

    # Output Actions (Bottom)
    action_frame = ttk.Frame(preview_frame)
    action_frame.pack(fill=tk.X, pady=(10, 0))
    gen_btn = ttk.Button(action_frame, text="Generate .cur (Multi-res)", command=generate_cur)
    gen_btn.pack(side=tk.RIGHT, pady=10)

    # 初回プレビュー更新
    update_preview()
