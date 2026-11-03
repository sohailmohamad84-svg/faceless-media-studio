import asyncio
import json
import os
import time
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACT_DIR = Path(r"C:\Users\Sohail\.gemini\antigravity\brain\eb4bd0b7-d463-4e01-b351-a971179e01ed")
PROJECT_FILE = "data/azorian_flow_project.json"
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

async def main():
    with open(PROJECT_FILE, "r") as f:
        proj_data = json.load(f)
    project_url = proj_data["project_url"]

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_DATA_DIR,
            executable_path=CHROME_EXE,
            headless=True
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(project_url, timeout=30000)
        await page.wait_for_timeout(3000)
        
        start_t = time.time()
        for i in range(25):  # monitor up to ~2 minutes
            stop_btn = page.locator("button:has-text('Stop'), [aria-label*='Stop']")
            is_generating = (await stop_btn.count() > 0 and await stop_btn.first.is_visible())
            
            tiles = await page.locator("flow-video-tile, video, flow-media-tile, flow-chat-video").count()
            print(f"[{int(time.time() - start_t)}s] Generating: {is_generating} | Video/tiles count: {tiles}")
            
            if not is_generating and i > 2:
                print("Generation completed or stopped!")
                break
                
            await page.wait_for_timeout(5000)
            
        out_path = ARTIFACT_DIR / "azorian_generation_result.png"
        await page.screenshot(path=str(out_path), full_page=True)
        print(f"Result screenshot saved: {out_path}")
        
        # Dump HTML or video elements
        videos = await page.locator("video, [aria-label*='Download'], button:has-text('download')").all()
        print("Found video / download elements:", len(videos))
        for idx, v in enumerate(videos):
            tag = await v.evaluate("e => e.tagName")
            src = await v.evaluate("e => e.src || e.getAttribute('src') || ''")
            print(f"  [{idx}] {tag}: src={src[:80]}")
            
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(main())
