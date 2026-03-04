import io
import tkinter as tk
import json
import importlib.metadata
import platformdirs
from pathlib import Path
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageTk
from mouse_pointer.generators.basic import create_cursor_image
from mouse_pointer.core.cursor import save_cursor, save_multi_cursor

from mouse_pointer.ui.tabs.editor_tab import build_editor_tab
from mouse_pointer.ui.tabs.export_tab import build_export_tab
from mouse_pointer.ui.tabs.fonts_tab import build_fonts_tab

class CursorGeneratorGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        try:
            version = importlib.metadata.version("mouse-pointer")
        except importlib.metadata.PackageNotFoundError:
            version = "unknown"

        self.title(f"Mouse Cursor Generator v{version}")
        self.geometry("680x560")
        self.configure(padx=10, pady=10)

        # Variables
        self.var_shape = tk.StringVar(value="arrow")
        self.var_size = tk.IntVar(value=32)
        self.var_color = tk.StringVar(value="#800080")       # Default Purple
        self.var_border_color = tk.StringVar(value="#000000") # Default Black
        self.var_border_thickness = tk.IntVar(value=1)
        self.var_tr_text = tk.StringVar(value="")
        self.var_tr_size = tk.IntVar(value=12)
        self.var_mr_text = tk.StringVar(value="")
        self.var_mr_size = tk.IntVar(value=12)
        self.var_caption_text = tk.StringVar(value="")
        self.var_caption_size = tk.IntVar(value=12)
        self.var_caption_color = tk.StringVar(value="#000000") # Default Black
        self.var_caption_bg_color = tk.StringVar(value="#ffffff") # Default White
        self.var_caption_aa = tk.BooleanVar(value=True)
        self.var_caption_outline = tk.BooleanVar(value=False)
        self.var_show_grid = tk.BooleanVar(value=True)
        self.var_drop_shadow = tk.BooleanVar(value=True)

        # SVG Overlay Variables
        self.var_base_name = tk.StringVar(value="")
        self.var_badge1_name = tk.StringVar(value="")
        self.var_badge2_name = tk.StringVar(value="")

        self.preview_image = None
        self.img_tk = None
        self.current_hotspot = (0, 0)
        self._unscaled_preview_cache = [] # To prevent GC

        # Pictograms data
        self.base_choices = [""]
        self.badge_choices = [""]
        self.pictograms_data = {}

        self.load_settings()
        self.load_pictograms()

        self.create_widgets()
        
        # Bind events to preview canvas
        self.preview_canvas.bind("<Motion>", self._on_mouse_move)
        self.preview_canvas.bind("<Leave>", self._on_mouse_leave)
        
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.update_preview()

    def get_settings_path(self) -> Path:
        """プラットフォーム固有の設定ファイルパスを返す"""
        config_dir = Path(platformdirs.user_config_dir(appname="work.moukaeritai/mouse-pointer", appauthor=False))
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / "editor_settings.json"

    def save_settings(self):
        """現在のエディタ設定をJSONファイルに保存する"""
        settings = {
            "shape": self.var_shape.get(),
            "size": self.var_size.get(),
            "color": self.var_color.get(),
            "border_color": self.var_border_color.get(),
            "border_thickness": self.var_border_thickness.get(),
            "tr_text": self.var_tr_text.get(),
            "tr_size": self.var_tr_size.get(),
            "mr_text": self.var_mr_text.get(),
            "mr_size": self.var_mr_size.get(),
            "caption_text": self.var_caption_text.get(),
            "caption_size": self.var_caption_size.get(),
            "caption_color": self.var_caption_color.get(),
            "caption_bg_color": self.var_caption_bg_color.get(),
            "caption_aa": self.var_caption_aa.get(),
            "caption_outline": self.var_caption_outline.get(),
            "show_grid": self.var_show_grid.get(),
            "drop_shadow": self.var_drop_shadow.get(),
            "base_name": self.var_base_name.get(),
            "badge1_name": self.var_badge1_name.get(),
            "badge2_name": self.var_badge2_name.get(),
        }
        try:
            with open(self.get_settings_path(), "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save settings: {e}")

    def load_settings(self):
        """保存されているエディタ設定を読み込んで反映する"""
        path = self.get_settings_path()
        if not path.exists():
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                settings = json.load(f)
                
                def set_val(var, key, type_cast=None):
                    if key in settings:
                        val = settings[key]
                        if type_cast:
                            try:
                                # Special case for bool in JSON
                                if type_cast is bool and isinstance(val, str):
                                    val = val.lower() == "true"
                                else:
                                    val = type_cast(val)
                            except: return
                        var.set(val)

                set_val(self.var_shape, "shape")
                set_val(self.var_size, "size", int)
                set_val(self.var_color, "color")
                set_val(self.var_border_color, "border_color")
                set_val(self.var_border_thickness, "border_thickness", int)
                set_val(self.var_tr_text, "tr_text")
                set_val(self.var_tr_size, "tr_size", int)
                set_val(self.var_mr_text, "mr_text")
                set_val(self.var_mr_size, "mr_size", int)
                set_val(self.var_caption_text, "caption_text")
                set_val(self.var_caption_size, "caption_size", int)
                set_val(self.var_caption_color, "caption_color")
                set_val(self.var_caption_bg_color, "caption_bg_color")
                set_val(self.var_caption_aa, "caption_aa", bool)
                set_val(self.var_caption_outline, "caption_outline", bool)
                set_val(self.var_show_grid, "show_grid", bool)
                set_val(self.var_drop_shadow, "drop_shadow", bool)
                set_val(self.var_base_name, "base_name")
                set_val(self.var_badge1_name, "badge1_name")
                set_val(self.var_badge2_name, "badge2_name")
        except Exception as e:
            print(f"Failed to load settings: {e}")

    def on_close(self):
        """終了時に設定を保存して終了する"""
        self.save_settings()
        self.destroy()

    def load_pictograms(self):
        assets_dir = Path(__file__).parent.parent.parent / "pictogram" / "src" / "assets"
        json_path = assets_dir / "pictograms.json"
        if json_path.exists():
            try:
                with open(json_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.pictograms_data = data
                    self.base_choices.extend(list(data.get("bases", {}).keys()))
                    self.badge_choices.extend(list(data.get("badges", {}).keys()))
            except Exception as e:
                print(f"Failed to load pictograms.json: {e}")

    def hex_to_rgba(self, hex_color):
        hex_color = hex_color.lstrip('#')
        # Handle short hex format like #f00
        if len(hex_color) == 3:
            hex_color = ''.join(c + c for c in hex_color)
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, 255)

    def render_svg_thumbnail(self, svg_data, size=48, stroke_color="#800080"):
        """SVGデータをPIL Imageとしてレンダリングして返す（透明背景）。失敗時はNone。"""
        try:
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPM

            content = svg_data.get("content", "")
            viewBox = svg_data.get("viewBox", "0 0 32 32")
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

            # svglib/reportlab は透明PNG出力を正しくサポートしないため
            # black/white matte 技法でアルファチャンネルを抽出する:
            #   白背景: pixel_w = C * a + 255 * (1 - a)
            #   黒背景: pixel_b = C * a
            #   → a = 1 - (pixel_w - pixel_b) / 255
            #   → C = pixel_b / a  (a > 0 の場合)
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
            out = []
            for (rw, gw, bw), (rb, gb, bb) in zip(pw, pb):
                # アルファ: 各チャンネルで計算し最大値を採用
                a = max(
                    1.0 - (rw - rb) / 255.0,
                    1.0 - (gw - gb) / 255.0,
                    1.0 - (bw - bb) / 255.0,
                    0.0
                )
                a = min(a, 1.0)
                if a > 0:
                    r = min(int(rb / a), 255)
                    g = min(int(gb / a), 255)
                    b = min(int(bb / a), 255)
                else:
                    r, g, b = 0, 0, 0
                out.append((r, g, b, int(a * 255)))

            result = Image.new("RGBA", (size, size))
            result.putdata(out)
            return result

        except Exception as e:
            print(f"SVG thumbnail render error: {e}")
            return None

    def create_widgets(self):
        # スタイルを設定
        style = ttk.Style(self)
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # トップレベルNotebookでタブを管理
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # ---- Tab 1: Cursor Editor ----
        editor_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(editor_tab, text="  Cursor Editor  ")
        build_editor_tab(self, editor_tab)

        # ---- Tab 2: Bases Gallery ----
        bases_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(bases_tab, text="  Bases  ")
        self._build_pictogram_list(
            bases_tab,
            self.pictograms_data.get("bases", {}),
            click_callback=self._on_base_selected,
            thumb_size=48,
        )

        # ---- Tab 3: Badges Gallery ----
        badges_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(badges_tab, text="  Badges  ")
        self._build_pictogram_list(
            badges_tab,
            self.pictograms_data.get("badges", {}),
            click_callback=self._on_badge_selected,
            thumb_size=40,
        )

        # ---- Tab 4: Vector Font List ----
        vector_fonts_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(vector_fonts_tab, text="  Vector Fonts  ")
        build_fonts_tab(self, vector_fonts_tab, tab_type="vector")

        # ---- Tab 5: Bitmap Font List ----
        bitmap_fonts_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(bitmap_fonts_tab, text="  Bitmap Fonts  ")
        build_fonts_tab(self, bitmap_fonts_tab, tab_type="bitmap")

        # ---- Tab 6: Export Set ----
        export_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(export_tab, text="  Export Set  ")
        build_export_tab(self, export_tab)

    # ------------------------------------------------------------------
    #  Gallery helpers
    # ------------------------------------------------------------------

    def _build_pictogram_list(self, parent, items: dict, click_callback, thumb_size: int = 48):
        """スクロール可能なピクトグラムグリッドを parent に描画する。"""
        if not items:
            ttk.Label(parent, text="データが見つかりませんでした。").pack(padx=20, pady=20)
            return

        # Canvas + Scrollbar でスクロール対応
        canvas = tk.Canvas(parent, highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        inner = ttk.Frame(canvas)
        canvas_window = canvas.create_window((0, 0), window=inner, anchor="nw")

        def _on_frame_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def _on_canvas_configure(event):
            canvas.itemconfig(canvas_window, width=event.width)

        inner.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_canvas_configure)

        # マウスホイールスクロール
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        # グリッドに並べる列数（固定）
        COLS = 6
        # サムネイルのキャッシュ（GC対策）
        self._thumb_cache = getattr(self, "_thumb_cache", [])

        stroke_color = self.var_color.get()

        for idx, (name, svg_data) in enumerate(items.items()):
            col = idx % COLS
            row = idx // COLS

            cell = ttk.Frame(inner, padding=4)
            cell.grid(row=row, column=col, padx=4, pady=4)

            # サムネイル生成
            pil_img = self.render_svg_thumbnail(svg_data, size=thumb_size, stroke_color=stroke_color)
            if pil_img:
                img_tk = ImageTk.PhotoImage(pil_img)
            else:
                # レンダリング失敗時は透明なダミー
                dummy = Image.new("RGBA", (thumb_size, thumb_size), (0, 0, 0, 0))
                img_tk = ImageTk.PhotoImage(dummy)

            self._thumb_cache.append(img_tk)

            btn = tk.Button(
                cell,
                image=img_tk,
                relief=tk.FLAT,
                bd=0,
                cursor="hand2",
                activebackground="#d0e8ff",
                command=lambda n=name: click_callback(n),
            )
            btn.pack()

            ttk.Label(cell, text=name, font=("Segoe UI", 7), wraplength=thumb_size + 16, justify=tk.CENTER).pack()

    # ------------------------------------------------------------------
    #  Gallery – クリックコールバック
    # ------------------------------------------------------------------
    def _on_base_selected(self, name: str):
        """Baseサムネイルをクリックした時に Cursor Editor の SVG Base に反映。"""
        self.var_base_name.set(name)
        self.notebook.select(0)   # Cursor Editor タブへ切り替え
        self.update_preview()

    def _on_badge_selected(self, name: str):
        """Badgeサムネイルをクリックした時に Cursor Editor の Badge 1 (BR) に反映。"""
        self.var_badge1_name.set(name)
        self.notebook.select(0)
        self.update_preview()

    # ------------------------------------------------------------------
    #  Existing methods (unchanged)
    # ------------------------------------------------------------------
    def choose_color(self, target):
        if target == "fill":
            init_color = self.var_color.get()
            color = colorchooser.askcolor(initialcolor=init_color, title="Select Fill Color")
            if color[1]:
                self.var_color.set(color[1])
                self.color_preview.config(bg=color[1])
                self.update_preview()
        elif target == "border":
            init_color = self.var_border_color.get()
            color = colorchooser.askcolor(initialcolor=init_color, title="Select Border Color")
            if color[1]:
                self.var_border_color.set(color[1])
                self.border_preview.config(bg=color[1])
                self.update_preview()
        elif target == "caption_text":
            init_color = self.var_caption_color.get()
            color = colorchooser.askcolor(initialcolor=init_color, title="Select Caption Text Color")
            if color[1]:
                self.var_caption_color.set(color[1])
                self.cap_color_preview.config(bg=color[1])
                self.update_preview()
        elif target == "caption_bg":
            init_color = self.var_caption_bg_color.get()
            color = colorchooser.askcolor(initialcolor=init_color, title="Select Caption Background Color")
            if color[1]:
                self.var_caption_bg_color.set(color[1])
                self.cap_bg_preview.config(bg=color[1])
                self.update_preview()

    def on_change(self, event=None):
        self.update_preview()

    def update_preview(self):
        if not hasattr(self, 'preview_canvas') or not hasattr(self, 'hotspot_label'):
            return
            
        try:
            size = self.var_size.get()
            fill_rgba = self.hex_to_rgba(self.var_color.get())
            border_rgba = self.hex_to_rgba(self.var_border_color.get())
            cap_rgba = self.hex_to_rgba(self.var_caption_color.get())
            cap_bg_rgba = self.hex_to_rgba(self.var_caption_bg_color.get())

            try:
                tr_s = self.var_tr_size.get()
            except tk.TclError:
                tr_s = 12
            try:
                mr_s = self.var_mr_size.get()
            except tk.TclError:
                mr_s = 12
            try:
                cap_s = self.var_caption_size.get()
            except tk.TclError:
                cap_s = 12

            img, hotspot = create_cursor_image(
                size=size,
                color=fill_rgba,
                shape=self.var_shape.get(),
                border_color=border_rgba,
                border_thickness=self.var_border_thickness.get(),
                tr_text=self.var_tr_text.get(),
                tr_text_size=tr_s,
                mr_text=self.var_mr_text.get(),
                mr_text_size=mr_s,
                caption_text=self.var_caption_text.get(),
                caption_text_size=cap_s,
                caption_color=cap_rgba,
                caption_bg_color=cap_bg_rgba,
                caption_aa=self.var_caption_aa.get(),
                caption_outline=self.var_caption_outline.get(),
                drop_shadow=self.var_drop_shadow.get(),
                base_name=self.var_base_name.get(),
                badge1_name=self.var_badge1_name.get(),
                badge2_name=self.var_badge2_name.get()
            )

            self.preview_image = img
            self.current_hotspot = hotspot

            # Update info labels
            self.hotspot_label.config(text=f"Hotspot: {hotspot}")
            self.coordinate_label.config(text="Coord: -")

            # Scale image so that the preview size is consistent (128x128) regardless of cursor resolution
            preview_scaled = img.resize((128, 128), Image.Resampling.NEAREST)

            self.img_tk = ImageTk.PhotoImage(preview_scaled)

            # Clear canvas and draw
            self.preview_canvas.delete("all")
            
            cw, ch = 256, 256 # Updated canvas size
            img_w, img_h = 128, 128
            offset_x = (cw - img_w) // 2
            offset_y = (ch - img_h) // 2

            # 1. Draw restricted checkerboard pattern for transparency
            # Center the checkerboard to exactly match the 128x128 image area
            for i in range(0, img_w, 10):
                for j in range(0, img_h, 10):
                    c = "#ffffff" if (i//10 + j//10) % 2 == 0 else "#cccccc"
                    x1, y1 = offset_x + i, offset_y + j
                    x2, y2 = min(x1 + 10, offset_x + img_w), min(y1 + 10, offset_y + img_h)
                    self.preview_canvas.create_rectangle(x1, y1, x2, y2, fill=c, outline=c, tags="bg")

            # 2. Draw border around the image area
            self.preview_canvas.create_rectangle(offset_x - 1, offset_y - 1, offset_x + img_w, offset_y + img_h, outline="#ff4444", width=1, tags="border")

            # 3. Draw the image
            self.preview_canvas.create_image(cw//2, ch//2, image=self.img_tk, anchor=tk.CENTER, tags="cursor")

            # 4. Draw Pixel Grid (if enabled)
            if self.var_show_grid.get():
                grid_scale = 128 / size
                for i in range(size + 1):
                    pos = i * grid_scale
                    # Vertical lines
                    self.preview_canvas.create_line(offset_x + pos, offset_y, offset_x + pos, offset_y + img_h, fill="#888888", dash=(1, 3), tags="grid")
                    # Horizontal lines
                    self.preview_canvas.create_line(offset_x, offset_y + pos, offset_x + img_w, offset_y + pos, fill="#888888", dash=(1, 3), tags="grid")

            # 5. Draw hotspot crosshair marker
            scale = 128 / size
            hx = offset_x + hotspot[0] * scale
            hy = offset_y + hotspot[1] * scale
            r = 6  # crosshair arm length
            # White outline for contrast
            self.preview_canvas.create_line(hx - r - 1, hy, hx + r + 1, hy, fill="white", width=3, tags="hotspot")
            self.preview_canvas.create_line(hx, hy - r - 1, hx, hy + r + 1, fill="white", width=3, tags="hotspot")
            # Red crosshair
            self.preview_canvas.create_line(hx - r, hy, hx + r, hy, fill="#ff2222", width=1, tags="hotspot")
            self.preview_canvas.create_line(hx, hy - r, hx, hy + r, fill="#ff2222", width=1, tags="hotspot")
            # Center dot
            self.preview_canvas.create_oval(hx - 1.5, hy - 1.5, hx + 1.5, hy + 1.5, fill="#ff2222", outline="white", tags="hotspot")

            # 6. Update Unscaled Previews
            if hasattr(self, 'unscaled_preview_labels'):
                self._unscaled_preview_cache = []
                preview_sizes = [32, 48, 64, 96, 128]
                for s in preview_sizes:
                    if s in self.unscaled_preview_labels:
                        # Generate at native size
                        native_img, _ = create_cursor_image(
                            size=s,
                            color=fill_rgba,
                            shape=self.var_shape.get(),
                            border_color=border_rgba,
                            border_thickness=self.var_border_thickness.get(),
                            tr_text=self.var_tr_text.get(),
                            tr_text_size=max(8, s // 4), # Scale font slightly with size if needed
                            mr_text=self.var_mr_text.get(),
                            mr_text_size=mr_s,
                            caption_text=self.var_caption_text.get(),
                            caption_text_size=cap_s,
                            caption_color=cap_rgba,
                            caption_bg_color=cap_bg_rgba,
                            caption_aa=self.var_caption_aa.get(),
                            caption_outline=self.var_caption_outline.get(),
                            drop_shadow=self.var_drop_shadow.get(),
                            base_name=self.var_base_name.get(),
                            badge1_name=self.var_badge1_name.get(),
                            badge2_name=self.var_badge2_name.get()
                        )
                        tk_native = ImageTk.PhotoImage(native_img)
                        self._unscaled_preview_cache.append(tk_native)
                        self.unscaled_preview_labels[s].config(image=tk_native)

        except Exception as e:
            print(f"Preview update error: {e}")

    def _on_mouse_move(self, event):
        if not hasattr(self, "coordinate_label") or not hasattr(self, "var_size"):
            return
            
        size = self.var_size.get()
        cw, ch = 256, 256
        img_w, img_h = 128, 128
        offset_x = (cw - img_w) // 2
        offset_y = (ch - img_h) // 2
        
        # Check if mouse is inside image area
        rel_x = event.x - offset_x
        rel_y = event.y - offset_y
        
        if 0 <= rel_x < img_w and 0 <= rel_y < img_h:
            scale = 128 / size
            px = int(rel_x / scale)
            py = int(rel_y / scale)
            # Ensure within bounds due to floating point
            px = min(max(px, 0), size - 1)
            py = min(max(py, 0), size - 1)
            self.coordinate_label.config(text=f"Coord: ({px}, {py})")
        else:
            self.coordinate_label.config(text="Coord: -")

    def _on_mouse_leave(self, event):
        if hasattr(self, "coordinate_label"):
            self.coordinate_label.config(text="Coord: -")

    def generate_cur(self):
        if not self.preview_image:
            messagebox.showerror("Error", "No image to save.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".cur",
            filetypes=[("Cursor files", "*.cur"), ("All files", "*.*")],
            title="Save Cursor As"
        )

        if file_path:
            try:
                # 設定を取得してマルチ解像度を生成
                sizes_to_generate = [32, 48, 64]
                fill_rgba = self.hex_to_rgba(self.var_color.get())
                border_rgba = self.hex_to_rgba(self.var_border_color.get())
                cap_rgba = self.hex_to_rgba(self.var_caption_color.get())
                cap_bg_rgba = self.hex_to_rgba(self.var_caption_bg_color.get())

                try: tr_s = self.var_tr_size.get()
                except tk.TclError: tr_s = 12
                try: mr_s = self.var_mr_size.get()
                except tk.TclError: mr_s = 12
                try: cap_s = self.var_caption_size.get()
                except tk.TclError: cap_s = 12

                multi_image_data = []
                for s in sizes_to_generate:
                    # それぞれのサイズで生成
                    img, hotspot = create_cursor_image(
                        size=s,
                        color=fill_rgba,
                        shape=self.var_shape.get(),
                        border_color=border_rgba,
                        border_thickness=self.var_border_thickness.get(),
                        tr_text=self.var_tr_text.get(),
                        tr_text_size=tr_s,
                        mr_text=self.var_mr_text.get(),
                        mr_text_size=mr_s,
                        caption_text=self.var_caption_text.get(),
                        caption_text_size=cap_s,
                        caption_color=cap_rgba,
                        caption_bg_color=cap_bg_rgba,
                        caption_aa=self.var_caption_aa.get(),
                        caption_outline=self.var_caption_outline.get(),
                        drop_shadow=self.var_drop_shadow.get(),
                        base_name=self.var_base_name.get(),
                        badge1_name=self.var_badge1_name.get(),
                        badge2_name=self.var_badge2_name.get()
                    )
                    multi_image_data.append((img, hotspot))

                # マルチ解像度で保存 (.cur 1ファイルに複数画像を含める)
                save_multi_cursor(multi_image_data, file_path)

                messagebox.showinfo("Success", f"Multi-resolution Cursor (32, 48, 64px) saved successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save cursor:\n{str(e)}")

    # ------------------------------------------------------------------
    #  Tab 4 – Export Set
    # ------------------------------------------------------------------

    def _build_export_tab(self, parent):
        """17種類のカーソルセットを一括出力するタブを構築する。"""
        from mouse_pointer.generators.cursor_roles import CURSOR_ROLES

        info = ttk.Label(
            parent,
            text=(
                "Cursor Editor で設定したデザインを元に、Windows 標準の 17 種類のカーソルを"
                " 一括で出力します。各ロールの右下ラベル (BR) を個別に編集できます。"
            ),
            wraplength=620,
            justify=tk.LEFT,
        )
        info.pack(anchor=tk.W, pady=(0, 8))

        # --- ロール一覧テーブル ---
        cols = ("name", "filename", "label_br")
        tree_frame = ttk.Frame(parent)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL)
        self.export_tree = ttk.Treeview(
            tree_frame,
            columns=cols,
            show="headings",
            height=14,
            yscrollcommand=scrollbar.set,
        )
        scrollbar.config(command=self.export_tree.yview)

        self.export_tree.heading("name",     text="ロール名")
        self.export_tree.heading("filename", text="出力ファイル名")
        self.export_tree.heading("label_br", text="BR ラベル")
        self.export_tree.column("name",     width=220, anchor=tk.W)
        self.export_tree.column("filename", width=180, anchor=tk.W)
        self.export_tree.column("label_br", width=80,  anchor=tk.CENTER)

        for role in CURSOR_ROLES:
            self.export_tree.insert(
                "", tk.END,
                values=(role["name"], role["filename"], role["label_br"]),
                tags=(role["registry_key"],),
            )

        self.export_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # --- BRラベル編集エリア ---
        edit_frame = ttk.LabelFrame(parent, text=" BR ラベル編集 ", padding=6)
        edit_frame.pack(fill=tk.X, pady=(6, 0))

        ttk.Label(edit_frame, text="選択したロールの BR ラベル:").pack(side=tk.LEFT)
        self.var_export_br = tk.StringVar()
        br_entry = ttk.Entry(edit_frame, textvariable=self.var_export_br, width=10)
        br_entry.pack(side=tk.LEFT, padx=4)

        def _apply_br_edit():
            sel = self.export_tree.selection()
            if not sel:
                return
            item = sel[0]
            vals = list(self.export_tree.item(item, "values"))
            vals[2] = self.var_export_br.get()
            self.export_tree.item(item, values=vals)

        ttk.Button(edit_frame, text="適用", command=_apply_br_edit).pack(side=tk.LEFT)

        def _on_select(event):
            sel = self.export_tree.selection()
            if sel:
                self.var_export_br.set(self.export_tree.item(sel[0], "values")[2])

        self.export_tree.bind("<<TreeviewSelect>>", _on_select)

def run_gui():
    app = CursorGeneratorGUI()
    app.mainloop()


if __name__ == "__main__":
    run_gui()
