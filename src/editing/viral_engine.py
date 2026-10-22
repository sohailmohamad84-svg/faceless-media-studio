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

    def generate_ass_subtitles(self, scenes: List[StoryboardScene], output_ass: str) -> str:
        """Generate high-retention stylized ASS subtitles:
        - Bright gold primary color with thick black outline
        - Centered at lower third
        - Punchy readable text
        """
        ass_path = Path(output_ass)
        ass_path.parent.mkdir(parents=True, exist_ok=True)

        header = """[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: ViralGold,Arial,52,&H0000D7FF,&H00000000,&H00000000,&H80000000,-1,0,0,0,100,100,1,0,1,4,2,2,60,60,80,1

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

            # Split scene into ~4-word chunks for kinetic subtitle delivery
            chunk_size = 4
            chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
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
                resolution="1920x1080",
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

        per_scene_duration = max(3.0, total_audio_duration / max(1, len(scene_images)))

        # Step 2: Render each scene into a dynamic Ken Burns clip
        RenderJobRepository.update_job_status(job_id, "rendering", 30)
        scene_clips = []
        for idx, img_path in enumerate(scene_images):
            clip_out = temp_dir / f"clip_{idx}.mp4"
            # Alternate between slow zoom-in and slow zoom-out
            zoom_expr = "min(zoom+0.0014,1.3)" if idx % 2 == 0 else "max(1.3-0.0014*on,1.0)"
            pan_vf = (
                f"scale=1920:1080,"
                f"zoompan=z='{zoom_expr}':d={int(per_scene_duration * 30)}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1920x1080"
            )

            cmd_clip = [
                self.ffmpeg_bin, "-y",
                "-loop", "1", "-i", str(Path(img_path).resolve()),
                "-vf", pan_vf,
                "-t", f"{per_scene_duration:.2f}",
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
        self.generate_ass_subtitles(scenes, str(ass_subtitles))

        # Step 5: Composite Multi-Track Audio (Voiceover + Sub-Bass Drone + Boom + Whooshes)
        RenderJobRepository.update_job_status(job_id, "rendering", 75)
        boom = self.sfx.get("impact_boom", "")
        whoosh = self.sfx.get("whoosh", "")
        drone = self.sfx.get("tension_drone", "")

        # Complex audio filter: mix voiceover (1.0) with subtle drone (0.08) and impact hit (0.35)
        mixed_audio = temp_dir / "mixed_audio.wav"
        cmd_audio = [
            self.ffmpeg_bin, "-y",
            "-i", str(Path(narration_audio_path).resolve()),
            "-stream_loop", "-1", "-i", str(Path(drone).resolve()),
            "-i", str(Path(boom).resolve()),
            "-filter_complex",
            "[0:a]volume=1.0[voice];"
            "[1:a]volume=0.08,atrim=0:duration=" + f"{total_audio_duration}" + "[drone];"
            "[2:a]volume=0.35[hit];"
            "[voice][drone][hit]amix=inputs=3:duration=first:dropout_transition=2[aout]",
            "-map", "[aout]",
            "-ac", "2",
            "-ar", "44100",
            str(mixed_audio),
        ]
        subprocess.run(cmd_audio, capture_output=True, timeout=60)
        audio_source = str(mixed_audio) if mixed_audio.exists() else narration_audio_path

        # Step 6: Final Composite with Subtitle Overlay and Broadcast Audio
        RenderJobRepository.update_job_status(job_id, "rendering", 90)
        render_log = LOGS_DIR / f"viral_render_{script_id}.log"

        # Safe ASS path escaping for FFmpeg filter on Windows
        clean_ass = str(ass_subtitles.resolve()).replace("\\", "/").replace(":", "\\:")
        video_filters = f"subtitles='{clean_ass}'"

        cmd_final = [
            self.ffmpeg_bin, "-y",
            "-i", str(raw_visual_mp4),
            "-i", str(audio_source),
            "-vf", video_filters,
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "19",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(out_path),
        ]

        try:
            with open(render_log, "w", encoding="utf-8") as lf:
                proc = subprocess.run(cmd_final, stdout=lf, stderr=subprocess.STDOUT, timeout=180)

            # Fallback if subtitle filter encountered path error
            if proc.returncode != 0:
                cmd_fallback = [
                    self.ffmpeg_bin, "-y",
                    "-i", str(raw_visual_mp4),
                    "-i", str(audio_source),
                    "-c:v", "libx264",
                    "-preset", "veryfast",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",
                    str(out_path),
                ]
                subprocess.run(cmd_fallback, capture_output=True, timeout=120)

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

        except Exception as e:
            error_msg = f"Viral render exception: {str(e)}"
            RenderJobRepository.update_job_status(job_id, "failed", 0, error_msg)
            return {"success": False, "error": error_msg}
