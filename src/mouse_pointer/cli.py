import argparse
import sys
from typing import Tuple, Any, Dict
from mouse_pointer.core.cursor import save_cursor
from mouse_pointer.generators.basic import create_cursor_image
from mouse_pointer.gui import run_gui

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate Windows mouse cursors.")
    subparsers = parser.add_subparsers(dest="command", help="Sub-commands")
    
    # GUI Command
    gui_parser = subparsers.add_parser("gui", help="Launch the GUI cursor generator")
    
    # CLI Generate Command
    gen_parser = subparsers.add_parser("generate", help="Generate cursor from command line")
    gen_parser.add_argument("--color", type=str, default="purple", help="Color of the cursor (name or hex)")
    gen_parser.add_argument("--output", type=str, default="output.cur", help="Output filename")
    gen_parser.add_argument("--size", type=int, default=32, help="Cursor size (px)")
    gen_parser.add_argument("--shape", type=str, default="arrow", choices=["arrow", "triangle", "cross"], help="Shape of the cursor")
    gen_parser.add_argument("--tr-text", type=str, default="", help="Text to display in the top-right corner")
    gen_parser.add_argument("--tr-size", type=int, default=12, help="Font size for top-right text")
    gen_parser.add_argument("--mr-text", type=str, default="", help="Text to display in the middle-right area")
    gen_parser.add_argument("--mr-size", type=int, default=12, help="Font size for middle-right text")
    gen_parser.add_argument("--caption-text", "-c", type=str, default="", help="Text to display below the cursor")
    gen_parser.add_argument("--caption-size", "-cs", type=int, default=12, help="Font size for caption text")
    gen_parser.add_argument("--caption-color", "-cc", type=str, default="black", help="Color of the caption text (name or hex)")
    gen_parser.add_argument("--caption-bg-color", "-cbc", type=str, default="white", help="Background color of the caption (name or hex, 'none' for transparent)")
    # Enhanced Text/Border
    gen_parser.add_argument("--border-color", type=str, default="black", help="Color of the cursor border")
    gen_parser.add_argument("--border-thickness", type=int, default=1, help="Thickness of the cursor border")
    gen_parser.add_argument("--tr-color", type=str, default="white", help="Top-right text color")
    gen_parser.add_argument("--tr-bg-color", type=str, default="black", help="Top-right background color")
    gen_parser.add_argument("--mr-color", type=str, default="white", help="Middle-right text color")
    gen_parser.add_argument("--mr-bg-color", type=str, default="black", help="Middle-right background color")
    
    # SVG Bases & Badges
    gen_parser.add_argument("--base-name", type=str, default="", help="Name of the base SVG to use")
    gen_parser.add_argument("--badge1-name", type=str, default="", help="Name of the first badge SVG")
    gen_parser.add_argument("--badge2-name", type=str, default="", help="Name of the second badge SVG")
    gen_parser.add_argument("--no-svg-aa", action="store_true", help="Disable SVG anti-aliasing")
    
    # Animations
    gen_parser.add_argument("--anim-gradient", action="store_true", help="Enable gradient waving animation")
    gen_parser.add_argument("--anim-scroll", action="store_true", help="Enable caption scroll animation")
    gen_parser.add_argument("--anim-frames", type=int, default=15, help="Total frames for animation")
    gen_parser.add_argument("--anim-speed", type=int, default=10, help="Frame delay in jiffies (1/60s)")
    
    # Existing features
    gen_parser.add_argument("--drop-shadow", action="store_true", help="Enable drop shadow effect")
    
    args = parser.parse_args()
    
    # GUI is default if no command provided, or 'gui' is explicitly called
    if args.command == "gui" or args.command is None:
        run_gui()
        return

    if args.command == "generate":
        # 簡易的な色指定の処理
        color_map = {
            "purple": (128, 0, 128, 255),
            "red": (255, 0, 0, 255),
            "blue": (0, 0, 255, 255),
            "green": (0, 128, 0, 255),
            "black": (0, 0, 0, 255),
            "white": (255, 255, 255, 255),
        }
        
        def parse_color(c_str: str, default_rgba: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
            if c_str.lower() == "none" or c_str == "":
                return (0, 0, 0, 0) # Transparent
            if c_str.startswith("#"):
                hex_c = c_str.lstrip('#')
                if len(hex_c) == 3: hex_c = ''.join(c*2 for c in hex_c)
                try:
                    return (int(hex_c[0:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16), 255)
                except ValueError:
                    return default_rgba
            return color_map.get(c_str.lower(), default_rgba)

        # Parse colors
        color = parse_color(args.color, (128, 0, 128, 255))
        b_color = parse_color(args.border_color, (0, 0, 0, 255))
        tr_c = parse_color(args.tr_color, (255, 255, 255, 255))
        tr_bg = parse_color(args.tr_bg_color, (0, 0, 0, 255))
        mr_c = parse_color(args.mr_color, (255, 255, 255, 255))
        mr_bg = parse_color(args.mr_bg_color, (0, 0, 0, 255))
        cap_color = parse_color(args.caption_color, (0, 0, 0, 255))
        cap_bg_color = parse_color(args.caption_bg_color, (255, 255, 255, 255))
        
        # Common kwargs for rendering
        render_kwargs = {
            "color": color,
            "shape": args.shape,
            "border_color": b_color,
            "border_thickness": args.border_thickness,
            "tr_text": args.tr_text,
            "tr_text_size": args.tr_size,
            "tr_color": tr_c, "tr_bg_color": tr_bg,
            "mr_text": args.mr_text,
            "mr_text_size": args.mr_size,
            "mr_color": mr_c, "mr_bg_color": mr_bg,
            "caption_text": args.caption_text,
            "caption_text_size": args.caption_size,
            "caption_color": cap_color,
            "caption_bg_color": cap_bg_color,
            "drop_shadow": args.drop_shadow,
            "base_name": args.base_name,
            "badge1_name": args.badge1_name,
            "badge2_name": args.badge2_name,
            "svg_aa": not args.no_svg_aa
        }
        
        if args.output.lower().endswith(".ani"):
            print(f"Generating animated {args.color} {args.shape} cursor at {args.output}...")
            from mouse_pointer.generators.basic import create_animated_cursor_frames
            from mouse_pointer.core.cursor import save_animated_cursor
            
            frames = create_animated_cursor_frames(
                size=args.size,
                total_frames=args.anim_frames,
                anim_gradient=args.anim_gradient,
                anim_scroll=args.anim_scroll,
                **render_kwargs
            )
            # CLI uses single specified size for ANI currently (or we could use multi-res, but single is fine for now)
            ani_frames = [[f] for f in frames]
            save_animated_cursor(ani_frames, args.output, jif_rate=args.anim_speed)
        else:
            print(f"Generating multi-resolution (32, 48, 64) {args.color} {args.shape} cursor at {args.output}...")
            from mouse_pointer.core.cursor import save_multi_cursor
            
            sizes_to_generate = [32, 48, 64]
            multi_image_data = []
            
            for s in sizes_to_generate:
                img, hotspot = create_cursor_image(size=s, **render_kwargs)
                multi_image_data.append((img, hotspot))
                
            save_multi_cursor(multi_image_data, args.output)
            
        print("Done!")

if __name__ == "__main__":
    main()
