"""Comprehensive Automated Test Suite for Faceless Media Studio.
Tests central configuration, topic discovery scoring, claim ledger verification,
asset rights enforcement, thumbnail generation and dimensions, 12-gate quality audit,
cryptographic approval invalidation, and upload blocking.
"""
import hashlib
import json
import os
import shutil
import tempfile
from pathlib import Path
import pytest

from src.config.production_config import ProductionConfig
from src.research.topic_discovery import TopicDiscoveryEngine, CandidateTopic, TopicScore
from src.research.claim_auditor import ClaimLedger, ClaimEntry, ClaimType, VerificationStatus
from src.assets.asset_rights_checker import AssetRightsChecker, AssetManifestEntry, RightsStatus
from src.scripting.script_generator import ScriptGenerator
from src.thumbnails.thumbnail_generator import ThumbnailGenerator
from src.thumbnails.thumbnail_validator import ThumbnailValidator
from src.quality.approval_manager import CreatorApprovalManager
from src.quality.repair_loop import QualityRepairEngine


# --- 1. CONFIGURATION VALIDATION TESTS ---

def test_production_config_load_and_validate():
    """Verify production.yaml loads cleanly and validates against broadcast constraints."""
    cfg = ProductionConfig.load(force_reload=True)
    assert cfg is not None
    assert "channel" in cfg
    assert "video" in cfg
    assert "workflow" in cfg
    assert "integrations" in cfg

    # Constraints
    assert cfg["video"]["output_resolution"]["width"] == 1080
    assert cfg["video"]["output_resolution"]["height"] == 1920
    assert cfg["video"]["audio_true_peak_ceiling_dbtp"] <= -1.20
    assert cfg["workflow"]["default_upload_permission"] == "DENIED"
    assert cfg["workflow"]["creator_approval_required"] is True


def test_production_config_invalid_resolution_rejected():
    """Verify that an invalid resolution raises a ValueError."""
    bad_cfg = {
        "channel": {},
        "video": {"output_resolution": {"width": 1920, "height": 1080}},
        "workflow": {"default_upload_permission": "DENIED", "creator_approval_required": True},
        "integrations": {}
    }
    with pytest.raises(ValueError, match="Output resolution must be 1080x1920"):
        ProductionConfig.validate(bad_cfg)


# --- 2. TOPIC DISCOVERY & 100-POINT SCORING TESTS ---

def test_topic_discovery_100_point_scoring():
    """Verify that candidate topics are evaluated against the exact 100-point model."""
    res = TopicDiscoveryEngine.discover_daily_candidates()
    assert "recommended_topic" in res
    assert "alternative_topics" in res

    rec = res["recommended_topic"]
    assert rec is not None
    assert rec["total_score"] >= 90.0
    assert len(rec["key_claims_to_investigate"]) >= 3
    assert len(rec["preliminary_sources"]) >= 1

    # Check scoring breakdown components sum to total score
    scores = rec["scores"]
    summed = (
        scores["curiosity_hook"] +
        scores["evidence_strength"] +
        scores["visual_potential"] +
        scores["audience_appeal"] +
        scores["novelty_distinctiveness"] +
        scores["retention_narrative"] +
        scores["feasibility_assets"]
    )
    assert abs(summed - rec["total_score"]) < 0.1


# --- 3. CLAIM LEDGER & FACTUAL AUDIT TESTS ---

def test_claim_ledger_all_verified_passes():
    """Verify claim ledger passes when all material claims have authoritative sources."""
    ledger = ClaimLedger("test_topic", "Test Title")
    ledger.add_claim(ClaimEntry(
        claim_id="CLM-01",
        claim_text="The mass is 660 metric tons.",
        claim_type=ClaimType.NUMERICAL_MEASUREMENT.value,
        source_title="Taipei 101 Specifications",
        source_url="https://example.com/damper",
        publisher="Motioneering Inc.",
        publication_date="2024-01-01",
        access_date="2026-10-28",
        supporting_excerpt_or_notes="Verified in engineering blueprints.",
        confidence=1.0,
        verification_status=VerificationStatus.VERIFIED.value,
        script_location="Scene 1",
        is_material_numerical=True
    ))

    result = ledger.verify_all()
    assert result["passed"] is True
    assert result["factual_integrity_score"] == 100.0
    assert len(result["blocking_failures"]) == 0


