"""Viral Video Assembly Engine: Ken Burns zooms, multi-track sound design, and kinetic subtitles."""
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from config.settings import get_ffmpeg_path, EXPORTS_DIR, LOGS_DIR
from src.database.models import StoryboardScene, RenderJob, VideoExport
from src.database.repository import RenderJobRepository, VideoExportRepository
from src.assets.sound_designer import SoundDesigner
from src.quality.media_validator import validate_media_file


class ViralEngine:
    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_path()
        self.sfx = SoundDesigner.ensure_sfx_library()

    def generate_ass_subtitles(
        self, scenes: List[StoryboardScene], output_ass: str, is_shorts: bool = False
    ) -> str:
        """Generate high-retention stylized ASS subtitles:
        - Bright gold primary color with thick black outline
        - Centered in the sweet spot (above Shorts bottom UI)
        - Punchy readable text
        """
        ass_path = Path(output_ass)
        ass_path.parent.mkdir(parents=True, exist_ok=True)

        if is_shorts:
            res_x, res_y = 1080, 1920
            font_size = 60
            margin_v = 360
            chunk_size = 3
        else:
            res_x, res_y = 1920, 1080
            font_size = 52
            margin_v = 90
            chunk_size = 4

        header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {res_x}
PlayResY: {res_y}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ViralGold,Arial,{font_size},&H0024E6FF,&H00000000,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,4,2,2,40,40,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        current_time = 0.0
        dialogues = []

        def fmt_ass_time(sec: float) -> str:
            hrs = int(sec // 3600)
            mins = int((sec % 3600) // 60)
            secs = int(sec % 60)
            cs = int((sec - int(sec)) * 100)
            return f"{hrs}:{mins:02d}:{secs:02d}.{cs:02d}"

        for scene in scenes:
            scene_duration = max(2.5, scene.duration_sec)
            words = scene.narration_text.split()
            if not words:
                continue

            chunks = [" ".join(words[i : i + chunk_size]) for i in range(0, len(words), chunk_size)]
            per_chunk_time = scene_duration / max(1, len(chunks))

            for chunk in chunks:
                start_t = current_time
                end_t = current_time + per_chunk_time
                current_time = end_t
                clean_chunk = chunk.replace("\n", " ").strip()
                dialogues.append(
                    f"Dialogue: 0,{fmt_ass_time(start_t)},{fmt_ass_time(end_t)},ViralGold,,0,0,0,,{clean_chunk.upper()}"
                )

        full_content = header + "\n".join(dialogues) + "\n"
        with open(ass_path, "w", encoding="utf-8") as f:
            f.write(full_content)

        return str(ass_path)

    def assemble_viral_video(
        self,
        script_id: int,
        scenes: List[StoryboardScene],
        scene_images: List[str],
        narration_audio_path: str,
        output_mp4_path: str,
        thumbnail_path: Optional[str] = None,
        job_id: Optional[int] = None,
        is_shorts: bool = False,
    ) -> Dict[str, Any]:
        """Assemble a high-retention viral 1080p MP4:
        1. Dynamic Ken Burns camera zooms (zoompan) on each scene
        2. Multi-track sound design (voiceover + sub-bass tension drone + whoosh + impact hit)
        3. Burned-in golden kinetic subtitles
        """
        start_time = time.time()
        out_path = Path(output_mp4_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        temp_dir = out_path.parent / f"temp_{script_id}"
        temp_dir.mkdir(parents=True, exist_ok=True)

        if not job_id:
            job = RenderJob(
                script_id=script_id,
                output_path=str(out_path),
                resolution="1080x1920" if is_shorts else "1920x1080",
                fps=30,
                status="rendering",
                progress_pct=10,
            )
            job_id = RenderJobRepository.create_job(job)
        else:
            RenderJobRepository.update_job_status(job_id, "rendering", 15)

        # Step 1: Validate input audio
        media_info = validate_media_file(narration_audio_path)
        total_audio_duration = media_info.get("duration", 0.0)
        if total_audio_duration <= 0.0:
            total_audio_duration = sum(s.duration_sec for s in scenes)

        # Proportional scene timing matching spoken narration sentences exactly
        num_images = max(1, len(scene_images))
        if scenes and len(scenes) == len(scene_images):
            raw_durations = [max(2.5, s.duration_sec) for s in scenes]
            sum_target = sum(raw_durations)
            scale = total_audio_duration / sum_target if sum_target > 0 else 1.0
            scene_durations = [d * scale for d in raw_durations]
        else:
            per_dur = max(3.0, total_audio_duration / num_images)
            scene_durations = [per_dur] * num_images

        # Step 2: Render each scene into a dynamic Ken Burns clip
        RenderJobRepository.update_job_status(job_id, "rendering", 30)
        scene_clips = []
        scale_arg = "1080:1920" if is_shorts else "1920:1080"
        size_arg = "1080x1920" if is_shorts else "1920x1080"
        for idx, img_path in enumerate(scene_images):
            clip_out = temp_dir / f"clip_{idx}.mp4"
            dur = scene_durations[idx]
            num_frames = int(dur * 30)

            # Alternate between dynamic push-in and pull-out camera movement
            zoom_expr = "min(zoom+0.0016,1.26)" if idx % 2 == 0 else "max(1.26-0.0016*on,1.0)"
            pan_vf = (
                f"scale={scale_arg},"
                f"zoompan=z='{zoom_expr}':d={num_frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={size_arg}:fps=30"
            )

            cmd_clip = [
                self.ffmpeg_bin, "-y",
                "-loop", "1", "-i", str(Path(img_path).resolve()),
                "-vf", pan_vf,
                "-t", f"{dur:.2f}",
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-pix_fmt", "yuv420p",
                "-r", "30",
                str(clip_out),
            ]
            subprocess.run(cmd_clip, capture_output=True, timeout=60)
            if clip_out.exists():
                scene_clips.append(str(clip_out))

        if not scene_clips:
            error_msg = "Failed to render dynamic scene clips."
            RenderJobRepository.update_job_status(job_id, "failed", 0, error_msg)
            return {"success": False, "error": error_msg}

        # Step 3: Concat video clips
        RenderJobRepository.update_job_status(job_id, "rendering", 55)
        concat_txt = temp_dir / "concat_list.txt"
        with open(concat_txt, "w", encoding="utf-8") as f:
            for c in scene_clips:
                clean_path = str(Path(c).resolve()).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        raw_visual_mp4 = temp_dir / "raw_visual.mp4"
        cmd_concat = [
            self.ffmpeg_bin, "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c", "copy",
            str(raw_visual_mp4),
        ]
        subprocess.run(cmd_concat, capture_output=True, timeout=60)

        # Step 4: Generate stylized subtitles
        ass_subtitles = temp_dir / "subtitles.ass"
        self.generate_ass_subtitles(scenes, str(ass_subtitles), is_shorts=is_shorts)

        # Step 5: Composite Multi-Track Audio (Voiceover + Sub-Bass Drone + Precision SFX Cues)
        RenderJobRepository.update_job_status(job_id, "rendering", 75)
        scene_cues = []
        cur_t = 0.0
        for idx, s in enumerate(scenes):
            dur = scene_durations[idx] if idx < len(scene_durations) else 6.0
            vtype = getattr(s, "visual_type", "")
            if idx == 0:
                scene_cues.append((cur_t, "impact_boom", 0.55))
            elif vtype == "archival_photo":
                scene_cues.append((cur_t, "shutter_click", 0.45))
            elif vtype == "newspaper":
                scene_cues.append((cur_t, "paper_rustle", 0.45))
            elif vtype == "court_docket":
                scene_cues.append((cur_t, "stamp_thud", 0.55))
            elif vtype == "financial_autopsy":
                scene_cues.append((cur_t, "impact_boom", 0.40))
            elif vtype == "split_verdict":
                scene_cues.append((cur_t, "stamp_thud", 0.50))
            elif vtype == "cliffhanger":
                scene_cues.append((cur_t, "impact_boom", 0.65))
            else:
                scene_cues.append((cur_t, "whoosh", 0.35))
            cur_t += dur

        mixed_audio = temp_dir / "mixed_audio.wav"
        try:
            audio_source = SoundDesigner.composite_master_soundtrack(
                narration_audio_path=narration_audio_path,
                scene_cues=scene_cues,
                output_wav_path=str(mixed_audio),
                ffmpeg_bin=self.ffmpeg_bin,
            )
        except Exception:
            audio_source = narration_audio_path

        # Step 6: Final Composite with MagnatesMedia Film Grain, Vignette & Kinetic Subtitles
        RenderJobRepository.update_job_status(job_id, "rendering", 90)
        render_log = LOGS_DIR / f"viral_render_{script_id}.log"

        # Safe ASS path escaping for FFmpeg filter on Windows
        clean_ass = str(ass_subtitles.resolve()).replace("\\", "/").replace(":", "\\:")
        if is_shorts:
            video_filters = (
                f"noise=alls=10:allf=t+u,"
                f"eq=contrast=1.10:brightness=0.01:saturation=1.16,"
                f"subtitles='{clean_ass}'"
            )
        else:
            video_filters = (
                f"noise=alls=10:allf=t+u,"
                f"vignette=PI/4,"
                f"eq=contrast=1.12:brightness=-0.01:saturation=1.15,"
                f"subtitles='{clean_ass}'"
            )

        cmd_final = [
            self.ffmpeg_bin, "-y",
            "-i", str(raw_visual_mp4),
            "-i", str(audio_source),
            "-vf", video_filters,
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-crf", "20",
            "-threads", "0",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(out_path),
        ]

        try:
            with open(render_log, "w", encoding="utf-8") as lf:
                proc = subprocess.run(cmd_final, stdout=lf, stderr=subprocess.STDOUT, timeout=600)

            # Fallback if subtitle filter encountered path error
            if proc.returncode != 0:
                cmd_fallback = [
                    self.ffmpeg_bin, "-y",
                    "-i", str(raw_visual_mp4),
                    "-i", str(audio_source),
                    "-c:v", "libx264",
                    "-preset", "veryfast",
                    "-threads", "0",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",
                    str(out_path),
                ]
                subprocess.run(cmd_fallback, capture_output=True, timeout=300)
        except subprocess.TimeoutExpired:
            error_msg = f"Viral render timed out after 600s."
            RenderJobRepository.update_job_status(job_id, "failed", 0, error_msg)
            return {"success": False, "error": error_msg}

        # Clean up intermediate clips
        shutil.rmtree(temp_dir, ignore_errors=True)

        # Step 7: Verify rendered video
        validation = validate_media_file(str(out_path))
        render_duration = round(time.time() - start_time, 2)

        if not validation.get("valid", False):
            error_msg = f"Viral render verification failed: {validation}"
            RenderJobRepository.update_job_status(job_id, "failed", 0, error_msg)
            return {"success": False, "error": error_msg}

        # Register video export
        import hashlib
        with open(out_path, "rb") as f:
            content_hash = hashlib.sha256(f.read()).hexdigest()

        export = VideoExport(
            render_job_id=job_id,
            script_id=script_id,
            file_path=str(out_path.resolve()),
            thumbnail_path=str(thumbnail_path) if thumbnail_path else "",
            duration_sec=validation.get("duration", 0.0),
            resolution=validation.get("resolution", "1920x1080"),
            file_size_bytes=validation.get("size_bytes", 0),
            content_hash=content_hash,
            verified=True,
        )
        export_id = VideoExportRepository.add_export(export)
        export.id = export_id

        RenderJobRepository.update_job_status(
            job_id,
            status="completed",
            progress_pct=100,
            render_time=render_duration,
        )

        return {
            "success": True,
            "video_export_id": export_id,
            "job_id": job_id,
            "file_path": str(out_path),
            "duration_sec": validation.get("duration", 0.0),
            "resolution": validation.get("resolution", "1920x1080"),
            "file_size_bytes": validation.get("size_bytes", 0),
            "content_hash": content_hash,
            "render_time_sec": render_duration,
        }
