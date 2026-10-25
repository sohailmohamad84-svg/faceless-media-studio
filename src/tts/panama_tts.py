"""Voiceover synthesis module for the full Panama Canal documentary."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import asyncio
import subprocess
import edge_tts
from src.scripting.panama_script import PANAMA_CANAL_SCRIPT

async def synthesize_all_scenes():
    out_dir = Path("scratch/panama_audio")
    out_dir.mkdir(parents=True, exist_ok=True)
    voice = "en-US-ChristopherNeural"
    
    scene_durations = {}
    total_sec = 0.0
    
    print("Synthesizing voiceover for 18 scenes with Edge-TTS...")
    for act in PANAMA_CANAL_SCRIPT["acts"]:
        for sc in act["scenes"]:
            sc_id = sc["scene_id"]
            sc_file = out_dir / f"{sc_id}.mp3"
            
            # Synthesize with communicate
            c = edge_tts.Communicate(sc["narration"], voice, rate="+2%")
            await c.save(str(sc_file))
            
            # Get precise duration with ffprobe
            cmd = [
                "ffprobe", "-v", "error", "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1", str(sc_file)
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            dur = float(res.stdout.strip())
            scene_durations[sc_id] = dur
            total_sec += dur
            print(f"[{sc_id}] ({dur:.2f}s) {sc['title']}")
            
    print("-" * 50)
    print(f"Total Spoken Narration Duration: {total_sec:.2f} seconds ({total_sec / 60.0:.2f} minutes)")
    return scene_durations, total_sec

if __name__ == '__main__':
    asyncio.run(synthesize_all_scenes())
