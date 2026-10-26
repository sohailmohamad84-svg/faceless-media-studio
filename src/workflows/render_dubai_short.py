"""Render and publish Dubai Sinking Islands Short with 5 Dedicated Dynamic 9:16 Scenes."""
import asyncio
import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Force UTF-8 stdout
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure project root in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.editing.flow_master_engine import FlowMasterEngine
from src.youtube.uploader import YouTubePublisher

ASSETS_DIR = Path("data/dubai_assets")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

CLIPS_CONFIG = [
    {
        "img": ASSETS_DIR / "dubai_act1_world_islands.jpg",
        "clip": ASSETS_DIR / "dubai_clip_1.mp4",
        "filter": "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0008,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=240:s=1080x1920:fps=24"
    },
    {
        "img": ASSETS_DIR / "dubai_act2_hopper_dredger.jpg",
        "clip": ASSETS_DIR / "dubai_clip_2.mp4",
        "filter": "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0010,1.18)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)+60':d=240:s=1080x1920:fps=24"
    },
    {
        "img": ASSETS_DIR / "dubai_act3_abandoned_cranes.jpg",
        "clip": ASSETS_DIR / "dubai_clip_3.mp4",
        "filter": "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='1.12':x='iw/2-(iw/zoom/2)':y='ih*0.05+ih*(on/240)*0.08':d=240:s=1080x1920:fps=24"
    },
    {
        "img": ASSETS_DIR / "dubai_act4_satellite_radar.jpg",
        "clip": ASSETS_DIR / "dubai_clip_4.mp4",
        "filter": "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0006,1.12)':x='iw/2-(iw/zoom/2)':y='ih*0.05+ih*(on/240)*0.06':d=240:s=1080x1920:fps=24"
    },
    {
        "img": ASSETS_DIR / "dubai_act5_seawall_sunset.jpg",
        "clip": ASSETS_DIR / "dubai_clip_5.mp4",
        "filter": "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='max(1.15-0.0006*on,1.0)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=240:s=1080x1920:fps=24"
    }
]

def render_dynamic_clip(img_path: Path, out_clip: Path, vf_filter: str):
    print(f"[RENDER] Ken Burns clip: {out_clip.name} from {img_path.name}...")
    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", str(img_path),
        "-vf", vf_filter,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-t", "10",
        "-pix_fmt", "yuv420p",
        str(out_clip)
    ]
    subprocess.run(cmd, check=True)
    print(f"[OK] Created {out_clip.name} ({out_clip.stat().st_size / (1024*1024):.2f} MB)")

