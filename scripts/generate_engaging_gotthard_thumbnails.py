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

def generate_gotthard_thumbnails():
    print("Generating high-CTR YouTube Shorts thumbnails for Gotthard Base Tunnel...")
    scratch_dir = Path("scratch")
    scratch_dir.mkdir(parents=True, exist_ok=True)

    # 1. Extract 1080x1920 frames from raw Veo clips
    # Clip 3: TBM Cutterhead grinding granite
    tbm_frame = scratch_dir / "gotthard_thumb_src_tbm.jpg"
    subprocess.run([
        "ffmpeg", "-y", "-ss", "3.0", "-i", "data/flow_clips/gotthard_scene_3.mp4",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920",
        "-vframes", "1", "-q:v", "1", str(tbm_frame)
    ], check=True)

    # Clip 1: Portal Entry
    portal_frame = scratch_dir / "gotthard_thumb_src_portal.jpg"
    subprocess.run([
        "ffmpeg", "-y", "-ss", "2.0", "-i", "data/flow_clips/gotthard_scene_1.mp4",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920",
        "-vframes", "1", "-q:v", "1", str(portal_frame)
    ], check=True)

    # Clip 4: Geothermal heat / steam
    geo_frame = scratch_dir / "gotthard_thumb_src_geo.jpg"
    subprocess.run([
        "ffmpeg", "-y", "-ss", "3.0", "-i", "data/flow_clips/gotthard_scene_4.mp4",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920",
        "-vframes", "1", "-q:v", "1", str(geo_frame)
    ], check=True)

    # -------------------------------------------------------------
    # THUMBNAIL MAIN (Option A): Visceral TBM Cutterhead (Highest CTR)
    # -------------------------------------------------------------
    base = Image.open(tbm_frame).convert("RGBA")
    
    # Enhance contrast and saturation for vivid mobile punch
    enh_c = ImageEnhance.Contrast(base)
    base = enh_c.enhance(1.18)
    enh_s = ImageEnhance.Color(base)
    base = enh_s.enhance(1.22)
    
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Gradient shading for text readability
    for y in range(0, 520):
        alpha = int(180 * (1.0 - y / 520.0))
        draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))
        
    for y in range(1300, 1920):
        alpha = int(220 * ((y - 1300) / 620.0))
        draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))

    # Top Badge: Red/White Engineering Badge
    badge_x, badge_y, badge_w, badge_h = 60, 120, 500, 70
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=14, fill=(220, 38, 38, 235), outline=(254, 202, 202), width=2)
    f_badge = get_font(32, bold=True)
    draw.text((badge_x + 30, badge_y + 16), "SWISS ALPINE ARCHIVE", font=f_badge, fill=(255, 255, 255))
    
    # Technical Telemetry HUD
    hud_y = 220
    draw.line([(60, hud_y), (1020, hud_y)], fill=(0, 215, 255, 180), width=2)
    f_hud = get_font(26, bold=True)
    draw.text((60, hud_y + 10), "DEPTH: 7,500 FT // LENGTH: 35 MILES // ROCK TEMP: 115°F", font=f_hud, fill=(0, 215, 255, 240))
    draw.text((60, hud_y + 44), "EXCAVATION: 28M TONS // TBM CUTTERHEAD: 9.5M", font=f_hud, fill=(255, 215, 0, 240))
    draw.line([(60, hud_y + 84), (1020, hud_y + 84)], fill=(0, 215, 255, 180), width=2)

    # Core Headline Typography (Massive & High Impact)
    f_huge1 = get_font(136, bold=True)
    f_huge2 = get_font(136, bold=True)
    f_sub = get_font(44, bold=True)
    
    text_y = 1380
    draw_text_with_outline(draw, (60, text_y), "35-MILE", f_huge1, fill=(255, 255, 255), outline=(0, 0, 0), width=9)
    draw_text_with_outline(draw, (60, text_y + 130), "FURNACE", f_huge2, fill=(255, 204, 0), outline=(0, 0, 0), width=9)
    
    # Subtitle Pill
    sub_y = text_y + 275
    draw.rounded_rectangle([60, sub_y, 1020, sub_y + 68], radius=10, fill=(0, 0, 0, 180), outline=(255, 204, 0, 180), width=2)
    draw.text((80, sub_y + 12), "UNDER 7,500 FT OF CRUSHING GRANITE", font=f_sub, fill=(240, 240, 240))

    final_main = Image.alpha_composite(base, overlay).convert("RGB")
    main_path = DATA_THUMBS / "gotthard_base_tunnel_thumb_main.jpg"
    final_main.save(main_path, quality=95)
    print(f"Saved: {main_path} ({main_path.stat().st_size:,} bytes)")

    # -------------------------------------------------------------
    # THUMBNAIL ALT A (Option B): Portal Entry / 155 MPH Train
    # -------------------------------------------------------------
    base_alt = Image.open(portal_frame).convert("RGBA")
    enh_c = ImageEnhance.Contrast(base_alt)
    base_alt = enh_c.enhance(1.15)
    
    overlay_alt = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw_alt = ImageDraw.Draw(overlay_alt)
    
    for y in range(0, 520):
        alpha = int(180 * (1.0 - y / 520.0))
        draw_alt.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))
        
    for y in range(1300, 1920):
        alpha = int(220 * ((y - 1300) / 620.0))
        draw_alt.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))

    # Badge
    draw_alt.rounded_rectangle([60, 120, 580, 190], radius=14, fill=(15, 118, 110, 235), outline=(94, 234, 212), width=2)
    draw_alt.text((90, 136), "EXTREME ENGINEERING", font=f_badge, fill=(255, 255, 255))
    
    # Telemetry
    draw_alt.line([(60, hud_y), (1020, hud_y)], fill=(0, 215, 255, 180), width=2)
    draw_alt.text((60, hud_y + 10), "PORTAL ERSTFELD // SPEED: 155 MPH // DEPTH: 2,300M", font=f_hud, fill=(0, 215, 255, 240))
    draw_alt.text((60, hud_y + 44), "WORLD RECORD: LONGEST & DEEPEST RAIL TUNNEL", font=f_hud, fill=(255, 215, 0, 240))
    draw_alt.line([(60, hud_y + 84), (1020, hud_y + 84)], fill=(0, 215, 255, 180), width=2)

    # Headline
    draw_text_with_outline(draw_alt, (60, text_y), "DEEPEST", f_huge1, fill=(255, 255, 255), outline=(0, 0, 0), width=9)
    draw_text_with_outline(draw_alt, (60, text_y + 130), "TUNNEL", f_huge2, fill=(56, 189, 248), outline=(0, 0, 0), width=9)
    
    draw_alt.rounded_rectangle([60, sub_y, 1020, sub_y + 68], radius=10, fill=(0, 0, 0, 180), outline=(56, 189, 248, 180), width=2)
    draw_alt.text((80, sub_y + 12), "17 YEARS TO DRILL 57 KILOMETERS", font=f_sub, fill=(240, 240, 240))

    final_alt = Image.alpha_composite(base_alt, overlay_alt).convert("RGB")
    alt_path = DATA_THUMBS / "gotthard_base_tunnel_thumb_alt_a.jpg"
    final_alt.save(alt_path, quality=95)
    print(f"Saved: {alt_path} ({alt_path.stat().st_size:,} bytes)")

    # -------------------------------------------------------------
    # THUMBNAIL WIDE (16:9 1920x1080 Promo / Landscape Preview)
    # -------------------------------------------------------------
    wide_base = final_main.resize((1080, 1080)).crop((0, 0, 1080, 1080))
    wide_img = Image.new("RGB", (1920, 1080), (11, 15, 25))
    
    # Left: Center crop of TBM frame
    tbm_crop = Image.open(tbm_frame).resize((1080, 1080)).crop((0, 0, 1080, 1080))
    wide_img.paste(tbm_crop, (0, 0))
    
    # Right panel
    d_wide = ImageDraw.Draw(wide_img)
    # Gradient overlay across seam
    for x in range(900, 1200):
        alpha = int(255 * ((x - 900) / 300.0))
        d_wide.line([(x, 0), (x, 1080)], fill=(11, 15, 25, alpha))
    d_wide.rectangle([(1100, 0), (1920, 1080)], fill=(11, 15, 25))

    d_wide.rounded_rectangle([1120, 160, 1600, 226], radius=10, fill=(220, 38, 38), outline=(255, 100, 100), width=2)
    d_wide.text((1145, 175), "SWISS ALPINE ARCHIVE", font=get_font(28, bold=True), fill=(255, 255, 255))
    
    f_w1 = get_font(80, bold=True)
    f_w2 = get_font(80, bold=True)
    f_w_sub = get_font(34, bold=True)
    
    draw_text_with_outline(d_wide, (1120, 270), "THE 35-MILE", f_w1, fill=(255, 255, 255), outline=(0, 0, 0), width=6)
    draw_text_with_outline(d_wide, (1120, 360), "GRANITE FURNACE", f_w2, fill=(255, 204, 0), outline=(0, 0, 0), width=6)
    
    d_wide.text((1120, 480), "How 2,500 miners carved 28 million tons", font=f_w_sub, fill=(200, 210, 225))
    d_wide.text((1120, 525), "of rock under 115°F geothermal heat.", font=f_w_sub, fill=(200, 210, 225))

    d_wide.line([(1120, 600), (1850, 600)], fill=(0, 215, 255, 180), width=2)
    d_wide.text((1120, 620), "DEPTH: 7,500 FT // 57 KM BASE TUNNEL // 155 MPH", font=get_font(24, bold=True), fill=(0, 215, 255))

    wide_path = DATA_THUMBS / "gotthard_base_tunnel_thumb_wide.jpg"
    wide_img.save(wide_path, quality=95)
    print(f"Saved: {wide_path} ({wide_path.stat().st_size:,} bytes)")

    # Copy to brain artifact directory as well
    if ARTIFACT_DIR.exists():
        import shutil
        shutil.copy(main_path, ARTIFACT_DIR / "gotthard_thumb_main.jpg")
        shutil.copy(alt_path, ARTIFACT_DIR / "gotthard_thumb_alt_a.jpg")
        shutil.copy(wide_path, ARTIFACT_DIR / "gotthard_thumb_wide.jpg")
        print("Copied to artifacts directory for user preview.")

if __name__ == "__main__":
    generate_gotthard_thumbnails()