def test_claim_ledger_unsupported_claim_blocks():
    """Verify that an unsupported material claim immediately blocks publication."""
    ledger = ClaimLedger("test_topic_fail", "Test Title")
    ledger.add_claim(ClaimEntry(
        claim_id="CLM-02",
        claim_text="The tower moves 10 meters in every storm.",
        claim_type=ClaimType.NUMERICAL_MEASUREMENT.value,
        source_title="Social Media Rumor",
        source_url="",
        publisher="Unknown",
        publication_date="",
        access_date="2026-10-28",
        supporting_excerpt_or_notes="Unsubstantiated claim.",
        confidence=0.2,
        verification_status=VerificationStatus.UNSUPPORTED.value,
        script_location="Scene 3",
        is_material_numerical=True
    ))

    result = ledger.verify_all()
    assert result["passed"] is False
    assert len(result["blocking_failures"]) == 1
    assert "UNSUPPORTED" in result["blocking_failures"][0]["reason"]


# --- 4. ASSET RIGHTS CHECKER TESTS ---

def test_asset_rights_public_domain_and_pexels_verified():
    """Verify that CC0, Public Domain, and Pexels assets achieve verified status."""
    assets = [
        AssetManifestEntry(
            asset_id="AST-01",
            original_title="Satellite Radar Map",
            original_url="https://nasa.gov/earth",
            creator_or_rights_holder="NASA JPL",
            source_platform="NASA Public Domain",
            download_url="https://nasa.gov/dl",
            license_name="US Government Work (Public Domain)",
            license_url="https://nasa.gov/license",
            commercial_use_permitted=True,
            attribution_required=False,
            modification_permitted=True,
            restrictions_or_exclusions="None",
            download_date="2026-10-28",
            local_file_path="data/assets/nasa.jpg",
            intended_scene="Scene 1",
            verification_status=""
        ),
        AssetManifestEntry(
            asset_id="AST-02",
            original_title="Drone Cityscape",
            original_url="https://pexels.com/video/123",
            creator_or_rights_holder="Pexels Contributor",
            source_platform="Pexels",
            download_url="https://pexels.com/dl",
            license_name="Pexels License",
            license_url="https://pexels.com/license",
            commercial_use_permitted=True,
            attribution_required=False,
            modification_permitted=True,
            restrictions_or_exclusions="None",
            download_date="2026-10-28",
            local_file_path="data/assets/city.mp4",
            intended_scene="Scene 2",
            verification_status=""
        )
    ]

    res = AssetRightsChecker.verify_manifest(assets)
    assert res["passed"] is True
    assert len(res["blocking_failures"]) == 0


def test_asset_rights_noncommercial_blocks():
    """Verify that a Non-Commercial (NC) restricted asset blocks publication."""
    assets = [
        AssetManifestEntry(
            asset_id="AST-FAIL",
            original_title="Proprietary Documentary Clip",
            original_url="https://example.com/clip",
            creator_or_rights_holder="Third Party Studio",
            source_platform="Vimeo",
            download_url="https://example.com/dl",
            license_name="Creative Commons CC-BY-NC (Non-Commercial)",
            license_url="https://creativecommons.org",
            commercial_use_permitted=False,
            attribution_required=True,
            modification_permitted=False,
            restrictions_or_exclusions="No commercial monetisation",
            download_date="2026-10-28",
            local_file_path="data/assets/nc.mp4",
            intended_scene="Scene 5",
            verification_status=""
        )
    ]

    res = AssetRightsChecker.verify_manifest(assets)
    assert res["passed"] is False
    assert len(res["blocking_failures"]) == 1


# --- 5. THUMBNAIL GENERATION & VALIDATION TESTS ---

