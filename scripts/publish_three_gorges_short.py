import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, os.path.abspath("."))

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from src.youtube.uploader import YouTubePublisher
from src.workflows.daily_shorts_pipeline import VIRAL_SHORTS_QUEUE, DailyShortsPipeline

def main():
    target_id = "three_gorges_rotation"
    topic = next((t for t in VIRAL_SHORTS_QUEUE if t["id"] == target_id), None)
    if not topic:
        print(f"Error: Topic {target_id} not found in VIRAL_SHORTS_QUEUE")
        sys.exit(1)
        
    master_path = Path("exports/three_gorges_rotation_master_1080p.mp4")
    if not master_path.exists():
        print(f"Error: Master file not found at {master_path}")
        sys.exit(1)
        
    print(f"Starting YouTube Shorts publication for: '{topic['title']}'...")
    print(f"File: {master_path} ({master_path.stat().st_size:,} bytes)")
    print(f"Privacy: public")
    
    res = YouTubePublisher.upload_short_file(
        file_path=str(master_path),
        title=topic["title"],
        description=topic["description"],
        tags=topic["tags"],
        privacy_status="public",
    )
    
    print("Upload response:", res)
    
    if res.get("success"):
        url = res.get("url")
        video_id = res.get("youtube_video_id")
        print(f"SUCCESS! Video published live to YouTube Shorts: {url}")
        DailyShortsPipeline.record_published_id(topic["id"], url)
        print(f"Recorded {target_id} in data/daily_shorts_log.json")
    else:
        print(f"Upload failed: {res.get('error')}")
        sys.exit(1)

if __name__ == "__main__":
    main()
