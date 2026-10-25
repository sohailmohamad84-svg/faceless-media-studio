"""Delete old paused Suez Short and upload new seamlessly paced 34s Master to YouTube."""
import json
import sys
from pathlib import Path
from datetime import datetime

# Force UTF-8 stdout
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# Ensure project root in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from googleapiclient.discovery import build
from src.youtube.oauth import YouTubeAuthManager
from src.youtube.uploader import YouTubePublisher

OLD_VIDEO_ID = "NX2fEul0zvA"

def main():
    creds = YouTubeAuthManager.get_credentials()
    if not creds:
        print("[ERROR] No YouTube OAuth credentials found!")
        sys.exit(1)

    youtube = build("youtube", "v3", credentials=creds)

    # Step 1: Delete old video with pauses
    print(f"[DELETE] Deleting old video with pauses: {OLD_VIDEO_ID}...")
    try:
        youtube.videos().delete(id=OLD_VIDEO_ID).execute()
        print(f"[OK] Successfully deleted {OLD_VIDEO_ID} from YouTube.")
    except Exception as e:
        print(f"[WARN] Note on delete ({OLD_VIDEO_ID}): {e}")

    # Step 2: Upload new 34s seamless Short
    video_path = Path("exports/Suez_Canal_50s_Viral_Master_1080p.mp4")
    title = "The 24-Hour Ghost Fleet of the Suez Canal #shorts"
    description = (
        "How did one single rudder angle trap 400 cargo ships and freeze $10 billion in world trade daily? "
        "Discover the terrifying physics of the Suez Canal megajams.\n\n"
        "🚢 Like & Subscribe for daily high-retention engineering & business documentaries!\n\n"
        "#shorts #suezcanal #evergiven #engineering #megaprojects #maritime #history #logistics #facts"
    )
    tags = ["shorts", "suezcanal", "evergiven", "engineering", "megaprojects", "shipping", "documentary"]

    print(f"[UPLOAD] Uploading new seamlessly paced Short (34s) to YouTube...")
    result = YouTubePublisher.upload_short_file(
        file_path=str(video_path),
        title=title,
        description=description,
        tags=tags,
        privacy_status="public"
    )

    print("Result:", result)
    if result.get("success"):
        new_yt_id = result.get("youtube_video_id")
        short_url = f"https://youtube.com/shorts/{new_yt_id}"
        print(f"[SUCCESS] New seamlessly paced short is live at: {short_url}")

        # Update log
        log_file = Path("data/daily_shorts_log.json")
        entries = []
        if log_file.exists():
            try:
                with open(log_file, "r") as f:
                    entries = json.load(f)
            except Exception:
                entries = []

        # Filter out old suez entries
        entries = [e for e in entries if e.get("id") != "suez_canal_ghost_fleet"]

        entries.append({
            "id": "suez_canal_ghost_fleet",
            "title": title,
            "youtube_url": short_url,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        })

        with open(log_file, "w") as f:
            json.dump(entries, f, indent=2)

        print(f"[LOG] Updated {log_file}")
    else:
        print(f"[ERROR] Upload failed: {result.get('error')}")

if __name__ == "__main__":
    main()
