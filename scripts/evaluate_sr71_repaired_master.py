"""Evaluate the repaired SR-71 Blackbird Unstart Master Short across all 14 Quality Gates.
Generates comprehensive report and saves to data/sr71_blackbird_unstart_qa_report.json.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.workflows.daily_shorts_pipeline import VIRAL_SHORTS_QUEUE
from src.quality.publication_gate import PublicationGate

def main():
    video_path = Path("exports/sr71_blackbird_unstart_master_1080p.mp4")
    topic = next((t for t in VIRAL_SHORTS_QUEUE if t['id'] == 'sr71_blackbird_unstart'), None)
    
    print(f"Auditing repaired master video: {video_path}")
    print(f"File size: {video_path.stat().st_size:,} bytes")
    
    # Run all 14 Gates
    result = PublicationGate.evaluate_all_14_gates(
        video_path=video_path,
        topic_metadata=topic
    )
    
    qa_path = Path(f"data/{topic['id']}_qa_report.json")
    with open(qa_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
        
    print(f"\nSaved updated QA Report to: {qa_path}")
    print(f"File SHA-256: {result['file_sha256']}")
    print(f"Overall Technical Score: {result['score']}/100")
    print(f"Publication Status: {result['status']}")
    print(f"Overall Pass (Gate 14 Creator Approval): {result['overall_pass']}")
    print(f"Ready for Creator Review: {result['ready_for_review']}")
    print(f"Blocking Failures: {result['blocking_failures']}")
    
    print("\n--- 14-GATE EVALUATION BREAKDOWN ---")
    core_14_gates = [
        "GATE-01_FILE_INTEGRITY_DECODING",
        "GATE-02_CONTAINER_STANDARDS",
        "GATE-03_BITRATE_COMPRESSION_QUALITY",
        "GATE-04_AUDIO_LOUDNESS_INTELLIGIBILITY",
        "GATE-05_NARRATION_SUBTITLE_ALIGNMENT",
        "GATE-06_FACTUAL_ACCURACY_TRACEABILITY",
        "GATE-07_VISUAL_NARRATIVE_ALIGNMENT",
        "GATE-08_ENGINEERING_HISTORICAL_ACCURACY",
        "GATE-09_VISUAL_CONTINUITY_DISCONTINUITIES",
        "GATE-10_COPYRIGHT_ASSET_LICENSES",
        "GATE-11_THUMBNAIL_ACCURACY_READABILITY",
        "GATE-12_METADATA_ACCURACY",
        "GATE-13_CRYPTOGRAPHIC_HASH_IDENTITY",
        "GATE-14_CREATOR_APPROVAL_GATE"
    ]
    for g_id in core_14_gates:
        g_info = result["gates"].get(g_id, {})
        status_str = "PASS" if g_info.get("passed") else "BLOCKED / FAIL"
        details = g_info.get("details", "")
        print(f"[{status_str}] {g_id}: {details}")

if __name__ == "__main__":
    main()
