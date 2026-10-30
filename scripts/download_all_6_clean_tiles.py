import asyncio
import os
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

PROJECT_URL = "https://flow.google.com/project/4636eaaf-c702-4c9a-9c78-a73e4307f511"
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

# Grid mapping verified from visual canvas inspection:
# Tile 5: Stratosphere Cruise (Scene 1)
# Tile 4: Moveable Spike Cutaway (Scene 2)
# Tile 3: Shockwave Expulsion (Scene 3)
# Tile 2: Cockpit Telemetry (Scene 4)
# Tile 1: J58 Ramjet Cutaway (Scene 5)
# Tile 0: Titanium Expansion (Scene 6)
TILE_MAPPING = [
    {"scene_num": 1, "tile_idx": 5, "name": "Stratosphere Cruise"},
    {"scene_num": 2, "tile_idx": 4, "name": "Moveable Spike Cutaway"},
    {"scene_num": 3, "tile_idx": 3, "name": "Forensic Shockwave Expulsion"},
    {"scene_num": 4, "tile_idx": 2, "name": "Cockpit Violent Yaw Telemetry"},
    {"scene_num": 5, "tile_idx": 1, "name": "J58 Turbo-Ramjet Cutaway"},
    {"scene_num": 6, "tile_idx": 0, "name": "Titanium Thermal Expansion"},
]

async def download_all_tiles():
    print("Launching Chrome to download all 6 verified tiles...")
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_DATA_DIR,
            executable_path=CHROME_EXE,
            headless=True,
            accept_downloads=True
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(PROJECT_URL, timeout=40000)
        await page.wait_for_timeout(4000)
        
        for item in TILE_MAPPING:
            num = item["scene_num"]
            t_idx = item["tile_idx"]
            name = item["name"]
            dest = Path(f"data/flow_clips/sr71_flow_scene_{num}.mp4")
            
            print(f"\nDownloading Scene {num} ({name}) from Tile {t_idx}...")
            
            # Make sure viewer is closed
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(1000)
            
            target_tile = page.locator("flow-video-tile").nth(t_idx)
            await target_tile.scroll_into_view_if_needed()
            await page.wait_for_timeout(1000)
            
            box = await target_tile.bounding_box()
            if not box:
                print(f"Error: Tile {t_idx} has no bounding box!")
                continue
                
            # Click center of tile
            await page.mouse.click(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
            await page.wait_for_timeout(2500)
            
            # Find download button in viewer
            dl_btn = page.locator("button[aria-label='Download media'], button[aria-label='Download']")
            if await dl_btn.count() > 0 and await dl_btn.first.is_enabled():
                await dl_btn.first.click()
                await page.wait_for_timeout(1000)
                
                opt_720 = page.get_by_text("720p").first
                if await opt_720.count() > 0:
                    async with page.expect_download(timeout=35000) as d_info:
                        await opt_720.click()
                    d = await d_info.value
                    await d.save_as(str(dest))
                    print(f"SUCCESS: Scene {num} saved to {dest} ({dest.stat().st_size:,} bytes)")
                    
                    # Extract inspection frame
                    proof_jpg = Path(f"scratch/sr71_proof_scene_{num}.jpg")
                    subprocess.run(
                        ["ffmpeg", "-y", "-ss", "2.0", "-i", str(dest), "-vframes", "1", str(proof_jpg)],
                        capture_output=True
                    )
                    print(f"Extracted proof frame: {proof_jpg}")
                else:
                    print(f"720p option not found for Tile {t_idx}")
            else:
                print(f"Download button not found for Tile {t_idx}")
                
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(1500)
            
        print("\nAll 6 tiles processed!")
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(download_all_tiles())
