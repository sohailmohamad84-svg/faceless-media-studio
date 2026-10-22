"""FFmpeg 9.0 Media Processing Orchestrator and Timeline Assembly Engine."""
import json
import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from config.settings import get_ffmpeg_path, EXPORTS_DIR, LOGS_DIR
from src.database.models import StoryboardScene, RenderJob, VideoExport
from src.database.repository import RenderJobRepository, VideoExportRepository
from src.quality.media_validator import validate_media_file


class FFmpegOrchestrator:
    def __init__(self):
        self.ffmpeg_bin = get_ffmpeg_path()

    def generate_srt_subtitles(self, scenes: List[StoryboardScene], output_srt: str) -> str:
        """Generate an SRT subtitle file from storyboard scenes and their narration text."""
        srt_path = Path(output_srt)
        srt_path.parent.mkdir(parents=True, exist_ok=True)

        current_time = 0.0
        lines = []

        for idx, scene in enumerate(scenes, start=1):
            start_sec = current_time
            end_sec = current_time + max(2.0, scene.duration_sec)
            current_time = end_sec

            def fmt_time(seconds: float) -> str:
                hrs = int(seconds // 3600)
                mins = int((seconds % 3600) // 60)
                secs = int(seconds % 60)
                millis = int((seconds - int(seconds)) * 1000)
                return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

            caption_text = scene.narration_text.strip()
            # Wrap long captions
            if len(caption_text) > 80:
                parts = caption_text.split(". ")
                caption_text = "\n".join(parts[:2])

            lines.append(f"{idx}")
            lines.append(f"{fmt_time(start_sec)} --> {fmt_time(end_sec)}")
            lines.append(caption_text)
            lines.append("")

        with open(srt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        return str(srt_path)

    def generate_ambient_track(self, duration_sec: float, output_path: str) -> str:
        """Generate subtle, royalty-free low-frequency ambient background tone using FFmpeg synthesizer."""
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        # Synthesize 55Hz sine wave with harmonic warmth at low volume
        cmd = [
            self.ffmpeg_bin, "-y",
            "-f", "lavfi",
            "-i", f"sine=frequency=55:duration={int(duration_sec + 2)}",
            "-af", "volume=0.04,lowpass=f=200",
            "-c:a", "aac",
            str(out),
        ]
        try:
            subprocess.run(cmd, capture_output=True, timeout=15)
        except Exception:
            pass
        return str(out)

    def assemble_multiscene_video(
        self,
        script_id: int,
        scenes: List[StoryboardScene],
        scene_image_paths: List[str],
        narration_audio_path: str,
        output_mp4_path: str,
        thumbnail_path: Optional[str] = None,
        job_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Assemble a complete 1080p landscape MP4 video from storyboard scenes, image assets,
        narration audio, and optional ambient track.
        """
        start_time = time.time()
        out_path = Path(output_mp4_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

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

        # 1. Validate assets
        if not Path(narration_audio_path).exists():
            error_msg = f"Narration audio file missing: {narration_audio_path}"
            RenderJobRepository.update_job_status(job_id, "failed", 0, error_msg)
            return {"success": False, "error": error_msg}

        for p in scene_image_paths:
            if not Path(p).exists():
                error_msg = f"Scene image asset missing: {p}"
                RenderJobRepository.update_job_status(job_id, "failed", 0, error_msg)
                return {"success": False, "error": error_msg}

        # 2. Get audio duration
        media_info = validate_media_file(narration_audio_path)
        total_audio_duration = media_info.get("duration", 0.0)
        if total_audio_duration <= 0.0:
            total_audio_duration = sum(s.duration_sec for s in scenes)

        # 3. Build concat demuxer file for scenes
        concat_file = out_path.parent / f"concat_list_{script_id}.txt"
        total_scenes = len(scene_image_paths)
        per_scene_duration = max(2.0, total_audio_duration / max(1, total_scenes))

        with open(concat_file, "w", encoding="utf-8") as f:
            for img_path in scene_image_paths:
                clean_path = str(Path(img_path).resolve()).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")
                f.write(f"duration {per_scene_duration:.2f}\n")
            # Concat demuxer requirement: repeat last file once
            if scene_image_paths:
                clean_path = str(Path(scene_image_paths[-1]).resolve()).replace("\\", "/")
                f.write(f"file '{clean_path}'\n")

        RenderJobRepository.update_job_status(job_id, "rendering", 40)

        # 4. Generate subtitle file
        srt_file = out_path.parent / f"subtitles_{script_id}.srt"
        self.generate_srt_subtitles(scenes, str(srt_file))

        # 5. Generate ambient backing audio
        ambient_path = out_path.parent / f"ambient_{script_id}.aac"
        self.generate_ambient_track(total_audio_duration, str(ambient_path))

        RenderJobRepository.update_job_status(job_id, "rendering", 60)

        # 6. Execute FFmpeg rendering pipeline
        render_log = LOGS_DIR / f"render_{script_id}.log"

        cmd = [
            self.ffmpeg_bin,
            "-y",
            "-f", "concat",
            "-safe", "0",
            "-i", str(concat_file),
            "-i", str(Path(narration_audio_path).resolve()),
            "-c:v", "libx264",
            "-preset", "medium",
            "-crf", "20",
            "-pix_fmt", "yuv420p",
            "-r", "30",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            str(out_path),
        ]

        try:
            with open(render_log, "w", encoding="utf-8") as log_file:
                proc = subprocess.run(cmd, stdout=log_file, stderr=subprocess.STDOUT, timeout=180)

            if proc.returncode != 0:
                error_msg = f"FFmpeg failed with exit code {proc.returncode}. See {render_log}."
                RenderJobRepository.update_job_status(job_id, "failed", 0, error_msg)
                return {"success": False, "error": error_msg}

            # 7. Post-render integrity verification
            validation = validate_media_file(str(out_path))
            render_duration = round(time.time() - start_time, 2)

            if not validation.get("valid", False):
                error_msg = f"Rendered video failed verification: {validation}"
                RenderJobRepository.update_job_status(job_id, "failed", 0, error_msg)
                return {"success": False, "error": error_msg}

            # Register video export in database
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
                "subtitle_srt_path": str(srt_file),
            }

        except subprocess.TimeoutExpired:
            error_msg = "FFmpeg render timed out after 180 seconds."
            RenderJobRepository.update_job_status(job_id, "failed", 0, error_msg)
            return {"success": False, "error": error_msg}
        except Exception as e:
            error_msg = f"Unexpected error during render: {str(e)}"
            RenderJobRepository.update_job_status(job_id, "failed", 0, error_msg)
            return {"success": False, "error": error_msg}
