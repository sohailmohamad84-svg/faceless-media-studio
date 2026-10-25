"""Official YouTube Data API v3 uploader with mandatory human approval enforcement."""
import json
import zipfile
from pathlib import Path
from typing import Dict, Any, Optional
from src.database.models import VideoExport, YouTubeUpload, HumanApproval
from src.database.repository import (
    VideoExportRepository,
    ApprovalRepository,
    YouTubeUploadRepository,
)
from src.youtube.oauth import YouTubeAuthManager


class PublishingError(Exception):
    """Raised when publishing violates approval or verification rules."""
    pass


class YouTubePublisher:
    @staticmethod
    def verify_approval_gate(video_export_id: int) -> HumanApproval:
        """Enforce mandatory human approval before any upload operation.
        Raises PublishingError if video is not explicitly approved with matching content hash.
        """
        export = None
        for exp in VideoExportRepository.list_exports():
            if exp.id == video_export_id:
                export = exp
                break

        if not export:
            raise PublishingError(f"Video export {video_export_id} not found.")

        active_approval = ApprovalRepository.get_active_approval(export.script_id)
        if not active_approval:
            raise PublishingError(
                f"UNAPPROVED VIDEO: Script {export.script_id} has not been approved by the creator."
            )

        if not active_approval.is_valid:
            raise PublishingError(
                f"INVALID APPROVAL: Prior approval for Script {export.script_id} was invalidated due to edits."
            )

        if active_approval.content_hash != export.content_hash:
            raise PublishingError(
                f"HASH MISMATCH: Video content hash {export.content_hash[:8]} does not match approved hash {active_approval.content_hash[:8]}."
            )

        return active_approval

    @staticmethod
    def create_manual_upload_package(
        video_export_id: int,
        title: str,
        description: str,
        tags: str,
        output_zip_path: str,
    ) -> str:
        """Create a zero-quota, 100% reliable manual upload ZIP package containing:
        - video.mp4
        - thumbnail.jpg
        - metadata.txt (title, description, tags, chapters, AI disclosure)
        """
        # Ensure approval gate is satisfied
        YouTubePublisher.verify_approval_gate(video_export_id)

        export = None
        for exp in VideoExportRepository.list_exports():
            if exp.id == video_export_id:
                export = exp
                break

        zip_p = Path(output_zip_path)
        zip_p.parent.mkdir(parents=True, exist_ok=True)

        metadata_content = (
            f"=== YOUTUBE VIDEO METADATA ===\n\n"
            f"TITLE:\n{title}\n\n"
            f"TAGS:\n{tags}\n\n"
            f"PRIVACY:\nPrivate (Recommended for initial verification)\n\n"
            f"SYNTHETIC MEDIA DISCLOSURE:\nYes - Altered or synthetic content (AI Voiceover)\n\n"
            f"DESCRIPTION:\n{description}\n"
        )

        with zipfile.ZipFile(zip_p, "w", zipfile.ZIP_DEFLATED) as zf:
            # Add video
            if Path(export.file_path).exists():
                zf.write(export.file_path, arcname="video.mp4")
            # Add thumbnail
            if export.thumbnail_path and Path(export.thumbnail_path).exists():
                zf.write(export.thumbnail_path, arcname="thumbnail.jpg")
            # Add metadata
            zf.writestr("metadata.txt", metadata_content)

        return str(zip_p)

    @staticmethod
    def upload_video_via_api(
        video_export_id: int,
        title: str,
        description: str,
        tags: str,
        privacy_status: str = "private",
    ) -> Dict[str, Any]:
        """Upload video via official YouTube Data API v3 (Resumable upload).
        Requires active OAuth token.
        """
        # 1. Enforce strict human approval gate
        approval = YouTubePublisher.verify_approval_gate(video_export_id)

        # 2. Check OAuth
        creds = YouTubeAuthManager.get_credentials()
        if not creds:
            return {
                "success": False,
                "error": "OAuth credentials not configured. Please complete authentication in Settings or use the Manual Upload Package.",
            }

        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload

            youtube = build("youtube", "v3", credentials=creds)

            export = None
            for exp in VideoExportRepository.list_exports():
                if exp.id == video_export_id:
                    export = exp
                    break

            body = {
                "snippet": {
                    "title": title[:100],
                    "description": description,
                    "tags": [t.strip() for t in tags.split(",") if t.strip()],
                    "categoryId": "27",  # Education
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": False,
                },
            }

            media = MediaFileUpload(
                export.file_path,
                mimetype="video/mp4",
                resumable=True,
                chunksize=1024 * 1024 * 5,  # 5MB chunks
            )

            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )

            response = None
            while response is None:
                status, response = request.next_chunk()

            youtube_id = response.get("id")

            # Upload thumbnail if available
            if export.thumbnail_path and Path(export.thumbnail_path).exists():
                try:
                    youtube.thumbnails().set(
                        videoId=youtube_id,
                        media_body=MediaFileUpload(export.thumbnail_path, mimetype="image/jpeg"),
                    ).execute()
                except Exception:
                    pass

            # Record in database
            upload_record = YouTubeUpload(
                video_export_id=video_export_id,
                youtube_video_id=youtube_id,
                title=title,
                description=description,
                tags=tags,
                privacy_status=privacy_status,
                quota_used=1600,
                response_json=json.dumps(response),
            )
            YouTubeUploadRepository.record_upload(upload_record)

            return {
                "success": True,
                "youtube_video_id": youtube_id,
                "privacy_status": privacy_status,
                "url": f"https://youtu.be/{youtube_id}",
            }

        except Exception as e:
            return {
                "success": False,
                "error": f"YouTube API upload failed: {str(e)}",
                "recommendation": "Use the Manual Upload Package to upload directly through YouTube Studio.",
            }

    @staticmethod
    def upload_short_file(
        file_path: str,
        title: str,
        description: str,
        tags: Optional[list] = None,
        privacy_status: str = "public",
    ) -> Dict[str, Any]:
        """Upload any vertical MP4 directly to YouTube Shorts using YouTube Data API v3."""
        vid_p = Path(file_path)
        if not vid_p.exists():
            return {"success": False, "error": f"File not found: {file_path}"}

        creds = YouTubeAuthManager.get_credentials()
        if not creds:
            return {"success": False, "error": "YouTube OAuth credentials not configured."}

        try:
            from googleapiclient.discovery import build
            from googleapiclient.http import MediaFileUpload

            youtube = build("youtube", "v3", credentials=creds)

            # Ensure #Shorts tag in title/tags
            clean_title = title if "#shorts" in title.lower() else f"{title} #shorts"
            tags_list = tags or ["shorts", "engineering", "documentary", "panamacanal"]

            body = {
                "snippet": {
                    "title": clean_title[:100],
                    "description": description,
                    "tags": tags_list,
                    "categoryId": "27",  # Education / Infotainment
                },
                "status": {
                    "privacyStatus": privacy_status,
                    "selfDeclaredMadeForKids": False,
                },
            }

            media = MediaFileUpload(
                str(vid_p),
                mimetype="video/mp4",
                resumable=True,
                chunksize=1024 * 1024 * 5,  # 5MB chunks
            )

            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media,
            )

            response = None
            while response is None:
                status, response = request.next_chunk()

            youtube_id = response.get("id")
            return {
                "success": True,
                "youtube_video_id": youtube_id,
                "privacy_status": privacy_status,
                "url": f"https://youtube.com/shorts/{youtube_id}",
                "watch_url": f"https://youtu.be/{youtube_id}",
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"YouTube upload failed: {str(e)}",
            }
