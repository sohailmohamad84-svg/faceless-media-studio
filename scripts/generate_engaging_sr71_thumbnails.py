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
    # Outline
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx*dx + dy*dy <= width*width:
                draw.text((x + dx, y + dy), text, font=font, fill=outline)
    # Fill
    draw.text((x, y), text, font=font, fill=fill)

def generate_thumbnails():
    print("Generating high-engagement viral YouTube Shorts thumbnails...")
    
    # 1. Extract 4K/1080p source frames from clean Veo clips
    # Clip 4: Cockpit POV
    cockpit_frame = Path("scratch/thumb_src_cockpit.jpg")
    subprocess.run([
        "ffmpeg", "-y", "-ss", "3.0", "-i", "data/flow_clips/sr71_flow_scene_4.mp4",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920",
        "-vframes", "1", "-q:v", "1", str(cockpit_frame)
    ], check=True)
    
    # Clip 1: Stratosphere Cruise
    cruise_frame = Path("scratch/thumb_src_cruise.jpg")
    subprocess.run([
        "ffmpeg", "-y", "-ss", "2.0", "-i", "data/flow_clips/sr71_flow_scene_1.mp4",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920",
        "-vframes", "1", "-q:v", "1", str(cruise_frame)
    ], check=True)

    # Clip 3: Shockwave Cowl
    shock_frame = Path("scratch/thumb_src_shock.jpg")
    subprocess.run([
        "ffmpeg", "-y", "-ss", "3.5", "-i", "data/flow_clips/sr71_flow_scene_3.mp4",
        "-vf", "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920",
        "-vframes", "1", "-q:v", "1", str(shock_frame)
    ], check=True)

    # -------------------------------------------------------------
    # THUMBNAIL MAIN (Option A): Visceral Cockpit POV (Highest CTR)
    # -------------------------------------------------------------
    base = Image.open(cockpit_frame).convert("RGBA")
    
    # Boost contrast and saturation slightly for mobile pop
    enh_c = ImageEnhance.Contrast(base)
    base = enh_c.enhance(1.15)
    enh_s = ImageEnhance.Color(base)
    base = enh_s.enhance(1.18)
    
    # Overlay layer
    overlay = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    
    # Vignette / subtle top & bottom gradient for text contrast
    for y in range(0, 520):
        alpha = int(180 * (1.0 - y / 520.0))
        draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))
        
    for y in range(1400, 1920):
        alpha = int(210 * ((y - 1400) / 520.0))
        draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))

    # Top Pill Badge
    badge_x, badge_y, badge_w, badge_h = 60, 120, 480, 70
    draw.rounded_rectangle([badge_x, badge_y, badge_x + badge_w, badge_y + badge_h], radius=15, fill=(210, 30, 30, 230), outline=(255, 80, 80), width=2)
    f_badge = get_font(34, bold=True)
    draw.text((badge_x + 35, badge_y + 14), "SKUNK WORKS ARCHIVE", font=f_badge, fill=(255, 255, 255))
    
    # Tactical Telemetry Box
    hud_y = 220
    draw.line([(60, hud_y), (1020, hud_y)], fill=(0, 215, 255, 180), width=2)
    f_hud = get_font(26, bold=True)
    draw.text((60, hud_y + 10), "ALT: 85,000 FT // SPEED: MACH 3.20 // 2,200 MPH", font=f_hud, fill=(0, 215, 255, 230))
    draw.text((60, hud_y + 45), "CRITICAL: ASYMMETRIC THRUST YAW JERK", font=f_hud, fill=(255, 215, 0, 230))
    draw.line([(60, hud_y + 85), (1020, hud_y + 85)], fill=(0, 215, 255, 180), width=2)

    # Core Headline Typography (Massive & High Impact)
    f_huge1 = get_font(132, bold=True)
    f_huge2 = get_font(132, bold=True)
    f_sub = get_font(46, bold=True)
    
    text_y = 1380
    draw_text_with_outline(draw, (60, text_y), "MACH 3.2", f_huge1, fill=(255, 255, 255), outline=(0, 0, 0), width=8)
    draw_text_with_outline(draw, (60, text_y + 130), "UNSTART", f_huge2, fill=(255, 215, 0), outline=(0, 0, 0), width=9)
    
    # Yellow Callout Box
    box_y = text_y + 275
    draw.rounded_rectangle([60, box_y, 1020, box_y + 90], radius=16, fill=(20, 25, 35, 220), outline=(255, 215, 0), width=3)
    draw.text((85, box_y + 20), "ENGINE CHOKES IN 50 MILLISECONDS", font=f_sub, fill=(255, 255, 255))

    # Warning Box Banner at very bottom
    draw.rectangle([0, 1820, 1080, 1920], fill=(210, 30, 30, 240))
    f_bottom = get_font(36, bold=True)
    draw.text((120, 1845), "WARNING: SEVERE CANOPY HELMET STRIKE", font=f_bottom, fill=(255, 255, 255))

    final_main = Image.alpha_composite(base, overlay).convert("RGB")
    main_out = DATA_THUMBS / "sr71_blackbird_unstart_thumb_main.jpg"
    final_main.save(main_out, quality=95)
    final_main.save(ARTIFACT_DIR / "sr71_thumbnail_main.jpg", quality=95)
    print(f"Saved primary engaging thumbnail: {main_out}")

    # -------------------------------------------------------------
    # THUMBNAIL ALT A: Stratospheric Airframe Cruise (Option B)
    # -------------------------------------------------------------
    base_b = Image.open(cruise_frame).convert("RGBA")
    base_b = ImageEnhance.Contrast(base_b).enhance(1.2)
    overlay_b = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    draw_b = ImageDraw.Draw(overlay_b)
    
    # Top & Bottom gradients
    for y in range(0, 480):
        draw_b.line([(0, y), (1080, y)], fill=(0, 0, 0, int(180 * (1.0 - y / 480.0))))
    for y in range(1350, 1920):
        draw_b.line([(0, y), (1080, y)], fill=(0, 0, 0, int(220 * ((y - 1350) / 570.0))))

    # Top Badge
    draw_b.rounded_rectangle([60, 120, 520, 190], radius=15, fill=(0, 100, 220, 230), outline=(0, 215, 255), width=2)
    draw_b.text((90, 134), "SUPERSONIC FORENSICS", font=f_badge, fill=(255, 255, 255))
    
    draw_text_with_outline(draw_b, (60, 1370), "THE JET THAT", get_font(100, bold=True), fill=(255, 255, 255), outline=(0, 0, 0), width=7)
    draw_text_with_outline(draw_b, (60, 1480), "CHOKED", get_font(135, bold=True), fill=(255, 50, 50), outline=(0, 0, 0), width=9)

    call_b_y = 1635
    draw_b.rounded_rectangle([60, call_b_y, 1020, call_b_y + 90], radius=16, fill=(15, 20, 30, 230), outline=(0, 215, 255), width=3)
    draw_b.text((85, call_b_y + 20), "1mm SHOCKWAVE ERROR = SLAMMED SIDEWAYS", font=get_font(38, bold=True), fill=(0, 215, 255))

    final_alt_a = Image.alpha_composite(base_b, overlay_b).convert("RGB")
    alt_a_out = DATA_THUMBS / "sr71_blackbird_unstart_thumb_alt_a.jpg"
    final_alt_a.save(alt_a_out, quality=95)
    final_alt_a.save(ARTIFACT_DIR / "sr71_thumbnail_alt_a.jpg", quality=95)
    print(f"Saved Alternative A thumbnail: {alt_a_out}")

    # -------------------------------------------------------------
    # 16:9 Widescreen Promo Thumbnail (1920 x 1080)
    # -------------------------------------------------------------
    # Crop / compose 16:9 from the high-res 4K source
    base_wide = Image.open(cockpit_frame).convert("RGBA")
    # Take center 1080x1080 and expand to 1920x1080 with side panels
    thumb_wide = Image.new("RGBA", (1920, 1080), (10, 15, 25, 255))
    
    # Left half: Pilot POV cropped
    pilot_crop = base.crop((0, 300, 1080, 1380)).resize((1080, 1080), Image.Resampling.LANCZOS)
    thumb_wide.paste(pilot_crop, (0, 0))
    
    # Right half: Shockwave Cowl cropped
    shock_crop = base_b.crop((0, 400, 1080, 1480)).resize((840, 1080), Image.Resampling.LANCZOS)
    thumb_wide.paste(shock_crop, (1080, 0))
    
    # Center dividing gradient & border
    draw_w = ImageDraw.Draw(thumb_wide)
    draw_w.line([(1080, 0), (1080, 1080)], fill=(0, 215, 255, 200), width=4)
    
    # Bottom banner
    for y in range(700, 1080):
        draw_w.line([(0, y), (1920, y)], fill=(0, 0, 0, int(220 * ((y - 700) / 380.0))))
        
    draw_text_with_outline(draw_w, (80, 760), "SR-71 INLET UNSTART", get_font(95, bold=True), fill=(255, 215, 0), outline=(0, 0, 0), width=7)
    draw_text_with_outline(draw_w, (80, 880), "WHEN A JET ENGINE CHOKES AT MACH 3.2", get_font(48, bold=True), fill=(255, 255, 255), outline=(0, 0, 0), width=5)
    
    final_wide = thumb_wide.convert("RGB")
    wide_out = DATA_THUMBS / "sr71_blackbird_unstart_thumb_wide.jpg"
    promo_out = DATA_THUMBS / "sr71_blackbird_unstart_thumb_promo_16x9.jpg"
    final_wide.save(wide_out, quality=95)
    final_wide.save(promo_out, quality=95)
    final_wide.save(ARTIFACT_DIR / "sr71_thumbnail_wide.jpg", quality=95)
    print(f"Saved 16:9 widescreen thumbnails: {wide_out} & {promo_out}")

if __name__ == "__main__":
    generate_thumbnails()
