"""Path 2 Prototype Production Script:
Assembles a broadcast-quality documentary sample using:
1. Real 1080p time-lapse video footage (Wikimedia Commons)
2. 2.5D Ken Burns motion on authentic 1906 archival photographs
3. Animated NASA satellite isthmus map with glowing route line
4. Christopher Neural narration, Foley sound design, and documentary lower thirds
"""
import asyncio
import math
import subprocess
import wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
import numpy as np
import edge_tts

w, h = 1920, 1080
fps = 30
sr = 44100
work_dir = Path("scratch/path2_work")
work_dir.mkdir(parents=True, exist_ok=True)
broll_dir = Path("data/assets/path2_broll")
archival_dir = Path("data/assets/path2_archival")
sfx_dir = Path("data/sfx")

def get_font(size, bold=True):
    try:
        f = "arialbd.ttf" if bold else "arial.ttf"
        return ImageFont.truetype(f, size)
    except:
        return ImageFont.load_default()

def load_audio_pcm(file_path, sample_rate=44100):
    cmd = [
        "ffmpeg", "-y", "-i", str(file_path),
        "-f", "s16le", "-ac", "1", "-ar", str(sample_rate), "-"
    ]
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
    return np.frombuffer(res.stdout, dtype=np.int16).astype(np.float32) / 32768.0

SCENES = [
    {
        "id": "act1_locks_broll",
        "type": "VIDEO_BROLL",
        "ss": 25, # Timestamp in panama_timelapse_1.webm
        "text": "Eighty-five feet above sea level, massive steel gates hold back millions of tons of water—trapping ocean giants inside a mountain.",
        "badge": "MIRAFLORES LOCKS // PACIFIC TERMINUS",
        "sfx": [("ship_horn.wav", 0.4, 0.4), ("water_rush.wav", 1.8, 0.35)]
    },
    {
        "id": "act2_roosevelt_25d",
        "type": "PHOTO_25D",
        "photo": "teddy_roosevelt_panama.jpg",
        "title": "THE AMERICAN CRUSADE",
        "caption": "PRESIDENT THEODORE ROOSEVELT AT CULEBRA CUT STEAM SHOVEL (1906)",
        "stamp": "U.S. NATIONAL ARCHIVES",
        "text": "In 1904, President Teddy Roosevelt sent army engineers to blast through volcanic rock where the French had failed.",
        "sfx": [("wood_thud.wav", 0.8, 0.4), ("impact_boom.wav", 2.5, 0.3)]
    },
    {
        "id": "act3_satellite_map",
        "type": "SATELLITE_MAP",
        "photo": "panama_isthmus_satellite.jpg",
        "text": "To avoid the deadly eight-thousand-mile detour around South America, they engineered the ultimate shortcut: a staircase made of water.",
        "badge": "NASA EARTH OBSERVATORY // ISTHMUS OF PANAMA",
        "sfx": [("desert_wind.wav", 0.2, 0.3), ("radar_ping.wav", 2.0, 0.4)]
    },
    {
        "id": "act4_gatun_summit",
        "type": "VIDEO_BROLL",
        "ss": 160, # Timestamp in panama_timelapse_1.webm
        "text": "Without a single pump, natural mountain gravity lifts eighty-thousand-ton ships twenty-eight feet at a time.",
        "badge": "GATUN SUMMIT RESERVOIR // ELEVATION: +85 FT",
        "sfx": [("gate_clank.wav", 0.6, 0.4), ("water_rush.wav", 2.2, 0.35)]
    }
]

async def synthesize_narration():
    voice = "en-US-ChristopherNeural"
    total = 0.0
    for sc in SCENES:
        vo_p = work_dir / f"{sc['id']}_vo.mp3"
        c = edge_tts.Communicate(sc["text"], voice, rate="+5%")
        await c.save(str(vo_p))
        
        cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(vo_p)]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        dur = float(res.stdout.strip())
        sc["vo_dur"] = dur
        sc["clip_dur"] = dur + 0.5
        sc["vo_file"] = vo_p
        total += sc["clip_dur"]
        print(f"[{sc['id']}] VO: {dur:.2f}s | Clip: {sc['clip_dur']:.2f}s")
    print(f"Total Prototype Duration: {total:.2f}s")
    return total

