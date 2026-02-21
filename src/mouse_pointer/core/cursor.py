import struct
import io
from PIL import Image

def build_cursor_binary(image: Image.Image, hotspot=(0, 0)) -> bytes:
    """画像をWindowsの.cur形式のバイナリデータに変換する"""
    # 1. 画像をPNGとしてバイト配列に変換（Vista以降はPNGを格納可能）
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    png_data = img_byte_arr.getvalue()
    
    width, height = image.size
    
    # 2. CURヘッダー (6 bytes)
    header = struct.pack('<HHH', 0, 2, 1)
    
    # 3. CURディレクトリのエントリ (16 bytes)
    w = 0 if width == 256 else width
    h = 0 if height == 256 else height
    
    entry = struct.pack('<BBBBHHII', 
                        w, h, 0, 0, 
                        hotspot[0], hotspot[1], 
                        len(png_data), 22) # Header(6) + Entry(16) = 22
    
    return header + entry + png_data

def save_cursor(image: Image.Image, filename: str, hotspot=(0, 0)):
    """画像を.curファイルとして保存する"""
    data = build_cursor_binary(image, hotspot)
    with open(filename, 'wb') as f:
        f.write(data)
