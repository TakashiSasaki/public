import struct
from PIL import Image, ImageDraw
import io

def create_purple_cursor_image(size=32):
    """シンプルな紫色の矢印カーソル画像を作成する"""
    # RGBAモードで透明なキャンバスを作成
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # 紫色の矢印の頂点 (32x32スケールでの例)
    # 倍率に合わせてスケール
    s = size / 32
    points = [
        (0*s, 0*s),   # 先端
        (0*s, 22*s),  # 左下
        (6*s, 16*s),  # 切り欠き左
        (10*s, 25*s), # 足の左下
        (14*s, 23*s), # 足の右下
        (10*s, 14*s), # 切り欠き右
        (16*s, 14*s), # 右端
    ]
    
    # 紫色 (128, 0, 128) で塗りつぶし、黒の縁取り
    draw.polygon(points, fill=(128, 0, 128, 255), outline=(0, 0, 0, 255))
    
    return img

def save_as_cur(image, filename, hotspot=(0, 0)):
    """画像をWindowsの.cur形式で保存する"""
    # 1. 画像をPNGとしてバイト配列に変換（Vista以降はPNGを格納可能）
    img_byte_arr = io.BytesIO()
    image.save(img_byte_arr, format='PNG')
    png_data = img_byte_arr.getvalue()
    
    width, height = image.size
    
    # 2. CURヘッダー (ICONDIR)
    # idReserved: 2 bytes (0)
    # idType: 2 bytes (2 for CUR)
    # idCount: 2 bytes (1 image)
    header = struct.pack('<HHH', 0, 2, 1)
    
    # 3. CURディレクトリのエントリ (ICONDIRENTRY)
    # bWidth: 1 byte
    # bHeight: 1 byte
    # bColorCount: 1 byte (0 if >= 8bpp)
    # bReserved: 1 byte (0)
    # wXHotspot: 2 bytes
    # wYHotspot: 2 bytes
    # dwBytesInRes: 4 bytes (画像データのサイズ)
    # dwImageOffset: 4 bytes (ヘッダー(6) + エントリ(16) = 22)
    
    # 256pxの場合は 0 と記録するルール
    w = 0 if width == 256 else width
    h = 0 if height == 256 else height
    
    entry = struct.pack('<BBBBHHII', 
                        w, h, 0, 0, 
                        hotspot[0], hotspot[1], 
                        len(png_data), 22)
    
    # 4. 書き出し
    with open(filename, 'wb') as f:
        f.write(header)
        f.write(entry)
        f.write(png_data)

if __name__ == "__main__":
    cursor_img = create_purple_cursor_image(32)
    save_as_cur(cursor_img, "purple.cur", hotspot=(0, 0))
    print("purple.cur を生成しました。")
