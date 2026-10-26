"""Google Flow Credit and Generation Tracker.
Monitors Veo video generation credits, tracks usage per video project,
and feeds real-time status to the Streamlit Dashboard.
"""
import json
from pathlib import Path
from datetime import datetime

CREDITS_FILE = Path("data/flow_credits.json")

class FlowCreditTracker:
    DEFAULT_INITIAL_CREDITS = 500
    DEFAULT_CREDIT_PER_CLIP = 10

    @classmethod
    def _load_data(cls) -> dict:
        if not CREDITS_FILE.exists():
            data = {
                "initial_credits": cls.DEFAULT_INITIAL_CREDITS,
                "credits_used": 30,  # 3 clips generated today (Shot 1, Shot 2, Shot 3)
                "credits_remaining": cls.DEFAULT_INITIAL_CREDITS - 30,
                "last_updated": datetime.utcnow().isoformat(),
                "history": [
                    {
                        "clip_name": "Shot 1 - Cargo ship transits canal lock",
                        "credits": 10,
                        "timestamp": datetime.utcnow().isoformat(),
                        "notes": "Scene 1: Hook and staircase of water"
                    },
                    {
                        "clip_name": "Shot 2 - Container ship descending Panama lock",
                        "credits": 10,
                        "timestamp": datetime.utcnow().isoformat(),
                        "notes": "Scene 2: Hydraulic lock gates and gravity drain"
                    },
                    {
                        "clip_name": "Shot 3 - Container ships stranded on drought lake",
                        "credits": 10,
                        "timestamp": datetime.utcnow().isoformat(),
                        "notes": "Scene 3: Lake Gatun drought and 52M gallon flush"
                    }
                ]
            }
            cls._save_data(data)
            return data
            
        try:
            with open(CREDITS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "initial_credits": cls.DEFAULT_INITIAL_CREDITS,
                "credits_used": 30,
                "credits_remaining": cls.DEFAULT_INITIAL_CREDITS - 30,
                "last_updated": datetime.utcnow().isoformat(),
                "history": []
            }

    @classmethod
    def _save_data(cls, data: dict):
        CREDITS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CREDITS_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def get_status(cls) -> dict:
        data = cls._load_data()
        rem = data.get("credits_remaining", 0)
        est_clips = max(0, rem // cls.DEFAULT_CREDIT_PER_CLIP)
        est_videos = max(0, rem // (cls.DEFAULT_CREDIT_PER_CLIP * 6)) # ~6 shots per 60s video
        return {
            "initial_credits": data.get("initial_credits", cls.DEFAULT_INITIAL_CREDITS),
            "credits_used": data.get("credits_used", 0),
            "credits_remaining": rem,
            "estimated_clips_left": est_clips,
            "estimated_60s_videos_left": est_videos,
            "last_updated": data.get("last_updated"),
            "history": data.get("history", [])
        }

    @classmethod
    def get_credits(cls) -> dict:
        """Alias for get_status()"""
        return cls.get_status()

    @classmethod
    def set_balance(cls, current_balance: int):
        """Calibrate credit balance directly from user's live flow.google.com account."""
        data = cls._load_data()
        used = data.get("credits_used", 0)
        data["credits_remaining"] = current_balance
        data["initial_credits"] = current_balance + used
        data["last_updated"] = datetime.utcnow().isoformat()
        cls._save_data(data)

    @classmethod
    def record_generation(cls, clip_name: str, credits_spent: int = 10, notes: str = ""):
        data = cls._load_data()
        data["credits_used"] = data.get("credits_used", 0) + credits_spent
        data["credits_remaining"] = max(0, data.get("initial_credits", 500) - data["credits_used"])
        data["last_updated"] = datetime.utcnow().isoformat()
        if "history" not in data:
            data["history"] = []
        data["history"].append({
            "clip_name": clip_name,
            "credits": credits_spent,
            "timestamp": datetime.utcnow().isoformat(),
            "notes": notes
        })
        cls._save_data(data)
        return data["credits_remaining"]

    @classmethod
    def set_actual_balance(cls, current_balance: int):
        data = cls._load_data()
        data["credits_remaining"] = current_balance
        data["credits_used"] = max(0, data.get("initial_credits", 500) - current_balance)
        data["last_updated"] = datetime.utcnow().isoformat()
        cls._save_data(data)
        return data
