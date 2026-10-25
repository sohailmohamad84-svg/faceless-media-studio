"""Produce a viral 49-second 1080x1920 YouTube Short on 'The Panama Canal Mountain Trap'."""
import asyncio
import math
import subprocess
import wave
import numpy as np
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import edge_tts

fps = 30
vw, vh = 1080, 1920
shorts_dir = Path("scratch/panama_short_work")
shorts_dir.mkdir(parents=True, exist_ok=True)
v_assets_dir = Path("data/assets/panama_shorts")
p_assets_dir = Path("data/assets/panama_anim")

def get_font(size, bold=True):
    try:
        font_name = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(font_name, size)
    except:
        return ImageFont.load_default()

def load_audio_pcm(file_path, sample_rate=44100):
    cmd = [
        "ffmpeg", "-y", "-i", str(file_path),
        "-f", "s16le", "-ac", "1", "-ar", str(sample_rate), "-"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    return np.frombuffer(res.stdout, dtype=np.int16).astype(np.float32) / 32768.0

# Pre-load graphics
bg_elevator = Image.open(v_assets_dir / "bg_vertical_elevator.png").convert("RGBA")
bg_map = Image.open(v_assets_dir / "bg_vertical_map.png").convert("RGBA")
bg_lock = Image.open(v_assets_dir / "bg_vertical_lock.png").convert("RGBA")
bg_drought = Image.open(v_assets_dir / "bg_vertical_drought.png").convert("RGBA")
prop_ship = Image.open(p_assets_dir / "prop_container_ship.png").convert("RGBA")
prop_mule = Image.open(p_assets_dir / "prop_electric_mule.png").convert("RGBA")

SHORT_SCENES = [
    {
        "id": "s1_hook",
        "dur": 7.5,
        "text": "This eighty-thousand-ton cargo ship is floating eighty-five feet in the air—and it's trapped on top of a mountain.",
        "type": "ELEVATOR"
    },
    {
        "id": "s2_paradox",
        "dur": 9.5,
        "text": "Most people think the Panama Canal is a flat sea-level ditch. But if you dug a flat ditch here, the Pacific Ocean would literally drown Central America in lethal twenty-foot tidal waves.",
        "type": "MAP"
    },
    {
        "id": "s3_locks",
        "dur": 12.0,
        "text": "So instead, engineers built a massive water elevator. Without a single water pump, natural gravity floods the chambers with twenty-six million gallons, lifting the ship twenty-eight feet at a time.",
        "type": "LOCKS"
    },
    {
        "id": "s4_drought",
        "dur": 10.5,
        "text": "Every time ONE ship crosses, fifty-two million gallons of fresh drinking water are flushed into the ocean and lost forever! So when severe drought hit in 2023, the lake ran out of water!",
        "type": "DROUGHT"
    },
    {
        "id": "s5_auction_loop",
        "dur": 10.0,
        "text": "Over one hundred and sixty ships were stranded at sea, and one company paid a crazy four million dollar bribe at auction just to skip the line—proving that global trade lives and dies by jungle rain.",
        "type": "AUCTION"
    }
]

async def generate_short_audio():
    voice = "en-US-ChristopherNeural"
    durations = []
    for sc in SHORT_SCENES:
        out_f = shorts_dir / f"{sc['id']}.mp3"
        c = edge_tts.Communicate(sc["text"], voice, rate="+6%")
        await c.save(str(out_f))
        
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(out_f)]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        dur = float(res.stdout.strip())
        sc["actual_dur"] = dur
        durations.append(dur)
        print(f"Synthesized {sc['id']}: {dur:.2f}s")
    return durations

