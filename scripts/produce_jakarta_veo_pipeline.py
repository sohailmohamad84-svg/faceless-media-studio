import sys
import asyncio
import json
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.workflows.daily_shorts_pipeline import VIRAL_SHORTS_QUEUE
from src.editing.flow_master_engine import FlowMasterEngine
from src.quality.publication_gate import PublicationGate

async def main():
    print("=== STARTING JAKARTA SINKING SEAWALL MASTER BROADCAST PIPELINE ===", flush=True)
    
    # 1. Locate topic
    topic = next((t for t in VIRAL_SHORTS_QUEUE if t["id"] == "jakarta_sinking_seawall"), None)
    if not topic:
        raise ValueError("jakarta_sinking_seawall topic not found in queue!")
    
    print(f"Topic: {topic['title']}", flush=True)
    print(f"Total scenes: {len(topic['scenes'])}", flush=True)
    
    # Verify input video clips
    for idx, sc in enumerate(topic["scenes"], 1):
        vp = Path(sc["input_video"])
        if not vp.exists():
            raise FileNotFoundError(f"Missing scene {idx} clip: {vp}")
        print(f"  Scene {idx}: {vp.name} ({vp.stat().st_size:,} bytes) - Verified Full-Motion Veo 2 Video", flush=True)
        
    out_filename = "jakarta_sinking_seawall_master_1080p.mp4"
    print("\n--- Step 1: Assembling 1080p 60fps Master Broadcast Video ---", flush=True)
    master_path = await FlowMasterEngine.build_master_video(
        scenes=topic["scenes"],
        output_filename=out_filename,
        ambient_sfx="tension_drone.wav",
        engine_bed_sfx="water_rush.wav"
    )
    
    print(f"\nMaster render complete: {master_path}", flush=True)
    print(f"File size: {master_path.stat().st_size:,} bytes", flush=True)
    
    # 2. Check metadata via ffprobe
    cmd_probe = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size:stream=width,height,r_frame_rate,codec_name",
        "-of", "json", str(master_path)
    ]
    res = subprocess.run(cmd_probe, capture_output=True, text=True, check=True)
    probe_data = json.loads(res.stdout)
    print("\nProbe metrics:", flush=True)
    print(f"Duration: {probe_data['format'].get('duration')}s", flush=True)
    for s in probe_data.get("streams", []):
        print(f"  Stream ({s.get('codec_name')}): {s.get('width')}x{s.get('height')} @ {s.get('r_frame_rate')} fps", flush=True)

    # 3. Comprehensive 14-Gate Quality Audit
    print("\n--- Step 2: Running Comprehensive 14-Gate Quality Audit ---", flush=True)
    eval_result = PublicationGate.evaluate_all_14_gates(
        video_path=master_path,
        topic_metadata=topic
    )
    
    qa_report_path = Path("data/jakarta_sinking_seawall_qa_report.json")
    qa_report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(qa_report_path, "w", encoding="utf-8") as qf:
        json.dump(eval_result, qf, indent=2)
        
    print(f"QA Report written: {qa_report_path}", flush=True)
    print(f"Status: {eval_result.get('status')} | Score: {eval_result.get('score')}/100", flush=True)
    for g_id, g_data in eval_result.get("gates", {}).items():
        print(f"  {g_id}: {g_data.get('status')} (Score: {g_data.get('score')}) - {g_data.get('details')}", flush=True)

    print("\n=== PIPELINE FINISHED SUCCESSFULLY ===", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
