import math
import io
import json
import os
from pathlib import Path
from typing import Tuple, Optional, Any, List, Dict
from PIL import Image, ImageDraw, ImageFont

def get_default_font(size: int) -> ImageFont.ImageFont:
    """シンプルなフォントを取得する（フォントがない場合のフォールバック用）"""
    try:
        # Windowsの代表的なフォントを試す
        return ImageFont.truetype("segoeui.ttf", size)
    except IOError:
        try:
            return ImageFont.truetype("arial.ttf", size)
        except IOError:
            return ImageFont.load_default()

def render_svg_to_pil(svg_data: Dict[str, Any], target_size: int, color_hex: str = "#800080", anti_alias: bool = True) -> Optional[Image.Image]:
    """
    black/white matte技法でSVGを透明背景でレンダリングする。
    anti_aliasがFalseの場合、高解像度でレンダリングしてからNEARESTで縮小してジャギーを出す。
    """
    try:
        from svglib.svglib import svg2rlg
        from reportlab.graphics import renderPM

        content = svg_data.get("content", "")
        viewBox = svg_data.get("viewBox", "0 0 32 32")
        stroke_w = 1.5 if viewBox == "0 0 16 16" else 2

        # アンチエイリアス無効化のために高解像度で描画して縮小する
        render_size = target_size * 4 if not anti_alias else target_size
        
        full_svg = f'''<?xml version="1.0" encoding="utf-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewBox}" width="{render_size}" height="{render_size}" fill="none" stroke="{color_hex}" stroke-width="{stroke_w * (render_size/target_size)}" stroke-linecap="round" stroke-linejoin="round">
    {content}
</svg>'''

        drawing = svg2rlg(io.BytesIO(full_svg.encode('utf-8')))
        factor = render_size / float(drawing.width)
        drawing.scale(factor, factor)
        drawing.width = render_size
        drawing.height = render_size

        # White Background Matte
        buf_w = io.BytesIO()
        renderPM.drawToFile(drawing, buf_w, fmt="PNG", bg=0xFFFFFF)
        buf_w.seek(0)
        img_w = Image.open(buf_w).convert("RGB")

        # Black Background Matte
        buf_b = io.BytesIO()
        renderPM.drawToFile(drawing, buf_b, fmt="PNG", bg=0x000000)
        buf_b.seek(0)
        img_b = Image.open(buf_b).convert("RGB")

        pw = list(img_w.getdata())
        pb = list(img_b.getdata())
        out: List[Tuple[int, int, int, int]] = []
        for (rw, gw, bw), (rb, gb, bb) in zip(pw, pb):
            # Alpha calculation from matte
            a = max(1.0 - (rw - rb) / 255.0, 1.0 - (gw - gb) / 255.0, 1.0 - (bw - bb) / 255.0, 0.0)
            a = min(a, 1.0)
            if a > 0:
                r, g, b = min(int(rb / a), 255), min(int(gb / a), 255), min(int(bb / a), 255)
            else:
                r, g, b = 0, 0, 0
            out.append((r, g, b, int(a * 255)))

        result = Image.new("RGBA", (render_size, render_size))
        result.putdata(out)

        if not anti_alias:
            # 縮小時、NEARESTを指定することでジャギーを残す
            result = result.resize((target_size, target_size), Image.Resampling.NEAREST)
        
        return result
    except Exception as e:
        print(f"SVG render error: {e}")
        return None