def test_thumbnail_generation_and_validation(tmp_path):
    """Verify thumbnail generator creates exact 1080x1920 (9:16) and 1280x720 (16:9) files."""
    out_dir = tmp_path / "thumbnails"
    package = ThumbnailGenerator.generate_full_package(
        topic_id="test_damper",
        main_headline="THE 660-TON SPHERE",
        main_subtitle="THE SECRET INSIDE TAIPEI 101",
        alt_a_headline="HOW THIS DAMPER WORKS",
        alt_b_headline="SAVING A SKYSCRAPER",
        output_dir=out_dir
    )

    assert package["generated_count"] == 4
    for key, path_str in package.items():
        if key in ["topic_id", "generated_count"]:
            continue
        p = Path(path_str)
        assert p.exists()
        assert p.stat().st_size > 10_000

    val_res = ThumbnailValidator.validate_package(package)
    assert val_res["all_valid"] is True
    assert len(val_res["errors"]) == 0


# --- 6. CRYPTOGRAPHIC APPROVAL & PUBLISHING SAFETY TESTS ---

def test_creator_approval_hash_binding_and_invalidation(tmp_path, monkeypatch):
    """
    Verify Part 12:
    1. Unapproved file is blocked.
    2. Explicit approval binds to file hash.
    3. File bitstream modification invalidates approval immediately.
    """
    monkeypatch.setattr("src.quality.approval_manager.APPROVAL_STORE_PATH", tmp_path / "creator_approvals.json")
    test_video = tmp_path / "test_video_master.mp4"
    test_video.write_bytes(b"ORIGINAL_VIDEO_BITSTREAM_V1_CONTENT_DATA_123456789")

    # 1. Verify unapproved is denied
    auth_unapproved = CreatorApprovalManager.verify_upload_authorization("test_vid_01", test_video)
    assert auth_unapproved["authorized"] is False
    assert "UNAPPROVED VIDEO" in auth_unapproved["reason"]

    # 2. Grant approval
    rec = CreatorApprovalManager.grant_approval("test_vid_01", test_video, reviewer_name="Test Creator")
    assert rec["status"] == "CREATOR_APPROVED"

    # Verify authorization passes
    auth_approved = CreatorApprovalManager.verify_upload_authorization("test_vid_01", test_video)
    assert auth_approved["authorized"] is True

    # 3. Simulate re-render / bitstream modification
    test_video.write_bytes(b"MODIFIED_RERENDERED_BITSTREAM_V2_DATA_987654321")

    # Verify authorization is immediately invalidated due to hash mismatch
    auth_tampered = CreatorApprovalManager.verify_upload_authorization("test_vid_01", test_video)
    assert auth_tampered["authorized"] is False
    assert "HASH MISMATCH" in auth_tampered["reason"]


# --- 7. SCRIPT GENERATION & TIMING ESTIMATION TESTS ---

def test_script_timing_estimation():
    """Verify that speech timing estimation accounts for word count and punctuation pauses."""
    text = "Sitting across the Yangtze River is a concrete monster so heavy that it physically changed the rotation of planet Earth."
    dur = ScriptGenerator.estimate_speech_duration(text, speaking_rate=1.12)
    assert 6.0 <= dur <= 9.0


# --- 8. QUALITY REPAIR LOOP TESTS ---

def test_quality_repair_engine_diagnosis():
    """Verify that repair engine diagnoses true peak and bitrate failures accurately."""
    failures = [
        "GATE-06: Audio compliance failed (TP: -1.14 dBTP vs <= -1.20 dBTP).",
        "GATE-02: Video bitrate 8,200 kbps below minimum 9,000 kbps."
    ]
    metrics = {"true_peak_dbtp": -1.14, "bitrate_kbps": 8200}
    repairs = QualityRepairEngine.diagnose_and_suggest_repair(failures, metrics)

    assert len(repairs) == 2
    assert repairs[0]["action"] == "ADJUST_TRUE_PEAK_TARGET"
    assert repairs[1]["action"] == "INCREASE_ENCODING_BITRATE"
