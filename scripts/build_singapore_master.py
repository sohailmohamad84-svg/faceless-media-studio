"""Build and Inspect Singapore Sand Empire Broadcast Master Short.
Runs upgraded FlowMasterEngine:
- Dynamic audio ducking (-7 dB ambience, -30% Foley)
- EBU R128 loudness mastering (I=-14.0, TP=-1.0, LRA=7.0)
- Character-weighted kinetic gold ASS subtitles (Arial Black 58pt)
- Evaluates with AIVideoInspector 2.0 (8 categories, 8 blocking gates)
- Extracts verification proof frames from all 8 acts
"""
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Add project root to sys.path
sys.path.insert(0, os.path.abspath("."))

from src.editing.flow_master_engine import FlowMasterEngine
from src.quality.ai_video_inspector import AIVideoInspector
from src.workflows.daily_shorts_pipeline import VIRAL_SHORTS_QUEUE

async def build_and_evaluate():
    topic = next((t for t in VIRAL_SHORTS_QUEUE if t["id"] == "singapore_sand_empire"), None)
    if not topic:
        print("ERROR: Singapore topic not found in queue!")
        return False

    out_filename = "singapore_sand_empire_master_1080p.mp4"
    print("=======================================================", flush=True)
    print(f"🎬 BUILDING MASTER VIDEO: {topic['title']}", flush=True)
    print("=======================================================", flush=True)

    master_path = await FlowMasterEngine.build_master_video(
        scenes=topic["scenes"],
        output_filename=out_filename,
        ambient_sfx="tension_drone.wav"
    )

    print(f"\n✅ Master video assembled at: {master_path} ({os.path.getsize(master_path):,} bytes)", flush=True)

    # Run AIVideoInspector 2.0
    print("\n=======================================================", flush=True)
    print("🔍 RUNNING AI VIDEO INSPECTOR 2.0 COMPREHENSIVE QA AUDIT", flush=True)
    print("=======================================================", flush=True)

    eval_result = AIVideoInspector.evaluate_video(
        video_path=str(master_path),
        is_veo_flow_source=True,
        topic_metadata=topic
    )

    print("AI Quality Score:", f"{eval_result['score']}/100 | Verdict: {eval_result['verdict']}")
    print("\nCategory Breakdown Scores:")
    for cat, sc in eval_result.get("category_scores", {}).items():
        print(f"  - {cat}: {sc}")

    print("\nBlocking Gates:")
    for gate, status in eval_result.get("blocking_gates", {}).items():
        print(f"  - {gate}: {status}")

    print("\nEmpirical Technical & Audio Metrics:")
    for k, v in eval_result.get("metrics", {}).items():
        print(f"  - {k}: {v}")

    if eval_result.get("flags"):
        print("\nInspector Flags:", eval_result.get("flags"))

    # Extract 8 visual verification frames (one from each act)
    print("\n=======================================================", flush=True)
    print("📸 EXTRACTING VERIFICATION PROOF FRAMES (ACTS 1 TO 8)", flush=True)
    print("=======================================================", flush=True)
    
    artifact_dir = Path(r"C:\Users\Sohail\.gemini\antigravity\brain\eb4bd0b7-d463-4e01-b351-a971179e01ed")
    artifact_dir.mkdir(parents=True, exist_ok=True)
    
    duration = eval_result["metrics"].get("duration_seconds", 60.0)
    act_step = duration / 8.0
    
    for act_idx in range(1, 9):
        sample_time = min(duration - 0.5, (act_idx - 1) * act_step + (act_step * 0.45))
        frame_path = artifact_dir / f"singapore_act_{act_idx}_proof.jpg"
        
        cmd_snap = [
            "ffmpeg", "-y",
            "-ss", f"{sample_time:.2f}",
            "-i", str(master_path),
            "-vframes", "1",
            str(frame_path)
        ]
        subprocess.run(cmd_snap, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"  - Act {act_idx} frame at {sample_time:.1f}s -> {frame_path.name} ({frame_path.stat().st_size:,} bytes)")

    # Save QA results to JSON file
    qa_json_path = artifact_dir / "singapore_sand_empire_qa_report.json"
    with open(qa_json_path, "w", encoding="utf-8") as f:
        json.dump(eval_result, f, indent=2)
    print(f"\nSaved full QA audit report to: {qa_json_path}")
    print("=======================================================", flush=True)

    return eval_result["verdict"] == "PASS"

if __name__ == "__main__":
    success = asyncio.run(build_and_evaluate())
    if not success:
        sys.exit(1)
