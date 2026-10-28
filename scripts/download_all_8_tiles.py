import asyncio
import hashlib
import os
import shutil
import sys
import time
from playwright.async_api import async_playwright

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

PROJECT_URL = "https://flow.google.com/project/abffc76f-a50f-4cca-b4c6-7605f64e41e5"
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DOWNLOADS_DIR = os.path.expandvars(r"C:\Users\Sohail\Downloads")

GRID_CELLS = [
    {"idx": 0, "x": 322, "y": 207},
    {"idx": 1, "x": 486, "y": 207},
    {"idx": 2, "x": 650, "y": 207},
    {"idx": 3, "x": 814, "y": 207},
    {"idx": 4, "x": 322, "y": 486},
    {"idx": 5, "x": 486, "y": 486},
    {"idx": 6, "x": 650, "y": 486},
    {"idx": 7, "x": 814, "y": 486},
]

async def download_all_tiles():
    os.makedirs("data/flow_clips", exist_ok=True)
    print("=======================================================", flush=True)
    print("DOWNLOADING ALL 8 TILES FROM CANVAS GRID", flush=True)
    print("=======================================================", flush=True)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_DATA_DIR,
            executable_path=CHROME_EXE,
            headless=True,
            accept_downloads=True
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(PROJECT_URL, timeout=35000)
        await page.wait_for_timeout(5000)

        for cell in GRID_CELLS:
            idx = cell["idx"]
            x = cell["x"]
            y = cell["y"]
            dest_path = os.path.abspath(f"data/flow_clips/tile_{idx}.mp4")

            print(f"\n--- Downloading Tile {idx} at canvas ({x}, {y}) ---", flush=True)

            # Click tile on canvas
            await page.mouse.click(x, y)
            await page.wait_for_timeout(1500)

            # Check download button in toolbar
            dl_btn = page.locator("[aria-label*='Download media'], button:has-text('download')").first
            if await dl_btn.count() == 0:
                print("Retry click...")
                await page.mouse.click(x, y)
                await page.wait_for_timeout(1500)
                dl_btn = page.locator("[aria-label*='Download media'], button:has-text('download')").first

            if await dl_btn.count() == 0:
                print(f"FAILED: No download button for Tile {idx}!")
                continue

            before_files = set(os.listdir(DOWNLOADS_DIR)) if os.path.exists(DOWNLOADS_DIR) else set()
            await dl_btn.click()
            await page.wait_for_timeout(1000)

            opt_720 = page.get_by_text("720p").first
            if await opt_720.count() == 0:
                print(f"FAILED: 720p option not found for Tile {idx}!")
                await page.keyboard.press("Escape")
                continue

            print("Triggering 720p download...")
            try:
                async with page.expect_download(timeout=35000) as dl_info:
                    await opt_720.click()
                download = await dl_info.value
                await download.save_as(dest_path)
                print(f"SUCCESS: Tile {idx} saved to {dest_path} ({os.path.getsize(dest_path):,} bytes)", flush=True)
            except Exception as e:
                print(f"Direct download event error ({e}). Polling Downloads directory...", flush=True)
                found = None
                for _ in range(25):
                    await page.wait_for_timeout(1000)
                    now_files = set(os.listdir(DOWNLOADS_DIR))
                    diff = now_files - before_files
                    for f in diff:
                        if f.endswith(".mp4") and not f.endswith(".crdownload"):
                            found = os.path.join(DOWNLOADS_DIR, f)
                            break
                    if found:
                        break
                if found and os.path.exists(found):
                    shutil.copyfile(found, dest_path)
                    print(f"SUCCESS via Downloads dir: Tile {idx} ({os.path.getsize(dest_path):,} bytes)", flush=True)
                else:
                    print(f"FAILED: Could not retrieve Tile {idx} download.")

            # Deselect before next tile
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(1500)

        await context.close()

    print("\n=======================================================", flush=True)
    print("VERIFYING TILE HASHES:", flush=True)
    hashes = {}
    for idx in range(8):
        fpath = f"data/flow_clips/tile_{idx}.mp4"
        if os.path.exists(fpath):
            h = hashlib.sha256(open(fpath, "rb").read()).hexdigest()
            hashes[idx] = h
            print(f"  Tile {idx}: {os.path.getsize(fpath):,} bytes | SHA256: {h[:16]}...")
        else:
            print(f"  Tile {idx}: MISSING")

    unique_count = len(set(hashes.values()))
    print(f"Total tiles downloaded: {len(hashes)} | Unique clips: {unique_count}")
    print("=======================================================", flush=True)

if __name__ == "__main__":
    asyncio.run(download_all_tiles())
