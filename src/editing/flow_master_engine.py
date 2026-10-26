"""Autonomous Flow Master Engine.
Takes raw Google Flow / Veo video clips and corresponding scene scripts,
cleans the watermarks, generates pacing-controlled voiceover, layers organic Foley,
burns in kinetic mobile gold subtitles, and produces a broadcast-ready viral master.
"""
import asyncio
import subprocess
import wave
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import edge_tts

class FlowMasterEngine:
    CROP_FILTER = "crop=928:1650:76:0,scale=1080:1920:flags=lanczos,fps=60"
    SAMPLE_RATE = 48000
    VOICE_ID = "en-US-ChristopherNeural"
    FPS = 60
    CRF = 17

    @classmethod
    def _load_audio_pcm(cls, file_path: Path, sample_rate: int = 48000) -> np.ndarray:
        if not file_path.exists():
            return np.zeros(sample_rate, dtype=np.float32)
        cmd = [
            "ffmpeg", "-y", "-i", str(file_path),
            "-f", "s16le", "-ac", "1", "-ar", str(sample_rate), "-"
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
        return np.frombuffer(res.stdout, dtype=np.int16).astype(np.float32) / 32768.0

    @classmethod
    async def build_master_video(
        cls,
        scenes: List[Dict[str, Any]],
        output_filename: str,
        ambient_sfx: str = "desert_wind.wav"
    ) -> Path:
        """
        scenes is a list of dicts:
        [
            {
                "input_video": Path("data/flow_clips/shot1.mp4"),
                "narration_text": "...",
                "foley": [
                    {"sfx": "ship_horn.wav", "time_offset": 0.5, "gain": 0.35},
                    {"sfx": "water_rush.wav", "time_offset": 3.0, "gain": 0.28}
                ]
            },
            ...
        ]
        """
        work_dir = Path("scratch/flow_master_work")
        work_dir.mkdir(parents=True, exist_ok=True)
        sfx_dir = Path("data/sfx")
        
        # Step 1: Generate narration takes first to dynamically drive scene timing
        vo_files = []
        vo_durations = []
        scene_durations = []
        
        for idx, sc in enumerate(scenes):
            text = sc.get("narration_text", "")
            vo_path = work_dir / f"vo_{idx}.mp3"
            if text:
                comm = edge_tts.Communicate(text, cls.VOICE_ID, rate="+14%")
                await comm.save(str(vo_path))
                cmd_p = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(vo_path)]
                dur = float(subprocess.run(cmd_p, capture_output=True, text=True, check=True).stdout.strip())
            else:
                dur = 5.0
            vo_files.append(vo_path)
            vo_durations.append(dur)
            
            # Dynamic viral scene duration: voice duration + tight padding (zero dead air)
            # 0.15s leading, 0.25s trailing (0.6s trailing on the final scene for outro SFX)
            is_last = (idx == len(scenes) - 1)
            pad = 0.65 if is_last else 0.40
            sc_dur = dur + pad
            scene_durations.append(sc_dur)

        total_duration = sum(scene_durations)

        # Step 2: Clean, scale, and time-trim all video clips to exact scene durations
        clean_clips = []
        for idx, sc in enumerate(scenes):
            in_vid = Path(sc["input_video"])
            out_vid = work_dir / f"clean_scene_{idx}.mp4"
            is_clean = sc.get("is_clean", False)
            sc_dur = scene_durations[idx]
            
            # If already clean 1080x1920, don't crop watermark
            vfilter = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,fps=60" if is_clean else cls.CROP_FILTER
            
            cmd_clean = [
                "ffmpeg", "-y",
                "-i", str(in_vid),
                "-t", f"{sc_dur:.2f}",
                "-vf", vfilter,
                "-r", "60",
                "-c:v", "libx264", "-preset", "fast", "-crf", str(cls.CRF),
                "-pix_fmt", "yuv420p",
                "-an",
                str(out_vid)
            ]
            subprocess.run(cmd_clean, check=True)
            clean_clips.append(out_vid)
        
        # Concatenate clean video clips
        concat_txt = work_dir / "concat_master.txt"
        with open(concat_txt, "w") as f:
            for c in clean_clips:
                f.write(f"file '{c.resolve().as_posix()}'\n")
                
        merged_video = work_dir / "merged_master_video.mp4"
        cmd_cat = [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c", "copy",
            str(merged_video)
        ]
        subprocess.run(cmd_cat, check=True)
            
        # Step 3: Mix Multi-Track Audio
        total_samples = int(total_duration * cls.SAMPLE_RATE)
        master_pcm = np.zeros(total_samples, dtype=np.float32)
        
        # Room tone bed
        amb_path = sfx_dir / ambient_sfx
        if amb_path.exists():
            amb_pcm = cls._load_audio_pcm(amb_path, cls.SAMPLE_RATE) * 0.07
            for s in range(0, total_samples, len(amb_pcm)):
                e = min(total_samples, s + len(amb_pcm))
                master_pcm[s:e] += amb_pcm[:e - s]
                
        current_time_sec = 0.0
        ass_events = []
        
        for idx, sc in enumerate(scenes):
            sc_dur = scene_durations[idx]
            vo_dur = vo_durations[idx]
            text = sc.get("narration_text", "")
            
            # Place narration tightly: starts 0.15s after scene transition
            if text and vo_files[idx].exists():
                vo_pcm = cls._load_audio_pcm(vo_files[idx], cls.SAMPLE_RATE) * 1.05
                v_start_sec = current_time_sec + 0.15
                vs = int(v_start_sec * cls.SAMPLE_RATE)
                ve = min(total_samples, vs + len(vo_pcm))
                master_pcm[vs:ve] += vo_pcm[:ve - vs]
                
                # Subtitles for this scene (3 words per burst)
                words = text.split()
                chunk_sz = 3
                w_per_s = len(words) / vo_dur if vo_dur > 0 else 1.0
                for ci in range(0, len(words), chunk_sz):
                    c_words = words[ci:ci + chunk_sz]
                    c_text = " ".join(c_words).upper()
                    w_start = v_start_sec + (ci / w_per_s)
                    w_end = min(current_time_sec + sc_dur - 0.05, v_start_sec + ((ci + chunk_sz) / w_per_s))
                    
                    def fmt(sec):
                        h = int(sec // 3600)
                        m = int((sec % 3600) // 60)
                        s = int(sec % 60)
                        ms = int((sec - int(sec)) * 100)
                        return f"{h}:{m:02d}:{s:02d}.{ms:02d}"
                        
                    ass_events.append(f"Dialogue: 0,{fmt(w_start)},{fmt(w_end)},FlowSub,,0,0,0,,{c_text}")
                    
            # Scene Foley
            for foley in sc.get("foley", []):
                sfx_name = foley.get("sfx", "")
                offset = foley.get("time_offset", 0.0)
                gain = foley.get("gain", 0.3)
                f_path = sfx_dir / sfx_name
                if f_path.exists():
                    pcm = cls._load_audio_pcm(f_path, cls.SAMPLE_RATE) * gain
                    fs = int((current_time_sec + offset) * cls.SAMPLE_RATE)
                    fe = min(total_samples, fs + len(pcm))
                    if fs < total_samples:
                        master_pcm[fs:fe] += pcm[:fe - fs]
                        
            current_time_sec += sc_dur

        # End fade
        fade_len = int(0.6 * cls.SAMPLE_RATE)
        master_pcm[-fade_len:] *= np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
        
        # Normalize
        max_v = np.max(np.abs(master_pcm))
        if max_v > 0.95:
            master_pcm = (master_pcm / max_v) * 0.95
            
        master_wav = work_dir / "master_audio.wav"
        with wave.open(str(master_wav), "w") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(cls.SAMPLE_RATE)
            wf.writeframes((master_pcm * 32767).astype(np.int16).tobytes())
            
        # Write ASS subtitles
        ass_path = work_dir / "master_subtitles.ass"
        ass_content = [
            "[Script Info]", "ScriptType: v4.00+", "PlayResX: 1080", "PlayResY: 1920", "ScaledBorderAndShadow: yes", "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            "Style: FlowSub,Arial,64,&H0020FFFF,&H00000000,&H00000000,&HA0000000,-1,0,0,0,100,100,2,0,1,5.5,3.0,2,60,60,820,1", "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ] + ass_events
        
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write("\n".join(ass_content))
            
        # Final Mux
        out_final = Path(f"exports/{output_filename}")
        out_final.parent.mkdir(parents=True, exist_ok=True)
        
        # Relative path without colon to prevent FFmpeg filter parsing error on Windows/Linux
        clean_ass_sub = ass_path.as_posix().replace(":", r"\:")
        cmd_mux = [
            "ffmpeg", "-y",
            "-i", str(merged_video),
            "-i", str(master_wav),
            "-vf", f"subtitles={clean_ass_sub}",
            "-r", "60",
            "-c:v", "libx264", "-preset", "fast", "-crf", str(cls.CRF),
            "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
            "-t", f"{total_duration:.2f}",
            str(out_final)
        ]
        subprocess.run(cmd_mux, check=True)
        return out_final
