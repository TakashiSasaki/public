import io
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any, Optional, Dict, List, Tuple
from PIL import Image, ImageTk
from mouse_pointer.generators.basic import create_cursor_image

if TYPE_CHECKING:
    from mouse_pointer.gui import CursorGeneratorGUI

class PreviewPanel:
    """
    A reusable component that displays the live cursor preview 
    and the native size (unscaled) previews.
    """
    def __init__(self, app: "CursorGeneratorGUI", parent: tk.Widget):
        self.app = app
        
        # Container for Top row (Preview Canvas)
        self.preview_container = ttk.Frame(parent)
        self.preview_container.pack(fill=tk.BOTH, expand=True)

        # Live Preview Canvas
        self.canvas_frame = ttk.LabelFrame(self.preview_container, text="Live Preview")
        self.canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))
        
        self.preview_canvas = tk.Canvas(self.canvas_frame, width=256, height=256, bg="#f0f0f0", relief=tk.SUNKEN, borderwidth=1)
        self.preview_canvas.pack(padx=10, pady=10, anchor=tk.CENTER)

        self.info_frame = ttk.Frame(self.canvas_frame)
        self.info_frame.pack(pady=(0, 10))

        self.hotspot_label = ttk.Label(self.info_frame, text="Hotspot: (0, 0)")
        self.hotspot_label.pack(side=tk.LEFT, padx=10)

        self.coordinate_label = ttk.Label(self.info_frame, text="Coord: -")
        self.coordinate_label.pack(side=tk.LEFT, padx=10)

        # Asset cache for GC avoidance
        self.assets: Dict[str, Any] = {
            "preview_image": None,
            "img_tk": None,
            "current_hotspot": (0, 0),
            "_unscaled_preview_cache": [],
        }

        # Unscaled Native Sizes Preview (Bottom row)
        self.native_preview_frame = ttk.LabelFrame(parent, text="Native Sizes Preview (Unscaled 1:1)")
        self.native_preview_frame.pack(fill=tk.X, pady=(10, 0))

        self.native_container = ttk.Frame(self.native_preview_frame, padding=5)
        self.native_container.pack(fill=tk.X)

        self.unscaled_labels: Dict[int, tk.Label] = {}
        for s in [32, 48, 64, 96, 128]:
            cell = ttk.Frame(self.native_container)
            cell.pack(side=tk.LEFT, padx=10, fill=tk.Y)
            ttk.Label(cell, text=f"{s}px", font=("Segoe UI", 8)).pack()
            lbl = tk.Label(cell, bg="#cccccc", width=0, height=0, bd=1, relief=tk.SOLID)
            lbl.pack(pady=2)
            self.unscaled_labels[s] = lbl

        # Bindings
        self.preview_canvas.bind("<Motion>", self._on_mouse_move)
        self.preview_canvas.bind("<Leave>", self._on_mouse_leave)

        # Register auto-update on relevant variable changes
        self._bind_vars()

    def _bind_vars(self) -> None:
        def on_change(*args: Any) -> None:
            self.update_preview()

        vars_to_trace = [
            self.app.var_size, self.app.var_shape, self.app.var_color,
            self.app.var_border_color, self.app.var_border_thickness,
            self.app.var_tr_text, self.app.var_tr_size, self.app.var_tr_color, self.app.var_tr_bg_color, self.app.var_tr_bg_alpha, self.app.var_tr_aa, self.app.var_tr_outline,
            self.app.var_mr_text, self.app.var_mr_size, self.app.var_mr_color, self.app.var_mr_bg_color, self.app.var_mr_bg_alpha, self.app.var_mr_aa, self.app.var_mr_outline,
            self.app.var_caption_text, self.app.var_caption_size, self.app.var_caption_color, self.app.var_caption_bg_color, self.app.var_caption_bg_alpha, self.app.var_caption_aa, self.app.var_caption_outline,
            self.app.var_drop_shadow, self.app.var_show_grid,
            self.app.var_base_name, self.app.var_badge1_name, self.app.var_badge2_name,
            self.app.var_svg_aa,
        ]
        for v in vars_to_trace:
            v.trace_add("write", on_change)

    def update_preview(self) -> None:
        try:
            size_val = self.app.var_size.get()
            color_hex = self.app.var_color.get()
            fill_rgba = self.app.hex_to_rgba(color_hex)
            border_rgba = self.app.hex_to_rgba(self.app.var_border_color.get())
            cap_rgba = self.app.hex_to_rgba(self.app.var_caption_color.get())
            cap_bg_rgba = self.app.hex_to_rgba(self.app.var_caption_bg_color.get())
            
            try: tr_s = self.app.var_tr_size.get()
            except: tr_s = 12
            try: mr_s = self.app.var_mr_size.get()
            except: mr_s = 12
            try: cap_s = self.app.var_caption_size.get()
            except: cap_s = 12

            def get_text_data(color_var, bg_var, alpha_var):
                rgb = self.app.hex_to_rgba(color_var.get())[:3]
                bg_rgb = self.app.hex_to_rgba(bg_var.get())[:3]
                return (*rgb, 255), (*bg_rgb, alpha_var.get())

            tr_c, tr_bg = get_text_data(self.app.var_tr_color, self.app.var_tr_bg_color, self.app.var_tr_bg_alpha)
            mr_c, mr_bg = get_text_data(self.app.var_mr_color, self.app.var_mr_bg_color, self.app.var_mr_bg_alpha)
            cap_c, cap_bg = get_text_data(self.app.var_caption_color, self.app.var_caption_bg_color, self.app.var_caption_bg_alpha)

            # Use create_cursor_image with all current app variables
            img, hotspot = create_cursor_image(
                size=size_val, color=fill_rgba, shape=self.app.var_shape.get(),
                border_color=border_rgba, border_thickness=self.app.var_border_thickness.get(),
                tr_text=self.app.var_tr_text.get(), tr_text_size=tr_s, tr_color=tr_c, tr_bg_color=tr_bg, tr_aa=self.app.var_tr_aa.get(), tr_outline=self.app.var_tr_outline.get(),
                mr_text=self.app.var_mr_text.get(), mr_text_size=mr_s, mr_color=mr_c, mr_bg_color=mr_bg, mr_aa=self.app.var_mr_aa.get(), mr_outline=self.app.var_mr_outline.get(),
                caption_text=self.app.var_caption_text.get(), caption_text_size=cap_s,
                caption_color=cap_c, caption_bg_color=cap_bg,
                caption_aa=self.app.var_caption_aa.get(), caption_outline=self.app.var_caption_outline.get(),
                drop_shadow=self.app.var_drop_shadow.get(), base_name=self.app.var_base_name.get(),
                badge1_name=self.app.var_badge1_name.get(), badge2_name=self.app.var_badge2_name.get(),
                svg_aa=self.app.var_svg_aa.get()
            )
            self.assets["preview_image"] = img
            self.assets["current_hotspot"] = hotspot

            self.hotspot_label.config(text=f"Hotspot: {hotspot}")
            preview_scaled = img.resize((128, 128), Image.Resampling.NEAREST)
            self.assets["img_tk"] = ImageTk.PhotoImage(preview_scaled)
            self.preview_canvas.delete("all")
            
            cw, ch = 256, 256
            offset_x, offset_y = (cw - 128) // 2, (ch - 128) // 2
            for i in range(0, 128, 10):
                for j in range(0, 128, 10):
                    c = "#ffffff" if (i//10 + j//10) % 2 == 0 else "#cccccc"
                    self.preview_canvas.create_rectangle(offset_x + i, offset_y + j, min(offset_x + i + 10, offset_x + 128), min(offset_y + j + 10, offset_y + 128), fill=c, outline=c, tags="bg")
            
            self.preview_canvas.create_rectangle(offset_x - 1, offset_y - 1, offset_x + 128, offset_y + 128, outline="#ff4444", width=1, tags="border")
            self.preview_canvas.create_image(cw//2, ch//2, image=self.assets["img_tk"], anchor=tk.CENTER, tags="cursor")

            if self.app.var_show_grid.get():
                grid_scale = 128 / size_val
                for i in range(size_val + 1):
                    pos = i * grid_scale
                    self.preview_canvas.create_line(offset_x + pos, offset_y, offset_x + pos, offset_y + 128, fill="#888888", dash=(1, 3), tags="grid")
                    self.preview_canvas.create_line(offset_x, offset_y + pos, offset_x + 128, offset_y + pos, fill="#888888", dash=(1, 3), tags="grid")

            scale = 128 / size_val
            hx, hy = offset_x + hotspot[0] * scale, offset_y + hotspot[1] * scale
            self.preview_canvas.create_line(hx - 7, hy, hx + 7, hy, fill="white", width=3, tags="hotspot")
            self.preview_canvas.create_line(hx, hy - 7, hx, hy + 7, fill="white", width=3, tags="hotspot")
            self.preview_canvas.create_line(hx - 6, hy, hx + 6, hy, fill="#ff2222", width=1, tags="hotspot")
            self.preview_canvas.create_line(hx, hy - 6, hx, hy + 6, fill="#ff2222", width=1, tags="hotspot")
            self.preview_canvas.create_oval(hx - 1.5, hy - 1.5, hx + 1.5, hy + 1.5, fill="#ff2222", outline="white", tags="hotspot")

            # Update Unscaled Labels
            self.assets["_unscaled_preview_cache"] = []
            for s in [32, 48, 64, 96, 128]:
                if s in self.unscaled_labels:
                    native_img, _ = create_cursor_image(
                        size=s, color=fill_rgba, shape=self.app.var_shape.get(),
                        border_color=border_rgba, border_thickness=self.app.var_border_thickness.get(),
                        tr_text=self.app.var_tr_text.get(), tr_text_size=tr_s, tr_color=tr_c, tr_bg_color=tr_bg, tr_aa=self.app.var_tr_aa.get(), tr_outline=self.app.var_tr_outline.get(),
                        mr_text=self.app.var_mr_text.get(), mr_text_size=mr_s, mr_color=mr_c, mr_bg_color=mr_bg, mr_aa=self.app.var_mr_aa.get(), mr_outline=self.app.var_mr_outline.get(),
                        caption_text=self.app.var_caption_text.get(), caption_text_size=cap_s,
                        caption_color=cap_c, caption_bg_color=cap_bg,
                        caption_aa=self.app.var_caption_aa.get(), caption_outline=self.app.var_caption_outline.get(),
                        drop_shadow=self.app.var_drop_shadow.get(), base_name=self.app.var_base_name.get(),
                        badge1_name=self.app.var_badge1_name.get(), badge2_name=self.app.var_badge2_name.get(),
                        svg_aa=self.app.var_svg_aa.get()
                    )
                    tk_native = ImageTk.PhotoImage(native_img)
                    self.assets["_unscaled_preview_cache"].append(tk_native)
                    self.unscaled_labels[s].config(image=tk_native)
        except Exception as e: print(f"Preview update error: {e}")

    def _on_mouse_move(self, event: Any) -> None:
        size_val = self.app.var_size.get()
        cw, ch = 256, 256
        img_w, img_h = 128, 128
        offset_x, offset_y = (cw - img_w) // 2, (ch - img_h) // 2
        rel_x, rel_y = event.x - offset_x, event.y - offset_y
        if 0 <= rel_x < img_w and 0 <= rel_y < img_h:
            scale = 128 / size_val
            px, py = min(max(int(rel_x / scale), 0), size_val - 1), min(max(int(rel_y / scale), 0), size_val - 1)
            self.coordinate_label.config(text=f"Coord: ({px}, {py})")
        else: self.coordinate_label.config(text="Coord: -")

    def _on_mouse_leave(self, event: Any) -> None:
        self.coordinate_label.config(text="Coord: -")
