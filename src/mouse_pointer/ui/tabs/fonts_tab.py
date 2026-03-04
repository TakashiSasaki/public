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

    # Layout
    # Left: Listbox for fonts
    # Right: Preview area

    left_frame = ttk.Frame(fonts_frame)
    left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

    right_frame = ttk.Frame(fonts_frame)
    right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- Left Panel: Font List ---
    ttk.Label(left_frame, text="System Fonts (C:\\Windows\\Fonts\\*.ttf)").pack(anchor=tk.W)

    list_frame = ttk.Frame(left_frame)
    list_frame.pack(fill=tk.BOTH, expand=True)

    scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    font_listbox = tk.Listbox(list_frame, yscrollcommand=scrollbar.set, width=40, font=("Courier", 10))
    font_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    scrollbar.config(command=font_listbox.yview)

    # Load Fonts
    font_dir = Path("C:/Windows/Fonts")
    font_files = []
    if font_dir.exists():
        font_files = sorted([f.name for f in font_dir.glob("*.ttf")])
        for f_name in font_files:
            font_listbox.insert(tk.END, f_name)

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
        
        # Draw on PIL Image
        img = Image.new("RGBA", (800, 400), (255, 255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype(str(font_path), size)
            
            # Draw grid/baseline
            draw.line([(0, 200), (800, 200)], fill=(200, 200, 200, 255)) # Baseline
            draw.line([(400, 0), (400, 400)], fill=(200, 200, 200, 255)) # Center axis
            
            # Draw text centered
            try:
                draw.text((400, 200), text, font=font, fill=(0, 0, 0, 255), anchor="md")
            except ValueError:
                draw.text((400, 200), text, font=font, fill=(0, 0, 0, 255))

            photo = ImageTk.PhotoImage(img)
            preview_canvas.delete("all")
            # Store reference to prevent garbage collection
            preview_canvas.image = photo 
            # Place at center
            preview_canvas.create_image(
                preview_canvas.winfo_width() / 2, 
                preview_canvas.winfo_height() / 2, 
                image=photo, 
                anchor=tk.CENTER
            )
        except Exception as e:
            preview_canvas.delete("all")
            preview_canvas.create_text(
                preview_canvas.winfo_width() / 2, 
                preview_canvas.winfo_height() / 2, 
                text=f"Error loading font:\n{str(e)}", 
                fill="red", 
                justify=tk.CENTER
            )

    font_listbox.bind("<<ListboxSelect>>", update_font_preview)
    preview_text_var.trace_add("write", update_font_preview)
    preview_size_var.trace_add("write", lambda *a: update_font_preview())
    
    # Needs to bind canvas resize to re-center image
    preview_canvas.bind("<Configure>", lambda e: update_font_preview())
