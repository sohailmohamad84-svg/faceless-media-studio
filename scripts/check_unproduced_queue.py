import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.workflows.daily_shorts_pipeline import VIRAL_SHORTS_QUEUE

def main():
    with open("data/daily_shorts_log.json", "r", encoding="utf-8") as f:
        log = json.load(f)

    published_ids = {entry["id"] for entry in log}
    print("=== PUBLISHED TOPICS ON YOUTUBE ===")
    for p in sorted(list(published_ids), key=str):
        print(f"  [PUBLISHED] {p}")

    unproduced = [t for t in VIRAL_SHORTS_QUEUE if t["id"] not in published_ids]
    print(f"\n=== TRUE UNPRODUCED QUEUE ({len(unproduced)} REMAINING) ===")
    for i, t in enumerate(unproduced, 1):
        print(f"{i}. [{t.get('category', 'General')}] {t['id']} -> \"{t['title']}\"")

if __name__ == "__main__":
    main()
