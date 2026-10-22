"""One-time interactive browser authorization for your YouTube channel."""
import sys
from pathlib import Path

# Add root directory to sys.path
root_dir = Path(__file__).resolve().parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from src.youtube.oauth import YouTubeAuthManager


def main():
    print("=" * 60)
    print("  CONNECTING YOUR YOUTUBE CHANNEL TO FACELESS MEDIA STUDIO")
    print("=" * 60)
    print("Opening Google OAuth consent page in your default browser...")
    print("Please select your Google account that owns your YouTube channel.")
    print("If you see an 'unverified app' warning, click 'Advanced' -> 'Go to Faceless Media Studio (unsafe)'.")
    print("-" * 60)

    res = YouTubeAuthManager.authenticate_channel()
    if res.get("success"):
        print("\n✅ SUCCESS: YouTube Channel successfully authenticated!")
        print(f"Token saved securely at: {res['token_path']}")
        print("Your studio is now unlocked for 100% direct automated uploads!")
    else:
        print(f"\n❌ Error during authorization: {res.get('error')}")


if __name__ == "__main__":
    main()
