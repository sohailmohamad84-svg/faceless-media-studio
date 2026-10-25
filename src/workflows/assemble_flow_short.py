"""Master assembly script for the Google Flow + Studio Hybrid Viral Short."""
import asyncio
import subprocess
from pathlib import Path
import numpy as np
import edge_tts

fps = 24
vw, vh = 1080, 1920
work_dir = Path("scratch/flow_master_work")
work_dir.mkdir(parents=True, exist_ok=True)
clips_dir = Path("data/flow_clips")
sfx_dir = Path("data/sfx")

SCENES = [
    {
        "id": "s1_hook",
        "file": "scene1_cargo_ship_rising.mp4",
        "text": "This eighty-thousand-ton cargo ship is floating eighty-five feet in the air—and it's trapped on top of a mountain.",
        "sfx": [("ship_horn.wav", 0.4, 0.7), ("water_rush.wav", 2.2, 0.5)]
    },
    {
        "id": "s2_paradox",
        "file": "scene2_ocean_split.mp4",
        "text": "Most people think the Panama Canal is a flat ditch. But if you dug a sea-level canal, the Pacific Ocean would literally drown Central America in lethal twenty-foot tidal waves!",
        "sfx": [("water_rush.wav", 1.0, 0.6), ("whoosh.wav", 4.5, 0.4), ("impact_boom.wav", 6.8, 0.5)]
    },
    {
        "id": "s3_locks",
        "file": "scene3_lock_gates.mp4",
        "text": "So instead, natural gravity floods the chambers with twenty-six million gallons, lifting ships twenty-eight feet at a time without a single water pump!",
        "sfx": [("gate_clank.wav", 0.8, 0.7), ("water_rush.wav", 2.5, 0.6)]
    },
    {
        "id": "s4_drought",
        "file": "scene4_drought_lake.mp4",
        "text": "Every time ONE ship crosses, fifty-two million gallons of fresh drinking water are flushed into the ocean! So when severe drought hit in 2023, the lake ran out of water!",
        "sfx": [("desert_wind.wav", 0.2, 0.4), ("warning_beep.wav", 2.5, 0.5), ("impact_boom.wav", 7.0, 0.5)]
    },
    {
        "id": "s5_auction_gridlock",
        "file": "scene5_ship_gridlock.mp4",
        "text": "Over one hundred and sixty ships were stranded at sea, and one company paid a crazy four million dollar bribe at auction just to skip the line—proving that global trade lives and dies by jungle rain.",
        "sfx": [("ship_horn.wav", 0.8, 0.6), ("auction_gavel.wav", 3.2, 0.8), ("impact_boom.wav", 3.2, 0.6)]
    }
]

