"""Option B Master Production Script:
100% Correlated Technical Motion Schematics + Synchronized Narration + Audio Foley
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import asyncio
import subprocess
import wave
import numpy as np
import edge_tts
from src.assets.schematic_motion_designer import (
    render_scene1_elevation_schematic,
    render_scene2_tidal_schematic,
    render_scene3_hydraulic_schematic,
    render_scene4_drought_schematic,
    render_scene5_auction_schematic
)

fps = 30
sr = 44100
vw, vh = 1920, 1080
work_dir = Path("scratch/option_b_work")
work_dir.mkdir(parents=True, exist_ok=True)
sfx_dir = Path("data/sfx")

SCENES = [
    {
        "id": "sc1_elevation",
        "renderer": render_scene1_elevation_schematic,
        "text": "This eighty-thousand-ton cargo ship is floating eighty-five feet in the air—and it's trapped on top of a mountain!",
        "sfx": [("ship_horn.wav", 0.4, 0.45)]
    },
    {
        "id": "sc2_tidal",
        "renderer": render_scene2_tidal_schematic,
        "text": "If engineers dug a flat sea-level ditch here, the Pacific Ocean would drown Central America in lethal twenty-foot tidal waves!",
        "sfx": [("water_rush.wav", 1.2, 0.45)]
    },
    {
        "id": "sc3_hydraulic",
        "renderer": render_scene3_hydraulic_schematic,
        "text": "So natural gravity floods the chambers with twenty-six million gallons, lifting ships twenty-eight feet at a time without a single pump!",
        "sfx": [("gate_clank.wav", 0.6, 0.45), ("water_rush.wav", 2.0, 0.4)]
    },
    {
        "id": "sc4_drought",
        "renderer": render_scene4_drought_schematic,
        "text": "Every single ship flushes fifty-two million gallons of fresh drinking water into the sea! When drought hit, the lake ran dry!",
        "sfx": [("desert_wind.wav", 0.2, 0.35)]
    },
    {
        "id": "sc5_auction",
        "renderer": render_scene5_auction_schematic,
        "text": "Over one hundred and sixty ships were stranded at sea, with one company paying four million dollars at auction just to skip the line!",
        "sfx": [("auction_gavel.wav", 3.8, 0.65)]
    }
]

def load_audio_pcm(file_path, sample_rate=44100):
    cmd = [
        "ffmpeg", "-y", "-i", str(file_path),
        "-f", "s16le", "-ac", "1", "-ar", str(sample_rate), "-"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    return np.frombuffer(res.stdout, dtype=np.int16).astype(np.float32) / 32768.0

async def build_option_b():
    voice = "en-US-ChristopherNeural"
    
    # 1. Synthesize Narration Audio
    total_dur = 0.0
    for sc in SCENES:
        vo_out = work_dir / f"{sc['id']}_vo.mp3"
        c = edge_tts.Communicate(sc["text"], voice, rate="+7%")
        await c.save(str(vo_out))
        
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(vo_out)]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        dur = float(res.stdout.strip())
        sc["vo_dur"] = dur
        sc["clip_dur"] = dur + 0.4
        sc["vo_file"] = vo_out
        total_dur += sc["clip_dur"]
        print(f"[{sc['id']}] VO: {dur:.2f}s | Clip Duration: {sc['clip_dur']:.2f}s")
        
    print(f"Total Master Video Duration: {total_dur:.2f} seconds")
    
    # 2. Render all 5 high-clarity technical schematics
    rendered_clips = []
    for sc in SCENES:
        print(f"Rendering schematic for {sc['id']} (duration: {sc['clip_dur']:.2f}s)...")
        clip_p = sc["renderer"](sc["clip_dur"])
        rendered_clips.append(clip_p)
        
    # Concat video stream
    concat_txt = work_dir / "concat_option_b.txt"
    with open(concat_txt, "w") as f:
        for p in rendered_clips:
            clean_p = str(p.resolve()).replace("\\", "/")
            f.write(f"file '{clean_p}'\n")
            
    raw_video = work_dir / "raw_option_b.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(raw_video)], check=True)
    
    # 3. Foley Audio Mixing with continuous documentary tension bed
    total_samples = int(total_dur * sr)
    master = np.zeros(total_samples, dtype=np.float32)
    
    ambient = load_audio_pcm(sfx_dir / "tension_drone.wav", sr) * 0.12
    for s in range(0, total_samples, len(ambient)):
        e = min(total_samples, s + len(ambient))
        master[s:e] += ambient[:e - s]
        
    cur_t = 0.0
    for sc in SCENES:
        vo = load_audio_pcm(sc["vo_file"], sr) * 1.05
        vs = int((cur_t + 0.1) * sr)
        ve = min(total_samples, vs + len(vo))
        master[vs:ve] += vo[:ve - vs]
        
        for sfx_name, sfx_offset, sfx_vol in sc["sfx"]:
            sfx_p = sfx_dir / sfx_name
            if sfx_p.exists():
                s_data = load_audio_pcm(sfx_p, sr) * sfx_vol
                ss = int((cur_t + sfx_offset) * sr)
                se = min(total_samples, ss + len(s_data))
                if ss < total_samples:
                    master[ss:se] += s_data[:se - ss]
                    
        cur_t += sc["clip_dur"]
        
    # Audio end fade
    fade_len = int(0.6 * sr)
    if total_samples > fade_len:
        master[-fade_len:] *= np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
        
    max_v = np.max(np.abs(master))
    if max_v > 0.95:
        master = (master / max_v) * 0.95
        
    master_audio = work_dir / "master_audio_option_b.wav"
    with wave.open(str(master_audio), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((master * 32767).astype(np.int16).tobytes())
        
    # 4. Synchronized Subtitles
    ass_path = work_dir / "subtitles_option_b.ass"
    ass_lines = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: DocSub,Arial,48,&H00E8FFFF,&H00000000,&H00000000,&HA0000000,-1,0,0,0,100,100,1,0,1,4.0,2.5,2,80,80,95,1", "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]
    
    cur_t = 0.0
    for sc in SCENES:
        words = sc["text"].split()
        chunk_sz = 4
        dur = sc["vo_dur"]
        w_per_s = len(words) / dur
        
        for ci in range(0, len(words), chunk_sz):
            c_words = words[ci:ci + chunk_sz]
            c_text = " ".join(c_words)
            ws = cur_t + 0.1 + (ci / w_per_s)
            we = min(cur_t + sc["clip_dur"], cur_t + 0.1 + ((ci + chunk_sz) / w_per_s))
            
            def fmt(sec):
                h = int(sec // 3600)
                m = int((sec % 3600) // 60)
                s = int(sec % 60)
                ms = int((sec - int(sec)) * 100)
                return f"{h}:{m:02d}:{s:02d}.{ms:02d}"
                
            ass_lines.append(f"Dialogue: 0,{fmt(ws)},{fmt(we)},DocSub,,0,0,0,,{c_text}")
            
        cur_t += sc["clip_dur"]
        
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("\n".join(ass_lines))
        
    # 5. Final Mux
    out_final = Path("exports/Panama_Canal_OptionB_Schematic_Master_1080p.mp4")
    cmd_mux = [
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(master_audio),
        "-vf", "subtitles=scratch/option_b_work/subtitles_option_b.ass",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{total_dur:.2f}",
        str(out_final)
    ]
    subprocess.run(cmd_mux, check=True)
    print("=" * 60)
    print(f"OPTION B MASTER SCHEMATIC VIDEO PRODUCED: {out_final}")
    print(f"Duration: {total_dur:.2f}s | Resolution: 1920x1080 Full HD")
    print("=" * 60)
    return out_final

if __name__ == "__main__":
    asyncio.run(build_option_b())
