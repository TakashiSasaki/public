import argparse
import sys
from mouse_pointer.core.cursor import save_cursor
from mouse_pointer.generators.basic import create_cursor_image
from mouse_pointer.gui import run_gui

def main():
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
    gen_parser.add_argument("--br-text", type=str, default="", help="Text to display in the bottom-right corner")
    gen_parser.add_argument("--br-size", type=int, default=12, help="Font size for bottom-right text")
    gen_parser.add_argument("--caption-text", "-c", type=str, default="", help="Text to display below the cursor")
    gen_parser.add_argument("--caption-size", "-cs", type=int, default=12, help="Font size for caption text")
    gen_parser.add_argument("--caption-color", "-cc", type=str, default="black", help="Color of the caption text (name or hex)")
    gen_parser.add_argument("--caption-bg-color", "-cbc", type=str, default="white", help="Background color of the caption (name or hex, 'none' for transparent)")
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
        
        def parse_color(c_str, default_rgba):
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
        cap_color = parse_color(args.caption_color, (0, 0, 0, 255))
        cap_bg_color = parse_color(args.caption_bg_color, (255, 255, 255, 255))
        
        print(f"Generating multi-resolution (32, 48, 64) {args.color} {args.shape} cursor at {args.output}...")
        
        # CLIでもマルチ解像度エクスポートをデフォルトとする
        from mouse_pointer.core.cursor import save_multi_cursor
        sizes_to_generate = [32, 48, 64]
        multi_image_data = []
        
        for s in sizes_to_generate:
            img, hotspot = create_cursor_image(
                size=s, 
                color=color, 
                shape=args.shape,
                tr_text=args.tr_text,
                tr_text_size=args.tr_size,
                br_text=args.br_text,
                br_text_size=args.br_size,
                caption_text=args.caption_text,
                caption_text_size=args.caption_size,
                caption_color=cap_color,
                caption_bg_color=cap_bg_color,
                drop_shadow=args.drop_shadow
            )
            multi_image_data.append((img, hotspot))
            
        save_multi_cursor(multi_image_data, args.output)
        print("Done!")

if __name__ == "__main__":
    main()
