"""Script to re-master Taipei 101 Short with stereo audio and updated factual narration,
followed by full 12-gate evaluation and extraction of 8 proof frames.
"""
import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, os.path.abspath("."))

from src.editing.flow_master_engine import FlowMasterEngine
from src.quality.publication_gate import PublicationGate
from src.research.claim_auditor import ClaimLedger, ClaimEntry
from src.assets.asset_rights_checker import AssetManifestEntry
from src.workflows.daily_shorts_pipeline import VIRAL_SHORTS_QUEUE

TOPIC_ID = "taipei_101_damper"
ARTIFACT_DIR = Path(r"C:\Users\Sohail\.gemini\antigravity\brain\eb4bd0b7-d463-4e01-b351-a971179e01ed")

async def remaster():
    topic = next((t for t in VIRAL_SHORTS_QUEUE if t["id"] == TOPIC_ID), None)
    if not topic:
        print("Error: Topic not found in queue!")
        return

    out_filename = "taipei_101_damper_master_1080p.mp4"
    print("=======================================================", flush=True)
    print(f"RE-MASTERING BROADCAST SHORT: {topic['title']}", flush=True)
    print("=======================================================", flush=True)

    # 1. Build master video with stereo audio
    master_path = await FlowMasterEngine.build_master_video(
        scenes=topic["scenes"],
        output_filename=out_filename,
        ambient_sfx="tension_drone.wav"
    )
    print(f"\nMaster short generated at: {master_path} ({os.path.getsize(master_path):,} bytes)", flush=True)

    # 2. Load claim ledger
    ledger = ClaimLedger(TOPIC_ID, topic.get("title", ""))
    cl_path = Path("data/research/taipei_101_claim_ledger.json")
    if cl_path.exists():
        with open(cl_path, "r", encoding="utf-8") as f:
            cld = json.load(f)
            for c in cld.get("ledger", []):
                ledger.add_claim(ClaimEntry(
                    claim_id=c["claim_id"],
                    claim_text=c["claim_text"],
                    claim_type=c["claim_type"],
                    source_title=c["source_title"],
                    source_url=c["source_url"],
                    publisher=c["publisher"],
                    publication_date=c["publication_date"],
                    access_date=c.get("access_date", "2026-10-28"),
                    supporting_excerpt_or_notes=c.get("supporting_excerpt_or_notes", ""),
                    confidence=c.get("confidence", 1.0),
                    verification_status=c.get("verification_status", "VERIFIED"),
                    script_location=c.get("script_location", "Scene 1"),
                    is_material_numerical=c.get("is_material_numerical", True)
                ))

    # 3. Load asset manifest
    manifest = []
    am_path = Path("data/assets_manifest/taipei_101_assets_manifest.json")
    if am_path.exists():
        with open(am_path, "r", encoding="utf-8") as f:
            am_data = json.load(f)
            for item in am_data.get("manifest", []):
                manifest.append(AssetManifestEntry(**item))

    # 4. Thumbnail package
    thumbs = {
        "main_vertical": "data/thumbnails/taipei_101_damper_thumb_main.jpg",
        "alt_a_vertical": "data/thumbnails/taipei_101_damper_thumb_alt_a.jpg",
        "alt_b_vertical": "data/thumbnails/taipei_101_damper_thumb_alt_b.jpg",
        "promotional_landscape": "data/thumbnails/taipei_101_damper_thumb_promo_16x9.jpg"
    }

    # 5. Evaluate all 12 publication gates
    print("\n=======================================================", flush=True)
    print("RUNNING COMPREHENSIVE 12-GATE PUBLICATION AUDIT", flush=True)
    print("=======================================================", flush=True)
    eval_result = PublicationGate.evaluate_all_12_gates(
        video_path=master_path,
        claim_ledger=ledger,
        asset_manifest=manifest,
        thumbnail_package=thumbs,
        topic_metadata=topic
    )

    score = eval_result.get("score", 0)
    status = eval_result.get("status", "QC_PENDING")
    file_hash = eval_result.get("file_sha256", "")
    print(f"\nFinal Score: {score}/100 | Status: {status}")
    print(f"File SHA-256: {file_hash}")
    print(f"Ready for Review: {eval_result.get('ready_for_review')}")
    if eval_result.get("blocking_failures"):
        print("\nBlocking Failures:", eval_result["blocking_failures"])

    print("\n12-Gate Breakdown:")
    for g, d in eval_result.get("gates", {}).items():
        st = "[PASS]" if d.get("passed") else "[FAIL]"
        print(f"  {st} {g}: {d.get('details', d.get('metrics', ''))}")

    # 6. Extract 8 proof frames into artifact directory
    print("\nExtracting 8 Act Proof Frames...", flush=True)
    duration = eval_result.get("gates", {}).get("GATE-02_TECHNICAL_COMPLIANCE", {}).get("metrics", {}).get("duration_seconds", 60.0)
    step = duration / 8.0

    for act_idx in range(1, 9):
        sample_time = min(duration - 0.5, (act_idx - 1) * step + (step * 0.45))
        frame_path = ARTIFACT_DIR / f"taipei_act_{act_idx}_proof.jpg"
        cmd = [
            "ffmpeg", "-y",
            "-ss", f"{sample_time:.2f}",
            "-i", str(master_path),
            "-vframes", "1",
            str(frame_path)
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"  Act {act_idx} frame at {sample_time:.1f}s -> {frame_path.name}")

    # 7. Save machine report to data/taipei_101_qa_report.json
    report_path = Path("data/taipei_101_qa_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(eval_result, f, indent=2)
    print(f"\nSaved machine QA report to {report_path}")

if __name__ == "__main__":
    asyncio.run(remaster())
