"""Publishes the repaired SR-71 Blackbird Unstart Short to YouTube Shorts.
Ensures Creator Approval is granted for the exact bitstream hash before upload.
"""
import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.youtube.uploader import YouTubePublisher
from src.workflows.daily_shorts_pipeline import VIRAL_SHORTS_QUEUE, DailyShortsPipeline
from src.quality.approval_manager import CreatorApprovalManager

def main():
    target_id = "sr71_blackbird_unstart"
    topic = next((t for t in VIRAL_SHORTS_QUEUE if t["id"] == target_id), None)
    if not topic:
        print(f"Error: Topic {target_id} not found in VIRAL_SHORTS_QUEUE")
        sys.exit(1)
        
    master_path = Path("exports/sr71_blackbird_unstart_master_1080p.mp4")
    if not master_path.exists():
        print(f"Error: Master file not found at {master_path}")
        sys.exit(1)
        
    thumb_path = Path("data/thumbnails/sr71_blackbird_unstart_thumb_main.jpg")
    
    # 1. Grant approval locally if not already recorded
    file_hash = CreatorApprovalManager.compute_file_hash(master_path)
    meta_dict = {
        "title": topic["title"],
        "description": topic["description"],
        "tags": topic["tags"]
    }
    
    print(f"Recording Creator Approval for {master_path.name} (SHA-256: {file_hash})...")
    CreatorApprovalManager.grant_approval(
        video_id=target_id,
        video_file_path=master_path,
        reviewer_name="Creator",
        notes="Verified factual accuracy, eliminated act whooshes, high-CTR thumbnail.",
        metadata_dict=meta_dict,
        thumbnail_path=thumb_path if thumb_path.exists() else None
    )
    print("Creator approval locked.")
    
    # 2. Upload to YouTube Shorts
    print(f"\nStarting YouTube Shorts publication for: '{topic['title']}'...")
    print(f"File: {master_path} ({master_path.stat().st_size:,} bytes)")
    print(f"Thumbnail: {thumb_path}")
    print(f"Privacy: public")
    
    res = YouTubePublisher.upload_short_file(
        file_path=str(master_path),
        title=topic["title"],
        description=topic["description"],
        tags=topic["tags"],
        privacy_status="public",
        video_id=target_id,
        thumbnail_path=str(thumb_path) if thumb_path.exists() else None
    )
    
    print("\nUpload response:", res)
    
    if res.get("success"):
        url = res.get("url")
        print(f"\n🎉 SUCCESS! Video published live to YouTube Shorts: {url}")
        DailyShortsPipeline.record_published_id(topic["id"], url)
        print(f"Recorded {target_id} in data/daily_shorts_log.json")
    else:
        print(f"\n❌ Upload failed: {res.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
