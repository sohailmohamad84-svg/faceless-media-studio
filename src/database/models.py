"""Data models and schemas for Faceless Media Studio."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any


@dataclass
class Channel:
    id: Optional[int] = None
    name: str = "Apex Enterprise"
    handle: str = "@ApexEnterprise"
    target_niche: str = "Business Case Studies & Corporate Autopsies"
    editorial_promise: str = (
        "We dissect the balance sheets, boardroom blunders, and financial mechanics "
        "behind the world's most fascinating businesses."
    )
    currency: str = "INR"
    monthly_budget_ceiling: float = 3000.0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class Topic:
    id: Optional[int] = None
    title: str = ""
    angle: str = ""
    category_pillar: str = "Corporate Autopsies"
    primary_viewer_question: str = ""
    target_audience: str = "Entrepreneurs, Investors, Curious Professionals"
    evidence_summary: str = ""
    demand_score: float = 18.0
    originality_score: float = 15.0
    evergreen_score: float = 14.0
    commercial_score: float = 15.0
    competition_score: float = 10.0
    source_quality_score: float = 10.0
    feasibility_score: float = 10.0
    total_score: float = 92.0
    status: str = "backlog"  # backlog, selected, in_production, published, rejected
    why_this_topic: str = ""
    suggested_length_min: int = 12
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class Source:
    id: Optional[int] = None
    topic_id: int = 0
    title: str = ""
    url: str = ""
    publisher: str = ""
    source_type: str = "SEC 10-K Filing"
    excerpt: str = ""
    credibility_rating: int = 5
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class ClaimLedgerItem:
    id: Optional[int] = None
    script_id: int = 0
    claim_text: str = ""
    source_url: str = ""
    source_title: str = ""
    verified: bool = True
    notes: str = ""
    timestamp_marker: str = "00:00"


@dataclass
class Script:
    id: Optional[int] = None
    topic_id: int = 0
    version: str = "1.0"
    title: str = ""
    hook_text: str = ""
    promise_text: str = ""
    body_text: str = ""
    conclusion_text: str = ""
    call_to_action: str = ""
    word_count: int = 0
    target_duration_sec: int = 600
    content_hash: str = ""
    status: str = "draft"  # draft, in_review, approved, rejected
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class StoryboardScene:
    id: Optional[int] = None
    script_id: int = 0
    scene_order: int = 1
    scene_title: str = ""
    scene_type: str = "hook"  # hook, context, evidence, case_study, climax, conclusion
    duration_sec: float = 10.0
    narration_text: str = ""
    visual_prompt: str = ""
    visual_type: str = "title_card"  # title_card, chart, stock_photo, b_roll, infographic
    asset_id: Optional[int] = None
    on_screen_text: str = ""


@dataclass
class MediaAsset:
    id: Optional[int] = None
    name: str = ""
    asset_type: str = "chart"  # chart, stock_photo, title_card, b_roll, audio, thumbnail
    file_path: str = ""
    source_url: str = ""
    license_type: str = "procedural_matplotlib"  # cc0, pexels, pixabay, procedural_matplotlib, public_domain
    commercial_allowed: bool = True
    attribution_required: bool = False
    attribution_text: str = ""
    resolution: str = "1920x1080"
    file_size_bytes: int = 0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class Voiceover:
    id: Optional[int] = None
    script_id: int = 0
    engine: str = "edge_tts"
    voice_id: str = "en-US-ChristopherNeural"
    audio_path: str = ""
    duration_sec: float = 0.0
    sample_rate: int = 24000
    status: str = "ready"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class RenderJob:
    id: Optional[int] = None
    script_id: int = 0
    output_path: str = ""
    resolution: str = "1920x1080"
    fps: int = 30
    status: str = "queued"  # queued, rendering, completed, failed
    progress_pct: int = 0
    render_time_sec: float = 0.0
    error_message: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None


@dataclass
class VideoExport:
    id: Optional[int] = None
    render_job_id: int = 0
    script_id: int = 0
    file_path: str = ""
    thumbnail_path: str = ""
    duration_sec: float = 0.0
    resolution: str = "1920x1080"
    file_size_bytes: int = 0
    content_hash: str = ""
    verified: bool = False
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class HumanApproval:
    id: Optional[int] = None
    script_id: int = 0
    video_export_id: int = 0
    content_hash: str = ""
    approved_by: str = "Creator"
    approved_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    approval_notes: str = ""
    is_valid: bool = True


@dataclass
class YouTubeUpload:
    id: Optional[int] = None
    video_export_id: int = 0
    youtube_video_id: str = ""
    title: str = ""
    description: str = ""
    tags: str = ""
    privacy_status: str = "private"  # private, unlisted, public
    scheduled_publish_at: Optional[str] = None
    uploaded_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    quota_used: int = 1600
    response_json: str = ""


@dataclass
class AnalyticsSnapshot:
    id: Optional[int] = None
    date: str = field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d"))
    channel_views: int = 0
    watch_time_hours: float = 0.0
    impressions: int = 0
    ctr_pct: float = 0.0
    avg_view_duration_sec: float = 0.0
    avg_pct_viewed: float = 0.0
    subscribers_gained: int = 0
    estimated_revenue_usd: float = 0.0
    estimated_revenue_inr: float = 0.0


@dataclass
class CostRecord:
    id: Optional[int] = None
    service_name: str = ""
    operation: str = ""
    cost_inr: float = 0.0
    within_budget: bool = True
    notes: str = ""
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass
class WorkflowRun:
    id: Optional[int] = None
    workflow_name: str = ""
    status: str = "success"  # running, success, failed
    summary: str = ""
    duration_sec: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
