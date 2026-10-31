"""Fetches all published videos directly from the YouTube channel
and synchronizes data/daily_shorts_log.json to prevent ANY duplicates.
"""
import json
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.youtube.oauth import YouTubeAuthManager
from src.workflows.daily_shorts_pipeline import VIRAL_SHORTS_QUEUE
from googleapiclient.discovery import build

def main():
    creds = YouTubeAuthManager.get_credentials()
    if not creds:
        print("Error: Could not load YouTube credentials.")
        return

    youtube = build("youtube", "v3", credentials=creds)
    ch_res = youtube.channels().list(mine=True, part="contentDetails").execute()
    uploads_id = ch_res["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

    pl_res = youtube.playlistItems().list(playlistId=uploads_id, part="snippet", maxResults=50).execute()
    items = pl_res.get("items", [])
    print(f"Total live videos on channel: {len(items)}\n")

    live_videos = []
    for it in items:
        vid_id = it["snippet"]["resourceId"]["videoId"]
        title = it["snippet"]["title"]
        pub_at = it["snippet"]["publishedAt"]
        print(f"[{vid_id}] {title} ({pub_at})")
        live_videos.append({
            "video_id": vid_id,
            "title": title,
            "published_at": pub_at,
            "url": f"https://youtube.com/shorts/{vid_id}"
        })

    # Read current log
    log_path = Path("data/daily_shorts_log.json")
    current_log = []
    if log_path.exists():
        with open(log_path, "r", encoding="utf-8") as f:
            current_log = json.load(f)

    # Match each live video with topic in VIRAL_SHORTS_QUEUE
    synced_log = []
    matched_topic_ids = set()

    for lv in live_videos:
        vid_title = lv["title"].lower()
        matched_id = None
        for topic in VIRAL_SHORTS_QUEUE:
            t_title = topic["title"].lower().replace("#shorts", "").strip()
            # check substring match or keywords
            t_id = topic["id"]
            if t_id in vid_title or any(word in vid_title for word in t_id.split("_")):
                matched_id = topic["id"]
                break
            if t_title[:20] in vid_title:
                matched_id = topic["id"]
                break

        # Specific keyword heuristics
        if not matched_id:
            if "taipei" in vid_title or "damper" in vid_title or "660-ton" in vid_title:
                matched_id = "taipei_101_damper"
            elif "blackbird" in vid_title or "sr-71" in vid_title or "choked" in vid_title or "unstart" in vid_title:
                matched_id = "sr71_blackbird_unstart"
            elif "three gorges" in vid_title or "monster dam" in vid_title:
                matched_id = "three_gorges_rotation"
            elif "singapore" in vid_title or "sand" in vid_title:
                matched_id = "singapore_sand_empire"
            elif "concorde" in vid_title or "supersonic" in vid_title:
                matched_id = "concorde_sonic_tragedy"
            elif "maglev" in vid_title or "375 mph" in vid_title:
                matched_id = "japan_maglev_speed"
            elif "dubai" in vid_title or "sinking islands" in vid_title:
                matched_id = "dubai_sinking_islands"
            elif "suez" in vid_title or "ghost fleet" in vid_title:
                matched_id = "suez_canal_ghost_fleet"
            elif "panama" in vid_title or "80,000-ton" in vid_title:
                matched_id = "panama_canal_gravity_secret"

        print(f"Matched live video '{lv['title']}' -> topic_id: '{matched_id}'")
        matched_topic_ids.add(matched_id)
        synced_log.append({
            "id": matched_id or lv["video_id"],
            "title": lv["title"],
            "youtube_url": lv["url"],
            "timestamp": lv["published_at"]
        })

    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(synced_log, f, indent=2)

    print(f"\nSynced {len(synced_log)} videos into {log_path}!")
    print(f"Published topic IDs: {matched_topic_ids}")

if __name__ == "__main__":
    main()
