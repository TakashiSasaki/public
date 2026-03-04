import tkinter as tk
from tkinter import ttk
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageTk

def build_fonts_tab(app, parent):
    """
    Builds the Fonts tab to preview available system fonts.
    'app' is the CursorGeneratorGUI instance (controller).
    """
    fonts_frame = ttk.Frame(parent)
    fonts_frame.pack(fill=tk.BOTH, expand=True)

    # State for font data
    # List of (filename, is_monospace, is_bitmap)
    all_fonts_info = []

    # Layout
    left_frame = ttk.Frame(fonts_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    right_frame = ttk.Frame(fonts_frame)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- Left Panel: Font List Controls ---
    filter_frame = ttk.LabelFrame(left_frame, text=" Filters ", padding=5)
    filter_frame.pack(fill=tk.X, pady=(0, 10))

    var_mono = tk.BooleanVar(value=False)
    var_bitmap = tk.BooleanVar(value=False)

    def on_filter_toggle():
        refresh_listbox()

    ttk.Checkbutton(filter_frame, text="等幅のみ", variable=var_mono, command=on_filter_toggle).pack(anchor=tk.W)
    ttk.Checkbutton(filter_frame, text="ビットマップのみ", variable=var_bitmap, command=on_filter_toggle).pack(anchor=tk.W)

    ttk.Label(left_frame, text="System Fonts:").pack(anchor=tk.W)

    list_frame = ttk.Frame(left_frame)
    list_frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    font_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, width=40, font=("Courier", 10))
    font_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=font_listbox.yview)

    # --- Scanning Logic ---
    font_dir = Path("C:/Windows/Fonts")
    
    def scan_fonts():
        nonlocal all_fonts_info
        if not font_dir.exists():
            return
        
        # Extensions to look for
        exts = [".ttf", ".ttc", ".fon"]
        files = []
        for ext in exts:
            files.extend(font_dir.glob(f"*{ext}"))
        files.sort(key=lambda x: x.name.lower())

        for f_path in files:
            name_lower = f_path.name.lower()
            is_mono = False
            is_bitmap = False

            # Bitmap heuristic 1: extension
            if name_lower.endswith(".fon"):
                is_bitmap = True
            
            # Bitmap heuristic 2: keywords
            pixel_keywords = ["pixel", "dot", "bitmap", "misaki", "gothic", "mincho"]
            # Note: "gothic" is often used for bitmap-embedded fonts in Japan, 
            # but let's stick to more explicit ones if possible. 
            # Actually, "pixel" and "dot" are most reliable.
            if any(k in name_lower for k in ["pixel", "dot", "bitmap"]):
                is_bitmap = True

            # Monospace check
            try:
                # Use a small size for measurement
                f = ImageFont.truetype(str(f_path), 16)
                w_i = f.getlength("i")
                w_w = f.getlength("W")
                if w_i == w_w and w_i > 0:
                    is_mono = True
            except:
                # If loading fails (like some .fon files at size 16), it might be a bitmap font
                if name_lower.endswith(".fon"):
                    is_bitmap = True
                pass
            
            all_fonts_info.append((f_path.name, is_mono, is_bitmap))

    def refresh_listbox():
        font_listbox.delete(0, tk.END)
        only_mono = var_mono.get()
        only_bitmap = var_bitmap.get()

        for name, is_m, is_b in all_fonts_info:
            if only_mono and not is_m:
                continue
            if only_bitmap and not is_b:
                continue
            font_listbox.insert(tk.END, name)

    # Initialize
    scan_fonts()
    refresh_listbox()

    # --- Right Panel: Preview ---
    preview_lbl = ttk.LabelFrame(right_frame, text="Font Preview", padding=10)
    preview_lbl.pack(fill=tk.BOTH, expand=True)

    # Controls inside preview
    ctrl_frame = ttk.Frame(preview_lbl)
    ctrl_frame.pack(fill=tk.X, pady=5)
    
    ttk.Label(ctrl_frame, text="Preview Text:").pack(side=tk.LEFT)
    preview_text_var = tk.StringVar(value="AaBbCc 123 漢字")
    ttk.Entry(ctrl_frame, textvariable=preview_text_var, width=30).pack(side=tk.LEFT, padx=5)
    
    ttk.Label(ctrl_frame, text="Size:").pack(side=tk.LEFT, padx=(10, 0))
    preview_size_var = tk.IntVar(value=32)
    ttk.Spinbox(ctrl_frame, from_=8, to=128, textvariable=preview_size_var, width=5).pack(side=tk.LEFT, padx=5)

    # Canvas
    preview_canvas = tk.Canvas(preview_lbl, bg="white", width=400, height=200, relief=tk.SUNKEN, borderwidth=1)
    preview_canvas.pack(fill=tk.BOTH, expand=True, pady=10)
    
    def update_font_preview(*args):
        selection = font_listbox.curselection()
        if not selection:
            return
            
        font_name = font_listbox.get(selection[0])
        font_path = font_dir / font_name
        
        text = preview_text_var.get()
        size = preview_size_var.get()
        
        try:
            # Flexible font loading for fixed-size/bitmap fonts (.fon)
            try:
                font = ImageFont.truetype(str(font_path), size)
                scale_factor = 1.0
                native_size = size
            except OSError as e:
                if "invalid pixel size" in str(e).lower() or "unimplemented feature" in str(e).lower():
                    # Probe for a working size (bitmap fonts usually support specific sizes like 12, 16, etc.)
                    working_font = None
                    working_size = size
                    # Prioritize common sizes, then try a full range between 4 and 48
                    probe_sizes = [16, 12, 13, 15, 20, 24, 8, 10, 11, 17, 18, 14, 19, 21, 22, 23] + list(range(4, 48))
                    
                    for s in probe_sizes:
                        try:
                            working_font = ImageFont.truetype(str(font_path), s)
                            working_size = s
                            break
                        except OSError:
                            continue
                    
                    if working_font:
                        font = working_font
                        scale_factor = size / working_size
                        native_size = working_size
                    else:
                        raise e
                else:
                    raise e

            # Create an image at the 'native' size of the font (or requested size if scalable)
            # We use a large enough margin.
            temp_w, temp_h = 1200, 600
            img = Image.new("RGBA", (temp_w, temp_h), (255, 255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # Draw grid/baseline
            draw.line([(0, temp_h//2), (temp_w, temp_h//2)], fill=(220, 220, 220, 255))
            draw.line([(temp_w//2, 0), (temp_w//2, temp_h)], fill=(220, 220, 220, 255))
            
            # Draw text
            draw.text((temp_w//2, temp_h//2), text, font=font, fill=(0, 0, 0, 255), anchor="mm")

            # Scale if necessary (e.g. for .fon files)
            if scale_factor != 1.0:
                # We crop to the relevant part before scaling to avoid huge images and keep it centered
                # But for simplicity in a preview, we can just scale the whole thing or a sufficient chunk.
                # Let's scale around the center.
                final_w = int(temp_w * scale_factor)
                final_h = int(temp_h * scale_factor)
                img = img.resize((final_w, final_h), Image.Resampling.NEAREST)
            else:
                final_w, final_h = temp_w, temp_h

            photo = ImageTk.PhotoImage(img)
            preview_canvas.delete("all")
            preview_canvas.image = photo 
            
            # Re-center
            cw = preview_canvas.winfo_width()
            ch = preview_canvas.winfo_height()
            preview_canvas.create_image(cw / 2, ch / 2, image=photo, anchor=tk.CENTER)
            
        except Exception as e:
            preview_canvas.delete("all")
            preview_canvas.create_text(
                preview_canvas.winfo_width() / 2, 
                preview_canvas.winfo_height() / 2, 
                text=f"Error loading font:\n{font_name}\n({str(e)})", 
                fill="red", 
                justify=tk.CENTER
            )

    font_listbox.bind("<<ListboxSelect>>", update_font_preview)
    preview_text_var.trace_add("write", update_font_preview)
    preview_size_var.trace_add("write", lambda *a: update_font_preview())
    
    preview_canvas.bind("<Configure>", lambda e: update_font_preview())
