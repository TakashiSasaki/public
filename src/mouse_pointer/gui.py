import tkinter as tk
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageTk
from mouse_pointer.generators.basic import create_cursor_image
from mouse_pointer.core.cursor import save_cursor

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
        self.var_char = tk.StringVar(value="")
        
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
        
        # Inner Character
        ttk.Label(controls_frame, text="Inner Char:").grid(row=row, column=0, sticky=tk.W, pady=5)
        char_entry = ttk.Entry(controls_frame, textvariable=self.var_char, width=5)
        char_entry.grid(row=row, column=1, sticky=tk.W, pady=5)
        char_entry.bind("<KeyRelease>", self.on_change)
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
            
            img, hotspot = create_cursor_image(
                size=size,
                color=fill_rgba,
                shape=self.var_shape.get(),
                border_color=border_rgba,
                border_thickness=self.var_border_thickness.get(),
                inner_char=self.var_char.get()
            )
            
            self.preview_image = img
            self.current_hotspot = hotspot
            
            # Update info label
            self.hotspot_label.config(text=f"Hotspot: {hotspot}")
            
            # Scale image for preview if it's too small
            scale_factor = min(120 // size, max(1, 150 // size))
            if scale_factor > 1:
                preview_scaled = img.resize((size * scale_factor, size * scale_factor), Image.Resampling.NEAREST)
            else:
                preview_scaled = img
                
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
                save_cursor(self.preview_image, file_path, hotspot=self.current_hotspot)
                messagebox.showinfo("Success", f"Cursor saved successfully to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save cursor:\n{str(e)}")

def run_gui():
    app = CursorGeneratorGUI()
    app.mainloop()

if __name__ == "__main__":
    run_gui()