def render_short_scene(sc_idx, sc, duration):
    out_mp4 = shorts_dir / f"clip_{sc_idx}.mp4"
    total_frames = int(fps * duration)
    
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgba",
        "-s", f"{vw}x{vh}", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
        str(out_mp4)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    sc_type = sc["type"]
    np.random.seed(sc_idx * 23)
    
    for f in range(total_frames):
        t = f / fps
        frame = Image.new("RGBA", (vw, vh), (0, 0, 0, 255))
        
        if sc_type == "ELEVATOR":
            # Scene 1: Container ship sitting atop mountain locks with snap zoom
            frame = bg_elevator.copy()
            # Position container ship on summit water (y: 860 to 980)
            ship_w = 480
            ship_h = int(prop_ship.height * (ship_w / prop_ship.width))
            scaled_ship = prop_ship.resize((ship_w, ship_h), Image.Resampling.LANCZOS)
            
            # Snap zoom into ship at t = 2.0s
            if t < 2.0:
                zoom = 1.0
            elif t < 2.3:
                zoom = 1.0 + 0.35 * ((t - 2.0) / 0.3)
            else:
                zoom = 1.35 + 0.01 * math.sin((t - 2.3) * 12)
                
            # Ship bobbing in water
            bob = int(math.sin(t * 3.5) * 4)
            ship_layer = Image.new("RGBA", (vw, vh), (0, 0, 0, 0))
            ship_layer.alpha_composite(scaled_ship, (540, 830 + bob))
            frame.alpha_composite(ship_layer)
            
            if zoom > 1.001:
                cw, ch = int(vw / zoom), int(vh / zoom)
                cx, cy = 680, 900
                x1 = max(0, min(cx - cw // 2, vw - cw))
                y1 = max(0, min(cy - ch // 2, vh - ch))
                frame = frame.crop((x1, y1, x1 + cw, y1 + ch)).resize((vw, vh), Image.Resampling.BILINEAR)
                
        elif sc_type == "MAP":
            # Scene 2: Vertical map with pulsing tidal difference
            frame = bg_map.copy()
            hud = Image.new("RGBA", (vw, vh), (0, 0, 0, 0))
            h_draw = ImageDraw.Draw(hud)
            # Pulsing danger ring around Pacific entrance
            phase = (t * 2.5) % 1.0
            r = int(20 + phase * 70)
            alpha = int(240 * (1 - phase))
            h_draw.ellipse((380 - r, 940 - r, 380 + r, 940 + r), outline=(255, 60, 50, alpha), width=5)
            frame.alpha_composite(hud)
            
        elif sc_type == "LOCKS":
            # Scene 3: Lock interior with rising water level and container ship
            frame = bg_lock.copy()
            # Water level rises over duration
            rise_px = int(min(180, (t / duration) * 220))
            
            ship_w = 640
            ship_h = int(prop_ship.height * (ship_w / prop_ship.width))
            scaled_ship = prop_ship.resize((ship_w, ship_h), Image.Resampling.LANCZOS)
            # Ship floats up from y: 880 to y: 700
            sy = 880 - rise_px + int(math.sin(t * 3.5) * 4)
            frame.alpha_composite(scaled_ship, (220, sy))
            
            # Electric Mule on left track
            mule_w = 240
            mule_h = int(prop_mule.height * (mule_w / prop_mule.width))
            scaled_mule = prop_mule.resize((mule_w, mule_h), Image.Resampling.LANCZOS)
            frame.alpha_composite(scaled_mule, (40, 1080 - int(rise_px * 0.4)))
            
        elif sc_type == "DROUGHT":
            # Scene 4: Drought lake with sinking water line & heat mirage
            frame = bg_drought.copy()
            arr = np.array(frame)
            # Heat wave distortion
            y_start, y_end = 600, 1100
            sl = arr[y_start:y_end]
            shifts = (3.5 * np.sin(2 * np.pi * np.arange(y_end - y_start) / 45.0 - 6 * np.pi * t)).astype(int)
            for i, s in enumerate(shifts):
                if s != 0:
                    sl[i] = np.roll(sl[i], s, axis=0)
            arr[y_start:y_end] = sl
            frame = Image.fromarray(arr)
            
        else: # AUCTION
            # Scene 5: $4 Million Auction Climax & Loop Finale
            frame = bg_drought.copy()
            draw = ImageDraw.Draw(frame)
            # Dollar bills raining down
            for pi in range(25):
                px = (pi * 45 + int(t * 80)) % vw
                py = (pi * 95 + int(t * 240)) % vh
                draw.rectangle([px, py, px + 50, py + 26], fill=(120, 200, 110, 230), outline=(20, 80, 20, 255), width=2)
                draw.text((px + 12, py + 4), "$", font=get_font(18, True), fill=(20, 80, 20, 255))
                
            # Auction Gavel impact screen shake at t = 1.0s
            if 0.9 < t < 1.3:
                shake_x = int(math.sin((t - 0.9) * 80) * 12)
                shake_y = int(math.cos((t - 0.9) * 90) * 8)
                frame = frame.transform(frame.size, Image.AFFINE, (1, 0, shake_x, 0, 1, shake_y))
                
        # Universal Shorts Header Tag (Top of Mobile Screen)
        hud = Image.new("RGBA", (vw, vh), (0, 0, 0, 0))
        h_draw = ImageDraw.Draw(hud)
        h_draw.rounded_rectangle([60, 60, vw - 60, 130], radius=12, fill=(15, 20, 30, 220), outline=(255, 215, 0, 240), width=3)
        h_draw.text((110, 75), "THE PANAMA CANAL MYSTERY", font=get_font(28, True), fill=(255, 215, 0, 255))
        frame.alpha_composite(hud)
        
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print(f"Rendered Short Scene {sc_idx}: {out_mp4.name}")
    return out_mp4

def assemble_short(durations):
    total_dur = sum(durations) + len(durations) * 0.35
    print(f"Total Short Duration: {total_dur:.2f} seconds (<60s)")
    
    # 1. Concat video clips
    concat_txt = shorts_dir / "concat_short.txt"
    with open(concat_txt, "w") as f:
        for i in range(1, len(SHORT_SCENES) + 1):
            p = str((shorts_dir / f"clip_{i}.mp4").resolve()).replace("\\", "/")
            f.write(f"file '{p}'\n")
            
    combined_raw = shorts_dir / "combined_raw_short.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(combined_raw)], check=True)
    
    # 2. Multi-track Foley Audio Mix
    sr = 44100
    total_samples = int(total_dur * sr)
    master = np.zeros(total_samples, dtype=np.float32)
    sfx_dir = Path("data/sfx")
    
    # Background ambient bed
    wind = load_audio_pcm(sfx_dir / "desert_wind.wav", sr) * 0.2
    for s in range(0, total_samples, len(wind)):
        e = min(total_samples, s + len(wind))
        master[s:e] += wind[:e-s]
        
    # Place narration and Foley
    cur_t = 0.0
    cues_map = {
        0: [("ship_horn.wav", 0.5, 0.7), ("impact_boom.wav", 2.0, 0.5)],
        1: [("water_rush.wav", 1.0, 0.5), ("whoosh.wav", 5.0, 0.4)],
        2: [("gate_clank.wav", 1.5, 0.6), ("water_rush.wav", 3.0, 0.5)],
        3: [("warning_beep.wav", 2.0, 0.5), ("dry_wind.wav", 5.0, 0.4)],
        4: [("auction_gavel.wav", 1.0, 0.8), ("impact_boom.wav", 1.0, 0.6)]
    }
    
    for idx, sc in enumerate(SHORT_SCENES):
        vo_p = shorts_dir / f"{sc['id']}.mp3"
        vo = load_audio_pcm(vo_p, sr) * 1.0
        v_start = int((cur_t + 0.1) * sr)
        v_end = min(total_samples, v_start + len(vo))
        master[v_start:v_end] += vo[:v_end - v_start]
        
        # Place Foley
        for sfx_name, sfx_off, vol in cues_map.get(idx, []):
            s_file = sfx_dir / sfx_name
            if s_file.exists():
                s_data = load_audio_pcm(s_file, sr) * vol
                sf_start = int((cur_t + sfx_off) * sr)
                sf_end = min(total_samples, sf_start + len(s_data))
                if sf_start < total_samples:
                    master[sf_start:sf_end] += s_data[:sf_end - sf_start]
                    
        cur_t += sc["actual_dur"] + 0.35
        
    max_v = np.max(np.abs(master))
    if max_v > 0.95:
        master = (master / max_v) * 0.95
        
    out_wav = shorts_dir / "master_audio_short.wav"
    with wave.open(str(out_wav), 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((master * 32767).astype(np.int16).tobytes())
        
    # 3. Synchronized Vertical Subtitles (.ass)
    # Positioned at mobile center sweet-spot (MarginV: 780 for 1080x1920)
    ass_path = shorts_dir / "subtitles_short.ass"
    ass_lines = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: ShortSub,Arial,64,&H0020FFFF,&H00000000,&H00000000,&HA0000000,-1,0,0,0,100,100,2,0,1,5.0,3.0,2,60,60,820,1", "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]
    
    cur_t = 0.0
    for idx, sc in enumerate(SHORT_SCENES):
        words = sc["text"].split()
        chunk_sz = 3 # 3 words per popup for ultra punchy Shorts reading!
        dur = sc["actual_dur"]
        words_per_sec = len(words) / dur
        
        for ci in range(0, len(words), chunk_sz):
            c_words = words[ci:ci + chunk_sz]
            c_text = " ".join(c_words).upper()
            w_start = cur_t + (ci / words_per_sec)
            w_end = min(cur_t + dur, cur_t + ((ci + chunk_sz) / words_per_sec))
            
            def fmt(sec):
                h = int(sec // 3600)
                m = int((sec % 3600) // 60)
                s = int(sec % 60)
                ms = int((sec - int(sec)) * 100)
                return f"{h}:{m:02d}:{s:02d}.{ms:02d}"
                
            ass_lines.append(f"Dialogue: 0,{fmt(w_start)},{fmt(w_end)},ShortSub,,0,0,0,,{c_text}")
            
        cur_t += dur + 0.35
        
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("\n".join(ass_lines))
        
    # 4. Final Mux
    out_final = Path("exports/Panama_Canal_Trap_Viral_Short_1080x1920.mp4")
    clean_ass = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")
    
    cmd = [
        "ffmpeg", "-y",
        "-i", str(combined_raw),
        "-i", str(out_wav),
        "-vf", f"subtitles='{clean_ass}'",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{total_dur:.2f}",
        str(out_final)
    ]
    subprocess.run(cmd, check=True)
    print("=" * 60)
    print(f"VIRAL YOUTUBE SHORT PRODUCED: {out_final}")
    print(f"Duration: {total_dur:.2f}s | Resolution: 1080x1920")
    print("=" * 60)
    return out_final

async def main():
    print("Step 1: Generating Punchy Voiceovers...")
    durations = await generate_short_audio()
    
    print("Step 2: Rendering 5 Vertical Scenes...")
    for i, sc in enumerate(SHORT_SCENES, 1):
        render_short_scene(i, sc, sc["actual_dur"] + 0.35)
        
    print("Step 3: Assembling Master Short Video...")
    assemble_short(durations)

if __name__ == '__main__':
    asyncio.run(main())
