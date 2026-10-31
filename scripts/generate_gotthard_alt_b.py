import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

DATA_THUMBS = Path("data/thumbnails")
DATA_THUMBS.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR = Path(r"C:\Users\Sohail\.gemini\antigravity\brain\eb4bd0b7-d463-4e01-b351-a971179e01ed")

def get_font(size, bold=True):
    font_names = ["arialbd.ttf" if bold else "arial.ttf", "impact.ttf", "segoeui.ttf"]
    for fn in font_names:
        try:
            return ImageFont.truetype(fn, size)
        except Exception:
            pass
    return ImageFont.load_default()

def draw_text_with_outline(draw, pos, text, font, fill=(255, 255, 255), outline=(0, 0, 0), width=4):
    x, y = pos
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx*dx + dy*dy <= width*width:
                draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)

def generate_alt_b():
    scratch_dir = Path("scratch")
    scratch_dir.mkdir(parents=True, exist_ok=True)
    
    # Clip 6: Miner Breakthrough
    bt_frame = scratch_dir / "gotthard_thumb_src_breakthrough.jpg"
    subprocess.run([
        "ffmpeg", "-y", "-ss", "3.0", "-i", "data/flow_clips/gotthard_scene_6.mp4",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920",
        "-vframes", "1", "-q:v", "1", str(bt_frame)
    ], check=True)

    base = Image.open(bt_frame).convert("RGBA")
    enh_c = ImageEnhance.Contrast(base)
    base = enh_c.enhance(1.15)
    
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    for y in range(0, 520):
        alpha = int(180 * (1.0 - y / 520.0))
        draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))
        
    for y in range(1300, 1920):
        alpha = int(220 * ((y - 1300) / 620.0))
        draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))

    # Badge
    f_badge = get_font(32, bold=True)
    draw.rounded_rectangle([60, 120, 560, 190], radius=14, fill=(234, 88, 12, 235), outline=(253, 186, 116), width=2)
    draw.text((90, 136), "HISTORIC BREAKTHROUGH", font=f_badge, fill=(255, 255, 255))
    
    # Telemetry
    hud_y = 220
    f_hud = get_font(26, bold=True)
    draw.line([(60, hud_y), (1020, hud_y)], fill=(0, 215, 255, 180), width=2)
    draw.text((60, hud_y + 10), "HISTORIC BREAKTHROUGH // DISTANCE: 28 MILES", font=f_hud, fill=(0, 215, 255, 240))
    draw.text((60, hud_y + 44), "LASER ALIGNMENT DEVIATION: < 1.0 CM", font=f_hud, fill=(255, 215, 0, 240))
    draw.line([(60, hud_y + 84), (1020, hud_y + 84)], fill=(0, 215, 255, 180), width=2)

    # Headline
    f_huge1 = get_font(132, bold=True)
    f_huge2 = get_font(132, bold=True)
    f_sub = get_font(42, bold=True)
    
    text_y = 1380
    draw_text_with_outline(draw, (60, text_y), "BREAK", f_huge1, fill=(255, 255, 255), outline=(0, 0, 0), width=9)
    draw_text_with_outline(draw, (60, text_y + 130), "THROUGH", f_huge2, fill=(251, 146, 60), outline=(0, 0, 0), width=9)
    
    sub_y = text_y + 275
    draw.rounded_rectangle([60, sub_y, 1020, sub_y + 68], radius=10, fill=(0, 0, 0, 180), outline=(251, 146, 60, 180), width=2)
    draw.text((80, sub_y + 12), "MEETING UNDER 7,500 FT OF DARKNESS", font=f_sub, fill=(240, 240, 240))

    final_alt_b = Image.alpha_composite(base, overlay).convert("RGB")
    alt_b_path = DATA_THUMBS / "gotthard_base_tunnel_thumb_alt_b.jpg"
    final_alt_b.save(alt_b_path, quality=95)
    print(f"Saved: {alt_b_path} ({alt_b_path.stat().st_size:,} bytes)")
    
    if ARTIFACT_DIR.exists():
        import shutil
        shutil.copy(alt_b_path, ARTIFACT_DIR / "gotthard_thumb_alt_b.jpg")

if __name__ == "__main__":
    generate_alt_b()
