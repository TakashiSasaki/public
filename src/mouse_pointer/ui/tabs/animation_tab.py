import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from typing import TYPE_CHECKING
from mouse_pointer.generators.basic import create_animated_cursor_frames
from mouse_pointer.core.cursor import save_animated_cursor

if TYPE_CHECKING:
    from mouse_pointer.gui import CursorGeneratorGUI

def build_animation_tab(app: "CursorGeneratorGUI", parent: tk.Widget) -> ttk.Frame:
    """
    Builds the Animation settings tab.
    """
    anim_frame = ttk.Frame(parent, padding=10)
    anim_frame.pack(fill=tk.BOTH, expand=True)

    # Left Panel: Controls
    controls_frame = ttk.LabelFrame(anim_frame, text="Animation Settings", padding=10)
    controls_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

    ttk.Checkbutton(controls_frame, text="Enable Gradient Wave (Base)", variable=app.var_anim_gradient).pack(anchor=tk.W, pady=5)
    ttk.Checkbutton(controls_frame, text="Enable Caption Scrolling", variable=app.var_anim_scroll).pack(anchor=tk.W, pady=5)

    ttk.Label(controls_frame, text="Total Frames:").pack(anchor=tk.W, pady=(10, 0))
    ttk.Spinbox(controls_frame, from_=2, to=60, textvariable=app.var_anim_frames, width=10).pack(anchor=tk.W, pady=5)

    ttk.Label(controls_frame, text="Frame Delay (Jiffies, 1/60s):").pack(anchor=tk.W, pady=(10, 0))
    ttk.Spinbox(controls_frame, from_=1, to=120, textvariable=app.var_anim_speed, width=10).pack(anchor=tk.W, pady=5)
    ttk.Label(controls_frame, text="(10 ≈ 166ms delay)", font=("Segoe UI", 8)).pack(anchor=tk.W)

    def generate_ani():
        filename = filedialog.asksaveasfilename(
            defaultextension=".ani",
            filetypes=[("Animated Cursor", "*.ani")],
            title="Save Animated Cursor"
        )
        if not filename: return
        
        try:
            # Prepare kwargs from current app state
            def safe_int(var, default):
                try: 
                    v = var.get()
                    return int(v) if v else default
                except (ValueError, tk.TclError): 
                    return default

            def get_text_data(color_var, bg_var, alpha_var):
                rgb = app.hex_to_rgba(color_var.get())[:3]
                bg_rgb = app.hex_to_rgba(bg_var.get())[:3]
                return (*rgb, 255), (*bg_rgb, alpha_var.get())

            tr_c, tr_bg = get_text_data(app.var_tr_color, app.var_tr_bg_color, app.var_tr_bg_alpha)
            mr_c, mr_bg = get_text_data(app.var_mr_color, app.var_mr_bg_color, app.var_mr_bg_alpha)
            cap_c, cap_bg = get_text_data(app.var_caption_color, app.var_caption_bg_color, app.var_caption_bg_alpha)

            kwargs = {
                "color": app.hex_to_rgba(app.var_color.get()),
                "shape": app.var_shape.get(),
                "border_color": app.hex_to_rgba(app.var_border_color.get()),
                "border_thickness": app.var_border_thickness.get(),
                "tr_text": app.var_tr_text.get(),
                "tr_text_size": safe_int(app.var_tr_size, 12),
                "tr_color": tr_c, "tr_bg_color": tr_bg,
                "tr_aa": app.var_tr_aa.get(), "tr_outline": app.var_tr_outline.get(),
                "mr_text": app.var_mr_text.get(),
                "mr_text_size": safe_int(app.var_mr_size, 12),
                "mr_color": mr_c, "mr_bg_color": mr_bg,
                "mr_aa": app.var_mr_aa.get(), "mr_outline": app.var_mr_outline.get(),
                "caption_text": app.var_caption_text.get(),
                "caption_text_size": safe_int(app.var_caption_size, 12),
                "caption_color": cap_c, "caption_bg_color": cap_bg,
                "caption_aa": app.var_caption_aa.get(), "caption_outline": app.var_caption_outline.get(),
                "drop_shadow": app.var_drop_shadow.get(),
                "base_name": app.var_base_name.get(),
                "badge1_name": app.var_badge1_name.get(),
                "badge2_name": app.var_badge2_name.get(),
                "svg_aa": app.var_svg_aa.get(),
            }

            total_f = int(app.var_anim_frames.get())
            frames = create_animated_cursor_frames(
                size=app.var_size.get(),
                total_frames=total_f,
                anim_gradient=app.var_anim_gradient.get(),
                anim_scroll=app.var_anim_scroll.get(),
                **kwargs
            )
            
            # save_animated_cursor expects frames as List[List[Tuple[Image, hotspot]]]
            # where the inner list is different resolutions. 
            # For now we only generate the current size resolution per frame.
            ani_frames = [[f] for f in frames]
            
            save_animated_cursor(ani_frames, filename, jif_rate=int(app.var_anim_speed.get()))
            messagebox.showinfo("Success", f"Animated cursor saved to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate ANI: {e}")

    ttk.Button(controls_frame, text="Generate .ani File", command=generate_ani).pack(fill=tk.X, pady=20)

    # Info/Help panel
    info_frame = ttk.LabelFrame(anim_frame, text="Info", padding=10)
    info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    
    help_text = (
        "Animated Cursor (.ani) Features:\n\n"
        "• Gradient Wave: Rotates a horizontal color gradient across the cursor base.\n\n"
        "• Caption Scrolling: If the caption is wider than the cursor width, "
        "it will automatically scroll left over the animation frames.\n\n"
        "Note: Previewing the full animation in-app is not yet supported. "
        "Use Windows settings to test your generated .ani file."
    )
    ttk.Label(info_frame, text=help_text, wraplength=300, justify=tk.LEFT).pack(anchor=tk.NW)

    return anim_frame
