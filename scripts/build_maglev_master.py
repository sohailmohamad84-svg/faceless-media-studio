import asyncio
import json
import os
import sys
from pathlib import Path

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Add src to sys.path
sys.path.insert(0, os.path.abspath("."))

from src.editing.flow_master_engine import FlowMasterEngine
from src.quality.ai_video_inspector import AIVideoInspector
from src.workflows.daily_shorts_pipeline import VIRAL_SHORTS_QUEUE

async def main():
    print("=======================================================", flush=True)
    print("🚀 ASSEMBLING 60 FPS MASTER VIDEO (GOOGLE VEO 2 / FLOW)", flush=True)
    print("=======================================================", flush=True)
    
    # Find japan_maglev_speed in VIRAL_SHORTS_QUEUE
    topic = next((t for t in VIRAL_SHORTS_QUEUE if t["id"] == "japan_maglev_speed"), None)
    if not topic:
        print("Error: japan_maglev_speed topic not found in rotation!", flush=True)
        return
        
    scenes = topic["scenes"]
    print(f"Total scenes to assemble: {len(scenes)}", flush=True)
    for sc in scenes:
        print(f"  Scene {sc['scene_num']}: {sc['title']} -> {sc['input_video']} (Exists: {os.path.exists(sc['input_video'])})", flush=True)
        
    out_filename = "japan_maglev_speed_master_1080p.mp4"
    print(f"\nBuilding master video: exports/{out_filename}...", flush=True)
    master_path = await FlowMasterEngine.build_master_video(
        scenes=scenes,
        output_filename=out_filename,
        ambient_sfx="tension_drone.wav"
    )
    print(f"Master video built successfully at: {master_path}", flush=True)
    print(f"File size: {os.path.getsize(master_path)} bytes", flush=True)
    
    # Run AI Quality Inspector
    print("\n=======================================================", flush=True)
    print("🔍 RUNNING AI VIDEO QUALITY INSPECTOR (GATEKEEPER)", flush=True)
    print("=======================================================", flush=True)
    scorecard = AIVideoInspector.evaluate_video(str(master_path), is_veo_flow_source=True)
    print("Scorecard Result:")
    print(json.dumps(scorecard, indent=2))
    
    scorecard_path = Path("exports/japan_maglev_speed_scorecard.json")
    with open(scorecard_path, "w", encoding="utf-8") as f:
        json.dump(scorecard, f, indent=2)
    print(f"Scorecard saved to: {scorecard_path}", flush=True)

if __name__ == "__main__":
    asyncio.run(main())
