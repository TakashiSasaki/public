import argparse
from mouse_pointer.core.cursor import save_cursor
from mouse_pointer.generators.basic import create_arrow_image

def main():
    parser = argparse.ArgumentParser(description="Generate Windows mouse cursors.")
    parser.add_argument("--color", type=str, default="purple", help="Color of the cursor (name or hex)")
    parser.add_argument("--output", type=str, default="output.cur", help="Output filename")
    parser.add_argument("--size", type=int, default=32, help="Cursor size (px)")
    
    args = parser.parse_args()
    
    # 簡易的な色指定の処理
    color_map = {
        "purple": (128, 0, 128, 255),
        "red": (255, 0, 0, 255),
        "blue": (0, 0, 255, 255),
        "green": (0, 128, 0, 255),
    }
    
    color = color_map.get(args.color.lower(), (128, 0, 128, 255))
    
    print(f"Generating {args.color} cursor at {args.output}...")
    img = create_arrow_image(size=args.size, color=color)
    save_cursor(img, args.output, hotspot=(0, 0))
    print("Done!")

if __name__ == "__main__":
    main()
