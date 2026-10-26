import asyncio
import os
import shutil
import sys
import time
from playwright.async_api import async_playwright

DOWNLOADS_DIR = "C:\\Users\\Sohail\\Downloads"

async def download_tile_from_stack(tile_index, scene_num):
    dest_path = os.path.abspath(f"data/flow_clips/maglev_scene_{scene_num}.mp4")
    before_files = set(os.listdir(DOWNLOADS_DIR))
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        
        # Check flow-video-tile count
        tiles = await page.locator("flow-video-tile").all()
        print(f"Current visible video tiles: {len(tiles)}", flush=True)
        if tile_index >= len(tiles):
            print(f"Index {tile_index} out of range!", flush=True)
            return False
            
        target_tile = tiles[tile_index]
        print(f"Clicking Tile {tile_index+1} (Scene {scene_num})...", flush=True)
        await target_tile.scroll_into_view_if_needed()
        await target_tile.click()
        await page.wait_for_timeout(1000)
        
        # Download button
        dl_btn = page.locator("[aria-label*='Download media'], button:has-text('download')").first
        if await dl_btn.count() == 0:
            print("Download button not found!", flush=True)
            return False
            
        print("Clicking download button...", flush=True)
        await dl_btn.click()
        await page.wait_for_timeout(1000)
        
        opt_720 = page.locator("[role='menuitem']:has-text('720p')").first
        if await opt_720.count() == 0:
            print("720p option not found in menu!", flush=True)
            return False
            
        print("Clicking '720p Original size'...", flush=True)
        await opt_720.click()
        
    print(f"Waiting for download in {DOWNLOADS_DIR}...", flush=True)
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
        print(f"FAILED: Download for Scene {scene_num} not detected.", flush=True)
        return False

if __name__ == "__main__":
    idx = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    sc_num = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    asyncio.run(download_tile_from_stack(idx, sc_num))
