import tkinter as tk
from tkinter import ttk
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageTk

CHARSET_MAP = {
    0: "0 (ANSI)",
    1: "1 (Default)",
    2: "2 (Symbol)",
    77: "77 (Mac)",
    128: "128 (ShiftJIS)",
    129: "129 (Hangeul)",
    130: "130 (Johab)",
    134: "134 (GB2312)",
    136: "136 (CHINESEBIG5)",
    161: "161 (Greek)",
    162: "162 (Turkish)",
    163: "163 (Vietnamese)",
    177: "177 (Hebrew)",
    178: "178 (Arabic)",
    186: "186 (Baltic)",
    204: "204 (Russian)",
    222: "222 (Thai)",
    238: "238 (EastEurope)",
    255: "255 (OEM)",
}

def parse_fnt_charset(filepath):
    """
    NE/PE ヘッダを持つ .fon または直接の .fnt ファイルから dfCharSet と CodePage を取得する
    戻り値: (charset: int|None, codepage: int|None)
    """
    try:
        with open(filepath, "rb") as f:
            data = f.read()
            if len(data) < 2: return None, None
            
            def extract_from_fnt(fnt_data):
                cs = None
                cp = None
                if len(fnt_data) > 85:
                    cs = fnt_data[85]
                # Windows 3.0+ FNT header length is at least 148.
                # dfReserved (offset 135, 16 bytes) sometimes contains a codepage in the first 4 bytes for some custom bitmap fonts
                if len(fnt_data) >= 139:
                    # In some (mainly unofficial/localized) fonts, this field holds the code page.
                    potential_cp = int.from_bytes(fnt_data[135:139], byteorder='little')
                    if potential_cp > 0 and potential_cp < 65535: # Plausible code page
                        cp = potential_cp
                return cs, cp

            # .fnt (raw)
            if data[0:2] in (b'\x00\x02', b'\x00\x03'):
                return extract_from_fnt(data)
                    
            # .fon (MZ header)
            if data[0:2] != b'MZ':
                return None, None
                
            pe_ne_offset = int.from_bytes(data[0x3C:0x3E], byteorder='little')
            if pe_ne_offset >= len(data): return None, None
                
            signature = data[pe_ne_offset:pe_ne_offset+2]
            
            if signature == b'NE':
                # NE Header Parsing
                res_table_offset_rel = int.from_bytes(data[pe_ne_offset + 0x24: pe_ne_offset + 0x26], byteorder='little')
                res_table_offset = pe_ne_offset + res_table_offset_rel
                
                shift_count = int.from_bytes(data[res_table_offset:res_table_offset+2], byteorder='little')
                p = res_table_offset + 2
                
                while p < len(data):
                    type_id = int.from_bytes(data[p:p+2], byteorder='little')
                    if type_id == 0: break
                        
                    res_count = int.from_bytes(data[p+2:p+4], byteorder='little')
                    
                    if type_id == 0x8008: # RT_FONT
                        entry_p = p + 8
                        res_data_offset = int.from_bytes(data[entry_p:entry_p+2], byteorder='little') << shift_count
                        res_length = int.from_bytes(data[entry_p+2:entry_p+4], byteorder='little') << shift_count
                        
                        if res_data_offset + res_length <= len(data):
                            fnt_data = data[res_data_offset: res_data_offset + res_length]
                            return extract_from_fnt(fnt_data)
                        return None, None
                        
                    p += 8 + (res_count * 12)
                    
            # PE is more complex and less common for basic 16-bit .fon, ignoring for now
            
    except Exception:
        pass
    return None

