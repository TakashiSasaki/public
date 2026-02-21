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
    tr_text="",
    tr_text_size=10,
    br_text="",
    br_text_size=10
):
    """
    指定されたパラメータでカーソル画像を生成する。
    
    Args:
        size (int): 画像サイズ（正方形）
        color (tuple): 塗りつぶしの色 (R, G, B, A)
        shape (str): 形状 ("arrow", "triangle", "cross")
        border_color (tuple): 枠線の色 (R, G, B, A)
        border_thickness (int): 枠線の太さ
        tr_text (str): 右上に描画する文字
        tr_text_size (int): 右上の文字サイズ
        br_text (str): 右下に描画する文字
        br_text_size (int): 右下の文字サイズ
        
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
        
    # 2. 右上・右下の文字を描画
    def draw_outlined_text(text, position, font, anchor="lt"):
        if not text:
            return
        brightness = sum(color[:3]) / 3
        text_color = (0, 0, 0, 255) if brightness > 128 else (255, 255, 255, 255)
        text_bg = (255, 255, 255, 255) if brightness > 128 else (0, 0, 0, 255)
        
        offset = max(1, int(size * 0.03))
        x, y = position
        
        # フチドリ
        draw.text((x-offset, y), text, font=font, fill=text_bg, anchor=anchor)
        draw.text((x+offset, y), text, font=font, fill=text_bg, anchor=anchor)
        draw.text((x, y-offset), text, font=font, fill=text_bg, anchor=anchor)
        draw.text((x, y+offset), text, font=font, fill=text_bg, anchor=anchor)
        # ナナメのフチドリも追加するとより綺麗ですが、ここでは上下左右のみ
        
        # 本体
        draw.text((x, y), text, font=font, fill=text_color, anchor=anchor)

    if tr_text:
        tr_font = get_default_font(tr_text_size)
        draw_outlined_text(tr_text, (size - 2, 2), tr_font, anchor="rt")
        
    if br_text:
        br_font = get_default_font(br_text_size)
        draw_outlined_text(br_text, (size - 2, size - 2), br_font, anchor="rb")
        
    return img, hotspot
