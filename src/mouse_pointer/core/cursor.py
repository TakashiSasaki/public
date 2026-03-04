import struct
import io
from typing import List, Tuple, Union
from pathlib import Path
from PIL import Image

def build_multi_cursor_binary(image_data_list: List[Tuple[Image.Image, Tuple[int, int]]]) -> bytes:
    """複数の画像（ペア: Image, (hx, hy)）を1つのWindowsの.cur形式のバイナリデータに変換する"""
    
    # 1. 画像をPNGとしてバイト配列に変換し、データを準備
    encoded_images = []
    for img, hotspot in image_data_list:
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        png_data = img_byte_arr.getvalue()
        
        width, height = img.size
        w = 0 if width == 256 else width
        # カーソルフォーマットでは、PNGを含める場合でも height は 2倍 (XOR + AND マスク分) に設定するのが本来の仕様とされる場合があるが、
        # 近年のWindowsではPNGの場合はそのままのheightでも認識される。念のため画像高さはそのまま使用。
        h = 0 if height == 256 else height
        
        encoded_images.append({
            'w': w, 'h': h, 
            'hx': hotspot[0], 'hy': hotspot[1],
            'size': len(png_data),
            'data': png_data
        })
        
    image_count = len(encoded_images)
    
    # 2. CURヘッダー (6 bytes)
    # idReserved(2)=0, idType(2)=2(cursor), idCount(2)=N
    header = struct.pack('<HHH', 0, 2, image_count)
    
    # 3. リスト分のディレクトリエントリ (16 bytes * N) を構築
    entries_binary = b""
    image_data_binary = b""
    
    # 最初の画像データのオフセットは ヘッダーサイズ(6) + エントリサイズ(16) * 画像数
    current_offset = 6 + (16 * image_count)
    
    for info in encoded_images:
        # width, height, colors(0), reserved(0), hotspot.x, hotspot.y, size_bytes, offset
        entry = struct.pack('<BBBBHHII', 
                            info['w'], info['h'], 0, 0, 
                            info['hx'], info['hy'], 
                            info['size'], current_offset)
        entries_binary += entry
        image_data_binary += info['data']
        
        current_offset += info['size']
        
    return header + entries_binary + image_data_binary

def save_cursor(image: Image.Image, filename: Union[str, Path], hotspot: Tuple[int, int] = (0, 0)) -> None:
    """単一の画像を.curファイルとして保存する（後方互換用）"""
    save_multi_cursor([(image, hotspot)], filename)

def save_multi_cursor(image_data_list: List[Tuple[Image.Image, Tuple[int, int]]], filename: Union[str, Path]) -> None:
    """複数の画像を1つの.curファイルとして保存する"""
    if not image_data_list:
        raise ValueError("image_data_list cannot be empty")
        
    data = build_multi_cursor_binary(image_data_list)
    with open(filename, 'wb') as f:
        f.write(data)
