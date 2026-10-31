import os
import subprocess
from pathlib import Path
from PIL import Image

ARTIFACT_DIR = Path(r"C:\Users\Sohail\.gemini\antigravity\brain\eb4bd0b7-d463-4e01-b351-a971179e01ed")
VIDEO_PATH = Path("exports/jakarta_sinking_seawall_master_1080p.mp4")

timestamps = [
    (1, 4.0, "Submerged Street Hook"),
    (2, 13.0, "3D Groundwater Subsidence"),
    (3, 23.0, "3D Satellite Elevation DEM"),
    (4, 33.0, "Great Garuda Sea Wall"),
    (5, 43.0, "Tetrapod Rock Revetment"),
    (6, 53.0, "Nusantara Rainforest Capital"),
    (7, 63.0, "Archimedes Screw Pumping"),
    (8, 68.0, "Sunset Seawall Horizon")
]

frame_paths = []
for act_num, ts, title in timestamps:
    out_img = ARTIFACT_DIR / f"jakarta_act_{act_num}_{int(ts)}s.jpg"
    cmd = [
        "ffmpeg", "-y", "-ss", f"{ts:.2f}",
        "-i", str(VIDEO_PATH),
        "-vframes", "1", "-q:v", "2",
        str(out_img)
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
    frame_paths.append(out_img)
    print(f"Act {act_num} ({ts}s): {out_img.name} ({out_img.stat().st_size:,} bytes)")

# Create an 8-act contact sheet (4 columns x 2 rows)
thumb_w, thumb_h = 270, 480
contact_sheet = Image.new("RGB", (thumb_w * 4, thumb_h * 2), (11, 15, 25))

for idx, fp in enumerate(frame_paths):
    img = Image.open(fp).resize((thumb_w, thumb_h), Image.Resampling.LANCZOS)
    col = idx % 4
    row = idx // 4
    contact_sheet.paste(img, (col * thumb_w, row * thumb_h))

contact_path = ARTIFACT_DIR / "jakarta_cinematic_contact_sheet.jpg"
contact_sheet.save(contact_path, quality=92)
print(f"Contact sheet saved: {contact_path} ({contact_path.stat().st_size:,} bytes)")
