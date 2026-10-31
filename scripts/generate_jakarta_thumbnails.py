import os
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

DATA_THUMBS = Path("data/thumbnails")
DATA_THUMBS.mkdir(parents=True, exist_ok=True)
ARTIFACT_DIR = Path(r"C:\Users\Sohail\.gemini\antigravity\brain\eb4bd0b7-d463-4e01-b351-a971179e01ed")

def get_font(size, bold=True):
    font_names = ["impact.ttf", "arialbd.ttf" if bold else "arial.ttf", "segoeui.ttf"]
    for fn in font_names:
        try:
            return ImageFont.truetype(fn, size)
        except Exception:
            pass
    return ImageFont.load_default()

def draw_text_with_outline(draw, pos, text, font, fill=(255, 255, 255), outline=(0, 0, 0), width=5):
    x, y = pos
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx*dx + dy*dy <= width*width:
                draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)

def generate_jakarta_thumbnails():
    print("Generating high-CTR YouTube Shorts thumbnails for Jakarta Sinking Seawall...", flush=True)
    scratch_dir = Path("scratch")
    scratch_dir.mkdir(parents=True, exist_ok=True)

    # 1. Extract 1080x1920 frames from raw Veo clips
    # Clip 5: Marine crane barge dumping concrete tetrapods into sea
    tetrapod_frame = scratch_dir / "jakarta_thumb_src_tetrapod.jpg"
    if Path("data/flow_clips/jakarta_scene_5.mp4").exists():
        subprocess.run([
            "ffmpeg", "-y", "-ss", "2.5", "-i", "data/flow_clips/jakarta_scene_5.mp4",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920",
            "-vframes", "1", "-q:v", "1", str(tetrapod_frame)
        ], check=True)

    # Clip 1: Flooded street with shop signs & water
    flood_frame = scratch_dir / "jakarta_thumb_src_flood.jpg"
    if Path("data/flow_clips/jakarta_scene_1.mp4").exists():
        subprocess.run([
            "ffmpeg", "-y", "-ss", "2.0", "-i", "data/flow_clips/jakarta_scene_1.mp4",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920",
            "-vframes", "1", "-q:v", "1", str(flood_frame)
        ], check=True)

    # Clip 4: Great Garuda offshore dike
    garuda_frame = scratch_dir / "jakarta_thumb_src_garuda.jpg"
    if Path("data/flow_clips/jakarta_scene_4.mp4").exists():
        subprocess.run([
            "ffmpeg", "-y", "-ss", "2.0", "-i", "data/flow_clips/jakarta_scene_4.mp4",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920",
            "-vframes", "1", "-q:v", "1", str(garuda_frame)
        ], check=True)

    # -------------------------------------------------------------
    # THUMBNAIL MAIN: $40B SEAWALL HERO SHOT
    # -------------------------------------------------------------
    src_main = tetrapod_frame if tetrapod_frame.exists() else (flood_frame if flood_frame.exists() else None)
    if src_main and src_main.exists():
        base = Image.open(src_main).convert("RGBA")
        enhancer = ImageEnhance.Contrast(base)
        base = enhancer.enhance(1.25)
        enhancer_col = ImageEnhance.Color(base)
        base = enhancer_col.enhance(1.3)

        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Subtle vignette gradients
        for y in range(400):
            alpha = int(180 * (1.0 - y / 400.0))
            draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))
        for y in range(1500, 1920):
            alpha = int(220 * ((y - 1500) / 420.0))
            draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))

        font_top = get_font(72, bold=True)
        font_num = get_font(128, bold=True)
        font_sub = get_font(60, bold=True)

        draw_text_with_outline(draw, (80, 160), "40% OF CITY", font_top, fill=(255, 230, 0), outline=(0, 0, 0), width=6)
        draw_text_with_outline(draw, (80, 250), "UNDERWATER", font_num, fill=(255, 50, 50), outline=(0, 0, 0), width=8)
        draw_text_with_outline(draw, (80, 1650), "$40,000,000,000 SEA WALL", font_sub, fill=(255, 255, 255), outline=(0, 0, 0), width=5)

        composed = Image.alpha_composite(base, overlay).convert("RGB")
        out_main = DATA_THUMBS / "jakarta_sinking_seawall_thumb_main.jpg"
        composed.save(out_main, "JPEG", quality=95)
        print(f"Generated main thumbnail: {out_main} ({out_main.stat().st_size:,} bytes)", flush=True)

        if ARTIFACT_DIR.exists():
            art_main = ARTIFACT_DIR / "jakarta_thumb_main.jpg"
            composed.save(art_main, "JPEG", quality=90)

    # -------------------------------------------------------------
    # THUMBNAIL ALT A: FLOOD CRISIS
    # -------------------------------------------------------------
    if flood_frame.exists():
        base = Image.open(flood_frame).convert("RGBA")
        enhancer = ImageEnhance.Contrast(base)
        base = enhancer.enhance(1.2)
        enhancer_col = ImageEnhance.Color(base)
        base = enhancer_col.enhance(1.25)

        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        for y in range(450):
            alpha = int(190 * (1.0 - y / 450.0))
            draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))

        font_huge = get_font(120, bold=True)
        font_med = get_font(64, bold=True)

        draw_text_with_outline(draw, (80, 140), "SINKING 10\"", font_huge, fill=(255, 220, 0), outline=(0, 0, 0), width=7)
        draw_text_with_outline(draw, (80, 270), "EVERY YEAR", font_med, fill=(255, 255, 255), outline=(0, 0, 0), width=5)

        composed = Image.alpha_composite(base, overlay).convert("RGB")
        out_alt_a = DATA_THUMBS / "jakarta_sinking_seawall_thumb_alt_a.jpg"
        composed.save(out_alt_a, "JPEG", quality=95)
        print(f"Generated Alt A thumbnail: {out_alt_a} ({out_alt_a.stat().st_size:,} bytes)", flush=True)

        if ARTIFACT_DIR.exists():
            composed.save(ARTIFACT_DIR / "jakarta_thumb_alt_a.jpg", "JPEG", quality=90)

    # -------------------------------------------------------------
    # THUMBNAIL ALT B / WIDE 16:9
    # -------------------------------------------------------------
    if garuda_frame.exists():
        base = Image.open(garuda_frame).convert("RGBA")
        enhancer = ImageEnhance.Contrast(base)
        base = enhancer.enhance(1.2)
        
        # Crop to 16:9 1920x1080
        w, h = base.size
        target_h = int(w * 9 / 16)
        top = (h - target_h) // 2
        wide_crop = base.crop((0, top, w, top + target_h)).resize((1920, 1080), Image.Resampling.LANCZOS)
        
        overlay_w = Image.new("RGBA", wide_crop.size, (0, 0, 0, 0))
        draw_w = ImageDraw.Draw(overlay_w)
        font_w = get_font(84, bold=True)
        draw_text_with_outline(draw_w, (100, 100), "THE $40B SINKING CITY WALL", font_w, fill=(255, 230, 0), outline=(0, 0, 0), width=6)
        
        composed_w = Image.alpha_composite(wide_crop, overlay_w).convert("RGB")
        out_wide = DATA_THUMBS / "jakarta_sinking_seawall_thumb_wide.jpg"
        composed_w.save(out_wide, "JPEG", quality=95)
        print(f"Generated wide thumbnail: {out_wide} ({out_wide.stat().st_size:,} bytes)", flush=True)

    print("Thumbnails generation completed.", flush=True)

if __name__ == "__main__":
    generate_jakarta_thumbnails()
