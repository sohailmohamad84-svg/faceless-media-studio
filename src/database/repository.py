"""Repository layer for database operations in Faceless Media Studio."""
import hashlib
import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from src.database.connection import get_db_cursor
from src.database.models import (
    Channel,
    Topic,
    Source,
    ClaimLedgerItem,
    Script,
    StoryboardScene,
    MediaAsset,
    Voiceover,
    RenderJob,
    VideoExport,
    HumanApproval,
    YouTubeUpload,
    AnalyticsSnapshot,
    CostRecord,
    WorkflowRun,
)


class ChannelRepository:
    @staticmethod
    def get_channel() -> Channel:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM channels LIMIT 1")
            row = cursor.fetchone()
            if row:
                return Channel(**dict(row))
            return Channel()

    @staticmethod
    def update_budget_ceiling(new_ceiling: float) -> None:
        with get_db_cursor() as cursor:
            cursor.execute(
                "UPDATE channels SET monthly_budget_ceiling = ?, updated_at = datetime('now')",
                (new_ceiling,),
            )


class TopicRepository:
    @staticmethod
    def add_topic(topic: Topic) -> int:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO topics (
                    title, angle, category_pillar, primary_viewer_question, target_audience,
                    evidence_summary, demand_score, originality_score, evergreen_score,
                    commercial_score, competition_score, source_quality_score, feasibility_score,
                    total_score, status, why_this_topic, suggested_length_min, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    topic.title,
                    topic.angle,
                    topic.category_pillar,
                    topic.primary_viewer_question,
                    topic.target_audience,
                    topic.evidence_summary,
                    topic.demand_score,
                    topic.originality_score,
                    topic.evergreen_score,
                    topic.commercial_score,
                    topic.competition_score,
                    topic.source_quality_score,
                    topic.feasibility_score,
                    topic.total_score,
                    topic.status,
                    topic.why_this_topic,
                    topic.suggested_length_min,
                    topic.created_at,
                    topic.updated_at,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def list_topics(status: Optional[str] = None) -> List[Topic]:
        with get_db_cursor() as cursor:
            if status:
                cursor.execute(
                    "SELECT * FROM topics WHERE status = ? ORDER BY total_score DESC",
                    (status,),
                )
            else:
                cursor.execute("SELECT * FROM topics ORDER BY total_score DESC")
            return [Topic(**dict(row)) for row in cursor.fetchall()]

    @staticmethod
    def get_topic(topic_id: int) -> Optional[Topic]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM topics WHERE id = ?", (topic_id,))
            row = cursor.fetchone()
            return Topic(**dict(row)) if row else None

    @staticmethod
    def update_topic_status(topic_id: int, status: str) -> None:
        with get_db_cursor() as cursor:
            cursor.execute(
                "UPDATE topics SET status = ?, updated_at = datetime('now') WHERE id = ?",
                (status, topic_id),
            )

    @staticmethod
    def update_topic_score(topic_id: int, scores: Dict[str, float], total_score: float) -> None:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                UPDATE topics SET
                    demand_score = ?, originality_score = ?, evergreen_score = ?,
                    commercial_score = ?, competition_score = ?, source_quality_score = ?,
                    feasibility_score = ?, total_score = ?, updated_at = datetime('now')
                WHERE id = ?
                """,
                (
                    scores.get("demand_score", 0),
                    scores.get("originality_score", 0),
                    scores.get("evergreen_score", 0),
                    scores.get("commercial_score", 0),
                    scores.get("competition_score", 0),
                    scores.get("source_quality_score", 0),
                    scores.get("feasibility_score", 0),
                    total_score,
                    topic_id,
                ),
            )


class SourceRepository:
    @staticmethod
    def add_source(source: Source) -> int:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO sources (topic_id, title, url, publisher, source_type, excerpt, credibility_rating, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source.topic_id,
                    source.title,
                    source.url,
                    source.publisher,
                    source.source_type,
                    source.excerpt,
                    source.credibility_rating,
                    source.created_at,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def get_sources_for_topic(topic_id: int) -> List[Source]:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM sources WHERE topic_id = ? ORDER BY credibility_rating DESC",
                (topic_id,),
            )
            return [Source(**dict(row)) for row in cursor.fetchall()]


class ScriptRepository:
    @staticmethod
    def add_script(script: Script) -> int:
        full_text = f"{script.title} {script.hook_text} {script.body_text} {script.conclusion_text}"
        content_hash = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
        script.content_hash = content_hash
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO scripts (
                    topic_id, version, title, hook_text, promise_text, body_text,
                    conclusion_text, call_to_action, word_count, target_duration_sec,
                    content_hash, status, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    script.topic_id,
                    script.version,
                    script.title,
                    script.hook_text,
                    script.promise_text,
                    script.body_text,
                    script.conclusion_text,
                    script.call_to_action,
                    script.word_count,
                    script.target_duration_sec,
                    script.content_hash,
                    script.status,
                    script.created_at,
                    script.updated_at,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def get_script(script_id: int) -> Optional[Script]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM scripts WHERE id = ?", (script_id,))
            row = cursor.fetchone()
            return Script(**dict(row)) if row else None

    @staticmethod
    def get_script_for_topic(topic_id: int) -> Optional[Script]:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM scripts WHERE topic_id = ? ORDER BY id DESC LIMIT 1",
                (topic_id,),
            )
            row = cursor.fetchone()
            return Script(**dict(row)) if row else None

    @staticmethod
    def list_scripts() -> List[Script]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM scripts ORDER BY id DESC")
            return [Script(**dict(row)) for row in cursor.fetchall()]

    @staticmethod
    def update_script(script: Script) -> None:
        full_text = f"{script.title} {script.hook_text} {script.body_text} {script.conclusion_text}"
        new_hash = hashlib.sha256(full_text.encode("utf-8")).hexdigest()
        script.content_hash = new_hash
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                UPDATE scripts SET
                    version = ?, title = ?, hook_text = ?, promise_text = ?,
                    body_text = ?, conclusion_text = ?, call_to_action = ?,
                    word_count = ?, target_duration_sec = ?, content_hash = ?,
                    status = ?, updated_at = datetime('now')
                WHERE id = ?
                """,
                (
                    script.version,
                    script.title,
                    script.hook_text,
                    script.promise_text,
                    script.body_text,
                    script.conclusion_text,
                    script.call_to_action,
                    script.word_count,
                    script.target_duration_sec,
                    script.content_hash,
                    script.status,
                    script.id,
                ),
            )
            # Crucial: Invalidate downstream approvals on script edit!
            cursor.execute(
                "UPDATE approvals SET is_valid = 0 WHERE script_id = ?",
                (script.id,),
            )


