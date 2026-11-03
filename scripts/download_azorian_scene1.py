import asyncio
import os
import shutil
from pathlib import Path
from playwright.async_api import async_playwright

CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROJECT_URL = "https://flow.google.com/project/2c6f19c8-b792-4427-b525-40c5f99bed37"
DOWNLOADS_DIR = os.path.expandvars(r"C:\Users\Sohail\Downloads")
DEST_PATH = os.path.abspath("data/flow_clips/azorian_scene_1.mp4")

async def main():
    os.makedirs("data/flow_clips", exist_ok=True)
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_DATA_DIR,
            executable_path=CHROME_EXE,
            headless=True,
            accept_downloads=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            ignore_default_args=["--enable-automation"]
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
        await page.goto(PROJECT_URL, timeout=35000)
        await page.wait_for_timeout(3000)
        
        # Check tiles
        tiles = page.locator("flow-video-tile")
        print(f"Found {await tiles.count()} video tiles on canvas.")
        
        # Click the tile or video container
        tile = tiles.first
        print("Clicking video tile...")
        await tile.click()
        await page.wait_for_timeout(2000)
        
        # Check download button
        dl_btn = page.locator("button[aria-label*='Download'], button:has-text('download')").first
        for _ in range(10):
            if await dl_btn.count() > 0 and await dl_btn.is_enabled():
                print("Download button is ready!")
                break
            await page.wait_for_timeout(1000)
            
        before_files = set(os.listdir(DOWNLOADS_DIR)) if os.path.exists(DOWNLOADS_DIR) else set()
        print("Clicking download button...")
        await dl_btn.click()
        await page.wait_for_timeout(1000)
        
        opt_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p')").first
        if await opt_720.count() == 0:
            opt_720 = page.get_by_text("720p").first
            
        print("Selecting 720p resolution...")
        try:
            async with page.expect_download(timeout=35000) as dl_info:
                await opt_720.click()
            download = await dl_info.value
            temp_p = await download.path()
            shutil.copy2(temp_p, DEST_PATH)
            print(f"SUCCESS: Scene 1 downloaded and saved to {DEST_PATH} ({os.path.getsize(DEST_PATH):,} bytes)!")
        except Exception as e:
            print(f"Download notice: {e}. Checking downloads dir...")
            await page.wait_for_timeout(5000)
            after_files = set(os.listdir(DOWNLOADS_DIR)) if os.path.exists(DOWNLOADS_DIR) else set()
            new_files = list(after_files - before_files)
            mp4_files = [f for f in new_files if f.endswith(".mp4")]
            if mp4_files:
                latest = max([os.path.join(DOWNLOADS_DIR, f) for f in mp4_files], key=os.path.getmtime)
                shutil.copy2(latest, DEST_PATH)
                print(f"SUCCESS (fallback): Found {latest} -> saved to {DEST_PATH} ({os.path.getsize(DEST_PATH):,} bytes)!")
            else:
                print("ERROR: Download failed.")
                
        # Close editor
        done_btn = page.locator("button:has-text('Done'), button[aria-label='Done editing scene']").first
        if await done_btn.count() > 0 and await done_btn.is_visible():
            await done_btn.click()
        else:
            await page.keyboard.press("Escape")
        await page.wait_for_timeout(1000)
        
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(main())
