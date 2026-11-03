import asyncio
import hashlib
import os
import shutil
import subprocess
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACT_DIR = Path(r"C:\Users\Sohail\.gemini\antigravity\brain\eb4bd0b7-d463-4e01-b351-a971179e01ed")
PROJECT_URL = "https://flow.google.com/project/2c6f19c8-b792-4427-b525-40c5f99bed37"
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DOWNLOADS_DIR = os.path.expandvars(r"C:\Users\Sohail\Downloads")

def get_file_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()

async def download_all_8():
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
        await page.goto(PROJECT_URL, timeout=40000)
        await page.wait_for_timeout(5000)
        
        # Ensure any open drawer is closed
        done_btn = page.locator("button:has-text('Done'), button[aria-label='Done editing scene'], button[aria-label='Close']")
        if await done_btn.count() > 0 and await done_btn.first.is_visible():
            await done_btn.first.click()
            await page.wait_for_timeout(1500)
            
        tiles = await page.locator("flow-video-tile").all()
        print(f"Total tiles on canvas: {len(tiles)}")
        if len(tiles) < 8:
            raise RuntimeError(f"Expected 8 tiles, but found {len(tiles)}")
            
        seen_hashes = {}
        
        for idx in range(8):
            num = idx + 1
            dest_path = os.path.abspath(f"data/flow_clips/azorian_scene_{num}.mp4")
            print(f"\n=======================================================", flush=True)
            print(f"DOWNLOADING SCENE {num}/8 (Canvas Tile {idx})", flush=True)
            print(f"=======================================================", flush=True)
            
            # Re-locate tile by index
            tile = page.locator("flow-video-tile").nth(idx)
            box = await tile.bounding_box()
            if not box:
                raise RuntimeError(f"Could not get bounding box for Tile {idx}")
                
            cx = box["x"] + box["width"] / 2
            cy = box["y"] + box["height"] / 2
            print(f"Clicking Tile {idx} at center ({cx:.1f}, {cy:.1f})...", flush=True)
            
            # Click tile
            await page.mouse.click(cx, cy)
            await page.wait_for_timeout(2500)
            
            # Check download button
            dl_btn = page.locator("button[aria-label='Download media'], button:has-text('download')").first
            for _ in range(12):
                if await dl_btn.count() > 0 and await dl_btn.is_enabled():
                    break
                await page.wait_for_timeout(1000)
                
            if await dl_btn.count() == 0:
                print(f"Retrying click for Tile {idx}...", flush=True)
                await page.mouse.click(cx, cy)
                await page.wait_for_timeout(2000)
                dl_btn = page.locator("button[aria-label='Download media'], button:has-text('download')").first
                
            before_files = set(os.listdir(DOWNLOADS_DIR)) if os.path.exists(DOWNLOADS_DIR) else set()
            print("Clicking Download media...", flush=True)
            await dl_btn.click()
            await page.wait_for_timeout(1200)
            
            opt_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p')").first
            if await opt_720.count() == 0:
                opt_720 = page.get_by_text("720p").first
                
            print("Selecting 720p download...", flush=True)
            try:
                async with page.expect_download(timeout=40000) as dl_info:
                    await opt_720.click()
                download = await dl_info.value
                temp_p = await download.path()
                shutil.copy2(temp_p, dest_path)
            except Exception as ex:
                print(f"Download event notice: {ex}. Checking downloads directory...", flush=True)
                await page.wait_for_timeout(5000)
                after_files = set(os.listdir(DOWNLOADS_DIR)) if os.path.exists(DOWNLOADS_DIR) else set()
                diff = list(after_files - before_files)
                mp4s = [f for f in diff if f.endswith(".mp4")]
                if mp4s:
                    latest = max([os.path.join(DOWNLOADS_DIR, f) for f in mp4s], key=os.path.getmtime)
                    shutil.copy2(latest, dest_path)
                else:
                    raise RuntimeError(f"Failed to capture download for Scene {num}")
                    
            f_size = os.path.getsize(dest_path)
            f_hash = get_file_sha256(dest_path)
            print(f"SAVED: Scene {num} -> {dest_path} ({f_size:,} bytes | SHA256: {f_hash[:16]}...)", flush=True)
            
            # Check for duplicate
            if f_hash in seen_hashes:
                prev_scene = seen_hashes[f_hash]
                raise ValueError(f"DUPLICATE DETECTED! Scene {num} has identical SHA256 as Scene {prev_scene} ({f_hash})")
            seen_hashes[f_hash] = num
            
            # Close editor before proceeding to next tile
            done_btn = page.locator("button:has-text('Done'), button[aria-label='Done editing scene'], button[aria-label='Close']").first
            if await done_btn.count() > 0 and await done_btn.is_visible():
                await done_btn.click()
            else:
                await page.keyboard.press("Escape")
            await page.wait_for_timeout(2000)
            
        print("\n=======================================================", flush=True)
        print("ALL 8 SCENES DOWNLOADED WITH 100% UNIQUE SHA-256 HASHES!", flush=True)
        for h, n in seen_hashes.items():
            print(f"  Scene {n}: SHA256={h[:16]}... ({os.path.getsize(f'data/flow_clips/azorian_scene_{n}.mp4'):,} bytes)")
        print("=======================================================", flush=True)
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(download_all_8())
