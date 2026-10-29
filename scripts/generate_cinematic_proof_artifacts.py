"""Extract proof frames and assemble an accessible 8-scene contact sheet for the cinematic master short.
Saves individual act frames and assembled contact sheet to the artifacts directory.
"""
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ARTIFACT_DIR = Path(r"C:\Users\Sohail\.gemini\antigravity\brain\eb4bd0b7-d463-4e01-b351-a971179e01ed")
VIDEO_PATH = Path("exports/sr71_blackbird_unstart_master_1080p.mp4")

ACTS = [
    (1, 5.0, "Act 1: Stratospheric Cruise & Aero Tracking", "sr71_cinematic_act_1_5s.jpg"),
    (2, 16.0, "Act 2: Moveable Spike 26-Inch Translation", "sr71_cinematic_act_2_16s.jpg"),
    (3, 28.0, "Act 3: Forensic Shockwave Cowl Unstart", "sr71_cinematic_act_3_28s.jpg"),
    (4, 40.0, "Act 4: Cockpit Violent Yaw Lateral Jerk", "sr71_cinematic_act_4_40s.jpg"),
    (5, 52.0, "Act 5: Pratt & Whitney J58 Bypass Ramjet", "sr71_cinematic_act_5_52s.jpg"),
    (6, 63.0, "Act 6: Corrugated Titanium 600°F Expansion", "sr71_cinematic_act_6_63s.jpg"),
    (7, 75.0, "Act 7: Mach 3.2 High-Altitude Missile Evasion", "sr71_cinematic_act_7_75s.jpg"),
    (8, 86.0, "Act 8: Skunk Works Museum Golden Finish", "sr71_cinematic_act_8_86s.jpg"),
]

def main():
    if not VIDEO_PATH.exists():
        print(f"Error: {VIDEO_PATH} does not exist!")
        return

    extracted_imgs = []
    for act_num, ts, title, filename in ACTS:
        out_path = ARTIFACT_DIR / filename
        cmd = [
            "ffmpeg", "-y",
            "-ss", f"{ts:.2f}",
            "-i", str(VIDEO_PATH),
            "-vframes", "1",
            "-q:v", "2",
            str(out_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"Extracted Act {act_num} ({ts:.1f}s) -> {out_path.name}")
        extracted_imgs.append((act_num, title, out_path))

    # Assemble 2-row x 4-col high resolution contact sheet
    tile_w, tile_h = 360, 640
    padding = 20
    header_h = 80
    sheet_w = 4 * tile_w + 5 * padding
    sheet_h = 2 * tile_h + 3 * padding + header_h

    sheet = Image.new("RGB", (sheet_w, sheet_h), color=(15, 18, 24))
    draw = ImageDraw.Draw(sheet)

    # Title Banner
    try:
        font_title = ImageFont.truetype("arialbd.ttf", 32)
        font_sub = ImageFont.truetype("arial.ttf", 18)
        font_label = ImageFont.truetype("arialbd.ttf", 16)
    except Exception:
        font_title = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        font_label = ImageFont.load_default()

    draw.text((padding, 15), "SR-71 BLACKBIRD UNSTART // CINEMATIC OVERHAUL AUDIT PROOF", fill=(255, 215, 0), font=font_title)
    draw.text((padding, 50), "92.000000s Broadcast Master // Skunk Works HUD // Hollywood Camera Dynamics // 3-Layer Audio", fill=(180, 200, 220), font=font_sub)

    for idx, (act_num, title, img_path) in enumerate(extracted_imgs):
        row = idx // 4
        col = idx % 4
        x = padding + col * (tile_w + padding)
        y = header_h + padding + row * (tile_h + padding)

        with Image.open(img_path) as im:
            thumb = im.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
            sheet.paste(thumb, (x, y))

        # Border & Label Overlay
        draw.rectangle([x, y, x + tile_w, y + tile_h], outline=(255, 215, 0), width=2)
        draw.rectangle([x, y + tile_h - 40, x + tile_w, y + tile_h], fill=(0, 0, 0, 200))
        draw.text((x + 8, y + tile_h - 30), f"Act {act_num}: {title[:28]}", fill=(255, 255, 255), font=font_label)

    contact_path = ARTIFACT_DIR / "sr71_cinematic_contact_sheet.jpg"
    sheet.save(contact_path, quality=92)
    print(f"\nSaved master cinematic contact sheet: {contact_path}")

    # Also update sr71_repaired_contact_sheet.jpg for seamless artifact viewers
    sheet.save(ARTIFACT_DIR / "sr71_repaired_contact_sheet.jpg", quality=92)
    print("Updated sr71_repaired_contact_sheet.jpg")

if __name__ == "__main__":
    main()
