import json
import os
import sys
from pathlib import Path

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

# Add src to path
sys.path.insert(0, os.path.abspath("."))

from src.youtube.uploader import YouTubePublisher
from src.workflows.daily_shorts_pipeline import VIRAL_SHORTS_QUEUE, DailyShortsPipeline

def upload_staging():
    print("=======================================================", flush=True)
    print("📤 UPLOADING MAGLEV MASTER TO YOUTUBE (PRIVATE STAGING)", flush=True)
    print("=======================================================", flush=True)
    
    topic = next((t for t in VIRAL_SHORTS_QUEUE if t["id"] == "japan_maglev_speed"), None)
    if not topic:
        print("Error: Topic not found!", flush=True)
        return
        
    master_path = os.path.abspath("exports/japan_maglev_speed_master_1080p.mp4")
    if not os.path.exists(master_path):
        print(f"Error: Master file not found at {master_path}", flush=True)
        return
        
    print(f"File to upload: {master_path} ({os.path.getsize(master_path)} bytes)")
    print(f"Title: {topic['title']}")
    print(f"Privacy: private (staging for creator review)")
    
    res = YouTubePublisher.upload_short_file(
        file_path=master_path,
        title=topic["title"],
        description=topic["description"],
        tags=topic["tags"],
        privacy_status="private"
    )
    
    print("\nUpload Result:")
    print(json.dumps(res, indent=2))
    
    if res.get("success"):
        video_id = res.get("youtube_video_id")
        video_url = res.get("url")
        print(f"\n🎉 Successfully uploaded to YouTube as PRIVATE!")
        print(f"Video URL: {video_url}")
        
        # Record in log
        DailyShortsPipeline.record_published_id("japan_maglev_speed", video_url)
        print(f"Recorded 'japan_maglev_speed' in data/daily_shorts_log.json")

if __name__ == "__main__":
    upload_staging()
