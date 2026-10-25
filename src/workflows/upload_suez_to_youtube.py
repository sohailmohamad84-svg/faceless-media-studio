"""Upload Rebuilt Suez Canal Short to YouTube Shorts."""
import json
import sys
from pathlib import Path
from datetime import datetime

# Ensure project root in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.youtube.uploader import YouTubePublisher

def upload_short():
    video_path = Path("exports/Suez_Canal_50s_Viral_Master_1080p.mp4")
    if not video_path.exists():
        video_path = Path("data/showcase/Suez_Canal_50s_Viral_Master_1080p.mp4")

    title = "The 24-Hour Ghost Fleet of the Suez Canal #shorts"
    description = (
        "How did one single rudder angle trap 400 cargo ships and freeze $10 billion in world trade daily? "
        "Discover the terrifying physics of the Suez Canal megajams.\n\n"
        "🚢 Like & Subscribe for daily high-retention engineering & business documentaries!\n\n"
        "#shorts #suezcanal #evergiven #engineering #megaprojects #maritime #history #logistics #facts"
    )
    tags = ["shorts", "suezcanal", "evergiven", "engineering", "megaprojects", "shipping", "documentary"]

    print(f"Uploading {video_path.name} to YouTube Shorts (Public)...")
    result = YouTubePublisher.upload_short_file(
        file_path=str(video_path),
        title=title,
        description=description,
        tags=tags,
        privacy_status="public"
    )

    print("Result:", result)
    if result.get("success"):
        yt_id = result.get("youtube_video_id")
        short_url = f"https://youtube.com/shorts/{yt_id}"
        print(f"SUCCESS! Short is live at: {short_url}")

        # Update log
        log_file = Path("data/daily_shorts_log.json")
        entries = []
        if log_file.exists():
            try:
                with open(log_file, "r") as f:
                    entries = json.load(f)
            except Exception:
                entries = []

        entries.append({
            "id": "suez_canal_ghost_fleet",
            "title": title,
            "youtube_url": short_url,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

        with open(log_file, "w") as f:
            json.dump(entries, f, indent=2)

        print(f"Updated {log_file}")
    else:
        print("Upload failed:", result.get("error"))

if __name__ == "__main__":
    upload_short()
