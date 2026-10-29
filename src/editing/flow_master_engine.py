"""Autonomous Flow Master Engine.
Takes raw Google Flow / Veo video clips and corresponding scene scripts,
scales them cleanly without watermarking tampering (SynthID provenance badges preserved),
generates pacing-controlled voiceover, layers organic Foley with dynamic ducking,
masters audio to EBU R128 (-14 LUFS) broadcast loudness,
burns in kinetic mobile gold subtitles, and produces a broadcast-ready viral master.
"""
import asyncio
import json
import re
import subprocess
import wave
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional
import numpy as np
import edge_tts

class FlowMasterEngine:
    SAMPLE_RATE = 48000
    VOICE_ID = "en-US-ChristopherNeural"
    FPS = 60
    CRF = 17
    TARGET_LUFS = -14.0
    TARGET_TRUE_PEAK = -2.0
    TARGET_LRA = 7.0
    SCALE_FILTER = "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,fps=60"

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
    def _compute_phrase_timings(
        cls,
        phrases: List[str],
        v_start_sec: float,
        vo_dur: float
    ) -> List[Tuple[str, float, float]]:
        """Compute character-weighted subtitle timings for natural semantic phrases."""
        if not phrases or vo_dur <= 0:
            return []

        clean_lens = []
        for p in phrases:
            clean_text = re.sub(r"\{\\[^}]*\}", "", p).strip()
            clean_lens.append(max(1, len(clean_text)))

        total_len = max(1, sum(clean_lens))
        timed_phrases = []
        accum_time = v_start_sec

        for idx, p in enumerate(phrases):
            dur_fraction = (clean_lens[idx] / total_len) * vo_dur
            c_start = accum_time
            c_end = accum_time + dur_fraction
            accum_time = c_end
            timed_phrases.append((p.strip(), c_start, c_end))

        return timed_phrases

    @classmethod
    async def build_master_video(
        cls,
        scenes: List[Dict[str, Any]],
        output_filename: str,
        ambient_sfx: str = "tension_drone.wav",
        engine_bed_sfx: Optional[str] = None,
        target_scene_duration: Optional[float] = None
    ) -> Path:
        """
        Builds a broadcast-master short from scenes:
        scenes: List[dict] containing input_video, narration_text, and foley specifications.
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
            rate = sc.get("voice_rate", "+16%")
            if text:
                comm = edge_tts.Communicate(text, cls.VOICE_ID, rate=rate)
                await comm.save(str(vo_path))
                cmd_p = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(vo_path)]
                dur = float(subprocess.run(cmd_p, capture_output=True, text=True, check=True).stdout.strip())
            else:
                dur = 5.0
            vo_files.append(vo_path)
            vo_durations.append(dur)
            
            # Scene duration: explicit, parameter, 8-act standard (11.50s), or dynamic fallback
            if "duration" in sc:
                sc_dur = float(sc["duration"])
            elif target_scene_duration is not None:
                sc_dur = float(target_scene_duration)
            elif len(scenes) == 8:
                sc_dur = 11.50
            else:
                is_last = (idx == len(scenes) - 1)
                sc_dur = max(dur + (1.0 if is_last else 0.8), 13.5)
            scene_durations.append(sc_dur)

        total_duration = sum(scene_durations)

        # Step 2: Clean, scale, and time-trim all video/image assets to exact scene durations
        # Note: synthID / AI provenance badges are strictly preserved; no destructive delogo
        clean_clips = []
        for idx, sc in enumerate(scenes):
            in_vid = Path(sc["input_video"])
            out_vid = work_dir / f"clean_scene_{idx}.mp4"
            sc_dur = scene_durations[idx]
            
            # Check if input is an image (convert to 60fps dynamic motion clip)
            is_image = in_vid.suffix.lower() in [".jpg", ".jpeg", ".png"]
            
            if is_image and in_vid.exists():
                cmd_clean = [
                    "ffmpeg", "-y", "-threads", "2",
                    "-loop", "1",
                    "-i", str(in_vid),
                    "-t", f"{sc_dur:.2f}",
                    "-vf", "scale=1080:1920:force_original_aspect_ratio=increase:flags=lanczos,crop=1080:1920,zoompan=z='min(zoom+0.0008,1.15)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1200:s=1080x1920:fps=60",
                    "-r", str(cls.FPS),
                    "-c:v", "libx264", "-preset", "fast", "-crf", str(cls.CRF),
                    "-pix_fmt", "yuv420p",
                    "-an",
                    str(out_vid)
                ]
            else:
                cmd_clean = [
                    "ffmpeg", "-y", "-threads", "2",
                    "-stream_loop", "-1",
                    "-i", str(in_vid),
                    "-t", f"{sc_dur:.2f}",
                    "-vf", cls.SCALE_FILTER,
                    "-r", str(cls.FPS),
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
            
        # Step 3: Mix Multi-Track Audio with Dynamic Speech Ducking
        total_samples = int(total_duration * cls.SAMPLE_RATE)
        voice_track = np.zeros(total_samples, dtype=np.float32)
        foley_track = np.zeros(total_samples, dtype=np.float32)
        amb_track = np.zeros(total_samples, dtype=np.float32)
        engine_track = np.zeros(total_samples, dtype=np.float32)
        speech_mask = np.zeros(total_samples, dtype=bool)
        
        current_time_sec = 0.0
        ass_events = []
        
        def fmt_ass(sec):
            h = int(sec // 3600)
            m = int((sec % 3600) // 60)
            s = int(sec % 60)
            cs = int(round((sec - int(sec)) * 100))
            if cs >= 100:
                s += 1
                cs = 0
            return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

        for idx, sc in enumerate(scenes):
            sc_dur = scene_durations[idx]
            vo_dur = vo_durations[idx]
            text = sc.get("narration_text", "")
            
            # Place narration tightly: starts 0.15s after scene transition
            if text and vo_files[idx].exists():
                vo_pcm = cls._load_audio_pcm(vo_files[idx], cls.SAMPLE_RATE)
                v_start_sec = current_time_sec + 0.15
                vs = int(v_start_sec * cls.SAMPLE_RATE)
                ve = min(total_samples, vs + len(vo_pcm))
                voice_track[vs:ve] += vo_pcm[:ve - vs]
                speech_mask[vs:ve] = True
                
                # Subtitles with natural grammatical phrase boundaries & selective gold emphasis
                phrases = sc.get("subtitle_phrases")
                if not phrases:
                    words = text.split()
                    chunks = []
                    for ci in range(0, len(words), 4):
                        chunks.append(" ".join(words[ci:ci + 4]))
                    phrases = chunks

                timed_chunks = cls._compute_phrase_timings(phrases, v_start_sec, vo_dur)
                for c_text, w_start, w_end in timed_chunks:
                    c_end_clamped = min(current_time_sec + sc_dur - 0.04, w_end)
                    if c_end_clamped > w_start:
                        ass_events.append(f"Dialogue: 0,{fmt_ass(w_start)},{fmt_ass(c_end_clamped)},FlowSub,,0,0,0,,{c_text}")

            # Top-Center Classified HUD Telemetry Overlay
            hud_text = sc.get("hud_telemetry", "")
            if hud_text:
                c_end_hud = min(current_time_sec + sc_dur - 0.04, current_time_sec + sc_dur)
                ass_events.append(
                    f"Dialogue: 1,{fmt_ass(current_time_sec)},{fmt_ass(c_end_hud)},HudTop,,0,0,0,,{hud_text}"
                )
                    
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
                        foley_track[fs:fe] += pcm[:fe - fs]
                        
            current_time_sec += sc_dur

        # Build smooth ducking envelope (-6 dB during speech with 40ms attack/decay)
        smooth_win = int(0.04 * cls.SAMPLE_RATE)
        kernel = np.ones(smooth_win, dtype=np.float32) / smooth_win
        smoothed_speech = np.convolve(speech_mask.astype(np.float32), kernel, mode="same")
        # Attenuation factor: 1.0 when quiet, 0.45 (-7 dB) when speaking
        ducking_mult = 1.0 - (smoothed_speech * 0.55)

        # Ambient bed with ducking
        amb_path = sfx_dir / ambient_sfx
        if amb_path.exists():
            raw_amb = cls._load_audio_pcm(amb_path, cls.SAMPLE_RATE) * 0.08
            for s in range(0, total_samples, len(raw_amb)):
                e = min(total_samples, s + len(raw_amb))
                amb_track[s:e] += raw_amb[:e - s]
        amb_track *= ducking_mult

        # Continuous engine roar bed with ducking
        if engine_bed_sfx:
            eng_path = sfx_dir / engine_bed_sfx
            if eng_path.exists():
                raw_eng = cls._load_audio_pcm(eng_path, cls.SAMPLE_RATE) * 0.12
                for s in range(0, total_samples, len(raw_eng)):
                    e = min(total_samples, s + len(raw_eng))
                    engine_track[s:e] += raw_eng[:e - s]
                engine_track *= ducking_mult
        
        # Foley ducking during active speech (attenuate by 30% when overlapping speech)
        foley_duck_mult = 1.0 - (smoothed_speech * 0.30)
        foley_track *= foley_duck_mult

        # Sum tracks
        raw_mixed_pcm = voice_track + amb_track + foley_track + engine_track

        # End fade (0.4s)
        fade_len = int(0.4 * cls.SAMPLE_RATE)
        if fade_len < total_samples:
            raw_mixed_pcm[-fade_len:] *= np.linspace(1.0, 0.0, fade_len, dtype=np.float32)
            
        raw_wav = work_dir / "raw_master_audio.wav"
        stereo_pcm = np.empty((total_samples * 2,), dtype=np.int16)
        clipped_s16 = (np.clip(raw_mixed_pcm, -1.0, 1.0) * 32767).astype(np.int16)
        stereo_pcm[0::2] = clipped_s16  # Left
        stereo_pcm[1::2] = clipped_s16  # Right

        with wave.open(str(raw_wav), "w") as wf:
            wf.setnchannels(2)
            wf.setsampwidth(2)
            wf.setframerate(cls.SAMPLE_RATE)
            wf.writeframes(stereo_pcm.tobytes())

        # Step 4: Broadcast Loudness Mastering via EBU R128 (Integrated -14 LUFS, True Peak <= -1.5 dBTP)
        mastered_wav = work_dir / "master_audio_mastered.wav"
        cmd_loudnorm = [
            "ffmpeg", "-y",
            "-i", str(raw_wav),
            "-af", f"loudnorm=I={cls.TARGET_LUFS}:TP={cls.TARGET_TRUE_PEAK}:LRA={cls.TARGET_LRA}",
            "-ar", str(cls.SAMPLE_RATE),
            "-ac", "2",
            "-c:a", "pcm_s16le",
            str(mastered_wav)
        ]
        subprocess.run(cmd_loudnorm, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            
        # Step 5: Write Professional ASS Subtitles (Punchy gold, safe margin, high readability)
        ass_path = work_dir / "master_subtitles.ass"
        ass_content = [
            "[Script Info]",
            "ScriptType: v4.00+",
            "PlayResX: 1080",
            "PlayResY: 1920",
            "ScaledBorderAndShadow: yes",
            "",
            "[V4+ Styles]",
            "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
            "Style: FlowSub,Arial Black,54,&H00FFFFFF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,1.2,0,1,5.0,2.5,2,80,80,820,1",
            "Style: HudTop,Consolas,32,&H00D7FF&,&H00000000,&H00000000,&HA0000000,1,0,0,0,100,100,1.5,0,1,4.0,2.0,8,60,60,240,1",
            "",
            "[Events]",
            "Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"
        ] + ass_events
        
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write("\n".join(ass_content))
            
        # Step 6: Final Broadcast Mux
        out_final = Path(f"exports/{output_filename}")
        out_final.parent.mkdir(parents=True, exist_ok=True)
        
        # Escape path for FFmpeg subtitles filter
        clean_ass_sub = ass_path.as_posix().replace(":", r"\:")
        cmd_mux = [
            "ffmpeg", "-y", "-threads", "2",
            "-i", str(merged_video),
            "-i", str(mastered_wav),
            "-vf", f"subtitles={clean_ass_sub},format=yuv420p",
            "-r", str(cls.FPS),
            "-c:v", "libx264", "-preset", "fast",
            "-b:v", "8500k", "-minrate", "8200k", "-maxrate", "9000k", "-bufsize", "9000k", "-nal-hrd", "cbr",
            "-pix_fmt", "yuv420p",
            "-color_range", "1",
            "-colorspace", "bt709",
            "-color_primaries", "bt709",
            "-color_trc", "bt709",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
            "-t", f"{total_duration:.2f}",
            str(out_final)
        ]
        subprocess.run(cmd_mux, check=True)
        return out_final
