import io
import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any, Optional, Dict, List, Tuple
from PIL import Image, ImageTk
from mouse_pointer.generators.basic import render_svg_to_pil
from mouse_pointer.ui.components.preview_panel import PreviewPanel

if TYPE_CHECKING:
    from mouse_pointer.gui import CursorGeneratorGUI

def build_badges_tab(app: "CursorGeneratorGUI", parent: tk.Widget) -> ttk.Frame:
    """
    Builds the Badges selection tab.
    """
    badges_frame = ttk.Frame(parent)
    badges_frame.pack(fill=tk.BOTH, expand=True)

    # Left Panel (Controls)
    left_panel = ttk.Frame(badges_frame, padding=10)
    left_panel.pack(side=tk.LEFT, fill=tk.Y)

    controls_frame = ttk.LabelFrame(left_panel, text="Badge Selection", padding=10)
    controls_frame.pack(fill=tk.X, pady=(0, 10))

    row = 0
    # Badge 1 (MR)
    ttk.Label(controls_frame, text=" Badge 1 (MR):").grid(row=row, column=0, sticky=tk.W, pady=5)
    badge1_cb = ttk.Combobox(controls_frame, textvariable=app.var_badge1_name, values=[""] + list(app.pictograms_data.get("badges", {}).keys()), state="readonly", width=10)
    badge1_cb.grid(row=row, column=1, sticky=tk.EW, pady=5)
    row += 1

    # Badge 2 (TR)
    ttk.Label(controls_frame, text=" Badge 2 (TR):").grid(row=row, column=0, sticky=tk.W, pady=5)
    badge2_cb = ttk.Combobox(controls_frame, textvariable=app.var_badge2_name, values=[""] + list(app.pictograms_data.get("badges", {}).keys()), state="readonly", width=10)
    badge2_cb.grid(row=row, column=1, sticky=tk.EW, pady=5)
    row += 1

    # Right Panel (Pictogram list & Preview)
    right_panel = ttk.Frame(badges_frame, padding=10)
    right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Reusable Preview Component
    preview = PreviewPanel(app, right_panel)

    # Badges Pictograms Gallery
    picto_frame = ttk.LabelFrame(right_panel, text="Badges Pictograms")
    picto_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))

    # Assets cache for thumbnails (attach to frame to prevent GC)
    badges_frame.assets = {
        "thumb_cache": [],
    }

    def on_badge_selected(name: str):
        # We'll default to setting Badge 1 if one is clicked in this tab, 
        # or we could add a toggle for which badge slot to fill.
        # For simplicity, let's keep it as Badge 1 for now.
        app.var_badge1_name.set(name)

    def build_grid(parent, items, thumb_size):
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
            pil_img = render_svg_to_pil(svg_data, target_size=thumb_size, color_hex=stroke_color, anti_alias=True)
            img_tk = ImageTk.PhotoImage(pil_img if pil_img else Image.new("RGBA", (thumb_size, thumb_size), (0, 0, 0, 0)))
            badges_frame.assets["thumb_cache"].append(img_tk)
            tk.Button(cell, image=img_tk, relief=tk.FLAT, bd=0, cursor="hand2", command=lambda n=name: on_badge_selected(n)).pack()
            ttk.Label(cell, text=name, font=("Segoe UI", 7), wraplength=thumb_size + 16, justify=tk.CENTER).pack()

    build_grid(picto_frame, app.pictograms_data.get("badges", {}), 40)

    # Initial update
    preview.update_preview()

    return badges_frame