class ClaimLedgerRepository:
    @staticmethod
    def add_claim(item: ClaimLedgerItem) -> int:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO claim_ledger (script_id, claim_text, source_url, source_title, verified, notes, timestamp_marker)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    item.script_id,
                    item.claim_text,
                    item.source_url,
                    item.source_title,
                    1 if item.verified else 0,
                    item.notes,
                    item.timestamp_marker,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def get_claims_for_script(script_id: int) -> List[ClaimLedgerItem]:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM claim_ledger WHERE script_id = ? ORDER BY id ASC",
                (script_id,),
            )
            items = []
            for row in cursor.fetchall():
                d = dict(row)
                d["verified"] = bool(d["verified"])
                items.append(ClaimLedgerItem(**d))
            return items


class StoryboardRepository:
    @staticmethod
    def add_scene(scene: StoryboardScene) -> int:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO storyboards (
                    script_id, scene_order, scene_title, scene_type, duration_sec,
                    narration_text, visual_prompt, visual_type, asset_id, on_screen_text
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scene.script_id,
                    scene.scene_order,
                    scene.scene_title,
                    scene.scene_type,
                    scene.duration_sec,
                    scene.narration_text,
                    scene.visual_prompt,
                    scene.visual_type,
                    scene.asset_id,
                    scene.on_screen_text,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def get_scenes_for_script(script_id: int) -> List[StoryboardScene]:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM storyboards WHERE script_id = ? ORDER BY scene_order ASC",
                (script_id,),
            )
            return [StoryboardScene(**dict(row)) for row in cursor.fetchall()]

    @staticmethod
    def clear_scenes_for_script(script_id: int) -> None:
        with get_db_cursor() as cursor:
            cursor.execute("DELETE FROM storyboards WHERE script_id = ?", (script_id,))


