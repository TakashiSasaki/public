import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any

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
    size_spin.bind("<FocusOut>", app.on_change)
    row += 1

    # Shape
    ttk.Label(controls_frame, text=" Shape:").grid(row=row, column=0, sticky=tk.W, pady=5)
    shape_cb = ttk.Combobox(controls_frame, textvariable=app.var_shape, values=["arrow", "triangle", "cross"], state="readonly", width=10)
    shape_cb.grid(row=row, column=1, sticky=tk.EW, pady=5)
    shape_cb.bind("<<ComboboxSelected>>", app.on_change)
    row += 1

    # Fill Color
    ttk.Label(controls_frame, text=" Fill Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
    color_btn = ttk.Button(controls_frame, text="Choose...", command=lambda: app.choose_color("fill"))
    color_btn.grid(row=row, column=1, sticky=tk.EW, pady=5)
    app.color_preview = tk.Label(controls_frame, bg=app.var_color.get(), width=3)
    app.color_preview.grid(row=row, column=2, padx=5)
    row += 1

    # Border Color
    ttk.Label(controls_frame, text=" Border Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
    border_btn = ttk.Button(controls_frame, text="Choose...", command=lambda: app.choose_color("border"))
    border_btn.grid(row=row, column=1, sticky=tk.EW, pady=5)
    app.border_preview = tk.Label(controls_frame, bg=app.var_border_color.get(), width=3)
    app.border_preview.grid(row=row, column=2, padx=5)
    row += 1

    # TR Text
    ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
    row += 1
    ttk.Label(controls_frame, text=" TR Text:").grid(row=row, column=0, sticky=tk.W, pady=5)
    tr_entry = ttk.Entry(controls_frame, textvariable=app.var_tr_text, width=10)
    tr_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
    tr_entry.bind("<KeyRelease>", app.on_change)
    row += 1

    ttk.Label(controls_frame, text=" TR Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
    tr_spin = ttk.Spinbox(controls_frame, from_=8, to=72, textvariable=app.var_tr_size, width=5)
    tr_spin.grid(row=row, column=1, sticky=tk.EW, pady=5)
    tr_spin.bind("<FocusOut>", app.on_change)
    row += 1

    # MR Text
    ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=5)
    row += 1
    ttk.Label(controls_frame, text=" MR Text:").grid(row=row, column=0, sticky=tk.W, pady=5)
    mr_entry = ttk.Entry(controls_frame, textvariable=app.var_mr_text, width=10)
    mr_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
    mr_entry.bind("<KeyRelease>", app.on_change)
    row += 1

    ttk.Label(controls_frame, text=" MR Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
    mr_spin = ttk.Spinbox(controls_frame, from_=8, to=72, textvariable=app.var_mr_size, width=5)
    mr_spin.grid(row=row, column=1, sticky=tk.EW, pady=5)
    mr_spin.bind("<FocusOut>", app.on_change)
    row += 1

    # Caption Text
    ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=5)
    row += 1
    ttk.Label(controls_frame, text=" Caption:").grid(row=row, column=0, sticky=tk.W, pady=5)
    caption_entry = ttk.Entry(controls_frame, textvariable=app.var_caption_text, width=10)
    caption_entry.grid(row=row, column=1, sticky=tk.EW, pady=5)
    caption_entry.bind("<KeyRelease>", app.on_change)
    row += 1

    ttk.Label(controls_frame, text=" Cap Size:").grid(row=row, column=0, sticky=tk.W, pady=5)
    caption_spin = ttk.Spinbox(controls_frame, from_=8, to=72, textvariable=app.var_caption_size, width=5)
    caption_spin.grid(row=row, column=1, sticky=tk.EW, pady=5)
    caption_spin.bind("<FocusOut>", app.on_change)
    row += 1

    ttk.Label(controls_frame, text=" Cap Color:").grid(row=row, column=0, sticky=tk.W, pady=5)
    cap_color_btn = ttk.Button(controls_frame, text="Text Color", command=lambda: app.choose_color("caption_text"))
    cap_color_btn.grid(row=row, column=1, sticky=tk.EW, pady=5)
    app.cap_color_preview = tk.Label(controls_frame, bg=app.var_caption_color.get(), width=3)
    app.cap_color_preview.grid(row=row, column=2, padx=5)
    row += 1

    ttk.Label(controls_frame, text=" Cap BG:").grid(row=row, column=0, sticky=tk.W, pady=5)
    cap_bg_btn = ttk.Button(controls_frame, text="BG Color", command=lambda: app.choose_color("caption_bg"))
    cap_bg_btn.grid(row=row, column=1, sticky=tk.EW, pady=5)
    app.cap_bg_preview = tk.Label(controls_frame, bg=app.var_caption_bg_color.get(), width=3)
    app.cap_bg_preview.grid(row=row, column=2, padx=5)
    row += 1

    # Caption Render Options
    cap_opt_frame = ttk.Frame(controls_frame)
    cap_opt_frame.grid(row=row, column=1, columnspan=2, sticky=tk.W, pady=2)
    ttk.Checkbutton(cap_opt_frame, text="Anti-alias", variable=app.var_caption_aa, command=app.on_change).pack(side=tk.LEFT, padx=(0, 5))
    ttk.Checkbutton(cap_opt_frame, text="Outline", variable=app.var_caption_outline, command=app.on_change).pack(side=tk.LEFT)
    row += 1

    # --- SVG Overlays ---
    ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
    row += 1
    ttk.Label(controls_frame, text=" SVG Base:").grid(row=row, column=0, sticky=tk.W, pady=5)
    base_cb = ttk.Combobox(controls_frame, textvariable=app.var_base_name, values=[""] + list(app.pictograms_data.get("bases", {}).keys()), state="readonly", width=10)
    base_cb.grid(row=row, column=1, sticky=tk.EW, pady=5)
    base_cb.bind("<<ComboboxSelected>>", app.on_change)
    row += 1

    ttk.Label(controls_frame, text=" Badge 1 (MR):").grid(row=row, column=0, sticky=tk.W, pady=5)
    badge1_cb = ttk.Combobox(controls_frame, textvariable=app.var_badge1_name, values=[""] + list(app.pictograms_data.get("badges", {}).keys()), state="readonly", width=10)
    badge1_cb.grid(row=row, column=1, sticky=tk.EW, pady=5)
    badge1_cb.bind("<<ComboboxSelected>>", app.on_change)
    row += 1
    
    ttk.Label(controls_frame, text=" Badge 2 (TR):").grid(row=row, column=0, sticky=tk.W, pady=5)
    badge2_cb = ttk.Combobox(controls_frame, textvariable=app.var_badge2_name, values=[""] + list(app.pictograms_data.get("badges", {}).keys()), state="readonly", width=10)
    badge2_cb.grid(row=row, column=1, sticky=tk.EW, pady=5)
    badge2_cb.bind("<<ComboboxSelected>>", app.on_change)
    row += 1

    # Effects
    ttk.Separator(controls_frame, orient=tk.HORIZONTAL).grid(row=row, column=0, columnspan=3, sticky=tk.EW, pady=10)
    row += 1
    drop_shadow_chk = ttk.Checkbutton(controls_frame, text="Drop Shadow", variable=app.var_drop_shadow, command=app.on_change)
    drop_shadow_chk.grid(row=row, column=0, columnspan=2, sticky=tk.W, pady=2)
    row += 1
    show_grid_chk = ttk.Checkbutton(controls_frame, text="Show Grid", variable=app.var_show_grid, command=app.on_change)
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
        app.on_change()

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
    
    app.preview_canvas = tk.Canvas(canvas_frame, width=256, height=256, bg="#f0f0f0", relief=tk.SUNKEN, borderwidth=1)
    app.preview_canvas.pack(padx=10, pady=10, anchor=tk.CENTER)

    info_frame = ttk.Frame(canvas_frame)
    info_frame.pack(pady=(0, 10))

    app.hotspot_label = ttk.Label(info_frame, text="Hotspot: (0, 0)")
    app.hotspot_label.pack(side=tk.LEFT, padx=10)

    app.coordinate_label = ttk.Label(info_frame, text="Coord: -")
    app.coordinate_label.pack(side=tk.LEFT, padx=10)

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
    
    # Build grids inside the tabs
    app._build_pictogram_list(tab_bases, app.pictograms_data.get("bases", {}), app._on_base_selected)
    app._build_pictogram_list(tab_badges, app.pictograms_data.get("badges", {}), app._on_badge_selected)

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
        
        # We'll use a label to show the raw image. 
        # Using a canvas might be better for transparency grid, 
        # but for simplicity let's start with a Label on a gray background or with a small checkerboard if possible.
        # Actually, let's use a Label and we'll handle the images in gui.py
        lbl = tk.Label(cell, bg="#cccccc", width=0, height=0, bd=1, relief=tk.SOLID)
        lbl.pack(pady=2)
        app.unscaled_preview_labels[s] = lbl

    # Output Actions (Bottom)
    action_frame = ttk.Frame(preview_frame)
    action_frame.pack(fill=tk.X, pady=(10, 0))
    
    gen_btn = ttk.Button(action_frame, text="Generate .cur (Multi-res)", command=app.generate_cur)
    gen_btn.pack(side=tk.RIGHT, pady=10)