def build_fonts_tab(app, parent, tab_type="vector"):
    """
    Builds the Fonts tab to preview available system fonts.
    'app' is the CursorGeneratorGUI instance (controller).
    'tab_type' is either "vector" (TTF/TTC) or "bitmap" (FON/FNT).
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
    if tab_type == "bitmap":
        ttk.Checkbutton(filter_frame, text="ビットマップのみ", variable=var_bitmap, command=on_filter_toggle).pack(anchor=tk.W)
    else:
        var_bitmap.set(False)

    list_label = "Vector Fonts:" if tab_type == "vector" else "Bitmap Fonts:"
    ttk.Label(left_frame, text=list_label).pack(anchor=tk.W)

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
        if tab_type == "vector":
            exts = [".ttf", ".ttc", ".otf"]
        else:
            exts = [".fon", ".fnt"]
            
        files = []
        for ext in exts:
            files.extend(font_dir.glob(f"*{ext}"))
        files.sort(key=lambda x: x.name.lower())

        for f_path in files:
            name_lower = f_path.name.lower()
            is_mono = False
            is_bitmap = False
            is_supported = True

            # Bitmap heuristic 1: extension
            if name_lower.endswith(".fon") or name_lower.endswith(".fnt"):
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

            # Fast Support Check for Vector Fonts
            # Symbol fonts or fonts missing standard Latin glyphs are filtered out.
            if tab_type == "vector" and not is_bitmap:
                try:
                    f = ImageFont.truetype(str(f_path), 16)
                    # Test drawing 'A' and 'B' on small masks. 
                    # If they map to the same image (e.g. symbol-only or missing glyph), mark as unsupported.
                    img_a = Image.new("L", (20, 20), 0)
                    ImageDraw.Draw(img_a).text((0, 0), "A", font=f, fill=255)
                    img_b = Image.new("L", (20, 20), 0)
                    ImageDraw.Draw(img_b).text((0, 0), "B", font=f, fill=255)
                    
                    if img_a.tobytes() == img_b.tobytes():
                        is_supported = False
                except:
                    is_supported = False
            
            all_fonts_info.append((f_path.name, is_mono, is_bitmap, is_supported))

    def refresh_listbox():
        font_listbox.delete(0, tk.END)
        only_mono = var_mono.get()
        only_bitmap = var_bitmap.get()

        for name, is_m, is_b, is_s in all_fonts_info:
            if tab_type == "vector" and not is_s:
                continue
            if only_mono and not is_m:
                continue
            if only_bitmap and not is_b:
                continue
            font_listbox.insert(tk.END, name)

    # Initialize
    scan_fonts()
    refresh_listbox()

    # --- Right Panel: Preview & Info ---
    # Info Area
    info_frame = ttk.LabelFrame(right_frame, text=" Font Details ", padding=10)
    info_frame.pack(fill=tk.X, pady=(0, 10))

    var_font_path = tk.StringVar(value="-")
    var_font_size = tk.StringVar(value="-")
    var_font_charset = tk.StringVar(value="-")
    var_font_codepage = tk.StringVar(value="-")

    path_row = ttk.Frame(info_frame)
    path_row.pack(fill=tk.X)
    ttk.Label(path_row, text="Full Path:", width=10).pack(side=tk.LEFT)
    ttk.Entry(path_row, textvariable=var_font_path, state="readonly").pack(side=tk.LEFT, fill=tk.X, expand=True)

    size_row = ttk.Frame(info_frame)
    size_row.pack(fill=tk.X, pady=(5, 0))
    ttk.Label(size_row, text="File Size:", width=10).pack(side=tk.LEFT)
    ttk.Label(size_row, textvariable=var_font_size, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)

    if tab_type == "bitmap":
        attr_row = ttk.Frame(info_frame)
        attr_row.pack(fill=tk.X, pady=(5, 0))
        ttk.Label(attr_row, text="CharSet:", width=10).pack(side=tk.LEFT)
        ttk.Label(attr_row, textvariable=var_font_charset, font=("Segoe UI", 9, "bold"), width=15).pack(side=tk.LEFT)
        ttk.Label(attr_row, text="CodePage:", width=10).pack(side=tk.LEFT)
        ttk.Label(attr_row, textvariable=var_font_codepage, font=("Segoe UI", 9, "bold")).pack(side=tk.LEFT)

    # Preview Area
    preview_lbl = ttk.LabelFrame(right_frame, text=" Font Preview ", padding=10)
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
        
        # Update Info
        var_font_path.set(str(font_path))
        try:
            sz_bytes = font_path.stat().st_size
            var_font_size.set(f"{sz_bytes / 1024:,.1f} KB ({sz_bytes:,} bytes)")
        except:
            var_font_size.set("Unknown")

        var_font_charset.set("N/A")
        var_font_codepage.set("N/A")
        if font_name.lower().endswith((".fon", ".fnt")):
            cs, cp = parse_fnt_charset(str(font_path))
            if cs is not None:
                cs_name = CHARSET_MAP.get(cs, f"{cs} (Unknown)")
                var_font_charset.set(cs_name)
            if cp is not None:
                var_font_codepage.set(str(cp))
            else:
                var_font_codepage.set("Not specified")

        text = preview_text_var.get()
        size = preview_size_var.get()
        
        try:
            # Flexible font loading for fixed-size/bitmap fonts (.fon)
            try:
                font = ImageFont.truetype(str(font_path), size)
                scale_factor = 1.0
                native_size = size
            except OSError as e:
                err_msg = str(e).lower()
                if "invalid pixel size" in err_msg or "unimplemented feature" in err_msg:
                    # Probe for a working size (bitmap fonts usually support specific sizes like 12, 16, etc.)
                    working_font = None
                    working_size = size
                    
                    # Range for common bitmap pixels. Expanding to 48.
                    probe_sizes = [16, 12, 13, 15, 20, 24, 8, 10, 11, 14, 17, 18, 19, 21, 22, 23, 25, 26, 27, 28, 29, 30, 31, 32]
                    probe_sizes += list(range(4, 49))
                    
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
                        # If still no luck, it's likely an unsupported vector font or corrupted
                        raise ValueError("This font format (e.g., Windows legacy vector font) is not supported by the rendering engine.")
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