class AssetRepository:
    @staticmethod
    def add_asset(asset: MediaAsset) -> int:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO assets (
                    name, asset_type, file_path, source_url, license_type,
                    commercial_allowed, attribution_required, attribution_text,
                    resolution, file_size_bytes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    asset.name,
                    asset.asset_type,
                    asset.file_path,
                    asset.source_url,
                    asset.license_type,
                    1 if asset.commercial_allowed else 0,
                    1 if asset.attribution_required else 0,
                    asset.attribution_text,
                    asset.resolution,
                    asset.file_size_bytes,
                    asset.created_at,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def list_assets(asset_type: Optional[str] = None) -> List[MediaAsset]:
        with get_db_cursor() as cursor:
            if asset_type:
                cursor.execute(
                    "SELECT * FROM assets WHERE asset_type = ? ORDER BY id DESC",
                    (asset_type,),
                )
            else:
                cursor.execute("SELECT * FROM assets ORDER BY id DESC")
            items = []
            for row in cursor.fetchall():
                d = dict(row)
                d["commercial_allowed"] = bool(d["commercial_allowed"])
                d["attribution_required"] = bool(d["attribution_required"])
                items.append(MediaAsset(**d))
            return items

    @staticmethod
    def get_asset(asset_id: int) -> Optional[MediaAsset]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM assets WHERE id = ?", (asset_id,))
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d["commercial_allowed"] = bool(d["commercial_allowed"])
                d["attribution_required"] = bool(d["attribution_required"])
                return MediaAsset(**d)
            return None


class VoiceoverRepository:
    @staticmethod
    def add_voiceover(vo: Voiceover) -> int:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO voiceovers (script_id, engine, voice_id, audio_path, duration_sec, sample_rate, status, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    vo.script_id,
                    vo.engine,
                    vo.voice_id,
                    vo.audio_path,
                    vo.duration_sec,
                    vo.sample_rate,
                    vo.status,
                    vo.created_at,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def get_latest_voiceover(script_id: int) -> Optional[Voiceover]:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM voiceovers WHERE script_id = ? ORDER BY id DESC LIMIT 1",
                (script_id,),
            )
            row = cursor.fetchone()
            return Voiceover(**dict(row)) if row else None


class RenderJobRepository:
    @staticmethod
    def create_job(job: RenderJob) -> int:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO render_jobs (script_id, output_path, resolution, fps, status, progress_pct, render_time_sec, error_message, created_at, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.script_id,
                    job.output_path,
                    job.resolution,
                    job.fps,
                    job.status,
                    job.progress_pct,
                    job.render_time_sec,
                    job.error_message,
                    job.created_at,
                    job.completed_at,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def update_job_status(job_id: int, status: str, progress_pct: int = 100, error_message: str = "", render_time: float = 0.0) -> None:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                UPDATE render_jobs SET
                    status = ?, progress_pct = ?, error_message = ?,
                    render_time_sec = ?, completed_at = datetime('now')
                WHERE id = ?
                """,
                (status, progress_pct, error_message, render_time, job_id),
            )

    @staticmethod
    def list_jobs() -> List[RenderJob]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM render_jobs ORDER BY id DESC")
            return [RenderJob(**dict(row)) for row in cursor.fetchall()]


class VideoExportRepository:
    @staticmethod
    def add_export(export: VideoExport) -> int:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO video_exports (
                    render_job_id, script_id, file_path, thumbnail_path, duration_sec,
                    resolution, file_size_bytes, content_hash, verified, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    export.render_job_id,
                    export.script_id,
                    export.file_path,
                    export.thumbnail_path,
                    export.duration_sec,
                    export.resolution,
                    export.file_size_bytes,
                    export.content_hash,
                    1 if export.verified else 0,
                    export.created_at,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def get_latest_export(script_id: int) -> Optional[VideoExport]:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM video_exports WHERE script_id = ? ORDER BY id DESC LIMIT 1",
                (script_id,),
            )
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d["verified"] = bool(d["verified"])
                return VideoExport(**d)
            return None

    @staticmethod
    def list_exports() -> List[VideoExport]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM video_exports ORDER BY id DESC")
            items = []
            for row in cursor.fetchall():
                d = dict(row)
                d["verified"] = bool(d["verified"])
                items.append(VideoExport(**d))
            return items


class ApprovalRepository:
    @staticmethod
    def record_approval(approval: HumanApproval) -> int:
        with get_db_cursor() as cursor:
            # First invalidate any prior approvals for this script
            cursor.execute(
                "UPDATE approvals SET is_valid = 0 WHERE script_id = ?",
                (approval.script_id,),
            )
            cursor.execute(
                """
                INSERT INTO approvals (script_id, video_export_id, content_hash, approved_by, approved_at, approval_notes, is_valid)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    approval.script_id,
                    approval.video_export_id,
                    approval.content_hash,
                    approval.approved_by,
                    approval.approved_at,
                    approval.approval_notes,
                    1 if approval.is_valid else 0,
                ),
            )
            # Update script status to approved
            cursor.execute(
                "UPDATE scripts SET status = 'approved', updated_at = datetime('now') WHERE id = ?",
                (approval.script_id,),
            )
            return cursor.lastrowid

    @staticmethod
    def get_active_approval(script_id: int) -> Optional[HumanApproval]:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM approvals WHERE script_id = ? AND is_valid = 1 ORDER BY id DESC LIMIT 1",
                (script_id,),
            )
            row = cursor.fetchone()
            if row:
                d = dict(row)
                d["is_valid"] = bool(d["is_valid"])
                return HumanApproval(**d)
            return None

    @staticmethod
    def is_script_approved(script_id: int, current_content_hash: str) -> bool:
        active = ApprovalRepository.get_active_approval(script_id)
        if not active:
            return False
        return active.content_hash == current_content_hash and active.is_valid


