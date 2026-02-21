import math
from PIL import Image, ImageDraw, ImageFont

def get_default_font(size):
    """シンプルなフォントを取得する（フォントがない場合のフォールバック用）"""
    try:
        # Windowsの代表的なフォントを試す
        return ImageFont.truetype("segoeui.ttf", size)
    except IOError:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except IOError:
            return ImageFont.load_default()

def create_cursor_image(
    size=32, 
    color=(128, 0, 128, 255), 
    shape="arrow", 
    border_color=(0, 0, 0, 255), 
    border_thickness=1,
    inner_char=""
):
    """
    指定されたパラメータでカーソル画像を生成する。
    
    Args:
        size (int): 画像サイズ（正方形）
        color (tuple): 塗りつぶしの色 (R, G, B, A)
        shape (str): 形状 ("arrow", "triangle", "cross")
        border_color (tuple): 枠線の色 (R, G, B, A)
        border_thickness (int): 枠線の太さ
        inner_char (str): 内部に描画する1文字
        
    Returns:
        tuple: (Imageオブジェクト, (hotspot_x, hotspot_y))
    """
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    s = size / 32.0
    hotspot = (0, 0)
    
    if shape == "arrow":
        points = [
            (0*s, 0*s),   # 先端
            (0*s, 22*s),  # 左下
            (6*s, 16*s),  # 切り欠き左
            (10*s, 25*s), # 足の左下
            (14*s, 23*s), # 足の右下
            (10*s, 14*s), # 切り欠き右
            (16*s, 14*s), # 右端
        ]
        hotspot = (0, 0)
    elif shape == "triangle":
        points = [
            (16*s, 0*s),  # 上端（中央）
            (0*s, 30*s),  # 左下
            (32*s, 30*s), # 右下
        ]
        hotspot = (int(16*s), 0)
    elif shape == "cross":
        thick = 6 * s
        points = [
            (16*s - thick/2, 0*s),
            (16*s + thick/2, 0*s),
            (16*s + thick/2, 16*s - thick/2),
            (32*s, 16*s - thick/2),
            (32*s, 16*s + thick/2),
            (16*s + thick/2, 16*s + thick/2),
            (16*s + thick/2, 32*s),
            (16*s - thick/2, 32*s),
            (16*s - thick/2, 16*s + thick/2),
            (0*s, 16*s + thick/2),
            (0*s, 16*s - thick/2),
            (16*s - thick/2, 16*s - thick/2),
        ]
        hotspot = (int(16*s), int(16*s))
    else:
        # デフォルトは矢印
        points = [(0, 0), (0, 22*s), (6*s, 16*s), (16*s, 14*s)]
        hotspot = (0, 0)

    # 1. 枠線の描画（太さをシミュレーションするため、少しずらした位置に複数回描画するか、Pillow 9.2以降のwidthパラメータを使用）
    try:
        # widthがサポートされている場合
        draw.polygon(points, fill=color, outline=border_color, width=border_thickness)
    except TypeError:
        # サポートされていない古いPillowの場合は単純な描画
        draw.polygon(points, fill=color, outline=border_color)
        
    # 2. 内側の文字を描画（もしあれば）
    if inner_char:
        # 1文字だけ取得
        char = inner_char[0]
        
        # 文字のサイズは形状によって調整が必要だが、とりあえず全体サイズの一定比率とする
        font_size = int(size * 0.4)
        if shape == "arrow":
            # 矢印の場合は左上に寄りすぎないように少し右下にずらす
            text_x = 4 * s
            text_y = 6 * s
        elif shape == "triangle":
            text_x = 16 * s - font_size * 0.3
            text_y = 10 * s
        elif shape == "cross":
            text_x = 16 * s - font_size * 0.3
            text_y = 16 * s - font_size * 0.5
        else:
            text_x = 8 * s
            text_y = 8 * s
            
        font = get_default_font(font_size)
        
        # 文字の枠線（白文字・黒フチなどで見やすくする）
        # 反対色を簡易的に計算（ここでは白または黒）
        brightness = sum(color[:3]) / 3
        text_color = (0, 0, 0, 255) if brightness > 128 else (255, 255, 255, 255)
        text_bg = (255, 255, 255, 255) if brightness > 128 else (0, 0, 0, 255)
        
        # フチドリ文字
        offset = max(1, int(size * 0.03))
        draw.text((text_x-offset, text_y), char, font=font, fill=text_bg)
        draw.text((text_x+offset, text_y), char, font=font, fill=text_bg)
        draw.text((text_x, text_y-offset), char, font=font, fill=text_bg)
        draw.text((text_x, text_y+offset), char, font=font, fill=text_bg)
        
        # 本体文字
        draw.text((text_x, text_y), char, font=font, fill=text_color)
        
    return img, hotspot