def render_act2_photo_frame():
    """Build the high-res 2.5D archival photo composite using DocumentaryDesigner principles."""
    raw_photo = Image.open(archival_dir / "teddy_roosevelt_panama.jpg").convert("RGB")
    
    # 1. Darkroom blurred backdrop
    bg = ImageOps.fit(raw_photo, (w, h), method=Image.Resampling.LANCZOS)
    bg = bg.filter(ImageFilter.GaussianBlur(36))
    dark = Image.new("RGBA", (w, h), (12, 16, 24, 200))
    bg.paste(dark, (0, 0), dark)
    
    # 2. Main framed polaroid
    target_w, target_h = 1320, 740
    photo_crop = ImageOps.fit(raw_photo, (target_w, target_h), method=Image.Resampling.LANCZOS)
    
    pad = 22
    bottom_pad = 55
    fw = target_w + pad * 2
    fh = target_h + pad + bottom_pad
    
    frame = Image.new("RGBA", (fw, fh), (245, 242, 235, 255))
    frame.paste(photo_crop, (pad, pad))
    f_draw = ImageDraw.Draw(frame)
    f_draw.text((pad + 16, fh - 44), "PRESIDENT THEODORE ROOSEVELT AT CULEBRA CUT STEAM SHOVEL (1906)", fill=(40, 45, 55), font=get_font(20, True))
    
    # Shadow
    shadow = Image.new("RGBA", (fw + 40, fh + 40), (0, 0, 0, 190))
    shadow = shadow.filter(ImageFilter.GaussianBlur(24))
    
    px = (w - fw) // 2
    py = (h - fh) // 2 + 30
    
    bg.paste(shadow, (px - 10, py - 6), shadow)
    bg.paste(frame, (px, py), frame)
    
    # Badges and headers
    b_draw = ImageDraw.Draw(bg)
    b_draw.text((px, 45), "THE AMERICAN CRUSADE", fill=(245, 180, 40), font=get_font(42, True))
    
    # Red Archival badge
    badge_box = [px + fw - 330, py - 20, px + fw, py + 24]
    b_draw.rounded_rectangle(badge_box, radius=6, fill=(185, 30, 30))
    b_draw.text((badge_box[0] + 16, badge_box[1] + 8), "HISTORICAL ARCHIVE", fill=(255, 255, 255), font=get_font(20, True))
    
    # Red Stamp
    stamp_box = [px + 40, py + fh - 120, px + 440, py + fh - 55]
    b_draw.rounded_rectangle(stamp_box, radius=8, outline=(195, 40, 40), width=4)
    b_draw.text((stamp_box[0] + 18, stamp_box[1] + 10), "U.S. NATIONAL ARCHIVES", fill=(195, 40, 40), font=get_font(28, True))
    
    out_p = work_dir / "act2_roosevelt_framed.png"
    bg.save(out_p)
    print("Rendered 2.5D Archival Frame:", out_p)
    return out_p