def load_audio_pcm(file_path, sample_rate=44100):
    cmd = [
        "ffmpeg", "-y", "-i", str(file_path),
        "-f", "s16le", "-ac", "1", "-ar", str(sample_rate), "-"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    return np.frombuffer(res.stdout, dtype=np.int16).astype(np.float32) / 32768.0

async def build_short():
    sr = 44100
    voice = "en-US-ChristopherNeural"
    
    # 1. Synthesize Voiceovers & determine trim durations
    total_dur = 0.0
    for sc in SCENES:
        vo_out = work_dir / f"{sc['id']}_vo.mp3"
        c = edge_tts.Communicate(sc["text"], voice, rate="+7%")
        await c.save(str(vo_out))
        
        # Get duration
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(vo_out)]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        vo_dur = float(res.stdout.strip())
        clip_dur = max(vo_dur + 0.4, 7.5) # Dynamic clip duration tailored to narration
        sc["vo_dur"] = vo_dur
        sc["clip_dur"] = clip_dur
        sc["vo_file"] = vo_out
        total_dur += clip_dur
        print(f"[{sc['id']}] VO: {vo_dur:.2f}s | Clip Duration: {clip_dur:.2f}s")
        
    print(f"Total Master Video Duration: {total_dur:.2f} seconds (<60s)")
    
    # 2. Trim & Prepare Video Clips to exact duration
    trimmed_clips = []
    for i, sc in enumerate(SCENES):
        in_p = clips_dir / sc["file"]
        out_p = work_dir / f"trimmed_{i}.mp4"
        cmd = [
            "ffmpeg", "-y",
            "-i", str(in_p),
            "-t", f"{sc['clip_dur']:.2f}",
            "-vf", "scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,fps=24",
            "-c:v", "libx264", "-preset", "fast", "-crf", "18",
            "-an",
            str(out_p)
        ]
        subprocess.run(cmd, check=True)
        trimmed_clips.append(out_p)
        
    # Concatenate video stream
    concat_txt = work_dir / "concat.txt"
    with open(concat_txt, "w") as f:
        for p in trimmed_clips:
            clean_p = str(p.resolve()).replace("\\", "/")
            f.write(f"file '{clean_p}'\n")
            
    raw_video = work_dir / "raw_video.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(raw_video)], check=True)
    
    # 3. Foley Audio Mixing
    total_samples = int(total_dur * sr)
    master = np.zeros(total_samples, dtype=np.float32)
    
    # Ambient sound bed (ocean/wind)
    wind = load_audio_pcm(sfx_dir / "desert_wind.wav", sr) * 0.15
    for s in range(0, total_samples, len(wind)):
        e = min(total_samples, s + len(wind))
        master[s:e] += wind[:e-s]
        
    cur_t = 0.0
    for sc in SCENES:
        vo = load_audio_pcm(sc["vo_file"], sr) * 1.05
        vs = int((cur_t + 0.15) * sr)
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
        
    # Normalize audio
    max_v = np.max(np.abs(master))
    if max_v > 0.95:
        master = (master / max_v) * 0.95
        
    master_audio = work_dir / "master_audio.wav"
    import wave
    with wave.open(str(master_audio), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((master * 32767).astype(np.int16).tobytes())
        
    # 4. Mobile Sweet-Spot Subtitles (.ass)
    ass_path = work_dir / "subtitles.ass"
    ass_lines = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: FlowSub,Arial,66,&H0020FFFF,&H00000000,&H00000000,&HA0000000,-1,0,0,0,100,100,2,0,1,5.5,3.0,2,60,60,820,1", "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]
    
    cur_t = 0.0
    for sc in SCENES:
        words = sc["text"].split()
        chunk_sz = 3
        dur = sc["vo_dur"]
        w_per_s = len(words) / dur
        
        for ci in range(0, len(words), chunk_sz):
            c_words = words[ci:ci + chunk_sz]
            c_text = " ".join(c_words).upper()
            ws = cur_t + 0.15 + (ci / w_per_s)
            we = min(cur_t + sc["clip_dur"], cur_t + 0.15 + ((ci + chunk_sz) / w_per_s))
            
            def fmt(sec):
                h = int(sec // 3600)
                m = int((sec % 3600) // 60)
                s = int(sec % 60)
                ms = int((sec - int(sec)) * 100)
                return f"{h}:{m:02d}:{s:02d}.{ms:02d}"
                
            ass_lines.append(f"Dialogue: 0,{fmt(ws)},{fmt(we)},FlowSub,,0,0,0,,{c_text}")
            
        cur_t += sc["clip_dur"]
        
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("\n".join(ass_lines))
        
    # 5. Final Mux
    out_final = Path("exports/Panama_Canal_Trap_Google_Flow_Viral_Short.mp4")
    cmd_mux = [
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(master_audio),
        "-vf", "subtitles=scratch/flow_master_work/subtitles.ass",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{total_dur:.2f}",
        str(out_final)
    ]
    subprocess.run(cmd_mux, check=True)
    print("=" * 60)
    print(f"GOOGLE FLOW MASTER VIRAL SHORT CREATED: {out_final}")
    print(f"Duration: {total_dur:.2f}s | Resolution: 1080x1920")
    print("=" * 60)
    return out_final

if __name__ == "__main__":
    asyncio.run(build_short())
