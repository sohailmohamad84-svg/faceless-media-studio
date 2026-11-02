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

def draw_text_with_outline(draw, pos, text, font, fill=(255, 255, 255), outline=(0, 0, 0), width=6):
    x, y = pos
    for dx in range(-width, width + 1):
        for dy in range(-width, width + 1):
            if dx*dx + dy*dy <= width*width:
                draw.text((x + dx, y + dy), text, font=font, fill=outline)
    draw.text((x, y), text, font=font, fill=fill)

def generate_boeing_thumbnails():
    print("Generating high-CTR YouTube Shorts thumbnails for Boeing 747 Hump Secret...", flush=True)
    scratch_dir = Path("scratch")
    scratch_dir.mkdir(parents=True, exist_ok=True)

    # 1. Extract 1080x1920 frames from raw Veo clips
    # Clip 1: Sunset rotation showing iconic hump
    rotate_frame = scratch_dir / "boeing_thumb_src_rotate.jpg"
    if Path("data/flow_clips/boeing747_scene_1.mp4").exists():
        subprocess.run([
            "ffmpeg", "-y", "-ss", "2.0", "-i", "data/flow_clips/boeing747_scene_1.mp4",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920",
            "-vframes", "1", "-q:v", "1", str(rotate_frame)
        ], check=True)

    # Clip 3: 3D Swing-up nose cargo
    nose_frame = scratch_dir / "boeing_thumb_src_nose.jpg"
    if Path("data/flow_clips/boeing747_scene_3.mp4").exists():
        subprocess.run([
            "ffmpeg", "-y", "-ss", "2.5", "-i", "data/flow_clips/boeing747_scene_3.mp4",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920",
            "-vframes", "1", "-q:v", "1", str(nose_frame)
        ], check=True)

    # Clip 8: Golden hour soar
    soar_frame = scratch_dir / "boeing_thumb_src_soar.jpg"
    if Path("data/flow_clips/boeing747_scene_8.mp4").exists():
        subprocess.run([
            "ffmpeg", "-y", "-ss", "2.0", "-i", "data/flow_clips/boeing747_scene_8.mp4",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920",
            "-vframes", "1", "-q:v", "1", str(soar_frame)
        ], check=True)

    # -------------------------------------------------------------
    # THUMBNAIL MAIN: HERO 747 ROTATION + "WHY THE HUMP?"
    # -------------------------------------------------------------
    src_main = rotate_frame if rotate_frame.exists() else (soar_frame if soar_frame.exists() else None)
    if src_main and src_main.exists():
        base = Image.open(src_main).convert("RGBA")
        enhancer = ImageEnhance.Contrast(base)
        base = enhancer.enhance(1.25)
        enhancer_col = ImageEnhance.Color(base)
        base = enhancer_col.enhance(1.3)

        overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)
        
        # Vignettes
        for y in range(450):
            alpha = int(190 * (1.0 - y / 450.0))
            draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))
        for y in range(1450, 1920):
            alpha = int(210 * ((y - 1450) / 470.0))
            draw.line([(0, y), (1080, y)], fill=(0, 0, 0, alpha))

        font_top = get_font(76, bold=True)
        font_big = get_font(132, bold=True)
        font_bot = get_font(60, bold=True)

        draw_text_with_outline(draw, (80, 140), "THE SECRET OF THE", font_top, fill=(255, 255, 255), outline=(0, 0, 0), width=6)
        draw_text_with_outline(draw, (80, 240), "747 HUMP", font_big, fill=(255, 230, 0), outline=(0, 0, 0), width=8)
        draw_text_with_outline(draw, (80, 1650), "NEVER MEANT FOR PASSENGERS", font_bot, fill=(255, 60, 60), outline=(0, 0, 0), width=5)

        composed = Image.alpha_composite(base, overlay).convert("RGB")
        out_main = DATA_THUMBS / "boeing_747_hump_secret_thumb_main.jpg"
        composed.save(out_main, "JPEG", quality=95)
        print(f"Generated main thumbnail: {out_main} ({out_main.stat().st_size:,} bytes)", flush=True)

        if ARTIFACT_DIR.exists():
            composed.save(ARTIFACT_DIR / "boeing_thumb_main.jpg", "JPEG", quality=90)

    # -------------------------------------------------------------
    # THUMBNAIL ALT A: NOSE CARGO MAW
    # -------------------------------------------------------------
    if nose_frame.exists():
        base = Image.open(nose_frame).convert("RGBA")
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

        draw_text_with_outline(draw, (80, 140), "MILITARY CARGO", font_huge, fill=(255, 220, 0), outline=(0, 0, 0), width=7)
        draw_text_with_outline(draw, (80, 270), "SWING NOSE SECRET", font_med, fill=(255, 255, 255), outline=(0, 0, 0), width=5)

        composed = Image.alpha_composite(base, overlay).convert("RGB")
        out_alt_a = DATA_THUMBS / "boeing_747_hump_secret_thumb_alt_a.jpg"
        composed.save(out_alt_a, "JPEG", quality=95)
        print(f"Generated Alt A thumbnail: {out_alt_a} ({out_alt_a.stat().st_size:,} bytes)", flush=True)

        if ARTIFACT_DIR.exists():
            composed.save(ARTIFACT_DIR / "boeing_thumb_alt_a.jpg", "JPEG", quality=90)

    # -------------------------------------------------------------
    # THUMBNAIL WIDE 16:9
    # -------------------------------------------------------------
    src_wide = soar_frame if soar_frame.exists() else (rotate_frame if rotate_frame.exists() else None)
    if src_wide and src_wide.exists():
        base = Image.open(src_wide).convert("RGBA")
        enhancer = ImageEnhance.Contrast(base)
        base = enhancer.enhance(1.2)
        
        w, h = base.size
        target_h = int(w * 9 / 16)
        top = (h - target_h) // 2
        wide_crop = base.crop((0, top, w, top + target_h)).resize((1920, 1080), Image.Resampling.LANCZOS)
        
        overlay_w = Image.new("RGBA", wide_crop.size, (0, 0, 0, 0))
        draw_w = ImageDraw.Draw(overlay_w)
        font_w = get_font(84, bold=True)
        draw_text_with_outline(draw_w, (100, 100), "THE MILITARY SECRET OF THE 747 HUMP", font_w, fill=(255, 230, 0), outline=(0, 0, 0), width=6)
        
        composed_w = Image.alpha_composite(wide_crop, overlay_w).convert("RGB")
        out_wide = DATA_THUMBS / "boeing_747_hump_secret_thumb_wide.jpg"
        composed_w.save(out_wide, "JPEG", quality=95)
        print(f"Generated wide thumbnail: {out_wide} ({out_wide.stat().st_size:,} bytes)", flush=True)

    print("Thumbnails generation completed.", flush=True)

if __name__ == "__main__":
    generate_boeing_thumbnails()