async def main():
    print("=" * 60)
    print("[START] DUBAI SINKING ISLANDS SHORT: 5-SCENE MASTER RENDERING")
    print("=" * 60)

    # Step 1: Render each dynamic clip
    for item in CLIPS_CONFIG:
        if not item["clip"].exists():
            render_dynamic_clip(item["img"], item["clip"], item["filter"])
        else:
            print(f"[SKIP] {item['clip'].name} already exists.")

    # Step 2: Build master video using FlowMasterEngine with 5 scenes
    scenes = [
        {
            "input_video": str(ASSETS_DIR / "dubai_clip_1.mp4"),
            "narration_text": "Three hundred artificial islands were carved into the ocean to look like the planet Earth.",
            "is_clean": True,
            "foley": [
                {"sfx": "tension_drone.wav", "time_offset": 0.0, "gain": 0.35},
                {"sfx": "impact_boom.wav", "time_offset": 0.5, "gain": 0.4}
            ]
        },
        {
            "input_video": str(ASSETS_DIR / "dubai_clip_2.mp4"),
            "narration_text": "Over three hundred million cubic meters of sand were dredged from the seabed to build paradise.",
            "is_clean": True,
            "foley": [
                {"sfx": "drill_rumble.wav", "time_offset": 0.4, "gain": 0.35},
                {"sfx": "water_rush.wav", "time_offset": 1.0, "gain": 0.35}
            ]
        },
        {
            "input_video": str(ASSETS_DIR / "dubai_clip_3.mp4"),
            "narration_text": "Then the financial crash hit. Construction froze, and the ocean currents began reclaiming the coastlines.",
            "is_clean": True,
            "foley": [
                {"sfx": "gate_clank.wav", "time_offset": 0.5, "gain": 0.35},
                {"sfx": "dust_puff.wav", "time_offset": 1.5, "gain": 0.3}
            ]
        },
        {
            "input_video": str(ASSETS_DIR / "dubai_clip_4.mp4"),
            "narration_text": "Satellite tracking showed the islands slowly sinking and eroding back into the Persian Gulf.",
            "is_clean": True,
            "foley": [
                {"sfx": "radar_ping.wav", "time_offset": 0.4, "gain": 0.35},
                {"sfx": "warning_beep.wav", "time_offset": 1.2, "gain": 0.3}
            ]
        },
        {
            "input_video": str(ASSETS_DIR / "dubai_clip_5.mp4"),
            "narration_text": "Now, luxury developers are racing to fortify the sea walls before this hundred-billion-dollar wonder disappears.",
            "is_clean": True,
            "foley": [
                {"sfx": "impact_boom.wav", "time_offset": 0.5, "gain": 0.4},
                {"sfx": "desert_wind.wav", "time_offset": 1.0, "gain": 0.25}
            ]
        }
    ]

    master_filename = "Dubai_Islands_34s_Viral_Master_1080p.mp4"
    print(f"\n[BUILD] Assembling master short with narration, SFX, and kinetic subtitles...")
    out_path = await FlowMasterEngine.build_master_video(
        scenes=scenes,
        output_filename=master_filename,
        ambient_sfx="desert_wind.wav"
    )
    print(f"[SUCCESS] Master short assembled at: {out_path} ({out_path.stat().st_size / (1024*1024):.2f} MB)")

    # Copy to showcase folder
    showcase_dest = Path("data/showcase") / master_filename
    showcase_dest.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy(str(out_path), str(showcase_dest))
    print(f"[COPY] Copied to showcase folder: {showcase_dest}")

    # Step 3: Upload to YouTube Shorts
    title = "The $100 Billion Sinking Islands of Dubai #shorts"
    description = (
        "Three hundred artificial islands built with 320 million cubic meters of sand. "
        "Why is Dubai's most ambitious megaproject slowly being swallowed back into the Persian Gulf?\n\n"
        "🏝️ Like & Subscribe for daily high-retention engineering & business documentaries!\n\n"
        "#shorts #dubai #engineering #megaprojects #architecture #theworld #history #geopolitics"
    )
    tags = ["shorts", "dubai", "theworld", "megaprojects", "engineering", "architecture", "documentary"]

    print("\n[UPLOAD] Uploading Dubai Short to YouTube (Public)...")
    result = YouTubePublisher.upload_short_file(
        file_path=str(out_path),
        title=title,
        description=description,
        tags=tags,
        privacy_status="public"
    )

    print("Upload Result:", result)
    if result.get("success"):
        yt_id = result.get("youtube_video_id")
        short_url = f"https://youtube.com/shorts/{yt_id}"
        print(f"[LIVE] Short is live at: {short_url}")

        # Update log
        log_file = Path("data/daily_shorts_log.json")
        entries = []
        if log_file.exists():
            try:
                with open(log_file, "r") as f:
                    entries = json.load(f)
            except Exception:
                entries = []

        entries.append({
            "id": "dubai_sinking_islands",
            "title": title,
            "youtube_url": short_url,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

        with open(log_file, "w") as f:
            json.dump(entries, f, indent=2)

        print(f"[LOG] Updated {log_file}")
    else:
        print("[ERROR] Upload failed:", result.get("error"))

if __name__ == "__main__":
    asyncio.run(main())
