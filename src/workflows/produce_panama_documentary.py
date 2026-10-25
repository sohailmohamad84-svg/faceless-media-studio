"""Automated End-to-End Production Engine for 'The Panama Canal Trap' 1080p Full Documentary.
Renders all 18 animated scenes, mixes multi-track Foley & Edge-TTS narration, and exports the final video.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import math
import subprocess
import wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from src.scripting.panama_script import PANAMA_CANAL_SCRIPT

fps = 30
width, height = 1920, 1080

anim_dir = Path("data/assets/panama_anim")
clips_dir = Path("scratch/panama_clips")
clips_dir.mkdir(parents=True, exist_ok=True)
audio_dir = Path("scratch/panama_audio")

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

# Pre-load common assets
print("Loading base graphic assets...")
bg_map = Image.open(anim_dir / "bg_panama_map.png").convert("RGBA")
bg_cutaway = Image.open(anim_dir / "bg_mountain_locks_cutaway.png").convert("RGBA")
bg_lock_canyon = Image.open(anim_dir / "bg_lock_canyon.png").convert("RGBA")
bg_jungle = Image.open(anim_dir / "bg_jungle_rainstorm.png").convert("RGBA")
bg_drought = Image.open(anim_dir / "bg_drought_lake.png").convert("RGBA")
prop_ship = Image.open(anim_dir / "prop_container_ship.png").convert("RGBA")
prop_mule = Image.open(anim_dir / "prop_electric_mule.png").convert("RGBA")

# Also load GoDocs characters for comic gags
char_sheikh = Image.open("data/assets/godocs_anim/sheikh_neutral.png").convert("RGBA")
char_pointing = Image.open("data/assets/godocs_anim/sheikh_pointing.png").convert("RGBA")
char_bino = Image.open("data/assets/godocs_anim/sheikh_binoculars.png").convert("RGBA")
eyes_pop = Image.open("data/assets/godocs_anim/cartoon_bulging_eyes.png").convert("RGBA")

def render_scene(sc_idx, sc, duration):
    out_mp4 = clips_dir / f"clip_{sc_idx:02d}.mp4"
    if out_mp4.exists() and out_mp4.stat().st_size > 100000:
        print(f"Clip {sc_idx:02d} already exists, skipping...")
        return out_mp4
        
    total_frames = int(fps * duration)
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgba",
        "-s", f"{width}x{height}", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-preset", "ultrafast", "-pix_fmt", "yuv420p",
        str(out_mp4)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    sc_type = sc["visual_type"]
    print(f"Rendering Clip {sc_idx:02d}: {sc['title']} ({duration:.1f}s, {total_frames} frames)...")
    
    np.random.seed(sc_idx * 17)
    particles = [{'x': np.random.uniform(0, width), 'y': np.random.uniform(200, 1000),
                  'speed': np.random.uniform(10, 22), 'size': np.random.uniform(2, 6),
                  'alpha': np.random.randint(60, 180)} for _ in range(30)]
                  
    for f in range(total_frames):
        t = f / fps
        frame = Image.new("RGBA", (width, height), (0, 0, 0, 255))
        
        # Dispatch visual rendering based on scene type
        if "MAP" in sc_type:
            # Map with camera motion and animated routes
            zoom = 1.0 + 0.08 * (t / duration)
            cw, ch = int(width / zoom), int(height / zoom)
            crop = bg_map.crop(((width - cw)//2, (height - ch)//2, (width + cw)//2, (height + ch)//2))
            frame = crop.resize((width, height), Image.Resampling.BILINEAR)
            draw = ImageDraw.Draw(frame)
            
            # Draw glowing shipping routes
            if sc_idx == 1:
                # Cape horn route (red dashed line)
                prog = min(1.0, t / 14.0)
                if prog > 0:
                    draw.arc([600, 480, 1500, 1060], start=30, end=int(30 + prog * 150), fill=(240, 50, 50, 255), width=6)
                # Panama direct route (green arrow)
                if t > 18.0:
                    g_prog = min(1.0, (t - 18.0) / 4.0)
                    draw.line([(880, 520), (int(880 + g_prog * 80), int(520 + g_prog * 50))], fill=(0, 255, 120, 255), width=8)
            elif sc_idx == 15:
                # 160 ships traffic jam outside canal
                for si in range(min(25, int(t * 3) + 5)):
                    sx = 820 - (si % 5) * 45 - int(math.sin(t * 2 + si) * 5)
                    sy = 560 + (si // 5) * 35 + int(math.cos(t * 2 + si) * 4)
                    draw.rectangle([sx, sy, sx + 35, sy + 14], fill=(220, 60, 50, 240), outline=(255, 255, 255, 255), width=2)
                    
        elif "CUTAWAY" in sc_type or "ELEVATOR" in sc_type or "CROSS_SECTION" in sc_type:
            # Side-view water elevator schematic with moving container ship
            frame = bg_cutaway.copy()
            
            # Animate container ship rising over the mountain
            # Ship trajectory: starts at x=-200, climbs Gatun stairs, traverses summit lake, descends Pacific stairs
            total_travel_t = duration
            pos_prog = t / total_travel_t
            
            # Ship elevation profile y based on x
            ship_x = int(-200 + pos_prog * (width + 400))
            if ship_x < 320:
                ship_y = 710 # Atlantic sea level
            elif ship_x < 420:
                ship_y = 650 # Step 1
            elif ship_x < 520:
                ship_y = 590 # Step 2
            elif ship_x < 1280:
                ship_y = 510 # Lake Gatun summit (+85 ft)
            elif ship_x < 1380:
                ship_y = 590 # Pacific step 1
            elif ship_x < 1480:
                ship_y = 650 # Pacific step 2
            else:
                ship_y = 710 # Pacific sea level
                
            # Subtle ship rocking in water
            rock_y = int(math.sin(t * 4.0) * 3)
            # Scale container ship to ~280 px wide for schematic
            ship_w = 320
            ship_h = int(prop_ship.height * (ship_w / prop_ship.width))
            scaled_ship = prop_ship.resize((ship_w, ship_h), Image.Resampling.LANCZOS)
            frame.alpha_composite(scaled_ship, (ship_x, ship_y + rock_y))
            
        elif "JUNGLE" in sc_type or "STORM" in sc_type or "CHAOS" in sc_type:
            # Jungle storm with rain streaks and lightning
            frame = bg_jungle.copy()
            draw = ImageDraw.Draw(frame)
            
            # Lightning flash
            if int(t * 3) % 7 == 0:
                flash = Image.new("RGBA", (width, height), (255, 255, 255, 60))
                frame.alpha_composite(flash)
                
            # Rain streaks
            for p in particles:
                p['y'] += p['speed'] * 2
                p['x'] -= p['speed'] * 0.5
                if p['y'] > height:
                    p['y'] = 0
                    p['x'] = np.random.uniform(0, width)
                draw.line([(p['x'], p['y']), (p['x'] - 8, p['y'] + 22)], fill=(200, 220, 245, p['alpha']), width=2)
                
        elif "DROUGHT" in sc_type:
            # Sinking water line and heat distortion
            frame = bg_drought.copy()
            arr = np.array(frame)
            # Heat shimmer ripple
            y_start, y_end = 300, 600
            sl = arr[y_start:y_end]
            shifts = (3.0 * np.sin(2 * np.pi * np.arange(y_end - y_start) / 40.0 - 6 * np.pi * t)).astype(int)
            for i, s in enumerate(shifts):
                if s != 0:
                    sl[i] = np.roll(sl[i], s, axis=0)
            arr[y_start:y_end] = sl
            frame = Image.fromarray(arr)
            
        else:
            # Default lock canyon interior with container ship or electric mule
            frame = bg_lock_canyon.copy()
            # Position container ship in chamber rising with water level
            water_rise = int(min(120, t * 15))
            ship_w = 680
            ship_h = int(prop_ship.height * (ship_w / prop_ship.width))
            scaled_ship = prop_ship.resize((ship_w, ship_h), Image.Resampling.LANCZOS)
            # Ship rises from y=480 down to y=360
            cur_sy = 480 - water_rise + int(math.sin(t * 3) * 3)
            frame.alpha_composite(scaled_ship, (620, cur_sy))
            
            # Overlay electric mule on lock track (left side)
            mule_w = 260
            mule_h = int(prop_mule.height * (mule_w / prop_mule.width))
            scaled_mule = prop_mule.resize((mule_w, mule_h), Image.Resampling.LANCZOS)
            frame.alpha_composite(scaled_mule, (120, 560 - int(water_rise * 0.4)))
            
        # Global HUD overlay: Title & Scene Badge
        hud = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        h_draw = ImageDraw.Draw(hud)
        # Top-left scene title tag
        tag_text = f"ACT {sc_idx//4 + 1} | {sc['title'].upper()}"
        h_draw.rounded_rectangle([40, 36, 40 + len(tag_text)*14 + 30, 80], radius=8, fill=(15, 20, 30, 210), outline=(255, 215, 0, 240), width=2)
        h_draw.text((54, 46), tag_text, font=get_font(18, True), fill=(255, 215, 0, 255))
        frame.alpha_composite(hud)
        
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print(f"Finished Clip {sc_idx:02d}.")
    return out_mp4

def produce_documentary():
    print("=" * 60)
    print("STARTING AUTONOMOUS PRODUCTION: 'The Panama Canal Trap'")
    print("=" * 60)
    
    # 1. Load scene voiceovers and measure exact durations
    scene_durations = {}
    ordered_scenes = []
    for act in PANAMA_CANAL_SCRIPT["acts"]:
        for sc in act["scenes"]:
            sc_id = sc["scene_id"]
            sc_file = audio_dir / f"{sc_id}.mp3"
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(sc_file)]
            res = subprocess.run(cmd, capture_output=True, text=True, check=True)
            dur = float(res.stdout.strip())
            scene_durations[sc_id] = dur
            ordered_scenes.append((sc_id, sc, dur))
            
    total_narration_sec = sum(dur for _, _, dur in ordered_scenes)
    print(f"Total narration duration: {total_narration_sec:.2f}s ({total_narration_sec/60:.2f} mins)")
    
    # 2. Render all 18 scene clips
    clip_files = []
    for idx, (sc_id, sc, dur) in enumerate(ordered_scenes, 1):
        # Add 0.5s padding per scene for clean breathing room between cuts
        clip_dur = dur + 0.5
        clip_path = render_scene(idx, sc, clip_dur)
        clip_files.append((clip_path, clip_dur))
        
    # 3. Concat all 18 clips into single video stream
    concat_txt = clips_dir / "concat_all.txt"
    with open(concat_txt, "w") as f:
        for p, _ in clip_files:
            clean_p = str(p.resolve()).replace("\\", "/")
            f.write(f"file '{clean_p}'\n")
            
    combined_raw = clips_dir / "combined_raw_documentary.mp4"
    print("Concatenating 18 clips into single raw video stream...")
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(combined_raw)], check=True)
    
    # 4. Multi-Track Foley Audio Composition
    sr = 44100
    total_video_dur = sum(d for _, d in clip_files)
    total_samples = int(total_video_dur * sr)
    master_audio = np.zeros(total_samples, dtype=np.float32)
    
    # Lay down voiceover clips and Foley cues with sample accuracy
    current_time_sec = 0.0
    sfx_dir = Path("data/sfx")
    
    # Background environmental bed loop (desert wind + subtle jungle atmosphere)
    wind_bed = load_audio_pcm(sfx_dir / "desert_wind.wav", sr) * 0.15
    for loop_start in range(0, total_samples, len(wind_bed)):
        loop_end = min(total_samples, loop_start + len(wind_bed))
        master_audio[loop_start:loop_end] += wind_bed[:loop_end - loop_start]
        
    for idx, (sc_id, sc, dur) in enumerate(ordered_scenes, 1):
        # Place voiceover at current_time_sec + 0.15s
        vo_path = audio_dir / f"{sc_id}.mp3"
        vo_data = load_audio_pcm(vo_path, sr) * 1.0
        vo_start_s = int((current_time_sec + 0.15) * sr)
        vo_end_s = min(total_samples, vo_start_s + len(vo_data))
        master_audio[vo_start_s:vo_end_s] += vo_data[:vo_end_s - vo_start_s]
        
        # Place Foley cues
        for sfx_name, sfx_offset in sc.get("foley_cues", []):
            sfx_file = sfx_dir / f"{sfx_name}.wav"
            if not sfx_file.exists():
                sfx_file = sfx_dir / "whoosh.wav" # fallback
            if sfx_file.exists():
                sfx_data = load_audio_pcm(sfx_file, sr) * 0.45
                sfx_start_s = int((current_time_sec + sfx_offset) * sr)
                sfx_end_s = min(total_samples, sfx_start_s + len(sfx_data))
                if sfx_start_s < total_samples:
                    master_audio[sfx_start_s:sfx_end_s] += sfx_data[:sfx_end_s - sfx_start_s]
                    
        # Advance timeline by clip duration
        current_time_sec += dur + 0.5
        
    # Soft limiter to prevent clipping
    max_val = np.max(np.abs(master_audio))
    if max_val > 0.95:
        master_audio = (master_audio / max_val) * 0.95
        
    master_audio_wav = clips_dir / "master_audio_documentary.wav"
    int_samples = (master_audio * 32767).astype(np.int16)
    with wave.open(str(master_audio_wav), 'w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(int_samples.tobytes())
    print("Master Foley & Voiceover audio track compiled successfully!")
    
    # 5. Build Master Synchronized Subtitles (.ass)
    ass_path = clips_dir / "subtitles_documentary.ass"
    ass_lines = [
        "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1920", "PlayResY: 1080", "ScaledBorderAndShadow: yes", "",
        "[V4+ Styles]",
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
        "Style: GoDocs,Arial,52,&H0020FFFF,&H00000000,&H00000000,&HA0000000,-1,0,0,0,100,100,1,0,1,4.5,2.5,2,40,40,115,1", "",
        "[Events]",
        "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
    ]
    
    cur_t = 0.0
    for idx, (sc_id, sc, dur) in enumerate(ordered_scenes, 1):
        words = sc["narration"].split()
        chunk_size = 5
        words_per_sec = len(words) / dur
        
        for ci in range(0, len(words), chunk_size):
            chunk_words = words[ci:ci + chunk_size]
            c_text = " ".join(chunk_words).upper()
            w_start = cur_t + (ci / words_per_sec)
            w_end = min(cur_t + dur, cur_t + ((ci + chunk_size) / words_per_sec))
            
            def fmt_time(sec):
                h = int(sec // 3600)
                m = int((sec % 3600) // 60)
                s = int(sec % 60)
                ms = int((sec - int(sec)) * 100)
                return f"{h}:{m:02d}:{s:02d}.{ms:02d}"
                
            ass_lines.append(f"Dialogue: 0,{fmt_time(w_start)},{fmt_time(w_end)},GoDocs,,0,0,0,,{c_text}")
            
        cur_t += dur + 0.5
        
    with open(ass_path, "w", encoding="utf-8") as f:
        f.write("\n".join(ass_lines))
        
    # 6. Final Master Video Assembly (Burning subtitles + muxing master audio)
    out_final = Path("exports/The_Panama_Canal_Trap_Full_Documentary_1080p.mp4")
    clean_ass = str(ass_path.resolve()).replace("\\", "/").replace(":", "\\:")
    
    print("Muxing final 1080p documentary video...")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(combined_raw),
        "-i", str(master_audio_wav),
        "-vf", f"subtitles='{clean_ass}'",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "19",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{total_video_dur:.2f}",
        str(out_final)
    ]
    subprocess.run(cmd, check=True)
    
    print("=" * 60)
    print("MASTER DOCUMENTARY VIDEO SUCCESSFULLY PRODUCED!")
    print(f"File: {out_final}")
    print(f"Duration: {total_video_dur:.2f} seconds ({total_video_dur/60:.2f} minutes)")
    print("=" * 60)
    return out_final

if __name__ == '__main__':
    produce_documentary()