def render_act3_satellite_clip(duration):
    """Render animated NASA satellite flyover with glowing transit line."""
    raw_sat = Image.open(archival_dir / "panama_isthmus_satellite.jpg").convert("RGB")
    sat_base = ImageOps.fit(raw_sat, (w, h), method=Image.Resampling.LANCZOS)
    
    total_frames = int(fps * duration)
    out_mp4 = work_dir / "clip_2_satellite.mp4"
    
    cmd = [
        "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{w}x{h}", "-r", str(fps), "-i", "-",
        "-c:v", "libx264", "-preset", "fast", "-pix_fmt", "yuv420p",
        str(out_mp4)
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Route line coordinates across isthmus
    # Atlantic (Colon): (780, 420) -> Pacific (Panama City): (1120, 680)
    p_start = (780, 420)
    p_end = (1120, 680)
    
    for f in range(total_frames):
        t = f / fps
        progress = min(1.0, t / (duration * 0.75))
        
        # Slow camera push-in
        zoom = 1.0 + 0.12 * (t / duration)
        cw, ch = int(w / zoom), int(h / zoom)
        cx, cy = 950, 550
        x1 = max(0, min(cx - cw // 2, w - cw))
        y1 = max(0, min(cy - ch // 2, h - ch))
        
        frame = sat_base.crop((x1, y1, x1 + cw, y1 + ch)).resize((w, h), Image.Resampling.BILINEAR)
        draw = ImageDraw.Draw(frame)
        
        # Vignette border
        draw.rectangle([(0, 0), (w, h)], outline=(10, 15, 20), width=25)
        
        # Draw glowing route line up to current progress
        cur_x = int(p_start[0] + (p_end[0] - p_start[0]) * progress)
        cur_y = int(p_start[1] + (p_end[1] - p_start[1]) * progress)
        
        # Cyan glowing line
        draw.line([p_start, (cur_x, cur_y)], fill=(0, 220, 255), width=6)
        
        # Pulsing beacon rings at terminals
        pulse = (t * 3.0) % 1.0
        r = int(12 + pulse * 28)
        alpha = int(255 * (1 - pulse))
        draw.ellipse([p_start[0] - r, p_start[1] - r, p_start[0] + r, p_start[1] + r], outline=(0, 240, 255), width=3)
        draw.ellipse([p_start[0] - 8, p_start[1] - 8, p_start[0] + 8, p_start[1] + 8], fill=(255, 255, 255))
        draw.text((p_start[0] - 120, p_start[1] - 35), "ATLANTIC (COLON)", fill=(0, 230, 255), font=get_font(20, True))
        
        if progress > 0.8:
            draw.ellipse([p_end[0] - r, p_end[1] - r, p_end[0] + r, p_end[1] + r], outline=(255, 80, 80), width=3)
            draw.ellipse([p_end[0] - 8, p_end[1] - 8, p_end[0] + 8, p_end[1] + 8], fill=(255, 255, 255))
            draw.text((p_end[0] + 20, p_end[1] - 10), "PACIFIC (PANAMA CITY)", fill=(255, 100, 100), font=get_font(20, True))
            
        # Top HUD banner
        draw.rounded_rectangle([60, 45, 660, 100], radius=8, fill=(12, 18, 28), outline=(0, 200, 255), width=2)
        draw.text((85, 60), "NASA SATELLITE RADAR // 50-MILE TRANSIT", fill=(0, 220, 255), font=get_font(22, True))
        
        proc.stdin.write(frame.tobytes())
        
    proc.stdin.close()
    proc.wait()
    print("Rendered Satellite Flyover Clip:", out_mp4)
    return out_mp4

def build_clips():
    """Assemble each of the 4 scene clips with cinematic grading and motion."""
    # 1. Render Act 2 framed photo
    framed_photo_p = render_act2_photo_frame()
    
    clips = []
    
    # Clip 0 (Act 1): Real video timelapse
    sc0 = SCENES[0]
    out0 = work_dir / "clip_0_broll.mp4"
    cmd0 = [
        "ffmpeg", "-y",
        "-ss", str(sc0["ss"]),
        "-i", str(broll_dir / "panama_timelapse_1.webm"),
        "-t", f"{sc0['clip_dur']:.2f}",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,eq=contrast=1.12:brightness=0.02:saturation=1.15,drawbox=y=0:h=40:color=black:t=fill,drawbox=y=1040:h=40:color=black:t=fill,drawbox=x=60:y=60:w=580:h=50:color=black@0.75:t=fill,drawtext=text='MIRAFLORES LOCKS // PACIFIC TERMINUS':fontcolor=white:fontsize=22:x=80:y=74",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an",
        str(out0)
    ]
    subprocess.run(cmd0, check=True)
    clips.append(out0)
    
    # Clip 1 (Act 2): 2.5D Ken Burns zoom on framed photo
    sc1 = SCENES[1]
    out1 = work_dir / "clip_1_roosevelt.mp4"
    dur1_frames = int(sc1["clip_dur"] * fps)
    cmd1 = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(framed_photo_p),
        "-t", f"{sc1['clip_dur']:.2f}",
        "-vf", f"zoompan=z='min(zoom+0.0006,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={dur1_frames}:s=1920x1080:fps=30",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an",
        str(out1)
    ]
    subprocess.run(cmd1, check=True)
    clips.append(out1)
    
    # Clip 2 (Act 3): Animated Satellite Map
    sc2 = SCENES[2]
    out2 = render_act3_satellite_clip(sc2["clip_dur"])
    clips.append(out2)
    
    # Clip 3 (Act 4): Real video timelapse of ship rising
    sc3 = SCENES[3]
    out3 = work_dir / "clip_3_summit.mp4"
    cmd3 = [
        "ffmpeg", "-y",
        "-ss", str(sc3["ss"]),
        "-i", str(broll_dir / "panama_timelapse_1.webm"),
        "-t", f"{sc3['clip_dur']:.2f}",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=increase,crop=1920:1080,eq=contrast=1.12:brightness=0.02:saturation=1.15,drawbox=y=0:h=40:color=black:t=fill,drawbox=y=1040:h=40:color=black:t=fill,drawbox=x=60:y=60:w=620:h=50:color=black@0.75:t=fill,drawtext=text='GATUN SUMMIT RESERVOIR // ELEVATION\\: +85 FT':fontcolor=white:fontsize=22:x=80:y=74",
        "-c:v", "libx264", "-preset", "fast", "-crf", "18", "-an",
        str(out3)
    ]
    subprocess.run(cmd3, check=True)
    clips.append(out3)
    
    return clips

def assemble_master(clips, total_dur):
    # 1. Concat video clips with smooth crossfade/cut
    concat_txt = work_dir / "concat_path2.txt"
    with open(concat_txt, "w") as f:
        for p in clips:
            clean = str(p.resolve()).replace("\\", "/")
            f.write(f"file '{clean}'\n")
            
    raw_video = work_dir / "raw_video_path2.mp4"
    subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_txt), "-c", "copy", str(raw_video)], check=True)
    
    # 2. Multi-track Audio Mix (Score + Foley + Narration)
    total_samples = int(total_dur * sr)
    master = np.zeros(total_samples, dtype=np.float32)
    
    # Continuous tension drone bed
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
        
    # Smooth audio end fade
    fade_len = int(0.6 * sr)
    if total_samples > fade_len:
        master[-fade_len:] *= np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
        
    max_v = np.max(np.abs(master))
    if max_v > 0.95:
        master = (master / max_v) * 0.95
        
    master_audio = work_dir / "master_audio_path2.wav"
    with wave.open(str(master_audio), "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes((master * 32767).astype(np.int16).tobytes())
        
    # 3. Documentary Typography Subtitles
    ass_path = work_dir / "subtitles_path2.ass"
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
        chunk_sz = 4 # 4 words per popup for landscape 1080p
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
        
    # 4. Final Mux
    out_final = Path("exports/Panama_Canal_Trap_Path2_Documentary_Prototype.mp4")
    cmd_mux = [
        "ffmpeg", "-y",
        "-i", str(raw_video),
        "-i", str(master_audio),
        "-vf", "subtitles=scratch/path2_work/subtitles_path2.ass",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k",
        "-t", f"{total_dur:.2f}",
        str(out_final)
    ]
    subprocess.run(cmd_mux, check=True)
    print("=" * 60)
    print(f"PATH 2 DOCUMENTARY PROTOTYPE READY: {out_final}")
    print(f"Duration: {total_dur:.2f}s | Resolution: 1920x1080 Full HD")
    print("=" * 60)
    return out_final

async def main():
    print("Step 1: Generating Narration Audio...")
    total_dur = await synthesize_narration()
    
    print("Step 2: Building Real B-Roll, 2.5D Photos, and Satellite Map Clips...")
    clips = build_clips()
    
    print("Step 3: Assembling Master Documentary Video...")
    assemble_master(clips, total_dur)

if __name__ == "__main__":
    asyncio.run(main())
