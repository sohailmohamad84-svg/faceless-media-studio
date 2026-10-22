"""Automated test suite for Faceless Media Studio."""
import os
import tempfile
import pytest
from pathlib import Path
from config.settings import DEFAULT_VOICE_ID, get_ffmpeg_path
from src.database.connection import init_db
from src.database.models import (
    Topic,
    Script,
    StoryboardScene,
    MediaAsset,
    HumanApproval,
    VideoExport,
)
from src.database.repository import (
    TopicRepository,
    ScriptRepository,
    StoryboardRepository,
    AssetRepository,
    ApprovalRepository,
    VideoExportRepository,
    RenderJobRepository,
    CostRepository,
)
from src.research.scoring import calculate_topic_score
from src.research.discovery import TopicDiscoveryEngine
from src.scripting.generator import ScriptGenerator
from src.quality.editorial_qa import evaluate_script_quality
from src.quality.policy_checker import audit_youtube_compliance
from src.quality.media_validator import validate_media_file
from src.tts.voice_engine import VoiceEngine
from src.assets.chart_generator import ChartGenerator
from src.assets.thumbnail_designer import ThumbnailDesigner
from src.assets.license_tracker import LicenseTracker
from src.editing.ffmpeg_orchestrator import FFmpegOrchestrator
from src.youtube.uploader import YouTubePublisher, PublishingError
from src.analytics.revenue_calculator import calculate_revenue_projections
from src.workflows.cost_manager import CostManager, BudgetExceededError


@pytest.fixture(autouse=True)
def setup_test_environment(tmp_path, monkeypatch):
    """Set up temporary database for tests."""
    from src.database.connection import reset_db_connection
    reset_db_connection()
    db_file = tmp_path / "test_studio.db"
    monkeypatch.setattr("config.settings.DATABASE_PATH", db_file)
    init_db(db_file)
    yield
    reset_db_connection()


def test_database_initialization():
    """Verify database schema creation and default channel profile."""
    from src.database.repository import ChannelRepository
    channel = ChannelRepository.get_channel()
    assert channel.name == "Apex Enterprise"
    assert channel.currency == "INR"
    assert channel.monthly_budget_ceiling == 3000.0


def test_topic_scoring_and_normalization():
    """Verify topic scoring formula and normalization with missing values."""
    score = calculate_topic_score(
        demand=90.0,
        originality=85.0,
        evergreen=95.0,
        commercial=90.0,
        competition=80.0,
        source_quality=95.0,
        feasibility=90.0,
    )
    assert score["total_score"] >= 88.0
    assert score["grade"] in ["A+", "A"]

    # Test handling of None/missing inputs
    score_missing = calculate_topic_score(
        demand=None,
        originality=None,
        evergreen=None,
        commercial=None,
        competition=None,
        source_quality=None,
        feasibility=None,
    )
    assert score_missing["total_score"] == 50.0


def test_topic_discovery_seeding():
    """Verify seed topics are inserted into database."""
    seeded = TopicDiscoveryEngine.seed_initial_topics()
    assert seeded >= 5
    topics = TopicRepository.list_topics()
    assert len(topics) >= 5
    first = topics[0]
    assert "Costco" in first.title or first.total_score >= 80.0


def test_script_generation_and_claim_ledger():
    """Verify documentary script generator produces script, storyboard, and verified claims."""
    TopicDiscoveryEngine.seed_initial_topics()
    topic = TopicRepository.list_topics()[0]
    script, scenes, claims = ScriptGenerator.generate_full_production_package(topic)

    assert script.id is not None
    assert len(scenes) >= 4
    assert len(claims) >= 1
    assert script.word_count > 50
    assert script.content_hash != ""


def test_editorial_quality_gate():
    """Verify 12-point editorial scorecard evaluates hook, evidence, and readability."""
    TopicDiscoveryEngine.seed_initial_topics()
    topic = TopicRepository.list_topics()[0]
    script, scenes, claims = ScriptGenerator.generate_full_production_package(topic)

    qa = evaluate_script_quality(script, claims)
    assert qa["score_percentage"] >= 75.0
    assert "hook_strength" in qa["category_scores"]
    assert "factual_support" in qa["category_scores"]


def test_policy_and_ai_disclosure_checker():
    """Verify YouTube policy auditor enforces AI synthetic media disclosure."""
    TopicDiscoveryEngine.seed_initial_topics()
    topic = TopicRepository.list_topics()[0]
    script, scenes, claims = ScriptGenerator.generate_full_production_package(topic)

    audit = audit_youtube_compliance(script)
    assert audit["requires_ai_disclosure"] is True
    assert "neural voice" in audit["ai_disclosure_statement"].lower()


def test_budget_protection_circuit():
    """Verify spending circuit allows zero-cost operations and blocks costs over ceiling."""
    status = CostManager.get_spending_status()
    assert status["ceiling_inr"] == 3000.0

    # 1. Zero cost should always succeed
    assert CostManager.check_and_record_cost("Edge-TTS", "Voice synthesis", 0.0) is True

    # 2. Within budget should succeed
    assert CostManager.check_and_record_cost("Test Service", "Small charge", 100.0) is True

    # 3. Exceeding ceiling should raise BudgetExceededError
    with pytest.raises(BudgetExceededError):
        CostManager.check_and_record_cost("Expensive Cloud", "Large charge", 5000.0)


