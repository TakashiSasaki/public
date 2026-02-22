import io
import tkinter as tk
import json
from pathlib import Path
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageTk
from mouse_pointer.generators.basic import create_cursor_image
from mouse_pointer.core.cursor import save_cursor, save_multi_cursor


class CursorGeneratorGUI(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Mouse Cursor Generator")
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
        self.var_br_text = tk.StringVar(value="")
        self.var_br_size = tk.IntVar(value=12)
        self.var_drop_shadow = tk.BooleanVar(value=True)

        # SVG Overlay Variables
        self.var_base_name = tk.StringVar(value="")
        self.var_badge1_name = tk.StringVar(value="")
        self.var_badge2_name = tk.StringVar(value="")

        self.preview_image = None
        self.img_tk = None
        self.current_hotspot = (0, 0)

        # Load JSON data
        self.base_choices = [""]
        self.badge_choices = [""]
        self.pictograms_data = {}
        self.load_pictograms()

        self.create_widgets()
        self.update_preview()

    def load_pictograms(self):
        assets_dir = Path(__file__).parent.parent.parent / "gallery-app" / "src" / "assets"
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
        """SVGデータをPIL Imageとしてレンダリングして返す。失敗時はNone。"""
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
            buf = io.BytesIO()
            renderPM.drawToFile(drawing, buf, fmt="PNG")
            buf.seek(0)
            return Image.open(buf).convert("RGBA")
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
        self._build_editor_tab(editor_tab)

        # ---- Tab 2: Pictogram Gallery ----
        gallery_tab = ttk.Frame(self.notebook, padding=5)
        self.notebook.add(gallery_tab, text="  Pictograms  ")
        self._build_gallery_tab(gallery_tab)

    # ------------------------------------------------------------------
    #  Tab 1 – Cursor Editor
    # ------------------------------------------------------------------
    def _build_editor_tab(self, parent):
        # --- Left Panel (Controls) ---
        controls_frame = ttk.LabelFrame(parent, text="Settings", padding=15)
        controls_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        row = 0

        # Shape
        ttk.Label(controls_frame, text="Shape:").grid(row=row, column=0, sticky=tk.W, pady=5)
        shape_combo = ttk.Combobox(controls_frame, textvariable=self.var_shape, state="readonly", values=["arrow", "triangle", "cross"])
        shape_combo.grid(row=row, column=1, sticky=tk.EW, pady=5)
        shape_combo.bind("<<ComboboxSelected>>", self.on_change)
        row += 1

        # Size
        ttk.Label(controls_frame, text="Size (px):").grid(row=row, column=0, sticky=tk.W, pady=5)
        size_combo = ttk.Combobox(controls_frame, textvariable=self.var_size, state="readonly", values=[32, 48, 64])
        size_combo.grid(row=row, column=1, sticky=tk.EW, pady=5)
        size_combo.bind("<<ComboboxSelected>>", self.on_change)
        row += 1

        # Color
        ttk.Label(controls_frame, text="Fill Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
        color_btn = ttk.Button(controls_frame, text="Select Color", command=lambda: self.choose_color("fill"))
        color_btn.grid(row=row, column=1, sticky=tk.EW, pady=5)
        self.color_preview = tk.Label(controls_frame, bg=self.var_color.get(), width=3)
        self.color_preview.grid(row=row, column=2, padx=5)
        row += 1

        # Border Color
        ttk.Label(controls_frame, text="Border Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
        border_color_btn = ttk.Button(controls_frame, text="Select Color", command=lambda: self.choose_color("border"))
        border_color_btn.grid(row=row, column=1, sticky=tk.EW, pady=5)
        self.border_preview = tk.Label(controls_frame, bg=self.var_border_color.get(), width=3)
        self.border_preview.grid(row=row, column=2, padx=5)
        row += 1

        # Border Thickness
        ttk.Label(controls_frame, text="Border Thick:").grid(row=row, column=0, sticky=tk.W, pady=5)
        thickness_spin = ttk.Spinbox(controls_frame, from_=0, to=5, textvariable=self.var_border_thickness, command=self.on_change)
        thickness_spin.grid(row=row, column=1, sticky=tk.EW, pady=5)
        thickness_spin.bind("<Return>", self.on_change)
        thickness_spin.bind("<FocusOut>", self.on_change)
        row += 1

        # Top-Right Text
        ttk.Label(controls_frame, text="TR Text:").grid(row=row, column=0, sticky=tk.W, pady=5)
        tr_frame = ttk.Frame(controls_frame)
        tr_frame.grid(row=row, column=1, sticky=tk.EW, pady=5)
        tr_entry = ttk.Entry(tr_frame, textvariable=self.var_tr_text, width=4)
        tr_entry.pack(side=tk.LEFT)
        tr_entry.bind("<KeyRelease>", self.on_change)
        ttk.Label(tr_frame, text=" Size:").pack(side=tk.LEFT, padx=(5, 2))
        tr_spin = ttk.Spinbox(tr_frame, from_=8, to=32, textvariable=self.var_tr_size, width=3, command=self.on_change)
        tr_spin.pack(side=tk.LEFT)
        tr_spin.bind("<Return>", self.on_change)
        tr_spin.bind("<FocusOut>", self.on_change)
        row += 1

        # Bottom-Right Text
        ttk.Label(controls_frame, text="BR Text:").grid(row=row, column=0, sticky=tk.W, pady=5)
        br_frame = ttk.Frame(controls_frame)
        br_frame.grid(row=row, column=1, sticky=tk.EW, pady=5)
        br_entry = ttk.Entry(br_frame, textvariable=self.var_br_text, width=4)
        br_entry.pack(side=tk.LEFT)
        br_entry.bind("<KeyRelease>", self.on_change)
        ttk.Label(br_frame, text=" Size:").pack(side=tk.LEFT, padx=(5, 2))
        br_spin = ttk.Spinbox(br_frame, from_=8, to=32, textvariable=self.var_br_size, width=3, command=self.on_change)
        br_spin.pack(side=tk.LEFT)
        br_spin.bind("<Return>", self.on_change)
        br_spin.bind("<FocusOut>", self.on_change)
        row += 1

        # --- SVG Overlays ---
        ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
        row += 1

        # Base Overlay
        ttk.Label(controls_frame, text="SVG Base:").grid(row=row, column=0, sticky=tk.W, pady=5)
        base_combo = ttk.Combobox(controls_frame, textvariable=self.var_base_name, state="readonly", values=self.base_choices)
        base_combo.grid(row=row, column=1, sticky=tk.EW, pady=5)
        base_combo.bind("<<ComboboxSelected>>", self.on_change)
        row += 1

        # Badge 1 (Bottom Right)
        ttk.Label(controls_frame, text="Badge 1 (BR):").grid(row=row, column=0, sticky=tk.W, pady=5)
        badge1_combo = ttk.Combobox(controls_frame, textvariable=self.var_badge1_name, state="readonly", values=self.badge_choices)
        badge1_combo.grid(row=row, column=1, sticky=tk.EW, pady=5)
        badge1_combo.bind("<<ComboboxSelected>>", self.on_change)
        row += 1

        # Badge 2 (Top Left)
        ttk.Label(controls_frame, text="Badge 2 (TL):").grid(row=row, column=0, sticky=tk.W, pady=5)
        badge2_combo = ttk.Combobox(controls_frame, textvariable=self.var_badge2_name, state="readonly", values=self.badge_choices)
        badge2_combo.grid(row=row, column=1, sticky=tk.EW, pady=5)
        badge2_combo.bind("<<ComboboxSelected>>", self.on_change)
        row += 1

        # Drop Shadow
        ttk.Label(controls_frame, text="Effects:").grid(row=row, column=0, sticky=tk.W, pady=5)
        shadow_chk = ttk.Checkbutton(controls_frame, text="Drop Shadow", variable=self.var_drop_shadow, command=self.on_change)
        shadow_chk.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1

        # --- Right Panel (Preview & Action) ---
        right_frame = ttk.Frame(parent)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Preview Area
        preview_group = ttk.LabelFrame(right_frame, text="Live Preview", padding=15)
        preview_group.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.preview_canvas = tk.Canvas(preview_group, width=150, height=150, bg="#dddddd", highlightthickness=1, highlightbackground="#999")
        self.preview_canvas.pack(expand=True)

        self.hotspot_label = ttk.Label(preview_group, text="Hotspot: (0, 0)")
        self.hotspot_label.pack(pady=5)

        # Generate Button
        generate_btn = ttk.Button(right_frame, text="Generate .cur", command=self.generate_cur, style="Accent.TButton")
        generate_btn.pack(fill=tk.X, pady=10, ipady=10)

    # ------------------------------------------------------------------
    #  Tab 2 – Pictogram Gallery
    # ------------------------------------------------------------------
    def _build_gallery_tab(self, parent):
        """ピクトグラム一覧を bases / badges のサブタブで表示する。"""

        # 説明ラベル
        info_label = ttk.Label(
            parent,
            text="ピクトグラムの一覧です。クリックすると Cursor Editor の選択欄に反映されます。",
            wraplength=620,
            justify=tk.LEFT,
        )
        info_label.pack(anchor=tk.W, pady=(0, 6))

        # サブNotebook (Bases / Badges)
        sub_nb = ttk.Notebook(parent)
        sub_nb.pack(fill=tk.BOTH, expand=True)

        bases_frame = ttk.Frame(sub_nb)
        badges_frame = ttk.Frame(sub_nb)
        sub_nb.add(bases_frame, text="  Bases  ")
        sub_nb.add(badges_frame, text="  Badges  ")

        self._build_pictogram_list(
            bases_frame,
            self.pictograms_data.get("bases", {}),
            click_callback=self._on_base_selected,
            thumb_size=48,
        )
        self._build_pictogram_list(
            badges_frame,
            self.pictograms_data.get("badges", {}),
            click_callback=self._on_badge_selected,
            thumb_size=40,
        )

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
                # チェッカーボード背景に合成
                bg = Image.new("RGBA", (thumb_size, thumb_size), (220, 220, 220, 255))
                bg.paste(pil_img, (0, 0), pil_img)
                img_tk = ImageTk.PhotoImage(bg)
            else:
                # レンダリング失敗時はグレーのダミー
                dummy = Image.new("RGBA", (thumb_size, thumb_size), (200, 200, 200, 255))
                img_tk = ImageTk.PhotoImage(dummy)

            self._thumb_cache.append(img_tk)

            btn = tk.Button(
                cell,
                image=img_tk,
                relief=tk.FLAT,
                bd=1,
                cursor="hand2",
                bg="#f0f0f0",
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

    def on_change(self, event=None):
        self.update_preview()

    def update_preview(self):
        try:
            size = self.var_size.get()
            fill_rgba = self.hex_to_rgba(self.var_color.get())
            border_rgba = self.hex_to_rgba(self.var_border_color.get())

            try:
                tr_s = self.var_tr_size.get()
            except tk.TclError:
                tr_s = 12
            try:
                br_s = self.var_br_size.get()
            except tk.TclError:
                br_s = 12

            img, hotspot = create_cursor_image(
                size=size,
                color=fill_rgba,
                shape=self.var_shape.get(),
                border_color=border_rgba,
                border_thickness=self.var_border_thickness.get(),
                tr_text=self.var_tr_text.get(),
                tr_text_size=tr_s,
                br_text=self.var_br_text.get(),
                br_text_size=br_s,
                drop_shadow=self.var_drop_shadow.get(),
                base_name=self.var_base_name.get(),
                badge1_name=self.var_badge1_name.get(),
                badge2_name=self.var_badge2_name.get()
            )

            self.preview_image = img
            self.current_hotspot = hotspot

            # Update info label
            self.hotspot_label.config(text=f"Hotspot: {hotspot}")

            # Scale image so that the preview size is consistent (128x128) regardless of cursor resolution
            preview_scaled = img.resize((128, 128), Image.Resampling.NEAREST)

            self.img_tk = ImageTk.PhotoImage(preview_scaled)

            # Clear canvas and draw
            self.preview_canvas.delete("all")
            # Draw checkerboard pattern for transparency
            cw, ch = 150, 150
            for i in range(0, cw, 10):
                for j in range(0, ch, 10):
                    c = "#ffffff" if (i//10 + j//10) % 2 == 0 else "#cccccc"
                    self.preview_canvas.create_rectangle(i, j, i+10, j+10, fill=c, outline=c)

            # Center the image
            self.preview_canvas.create_image(cw//2, ch//2, image=self.img_tk, anchor=tk.CENTER)

        except Exception as e:
            print(f"Preview update error: {e}")

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

                try: tr_s = self.var_tr_size.get()
                except tk.TclError: tr_s = 12
                try: br_s = self.var_br_size.get()
                except tk.TclError: br_s = 12

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
                        br_text=self.var_br_text.get(),
                        br_text_size=br_s,
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


def run_gui():
    app = CursorGeneratorGUI()
    app.mainloop()


if __name__ == "__main__":
    run_gui()
