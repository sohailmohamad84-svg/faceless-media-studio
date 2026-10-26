import asyncio
import os
import shutil
import sys
import time
from playwright.async_api import async_playwright

DOWNLOADS_DIR = "C:\\Users\\Sohail\\Downloads"

async def download_scene(scene_num):
    dest_path = os.path.abspath(f"data/flow_clips/maglev_scene_{scene_num}.mp4")
    before_files = set(os.listdir(DOWNLOADS_DIR))
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        
        # Click the latest video tile
        tile = page.locator("flow-video-tile").last
        await tile.click()
        await page.wait_for_timeout(1000)
        
        # Click download button
        dl_btn = page.locator("[aria-label*='Download media'], button:has-text('download')").first
        print("Clicking download button...", flush=True)
        await dl_btn.click()
        await page.wait_for_timeout(1000)
        
        # Click 720p Original size
        opt_720 = page.locator("[role='menuitem']:has-text('720p')").first
        print("Clicking 720p Original size...", flush=True)
        await opt_720.click()
        
    print("Waiting for download to finish in Downloads folder...", flush=True)
    new_file = None
    for _ in range(30):
        time.sleep(1)
        now_files = set(os.listdir(DOWNLOADS_DIR))
        diff = now_files - before_files
        for f in diff:
            if f.endswith(".mp4") and not f.endswith(".crdownload"):
                new_file = os.path.join(DOWNLOADS_DIR, f)
                break
        if new_file:
            break
            
    if new_file and os.path.exists(new_file):
        shutil.copy2(new_file, dest_path)
        print(f"SUCCESS: Scene {scene_num} saved to {dest_path} (Size: {os.path.getsize(dest_path)} bytes)", flush=True)
        return True
    else:
        print("FAILED: Download not detected.", flush=True)
        return False

if __name__ == "__main__":
    asyncio.run(download_scene(2))