def test_asset_generation_procedural_charts(tmp_path):
    """Verify Matplotlib procedural chart generation."""
    chart_path = str(tmp_path / "test_markup_chart.png")
    out = ChartGenerator.generate_costco_markup_chart(chart_path)
    assert Path(out).exists()
    assert Path(out).stat().st_size > 5000


def test_thumbnail_designer(tmp_path):
    """Verify PIL YouTube thumbnail creation."""
    thumb_path = str(tmp_path / "test_thumbnail.jpg")
    out = ThumbnailDesigner.create_thumbnail(
        title_top="THE $1.50 HOT DOG",
        title_bottom="COSTCO'S SECRET ENGINE",
        badge_text="$1.50 FOREVER",
        output_path=thumb_path,
    )
    assert Path(out).exists()
    assert Path(out).stat().st_size > 10000


def test_human_approval_state_machine_and_invalidation(tmp_path):
    """Verify strict approval requirement and that script edits invalidate prior approval."""
    TopicDiscoveryEngine.seed_initial_topics()
    topic = TopicRepository.list_topics()[0]
    script, scenes, claims = ScriptGenerator.generate_full_production_package(topic)

    # Fake export
    fake_export_file = tmp_path / "fake_video.mp4"
    fake_export_file.write_bytes(b"0" * 20000)
    import hashlib
    content_hash = hashlib.sha256(fake_export_file.read_bytes()).hexdigest()

    # Create valid RenderJob for foreign key
    from src.database.models import RenderJob
    job = RenderJob(script_id=script.id, output_path=str(fake_export_file), status="completed")
    job_id = RenderJobRepository.create_job(job)

    export = VideoExport(
        render_job_id=job_id,
        script_id=script.id,
        file_path=str(fake_export_file),
        duration_sec=30.0,
        content_hash=content_hash,
        verified=True,
    )
    export_id = VideoExportRepository.add_export(export)
    export.id = export_id

    # 1. Unapproved video should be rejected by publisher
    with pytest.raises(PublishingError, match="UNAPPROVED VIDEO"):
        YouTubePublisher.verify_approval_gate(export_id)

    # 2. Grant approval
    approval = HumanApproval(
        script_id=script.id,
        video_export_id=export_id,
        content_hash=content_hash,
        approved_by="Creator",
        is_valid=True,
    )
    ApprovalRepository.record_approval(approval)

    # Approval verified
    verified_approval = YouTubePublisher.verify_approval_gate(export_id)
    assert verified_approval.is_valid is True

    # 3. Edit script -> MUST invalidate approval!
    script.body_text += " Added an unreviewed paragraph."
    ScriptRepository.update_script(script)

    with pytest.raises(PublishingError, match="(UNAPPROVED VIDEO|INVALID APPROVAL)"):
        YouTubePublisher.verify_approval_gate(export_id)


def test_revenue_projection_calculator():
    """Verify revenue model calculations and milestone projections."""
    proj = calculate_revenue_projections(
        monthly_views=100000,
        assumed_rpm_usd=14.0,
    )
    assert proj["adsense_usd"] == 1400.0
    assert proj["gross_inr"] > 100000.0  # ₹1.16 Lakh
    assert proj["milestones"]["views_needed_for_1_lakh_inr"] > 0
    assert proj["milestones"]["views_needed_for_5_lakh_inr"] > proj["milestones"]["views_needed_for_1_lakh_inr"]


def test_end_to_end_ffmpeg_assembly_and_validation(tmp_path):
    """Verify end-to-end multi-scene video assembly with FFmpeg and media validation."""
    # 0. Create test topic & script for foreign keys
    TopicDiscoveryEngine.seed_initial_topics()
    topic = TopicRepository.list_topics()[0]
    script = Script(topic_id=topic.id, title="FFmpeg Test", status="draft")
    script_id = ScriptRepository.add_script(script)

    # 1. Create 2 test slides
    slide1 = str(tmp_path / "scene1.png")
    slide2 = str(tmp_path / "scene2.png")
    ThumbnailDesigner.create_scene_slide("SCENE ONE", "Intro", slide1)
    ThumbnailDesigner.create_scene_slide("SCENE TWO", "Conclusion", slide2)

    # 2. Create short audio track via Edge-TTS (or fallback)
    audio_path = str(tmp_path / "narration.mp3")
    ve = VoiceEngine()
    ve.synthesize("Costco Wholesale Corporation. The $1.50 hot dog strategy.", audio_path)

    # 3. Assemble multiscene video
    scenes = [
        StoryboardScene(scene_order=1, scene_title="Scene 1", duration_sec=2.5, narration_text="Costco Wholesale Corporation."),
        StoryboardScene(scene_order=2, scene_title="Scene 2", duration_sec=2.5, narration_text="The $1.50 hot dog strategy."),
    ]
    output_mp4 = str(tmp_path / "test_multiscene.mp4")

    orchestrator = FFmpegOrchestrator()
    res = orchestrator.assemble_multiscene_video(
        script_id=script_id,
        scenes=scenes,
        scene_image_paths=[slide1, slide2],
        narration_audio_path=audio_path,
        output_mp4_path=output_mp4,
    )

    assert res["success"] is True
    assert Path(output_mp4).exists()
    assert res["duration_sec"] > 1.0
    assert res["resolution"] == "1920x1080"
    assert res["file_size_bytes"] > 10000

    # 4. Verify media validation
    validation = validate_media_file(output_mp4)
    assert validation["valid"] is True
    assert validation["has_video"] is True
    assert validation["has_audio"] is True
