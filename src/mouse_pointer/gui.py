import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageTk
from mouse_pointer.generators.basic import create_cursor_image
from mouse_pointer.core.cursor import save_cursor, save_multi_cursor

class CursorGeneratorGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Mouse Cursor Generator")
        self.geometry("600x500")
        self.configure(padx=20, pady=20)
        
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
        
        self.preview_image = None
        self.img_tk = None
        self.current_hotspot = (0, 0)
        
        self.create_widgets()
        self.update_preview()
        
    def hex_to_rgba(self, hex_color):
        hex_color = hex_color.lstrip('#')
        # Handle short hex format like #f00
        if len(hex_color) == 3:
            hex_color = ''.join(c + c for c in hex_color)
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b, 255)

    def create_widgets(self):
        # --- Left Panel (Controls) ---
        controls_frame = ttk.LabelFrame(self, text="Settings", padding=15)
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
        
        # Drop Shadow
        ttk.Label(controls_frame, text="Effects:").grid(row=row, column=0, sticky=tk.W, pady=5)
        shadow_chk = ttk.Checkbutton(controls_frame, text="Drop Shadow", variable=self.var_drop_shadow, command=self.on_change)
        shadow_chk.grid(row=row, column=1, sticky=tk.W, pady=5)
        row += 1
        
        # --- Right Panel (Preview & Action) ---
        right_frame = ttk.Frame(self)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Preview Area
        preview_group = ttk.LabelFrame(right_frame, text="Live Preview", padding=15)
        preview_group.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # To show transparency better, use a canvas with a grid background, or just a known color
        self.preview_canvas = tk.Canvas(preview_group, width=150, height=150, bg="#dddddd", highlightthickness=1, highlightbackground="#999")
        self.preview_canvas.pack(expand=True)
        
        self.hotspot_label = ttk.Label(preview_group, text="Hotspot: (0, 0)")
        self.hotspot_label.pack(pady=5)
        
        # Generate Button
        generate_btn = ttk.Button(right_frame, text="Generate .cur", command=self.generate_cur, style="Accent.TButton")
        generate_btn.pack(fill=tk.X, pady=10, ipady=10)
        
        # A simple style for the primary button
        style = ttk.Style(self)
        try:
            # Optionally use clam theme if available for a cleaner modern look
            style.theme_use('clam')
        except:
            pass
            
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
                drop_shadow=self.var_drop_shadow.get()
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
                        tr_text_size=tr_s, # 必要に応じてサイズ比率で動的計算してもよい
                        br_text=self.var_br_text.get(),
                        br_text_size=br_s,
                        drop_shadow=self.var_drop_shadow.get()
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
