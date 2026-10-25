"""Render Suez Canal Short with 5 Dedicated Dynamic 9:16 Scenes and Master Video."""
import asyncio
import os
import sys
import subprocess
from pathlib import Path

# Force UTF-8 stdout
if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure project root in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.editing.flow_master_engine import FlowMasterEngine

ASSETS_DIR = Path("data/suez_assets")
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

CLIPS_CONFIG = [
    {
        "img": ASSETS_DIR / "suez_act1_wedged_ship.jpg",
        "clip": ASSETS_DIR / "suez_clip_1.mp4",
        "filter": "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0008,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=240:s=1080x1920:fps=24"
    },
    {
        "img": ASSETS_DIR / "suez_act2_excavator_bow.jpg",
        "clip": ASSETS_DIR / "suez_clip_2.mp4",
        "filter": "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='1.12':x='iw/2-(iw/zoom/2)':y='ih*0.05+ih*(on/240)*0.1':d=240:s=1080x1920:fps=24"
    },
    {
        "img": ASSETS_DIR / "suez_act3_satellite_radar.jpg",
        "clip": ASSETS_DIR / "suez_clip_3.mp4",
        "filter": "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0006,1.12)':x='iw/2-(iw/zoom/2)':y='ih*0.05+ih*(on/240)*0.06':d=240:s=1080x1920:fps=24"
    },
    {
        "img": ASSETS_DIR / "suez_act4_tugboats_action.jpg",
        "clip": ASSETS_DIR / "suez_clip_4.mp4",
        "filter": "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0010,1.18)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)+80':d=240:s=1080x1920:fps=24"
    },
    {
        "img": ASSETS_DIR / "suez_act5_refloated_sunset.jpg",
        "clip": ASSETS_DIR / "suez_clip_5.mp4",
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
    print("[START] SUEZ CANAL SHORT: DYNAMIC 5-SCENE MASTER RENDERING")
    print("=" * 60)

    # Step 1: Render each dynamic clip if not existing
    for item in CLIPS_CONFIG:
        render_dynamic_clip(item["img"], item["clip"], item["filter"])

    # Step 2: Build master video using FlowMasterEngine with 5 scenes
    scenes = [
        {
            "input_video": str(ASSETS_DIR / "suez_clip_1.mp4"),
            "narration_text": "Four hundred cargo ships were trapped in the desert. Not by pirates. By an invisible wall of sand.",
            "is_clean": True,
            "foley": [
                {"sfx": "tension_drone.wav", "time_offset": 0.0, "gain": 0.35},
                {"sfx": "impact_boom.wav", "time_offset": 0.5, "gain": 0.4}
            ]
        },
        {
            "input_video": str(ASSETS_DIR / "suez_clip_2.mp4"),
            "narration_text": "A forty-knot wind struck the world's longest container ship, jamming its twenty-thousand-ton bow into solid clay.",
            "is_clean": True,
            "foley": [
                {"sfx": "gate_clank.wav", "time_offset": 0.4, "gain": 0.35}
            ]
        },
        {
            "input_video": str(ASSETS_DIR / "suez_clip_3.mp4"),
            "narration_text": "Every single hour it remained stuck cost the global economy four hundred million dollars in frozen cargo.",
            "is_clean": True,
            "foley": [
                {"sfx": "warning_beep.wav", "time_offset": 0.2, "gain": 0.3}
            ]
        },
        {
            "input_video": str(ASSETS_DIR / "suez_clip_4.mp4"),
            "narration_text": "Fourteen massive tugboats and thirty thousand tons of dredged silt fought against the Mediterranean tide.",
            "is_clean": True,
            "foley": [
                {"sfx": "water_rush.wav", "time_offset": 0.5, "gain": 0.35}
            ]
        },
        {
            "input_video": str(ASSETS_DIR / "suez_clip_5.mp4"),
            "narration_text": "Six days later, a full moon super-tide lifted the monster free, proving the fragility of modern civilization.",
            "is_clean": True,
            "foley": [
                {"sfx": "ship_horn.wav", "time_offset": 0.5, "gain": 0.45}
            ]
        }
    ]

    master_filename = "Suez_Canal_50s_Viral_Master_1080p.mp4"
    print(f"\n[BUILD] Assembling 50s master video with narration, SFX, and kinetic subtitles...")
    out_path = await FlowMasterEngine.build_master_video(
        scenes=scenes,
        output_filename=master_filename,
        ambient_sfx="desert_wind.wav"
    )
    print(f"[SUCCESS] Master successfully assembled at: {out_path} ({out_path.stat().st_size / (1024*1024):.2f} MB)")

    # Copy to showcase folder
    showcase_dest = Path("data/showcase") / master_filename
    showcase_dest.parent.mkdir(parents=True, exist_ok=True)
    import shutil
    shutil.copy(str(out_path), str(showcase_dest))
    print(f"[COPY] Copied to showcase folder: {showcase_dest}")

    # Step 3: Extract verification frames
    art_dir = Path(r"C:\Users\Sohail\.gemini\antigravity\brain\eb4bd0b7-d463-4e01-b351-a971179e01ed")
    frame_times = [
        (5.0, "suez_verify_act1_5s.jpg", "Act 1: Trapped in the Desert (0-10s)"),
        (15.0, "suez_verify_act2_15s.jpg", "Act 2: Excavator vs Colossal Bow (10-20s)"),
        (25.0, "suez_verify_act3_25s.jpg", "Act 3: Satellite Radar Gridlock (20-30s)"),
        (35.0, "suez_verify_act4_35s.jpg", "Act 4: High-Tension Tugboat Salvage (30-40s)"),
        (45.0, "suez_verify_act5_45s.jpg", "Act 5: Refloated Monster at Sunset (40-50s)")
    ]

    print("\n[VERIFY] Extracting verification snapshot frames from the finished master...")
    for t_sec, fname, label in frame_times:
        frame_out = art_dir / fname
        cmd_f = [
            "ffmpeg", "-y",
            "-ss", str(t_sec),
            "-i", str(out_path),
            "-vframes", "1",
            "-q:v", "2",
            str(frame_out)
        ]
        subprocess.run(cmd_f, check=True)
        print(f"  [FRAME] {label} -> {fname}")

    print("\n[DONE] All verification snapshots captured!")

if __name__ == "__main__":
    asyncio.run(main())
