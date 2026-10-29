"""Assemble the repaired 92.0-second SR-71 Blackbird Unstart Master Short.
Synthesizes speech (+16% rate), renders dynamic ducked audio bed, masters to EBU R128 (-14.0 LUFS),
applies kinetic gold subtitles with safe margins, and muxes to 1080x1920 60 FPS yuv420p broadcast master.
"""
import asyncio
import json
import subprocess
import sys
from pathlib import Path

# Ensure root in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.workflows.daily_shorts_pipeline import VIRAL_SHORTS_QUEUE
from src.editing.flow_master_engine import FlowMasterEngine

async def run_assembly():
    topic = next((t for t in VIRAL_SHORTS_QUEUE if t['id'] == 'sr71_blackbird_unstart'), None)
    if not topic:
        raise ValueError("Topic sr71_blackbird_unstart not found in VIRAL_SHORTS_QUEUE!")
        
    print(f"Loaded topic: {topic['title']}")
    print(f"Total scenes: {len(topic['scenes'])}")
    for sc in topic['scenes']:
        inp = Path(sc['input_video'])
        print(f"  Act {sc['scene_num']}: {sc['title']} -> {inp} (exists={inp.exists()})")
        
    out_filename = "sr71_blackbird_unstart_master_1080p.mp4"
    print(f"\nBuilding master video: exports/{out_filename}...")
    
    master_path = await FlowMasterEngine.build_master_video(
        scenes=topic['scenes'],
        output_filename=out_filename,
        ambient_sfx="tension_drone.wav",
        engine_bed_sfx="jet_engine_rumble.wav",
        target_scene_duration=11.50
    )
    
    print(f"\nSUCCESS: Master video assembled at: {master_path}")
    print(f"File size: {master_path.stat().st_size:,} bytes")
    
    # Probe result
    cmd = [
        "ffprobe", "-v", "quiet", "-print_format", "json",
        "-show_format", "-show_streams", str(master_path)
    ]
    res = json.loads(subprocess.check_output(cmd).decode())
    fmt = res["format"]
    v_st = next((s for s in res["streams"] if s["codec_type"] == "video"), {})
    a_st = next((s for s in res["streams"] if s["codec_type"] == "audio"), {})
    
    print("\nMaster Video Container Metrics:")
    print(f"  Duration: {float(fmt.get('duration', 0)):.6f} seconds")
    print(f"  Resolution: {v_st.get('width')}x{v_st.get('height')}")
    print(f"  Video Codec: {v_st.get('codec_name')} (Profile: {v_st.get('profile')})")
    print(f"  Pixel Format: {v_st.get('pix_fmt')}")
    print(f"  Color Range: {v_st.get('color_range')}")
    print(f"  Frame Rate: {v_st.get('r_frame_rate')} fps")
    print(f"  Video Bitrate: {int(fmt.get('bit_rate', 0)):,} bps (~{int(fmt.get('bit_rate', 0))/1_000_000:.2f} Mbps)")
    print(f"  Audio: {a_st.get('codec_name')} {a_st.get('sample_rate')}Hz, {a_st.get('channels')} channels")

if __name__ == "__main__":
    asyncio.run(run_assembly())
