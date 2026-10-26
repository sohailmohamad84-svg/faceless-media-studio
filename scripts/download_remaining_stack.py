import asyncio
import os
import shutil
import sys
import time
from playwright.async_api import async_playwright

DOWNLOADS_DIR = "C:\\Users\\Sohail\\Downloads"

# Mapping: (tile_index, scene_num)
ITEMS = [
    (3, 4),
    (4, 5),
    (5, 6),
    (6, 7),
    (7, 8),
]

async def download_all():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        
        # Expand stack if collapsed
        tiles = await page.locator("flow-video-tile").all()
        if len(tiles) <= 1:
            stack = page.locator("flow-tile-container").first
            if await stack.count() > 0:
                print("Clicking flow-tile-container to expand stack...", flush=True)
                await stack.click()
                await page.wait_for_timeout(2000)
                
        tiles = await page.locator("flow-video-tile").all()
        print(f"Total tiles after expansion: {len(tiles)}", flush=True)
        
        for tile_index, scene_num in ITEMS:
            dest_path = os.path.abspath(f"data/flow_clips/maglev_scene_{scene_num}.mp4")
            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000000:
                print(f"Scene {scene_num} already exists ({os.path.getsize(dest_path)} bytes), skipping.", flush=True)
                continue
                
            print(f"\n--- Downloading Tile {tile_index+1} -> Scene {scene_num} ---", flush=True)
            before_files = set(os.listdir(DOWNLOADS_DIR))
            
            # Before files
            before_files = set(os.listdir(DOWNLOADS_DIR))
            
            tiles = await page.locator("flow-video-tile").all()
            if tile_index >= len(tiles):
                print(f"Error: Tile {tile_index} out of range ({len(tiles)} total)", flush=True)
                continue
                
            target_tile = tiles[tile_index]
            await target_tile.scroll_into_view_if_needed()
            await target_tile.click()
            await page.wait_for_timeout(1000)
            
            dl_btn = page.locator("[aria-label*='Download media'], button:has-text('download')").first
            if await dl_btn.count() == 0:
                print(f"No download button for tile {tile_index}!", flush=True)
                continue
                
            await dl_btn.click()
            await page.wait_for_timeout(1000)
            
            opt_720 = page.locator("[role='menuitem']:has-text('720p')").first
            if await opt_720.count() == 0:
                print(f"720p option not found for tile {tile_index}!", flush=True)
                continue
                
            print("Clicking 720p...", flush=True)
            await opt_720.click()
            
            # Wait for file in downloads
            new_file = None
            for _ in range(30):
                await page.wait_for_timeout(1000)
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
                print(f"✅ Scene {scene_num} saved to {dest_path} ({os.path.getsize(dest_path)} bytes)", flush=True)
            else:
                print(f"❌ Failed to download Scene {scene_num}.", flush=True)
                
            await page.wait_for_timeout(2000)

if __name__ == "__main__":
    asyncio.run(download_all())
