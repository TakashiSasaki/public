from PIL import Image, ImageDraw

def create_arrow_image(size=32, color=(128, 0, 128, 255)):
    """シンプルな矢印カーソル画像を作成する"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
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
    
    draw.polygon(points, fill=color, outline=(0, 0, 0, 255))
    
    return img
