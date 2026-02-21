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
        
        # 16進数カラー対応の簡易ヘルパー
        if args.color.startswith("#"):
            hex_c = args.color.lstrip('#')
            if len(hex_c) == 3: hex_c = ''.join(c*2 for c in hex_c)
            color = (int(hex_c[0:2], 16), int(hex_c[2:4], 16), int(hex_c[4:6], 16), 255)
        else:
            color = color_map.get(args.color.lower(), (128, 0, 128, 255))
        
        print(f"Generating {args.color} {args.shape} cursor at {args.output}...")
        img, hotspot = create_cursor_image(size=args.size, color=color, shape=args.shape)
        save_cursor(img, args.output, hotspot=hotspot)
        print("Done!")

if __name__ == "__main__":
    main()