class YouTubeUploadRepository:
    @staticmethod
    def record_upload(upload: YouTubeUpload) -> int:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO youtube_uploads (
                    video_export_id, youtube_video_id, title, description, tags,
                    privacy_status, scheduled_publish_at, uploaded_at, quota_used, response_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    upload.video_export_id,
                    upload.youtube_video_id,
                    upload.title,
                    upload.description,
                    upload.tags,
                    upload.privacy_status,
                    upload.scheduled_publish_at,
                    upload.uploaded_at,
                    upload.quota_used,
                    upload.response_json,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def list_uploads() -> List[YouTubeUpload]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM youtube_uploads ORDER BY id DESC")
            return [YouTubeUpload(**dict(row)) for row in cursor.fetchall()]


class CostRepository:
    @staticmethod
    def record_cost(service_name: str, operation: str, cost_inr: float, notes: str = "") -> int:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO cost_records (service_name, operation, cost_inr, within_budget, notes, created_at)
                VALUES (?, ?, ?, ?, ?, datetime('now'))
                """,
                (service_name, operation, cost_inr, 1, notes),
            )
            return cursor.lastrowid

    @staticmethod
    def get_monthly_spend() -> float:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT SUM(cost_inr) FROM cost_records WHERE created_at >= date('now', 'start of month')"
            )
            row = cursor.fetchone()
            return float(row[0] or 0.0)

    @staticmethod
    def list_costs() -> List[CostRecord]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM cost_records ORDER BY id DESC LIMIT 100")
            items = []
            for row in cursor.fetchall():
                d = dict(row)
                d["within_budget"] = bool(d["within_budget"])
                items.append(CostRecord(**d))
            return items


class AnalyticsRepository:
    @staticmethod
    def add_snapshot(snapshot: AnalyticsSnapshot) -> int:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO analytics_snapshots (
                    date, channel_views, watch_time_hours, impressions, ctr_pct,
                    avg_view_duration_sec, avg_pct_viewed, subscribers_gained,
                    estimated_revenue_usd, estimated_revenue_inr
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    snapshot.date,
                    snapshot.channel_views,
                    snapshot.watch_time_hours,
                    snapshot.impressions,
                    snapshot.ctr_pct,
                    snapshot.avg_view_duration_sec,
                    snapshot.avg_pct_viewed,
                    snapshot.subscribers_gained,
                    snapshot.estimated_revenue_usd,
                    snapshot.estimated_revenue_inr,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def list_snapshots() -> List[AnalyticsSnapshot]:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM analytics_snapshots ORDER BY date ASC")
            return [AnalyticsSnapshot(**dict(row)) for row in cursor.fetchall()]


class WorkflowRepository:
    @staticmethod
    def log_run(run: WorkflowRun) -> int:
        with get_db_cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO workflow_runs (workflow_name, status, summary, duration_sec, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    run.workflow_name,
                    run.status,
                    run.summary,
                    run.duration_sec,
                    run.created_at,
                ),
            )
            return cursor.lastrowid

    @staticmethod
    def list_runs(limit: int = 50) -> List[WorkflowRun]:
        with get_db_cursor() as cursor:
            cursor.execute(
                "SELECT * FROM workflow_runs ORDER BY id DESC LIMIT ?", (limit,)
            )
            return [WorkflowRun(**dict(row)) for row in cursor.fetchall()]
