"""Google Flow Browser Automation Bridge.
Connects directly to user's active Google Chrome session over Chrome DevTools Protocol (CDP)
on port 9222, reads credit balance, injects scene prompts, monitors rendering,
and downloads finished 1080p video clips into data/flow_clips/.
"""
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, List
from playwright.sync_api import sync_playwright, Browser, Page

from src.workflows.flow_credits import FlowCreditTracker

CLIPS_DIR = Path("data/flow_clips")
CLIPS_DIR.mkdir(parents=True, exist_ok=True)
DOWNLOADS_DIR = Path.home() / "Downloads"

class FlowBrowserBridge:
    CDP_URL = "http://localhost:9222"

    @classmethod
    def is_chrome_running_with_cdp(cls) -> bool:
        """Check if Chrome is actively listening on CDP port 9222."""
        import socket
        try:
            with socket.create_connection(("127.0.0.1", 9222), timeout=1.5):
                return True
        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    @classmethod
    def get_flow_page(cls, browser: Browser) -> Optional[Page]:
        """Find an existing tab with flow.google.com, or open a new one."""
        for context in browser.contexts:
            for page in context.pages:
                if "flow.google.com" in page.url:
                    return page
        if browser.contexts:
            page = browser.contexts[0].new_page()
            page.goto("https://flow.google.com/", wait_until="networkidle")
            return page
        return None

    @classmethod
    def inspect_status(cls) -> Dict[str, Any]:
        """Connect to Chrome, check if logged into Flow, and inspect credit info."""
        if not cls.is_chrome_running_with_cdp():
            return {
                "connected": False,
                "error": "Chrome is not running with port 9222. Launch via 'Launch_Google_Flow_Studio.bat' on Desktop."
            }

        with sync_playwright() as p:
            try:
                browser = p.chromium.connect_over_cdp(cls.CDP_URL)
                page = cls.get_flow_page(browser)
                if not page:
                    return {"connected": True, "error": "Could not find or open flow.google.com tab."}

                url = page.url
                title = page.title()
                
                # Check if logged in
                is_logged_in = (
                    "accounts.google.com" not in url
                    and "about" not in url
                    and ("flow.google.com" in url or "project" in url or "workspace" in url)
                )
                
                # Try reading visible credit balance if present in the DOM
                credits_found = None
                credit_elements = page.query_selector_all("span, div, button")
                for el in credit_elements:
                    txt = el.inner_text().strip()
                    if "credit" in txt.lower() and any(c.isdigit() for c in txt):
                        credits_found = txt
                        break

                return {
                    "connected": True,
                    "url": url,
                    "title": title,
                    "is_logged_in": is_logged_in,
                    "credits_text": credits_found
                }
            except Exception as e:
                return {
                    "connected": False,
                    "error": str(e)
                }

    @classmethod
    def generate_and_download_shot(
        cls,
        prompt: str,
        expected_shot_name: str,
        timeout_sec: int = 240
    ) -> Optional[Path]:
        """
        Submits prompt to Google Flow, waits for generation to complete,
        and saves downloaded clip to data/flow_clips/<expected_shot_name>.mp4.
        """
        if not cls.is_chrome_running_with_cdp():
            raise RuntimeError("Chrome CDP port 9222 is not active. Double-click 'Launch_Google_Flow_Studio.bat' on your Desktop.")

        with sync_playwright() as p:
            browser = p.chromium.connect_over_cdp(cls.CDP_URL)
            page = cls.get_flow_page(browser)
            if not page:
                raise RuntimeError("Could not find flow.google.com tab in Chrome.")

            page.bring_to_front()
            
            # Locate prompt input (textarea or contenteditable div)
            prompt_input = page.query_selector("textarea, [contenteditable='true'], input[type='text']")
            if not prompt_input:
                raise RuntimeError("Could not locate Google Flow prompt input box on current page.")

            # Record download baseline
            existing_downloads = set(DOWNLOADS_DIR.glob("*.mp4"))

            # Type prompt
            prompt_input.click()
            prompt_input.fill("")
            prompt_input.fill(prompt)
            time.sleep(1)

            # Click Generate / Submit button
            submit_btn = page.query_selector("button:has-text('Generate'), button[aria-label*='Generate'], button[aria-label*='Submit']")
            if submit_btn:
                submit_btn.click()
            else:
                prompt_input.press("Enter")

            # Deduct credits in tracker
            FlowCreditTracker.record_generation(
                clip_name=expected_shot_name,
                credits_spent=10,
                notes=prompt[:80] + "..."
            )

            # Wait for generation and download
            start_time = time.time()
            downloaded_file = None
            while time.time() - start_time < timeout_sec:
                # Check if a new MP4 appears in Downloads
                current_downloads = set(DOWNLOADS_DIR.glob("*.mp4"))
                new_files = current_downloads - existing_downloads
                if new_files:
                    # Pick the newest
                    latest = max(new_files, key=lambda f: f.stat().st_mtime)
                    # Ensure file is done writing
                    initial_sz = latest.stat().st_size
                    time.sleep(2)
                    if latest.stat().st_size == initial_sz and initial_sz > 500000:
                        downloaded_file = latest
                        break
                        
                # Also check if download button appeared on page
                dl_btn = page.query_selector("button[aria-label*='Download'], a[download]")
                if dl_btn and not downloaded_file:
                    dl_btn.click()
                    time.sleep(3)

                time.sleep(3)

            if downloaded_file and downloaded_file.exists():
                target_dest = CLIPS_DIR / f"{expected_shot_name}.mp4"
                import shutil
                shutil.copy2(downloaded_file, target_dest)
                return target_dest

            return None
