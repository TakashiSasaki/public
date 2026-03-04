import math
import io
import json
import os
from pathlib import Path
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
    br_text_size=10,
    caption_text="",
    caption_text_size=10,
    caption_color=(0, 0, 0, 255),
    caption_bg_color=(255, 255, 255, 255),
    drop_shadow=False,
    base_name="",
    badge1_name="",
    badge2_name="",
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
        caption_text (str): 下部中央に描画するキャプション文字
        caption_text_size (int): キャプション文字サイズ
        caption_color (tuple): キャプション文字色 (R, G, B, A)
        caption_bg_color (tuple): キャプションの背景色 (R, G, B, A)
        
    Returns:
        tuple: (Imageオブジェクト, (hotspot_x, hotspot_y))
    """
    # ベースとなる画像
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    # シャドウ用として少し縮小するためのスケール調整（影がはみ出さないように）
    pad = 2 if drop_shadow else 0
    s_factor = (size - pad * 2) / 32.0
    s = s_factor
    
    # 描画位置のオフセット
    ox, oy = pad, pad
    
    # ホットスポットのオフセットも考慮
    hotspot = (ox, oy)
    
    if shape == "arrow":
        points = [
            (ox+0*s, oy+0*s),   # 先端
            (ox+0*s, oy+22*s),  # 左下
            (ox+6*s, oy+16*s),  # 切り欠き左
            (ox+10*s, oy+25*s), # 足の左下
            (ox+14*s, oy+23*s), # 足の右下
            (ox+10*s, oy+14*s), # 切り欠き右
            (ox+16*s, oy+14*s), # 右端
        ]
        hotspot = (int(ox+0), int(oy+0))
    elif shape == "triangle":
        points = [
            (ox+16*s, oy+0*s),  # 上端（中央）
            (ox+0*s, oy+30*s),  # 左下
            (ox+32*s, oy+30*s), # 右下
        ]
        hotspot = (int(ox+16*s), int(oy+0))
    elif shape == "cross":
        thick = 6 * s
        points = [
            (ox + 16*s - thick/2, oy + 0*s),
            (ox + 16*s + thick/2, oy + 0*s),
            (ox + 16*s + thick/2, oy + 16*s - thick/2),
            (ox + 32*s, oy + 16*s - thick/2),
            (ox + 32*s, oy + 16*s + thick/2),
            (ox + 16*s + thick/2, oy + 16*s + thick/2),
            (ox + 16*s + thick/2, oy + 32*s),
            (ox + 16*s - thick/2, oy + 32*s),
            (ox + 16*s - thick/2, oy + 16*s + thick/2),
            (ox + 0*s, oy + 16*s + thick/2),
            (ox + 0*s, oy + 16*s - thick/2),
            (ox + 16*s - thick/2, oy + 16*s - thick/2),
        ]
        hotspot = (int(ox+16*s), int(oy+16*s))
    else:
        # デフォルトは矢印
        points = [(ox+0, oy+0), (ox+0, oy+22*s), (ox+6*s, oy+16*s), (ox+16*s, oy+14*s)]
        hotspot = (int(ox+0), int(oy+0))
        
    # ドロップシャドウの描画
    if drop_shadow:
        from PIL import ImageFilter
        shadow_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        # 影は黒色で少しオフセット（右下にずらす）
        shadow_offset_x = int(size * 0.05)
        shadow_offset_y = int(size * 0.05)
        shadow_points = [(p[0] + shadow_offset_x, p[1] + shadow_offset_y) for p in points]
        
        # 影のシルエットを描画
        shadow_draw.polygon(shadow_points, fill=(0, 0, 0, 150))
        
        # ぼかしフィルターを適用
        shadow_blur_radius = max(1, size // 16)
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(shadow_blur_radius))
        
        # ベース画像に合成
        img.paste(shadow_img, (0, 0), shadow_img)
        
    draw = ImageDraw.Draw(img)

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

    if caption_text:
        caption_font = get_default_font(caption_text_size)
        cx, cy = size // 2, size - 2
        
        # 背景色が透明(Alpha 0)でなければ、矩形を描画する
        if len(caption_bg_color) == 4 and caption_bg_color[3] > 0:
            # Pillow >= 8.0.0 の draw.textbbox をサポート、古い場合は textsize にフォールバック
            try:
                left, top, right, bottom = draw.textbbox((cx, cy), caption_text, font=caption_font, anchor="mb")
                # 少しマージンを持たせる
                margin = 2
                draw.rectangle([left - margin, top - margin, right + margin, bottom + margin], fill=caption_bg_color)
            except AttributeError:
                # 非常に古いPillow向けフォールバック
                tw, th = draw.textsize(caption_text, font=caption_font)
                margin = 2
                draw.rectangle([cx - tw/2 - margin, cy - th - margin, cx + tw/2 + margin, cy + margin], fill=caption_bg_color)

        draw.text((cx, cy), caption_text, font=caption_font, fill=caption_color, anchor="mb")

    # 3. SVGオーバレイの合成 (Pictograms)
    if base_name or badge1_name or badge2_name:
        try:
            from svglib.svglib import svg2rlg
            from reportlab.graphics import renderPM
            
            # Load pictograms.json
            assets_dir = Path(__file__).parent.parent.parent.parent / "pictogram" / "src" / "assets"
            json_path = assets_dir / "pictograms.json"
            
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as f:
                    pictograms = json.load(f)
                    
                # Convert color tuple to CSS color
                r, g, b, a = color
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                
                def render_svg_to_pil(svg_data, target_size):
                    """black/white matte技法でSVGを透明背景でレンダリングする。"""
                    content = svg_data.get("content", "")
                    viewBox = svg_data.get("viewBox", "0 0 32 32")
                    stroke_w = 1.5 if viewBox == "0 0 16 16" else 2

                    full_svg = f'''<?xml version="1.0" encoding="utf-8"?>
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewBox}" width="{target_size}" height="{target_size}" fill="none" stroke="{hex_color}" stroke-width="{stroke_w}" stroke-linecap="round" stroke-linejoin="round">
                        {content}
                    </svg>'''

                    drawing = svg2rlg(io.BytesIO(full_svg.encode('utf-8')))
                    factor = target_size / float(drawing.width)
                    drawing.scale(factor, factor)
                    drawing.width = target_size
                    drawing.height = target_size

                    buf_w = io.BytesIO()
                    renderPM.drawToFile(drawing, buf_w, fmt="PNG", bg=0xFFFFFF)
                    buf_w.seek(0)
                    img_w = Image.open(buf_w).convert("RGB")

                    buf_b = io.BytesIO()
                    renderPM.drawToFile(drawing, buf_b, fmt="PNG", bg=0x000000)
                    buf_b.seek(0)
                    img_b = Image.open(buf_b).convert("RGB")

                    pw = list(img_w.getdata())
                    pb = list(img_b.getdata())
                    out = []
                    for (rw, gw, bw), (rb, gb, bb) in zip(pw, pb):
                        a = max(
                            1.0 - (rw - rb) / 255.0,
                            1.0 - (gw - gb) / 255.0,
                            1.0 - (bw - bb) / 255.0,
                            0.0,
                        )
                        a = min(a, 1.0)
                        if a > 0:
                            r = min(int(rb / a), 255)
                            g = min(int(gb / a), 255)
                            b = min(int(bb / a), 255)
                        else:
                            r, g, b = 0, 0, 0
                        out.append((r, g, b, int(a * 255)))

                    result = Image.new("RGBA", (target_size, target_size))
                    result.putdata(out)
                    return result

                # コンポジット用のキャンバス
                overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                
                # Base rendering
                if base_name and base_name in pictograms.get("bases", {}):
                    base_pil = render_svg_to_pil(pictograms["bases"][base_name], size)
                    overlay.paste(base_pil, (0, 0), base_pil)
                    
                # Badge 2 (Top Right)
                if badge2_name and badge2_name in pictograms.get("badges", {}):
                    badge2_size = size // 3
                    badge2_pil = render_svg_to_pil(pictograms["badges"][badge2_name], badge2_size)

                    # Clear the area under the badge
                    mask_draw = ImageDraw.Draw(overlay)
                    bx = size - badge2_size
                    by = 0
                    mask_draw.ellipse(
                        [(bx - badge2_size * 0.1, by - badge2_size * 0.1),
                         (bx + badge2_size * 1.1, by + badge2_size * 1.1)],
                        fill=(0, 0, 0, 0)
                    )

                    temp_badge_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                    temp_badge_layer.paste(badge2_pil, (bx, by), badge2_pil)
                    overlay = Image.alpha_composite(overlay, temp_badge_layer)

                # Badge 1 (Bottom Right)
                if badge1_name and badge1_name in pictograms.get("badges", {}):
                    badge1_size = size // 3
                    badge1_pil = render_svg_to_pil(pictograms["badges"][badge1_name], badge1_size)

                    mask_draw = ImageDraw.Draw(overlay)
                    bx = size - badge1_size
                    by = size - badge1_size
                    mask_draw.ellipse(
                        [(bx - badge1_size * 0.1, by - badge1_size * 0.1),
                         (bx + badge1_size * 1.1, by + badge1_size * 1.1)],
                        fill=(0, 0, 0, 0)
                    )

                    temp_badge_layer = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                    temp_badge_layer.paste(badge1_pil, (bx, by), badge1_pil)
                    overlay = Image.alpha_composite(overlay, temp_badge_layer)
                    
                # Finally composite the overlay onto the main cursor image
                img = Image.alpha_composite(img, overlay)
                
        except Exception as e:
            print(f"Error rendering SVG overlay: {e}")
            import traceback
            traceback.print_exc()
        
    return img, hotspot
