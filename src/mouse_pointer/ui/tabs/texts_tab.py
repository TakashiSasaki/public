import tkinter as tk
from tkinter import ttk, colorchooser
from typing import TYPE_CHECKING, Any
from mouse_pointer.ui.components.preview_panel import PreviewPanel

if TYPE_CHECKING:
    from mouse_pointer.gui import CursorGeneratorGUI

def build_texts_tab(app: "CursorGeneratorGUI", parent: tk.Widget) -> ttk.Frame:
    """
    Builds the Text settings tab.
    """
    texts_frame = ttk.Frame(parent)
    texts_frame.pack(fill=tk.BOTH, expand=True)

    # Left Panel (Controls)
    left_panel = ttk.Frame(texts_frame, padding=10)
    left_panel.pack(side=tk.LEFT, fill=tk.Y)

    controls_frame = ttk.LabelFrame(left_panel, text="Text Settings", padding=10)
    controls_frame.pack(fill=tk.X, pady=(0, 10))

    row = 0
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

    # Right Panel (Preview)
    right_panel = ttk.Frame(texts_frame, padding=10)
    right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Reusable Preview Component
    preview = PreviewPanel(app, right_panel)
    
    # Initial update
    preview.update_preview()

    return texts_frame