def create_cursor_image(
    size: int = 32, 
    color: Tuple[int, int, int, int] = (128, 0, 128, 255), 
    shape: str = "arrow", 
    border_color: Tuple[int, int, int, int] = (0, 0, 0, 255), 
    border_thickness: int = 1,
    tr_text: str = "",
    tr_text_size: int = 10,
    mr_text: str = "",
    mr_text_size: int = 10,
    caption_text: str = "",
    caption_text_size: int = 10,
    caption_color: Tuple[int, int, int, int] = (0, 0, 0, 255),
    caption_bg_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
    caption_aa: bool = True,
    caption_outline: bool = False,
    drop_shadow: bool = False,
    base_name: str = "",
    badge1_name: str = "",
    badge2_name: str = "",
    svg_aa: bool = True,
) -> Tuple[Image.Image, Tuple[int, int]]:
    """指定されたパラメータでカーソル画像を生成する。"""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    pad = 2 if drop_shadow else 0
    s_factor = (size - pad * 2) / 32.0
    s = s_factor
    ox, oy = pad, pad
    hotspot = (ox, oy)
    
    if shape == "arrow":
        points = [(ox+0*s, oy+0*s), (ox+0*s, oy+22*s), (ox+6*s, oy+16*s), (ox+10*s, oy+25*s), (ox+14*s, oy+23*s), (ox+10*s, oy+14*s), (ox+16*s, oy+14*s)]
        hotspot = (int(ox+0), int(oy+0))
    elif shape == "triangle":
        points = [(ox+16*s, oy+0*s), (ox+0*s, oy+30*s), (ox+32*s, oy+30*s)]
        hotspot = (int(ox+16*s), int(oy+0))
    elif shape == "cross":
        thick = 6 * s
        points = [(ox + 16*s - thick/2, oy + 0*s), (ox + 16*s + thick/2, oy + 0*s), (ox + 16*s + thick/2, oy + 16*s - thick/2), (ox + 32*s, oy + 16*s - thick/2), (ox + 32*s, oy + 16*s + thick/2), (ox + 16*s + thick/2, oy + 16*s + thick/2), (ox + 16*s + thick/2, oy + 32*s), (ox + 16*s - thick/2, oy + 32*s), (ox + 16*s - thick/2, oy + 16*s + thick/2), (ox + 0*s, oy + 16*s + thick/2), (ox + 0*s, oy + 16*s - thick/2), (ox + 16*s - thick/2, oy + 16*s - thick/2)]
        hotspot = (int(ox+16*s), int(oy+16*s))
    else:
        points = [(ox+0, oy+0), (ox+0, oy+22*s), (ox+6*s, oy+16*s), (ox+16*s, oy+14*s)]
        hotspot = (int(ox+0), int(oy+0))
        
    if drop_shadow:
        from PIL import ImageFilter
        shadow_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        shadow_draw = ImageDraw.Draw(shadow_img)
        shadow_offset_x, shadow_offset_y = int(size * 0.05), int(size * 0.05)
        shadow_points = [(p[0] + shadow_offset_x, p[1] + shadow_offset_y) for p in points]
        shadow_draw.polygon(shadow_points, fill=(0, 0, 0, 150))
        shadow_blur_radius = max(1, size // 16)
        shadow_img = shadow_img.filter(ImageFilter.GaussianBlur(shadow_blur_radius))
        img.paste(shadow_img, (0, 0), shadow_img)
        
    draw = ImageDraw.Draw(img)

    if caption_text:
        caption_font = get_default_font(caption_text_size)
        cx, cy = size // 2, size - 1
        def _draw_caption_text(target_draw, pos_x, pos_y, text, font, fill, is_aa):
            if is_aa: target_draw.text((pos_x, pos_y), text, font=font, fill=fill, anchor="mb")
            else:
                try: left, top, right, bottom = target_draw.textbbox((pos_x, pos_y), text, font=font, anchor="mb")
                except AttributeError:
                    tw, th = target_draw.textsize(text, font=font)
                    left, top, right, bottom = pos_x - tw/2, pos_y - th, pos_x + tw/2, pos_y
                w, h = int(right - left) + 4, int(bottom - top) + 4
                if w <= 0 or h <= 0: return
                mask = Image.new("1", (w, h), 0)
                ImageDraw.Draw(mask).text((2, 2), text, font=font, fill=1, anchor="lt")
                color_img = Image.new("RGBA", (w, h), fill)
                target_draw._image.paste(color_img, (int(left) - 2, int(top) - 2), mask)

        if caption_outline:
            offset = max(1, int(size * 0.03))
            _draw_caption_text(draw, cx - offset, cy, caption_text, caption_font, caption_bg_color, caption_aa)
            _draw_caption_text(draw, cx + offset, cy, caption_text, caption_font, caption_bg_color, caption_aa)
            _draw_caption_text(draw, cx, cy - offset, caption_text, caption_font, caption_bg_color, caption_aa)
            _draw_caption_text(draw, cx, min(cy + offset, size - 1), caption_text, caption_font, caption_bg_color, caption_aa)
        else:
            if len(caption_bg_color) == 4 and caption_bg_color[3] > 0:
                try:
                    left, top, right, bottom = draw.textbbox((cx, cy), caption_text, font=caption_font, anchor="mb")
                    draw.rectangle([left - 1, top - 1, right + 1, min(bottom + 1, size - 2)], fill=caption_bg_color)
                except AttributeError:
                    tw, th = draw.textsize(caption_text, font=caption_font)
                    draw.rectangle([cx - tw/2 - 1, cy - th - 1, cx + tw/2 + 1, cy - 1], fill=caption_bg_color)
        _draw_caption_text(draw, cx, cy, caption_text, caption_font, caption_color, caption_aa)

    try: draw.polygon(points, fill=color, outline=border_color, width=border_thickness)
    except TypeError: draw.polygon(points, fill=color, outline=border_color)
        
    def draw_outlined_text(text, position, font, anchor="lt"):
        if not text: return
        brightness = sum(color[:3]) / 3
        text_color = (0, 0, 0, 255) if brightness > 128 else (255, 255, 255, 255)
        text_bg = (255, 255, 255, 255) if brightness > 128 else (0, 0, 0, 255)
        offset = max(1, int(size * 0.03))
        x, y = position
        draw.text((x-offset, y), text, font=font, fill=text_bg, anchor=anchor)
        draw.text((x+offset, y), text, font=font, fill=text_bg, anchor=anchor)
        draw.text((x, y-offset), text, font=font, fill=text_bg, anchor=anchor)
        draw.text((x, y+offset), text, font=font, fill=text_bg, anchor=anchor)
        draw.text((x, y), text, font=font, fill=text_color, anchor=anchor)

    if tr_text: draw_outlined_text(tr_text, (size - 2, 2), get_default_font(tr_text_size), anchor="rt")
    if mr_text: draw_outlined_text(mr_text, (size - 2, size // 2), get_default_font(mr_text_size), anchor="rm")

    if base_name or badge1_name or badge2_name:
        try:
            assets_dir = Path(__file__).parent.parent.parent.parent / "pictogram" / "src" / "assets"
            json_path = assets_dir / "pictograms.json"
            if json_path.exists():
                with open(json_path, "r", encoding="utf-8") as f: pictograms = json.load(f)
                r, g, b, a = color
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                overlay = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                
                if base_name and base_name in pictograms.get("bases", {}):
                    base_pil = render_svg_to_pil(pictograms["bases"][base_name], size, hex_color, svg_aa)
                    if base_pil: overlay.paste(base_pil, (0, 0), base_pil)
                    
                if badge2_name and badge2_name in pictograms.get("badges", {}):
                    badge2_size = size // 3
                    badge2_pil = render_svg_to_pil(pictograms["badges"][badge2_name], badge2_size, hex_color, svg_aa)
                    if badge2_pil:
                        mask_draw, bx, by = ImageDraw.Draw(overlay), size - badge2_size, 0
                        mask_draw.ellipse([(bx - badge2_size*0.1, by - badge2_size*0.1), (bx + badge2_size*1.1, by + badge2_size*1.1)], fill=(0, 0, 0, 0))
                        temp = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                        temp.paste(badge2_pil, (bx, by), badge2_pil)
                        overlay = Image.alpha_composite(overlay, temp)

                if badge1_name and badge1_name in pictograms.get("badges", {}):
                    badge1_size = size // 3
                    badge1_pil = render_svg_to_pil(pictograms["badges"][badge1_name], badge1_size, hex_color, svg_aa)
                    if badge1_pil:
                        mask_draw, bx, by = ImageDraw.Draw(overlay), size - badge1_size, (size - badge1_size) // 2
                        mask_draw.ellipse([(bx - badge1_size*0.1, by - badge1_size*0.1), (bx + badge1_size*1.1, by + badge1_size*1.1)], fill=(0, 0, 0, 0))
                        temp = Image.new("RGBA", (size, size), (0, 0, 0, 0))
                        temp.paste(badge1_pil, (bx, by), badge1_pil)
                        overlay = Image.alpha_composite(overlay, temp)
                img = Image.alpha_composite(img, overlay)
        except Exception as e: print(f"Error rendering SVG overlay: {e}")
    return img, hotspot
