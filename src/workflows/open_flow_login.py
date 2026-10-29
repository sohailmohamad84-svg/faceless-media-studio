"""Open Google Flow in dedicated Studio Chrome for 1-time sign-in."""
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

def launch_flow_studio():
    profile_dir = Path("data/flow_chrome_profile").resolve()
    profile_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Opening Studio Chrome with profile at {profile_dir}...")
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=False,
            channel="chrome",
            args=["--start-maximized", "--remote-debugging-port=9222"]
        )
        page = context.pages[0] if context.pages else context.new_page()
        page.goto("https://flow.google.com/")
        print("Studio Chrome is active! Please sign in with your Google account.")
        print("Keep this window open or press Ctrl+C once signed in.")
        
        # Keep open for up to 10 minutes or until closed
        for _ in range(600):
            try:
                time.sleep(1)
                if page.is_closed():
                    break
            except KeyboardInterrupt:
                break
        context.close()

if __name__ == "__main__":
    launch_flow_studio()
