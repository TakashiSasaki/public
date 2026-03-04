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
    tr_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
    tr_bg_color: Tuple[int, int, int, int] = (0, 0, 0, 255),
    tr_aa: bool = True,
    tr_outline: bool = True,
    mr_color: Tuple[int, int, int, int] = (255, 255, 255, 255),
    mr_bg_color: Tuple[int, int, int, int] = (0, 0, 0, 255),
    mr_aa: bool = True,
    mr_outline: bool = True,
    drop_shadow: bool = False,
    base_name: str = "",
    badge1_name: str = "",
    badge2_name: str = "",
    svg_aa: bool = True,
    gradient_shift: float = 0.0, # 0.0 to 1.0 for waving effect
    caption_x_offset: int = 0,
    caption_wrap_width: int = 0, # If > 0, text wraps/loops
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
        
        img.paste(shadow_img, (0, 0), shadow_img)
        
    # Preparation for drawing the body (Fill)
    draw = ImageDraw.Draw(img)
    
    # Handle Gradient Fill if we wanted to support it as an option, 
    # but for now we'll just implement a simple two-color wave if color1!=color2
    # For now, let's just stick to the requested "waving gradient"
    # We'll use a linear gradient from the primary 'color' to a slightly lighter/darker version
    
    def _create_gradient_mask(size, points, shift):
        # Create a mask of the polygon
        mask = Image.new("L", (size, size), 0)
        ImageDraw.Draw(mask).polygon(points, fill=255)
        
        # Create gradient
        grad = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        g_draw = ImageDraw.Draw(grad)
        
        r, g, b, a = color
        # Secondary color for gradient (e.g. 50% lighter)
        c2 = (min(r+60, 255), min(g+60, 255), min(b+60, 255), a)
        
        for x in range(size):
            # Oscillate the gradient stop over time (0 to 1)
            # We'll use a sine wave based on x and shift
            t = (x / size + shift) % 1.0
            # Simple linear interp
            curr_r = int(r + (c2[0] - r) * (0.5 + 0.5 * math.sin(t * 2 * math.pi)))
            curr_g = int(g + (c2[1] - g) * (0.5 + 0.5 * math.sin(t * 2 * math.pi)))
            curr_b = int(b + (c2[2] - b) * (0.5 + 0.5 * math.sin(t * 2 * math.pi)))
            g_draw.line([(x, 0), (x, size)], fill=(curr_r, curr_g, curr_b, a))
        
        return grad, mask

    # Draw the main cursor body
    if gradient_shift != 0:
        grad_img, poly_mask = _create_gradient_mask(size, points, gradient_shift)
        img.paste(grad_img, (0, 0), poly_mask)
        # Still need the border
        try: draw.polygon(points, outline=border_color, width=border_thickness)
        except TypeError: draw.polygon(points, outline=border_color)
    else:
        try: draw.polygon(points, fill=color, outline=border_color, width=border_thickness)
        except TypeError: draw.polygon(points, fill=color, outline=border_color)

    def _render_text(draw_obj, text, font, pos, fill, bg, is_aa, is_outline, anchor):
        if not text: return
        
        # Get bounds
        try: left, top, right, bottom = draw_obj.textbbox(pos, text, font=font, anchor=anchor)
        except AttributeError:
            tw, th = draw_obj.textsize(text, font=font)
            px, py = pos
            if anchor == "mb": left, top, right, bottom = px - tw/2, py - th, px + tw/2, py
            elif anchor == "rt": left, top, right, bottom = px - tw, py, px, py + th
            elif anchor == "rm": left, top, right, bottom = px - tw, py - th/2, px, py + th/2
            else: left, top, right, bottom = px, py, px + tw, py + th

        # Draw background rectangle with alpha support
        if bg and bg[3] > 0:
            # We use a temp image to paste the rectangle with alpha correctly onto the RGBA img
            rect_img = Image.new("RGBA", (int(right-left)+2, int(bottom-top)+2), bg)
            img.paste(rect_img, (int(left)-1, int(top)-1), rect_img)

        def _draw_core(target_draw, p_x, p_y, f_color):
            if is_aa: target_draw.text((p_x, p_y), text, font=font, fill=f_color, anchor=anchor)
            else:
                # Aliased rendering using a 1-bit mask
                try: lb, tb, rb, bb = target_draw.textbbox((p_x, p_y), text, font=font, anchor=anchor)
                except AttributeError:
                    tw, th = target_draw.textsize(text, font=font)
                    if anchor == "mb": lb, tb, rb, bb = p_x - tw/2, p_y - th, p_x + tw/2, p_y
                    elif anchor == "rt": lb, tb, rb, bb = p_x - tw, p_y, p_x, p_y + th
                    elif anchor == "rm": lb, tb, rb, bb = p_x - tw, p_y - th/2, p_x, p_y + th/2
                    else: lb, tb, rb, bb = p_x, p_y, p_x + tw, p_y + th
                
                w, h = int(rb - lb) + 4, int(bb - tb) + 4
                if w <= 0 or h <= 0: return
                mask = Image.new("1", (w, h), 0)
                # Draw text to mask at 2,2 offset
                t_ix, t_iy = p_x - lb + 2, p_y - tb + 2
                ImageDraw.Draw(mask).text((t_ix, t_iy), text, font=font, fill=1, anchor=anchor)
                color_img = Image.new("RGBA", (w, h), f_color)
                # Paste using the 1-bit mask onto the main image
                img.paste(color_img, (int(lb) - 2, int(tb) - 2), mask)

        if is_outline:
            off = max(1, int(size * 0.03))
            _draw_core(draw_obj, pos[0]-off, pos[1], bg)
            _draw_core(draw_obj, pos[0]+off, pos[1], bg)
            _draw_core(draw_obj, pos[0], pos[1]-off, bg)
            _draw_core(draw_obj, pos[0], pos[1]+off, bg)
            
        _draw_core(draw_obj, pos[0], pos[1], fill)

    if caption_text:
        # If caption scrolls, adjust its center position
        cx = (size // 2) - caption_x_offset
        _render_text(draw, caption_text, get_default_font(caption_text_size), (cx, size - 1), caption_color, caption_bg_color, caption_aa, caption_outline, "mb")
        
        # Wrapping effect: Draw second copy following the first
        if caption_wrap_width > 0:
            _render_text(draw, caption_text, get_default_font(caption_text_size), (cx + caption_wrap_width, size - 1), caption_color, caption_bg_color, caption_aa, caption_outline, "mb")

    if tr_text:
        _render_text(draw, tr_text, get_default_font(tr_text_size), (size - 2, 2), tr_color, tr_bg_color, tr_aa, tr_outline, "rt")
    
    if mr_text:
        _render_text(draw, mr_text, get_default_font(mr_text_size), (size - 2, size // 2), mr_color, mr_bg_color, mr_aa, mr_outline, "rm")

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

def create_animated_cursor_frames(
    size: int = 32,
    total_frames: int = 15,
    anim_gradient: bool = True,
    anim_scroll: bool = True,
    **kwargs
) -> List[Tuple[Image.Image, Tuple[int, int]]]:
    """ANI用のフレームリストを生成する"""
    frames = []
    
    caption_text = kwargs.get("caption_text", "")
    cap_size = kwargs.get("caption_text_size", 10)
    
    # Measure caption width for scrolling
    text_width = 0
    if caption_text:
        font = get_default_font(cap_size)
        try:
            left, top, right, bottom = ImageDraw.Draw(Image.new("L", (1, 1))).textbbox((0, 0), caption_text, font=font)
            text_width = right - left
        except AttributeError:
            text_width, _ = ImageDraw.Draw(Image.new("L", (1, 1))).textsize(caption_text, font=font)
    
    for i in range(total_frames):
        g_shift = (i / total_frames) if anim_gradient else 0.0
        
        # Calculate scroll offset for wrapping loop
        c_off = 0
        wrap_w = 0
        if anim_scroll and caption_text:
            # Spacing between loop iterations (e.g. 1/3 of size)
            spacing = max(10, size // 3)
            wrap_w = text_width + spacing
            
            # Smoothly shift from 0 to wrap_w over total_frames
            c_off = int((i / total_frames) * wrap_w)

        frame_img, hotspot = create_cursor_image(
            size=size,
            gradient_shift=g_shift,
            caption_x_offset=c_off,
            caption_wrap_width=wrap_w,
            **kwargs
        )
        frames.append((frame_img, hotspot))
        
    return frames
