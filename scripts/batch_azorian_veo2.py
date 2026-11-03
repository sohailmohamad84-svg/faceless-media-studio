import asyncio
import os
import shutil
import sys
import time
from pathlib import Path
from playwright.async_api import async_playwright

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

PROJECT_URL = "https://flow.google.com/project/2c6f19c8-b792-4427-b525-40c5f99bed37"
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DOWNLOADS_DIR = os.path.expandvars(r"C:\Users\Sohail\Downloads")

ALL_SCENES = [
    {
        "num": 1,
        "title": "The Sunken Submarine Hook",
        "prompt": "Underwater cinematic shot in pitch black ocean depth where deep-sea submersible spotlights reveal the crushed black hull of Soviet nuclear missile submarine K-129 resting on the abyssal plain, 4k 60fps vertical 9:16"
    },
    {
        "num": 2,
        "title": "Howard Hughes Cover Story",
        "prompt": "3D architectural cutaway of the 618-foot Hughes Glomar Explorer ship, exterior showing deep-sea manganese nodule mining gear, interior cutaway revealing a gigantic secret submarine moon pool inside the hull, 4k 60fps vertical 9:16"
    },
    {
        "num": 3,
        "title": "The Clementine Mechanical Capture Claw",
        "prompt": "Massive 200-foot articulated steel capture claw named Clementine with colossal hydraulic mechanical fingers descending through a bottom well into dark ocean water, 4k 60fps vertical 9:16"
    },
    {
        "num": 4,
        "title": "Three-Mile Pipe String Physics",
        "prompt": "3D forensic simulation of three miles of threaded 30-foot heavy drill pipes lowering the heavy claw through abyssal ocean currents, tension and bending stresses glowing on the steel pipe string, 4k 60fps vertical 9:16"
    },
    {
        "num": 5,
        "title": "The Critical Claw Failure",
        "prompt": "Forensic underwater simulation of two steel claw fingers snapping under catastrophic shear load at 9,000 feet depth, sending two-thirds of the submarine hull tumbling back down into the abyss, 4k 60fps vertical 9:16"
    },
    {
        "num": 6,
        "title": "Recovered Bow & Formal Nuclear Burial",
        "prompt": "Inside the secret moon pool under sterile floodlights, naval engineers inspect the recovered 38-foot bow section containing nuclear torpedoes and lost crew members, 4k 60fps vertical 9:16"
    },
    {
        "num": 7,
        "title": "Glomar Response Legal Precedent",
        "prompt": "Declassified vintage CIA file stamps slamming onto confidential memos with glowing text: 'NEITHER CONFIRM NOR DENY', vintage film grain, 4k 60fps vertical 9:16"
    },
    {
        "num": 8,
        "title": "Open Ocean Horizon & Organic CTA",
        "prompt": "Cinematic golden hour drone shot flying over open Pacific Ocean waters with the sun setting on calm deep blue waves, warm reflective light, 4k 60fps vertical 9:16"
    }
]

async def download_tile_at_index(page, tile_idx, dest_path):
    print(f"Attempting download for tile index {tile_idx} -> {dest_path}...", flush=True)
    tiles = page.locator("flow-video-tile")
    count = await tiles.count()
    if tile_idx >= count:
        print(f"ERROR: Tile index {tile_idx} exceeds available tiles ({count})", flush=True)
        return False
        
    tile = tiles.nth(tile_idx)
    await tile.click()
    await page.wait_for_timeout(2000)
    
    dl_btn = page.locator("button[aria-label*='Download'], button:has-text('download')").first
    for _ in range(10):
        if await dl_btn.count() > 0 and await dl_btn.is_enabled():
            break
        await page.wait_for_timeout(1000)
        
    before_files = set(os.listdir(DOWNLOADS_DIR)) if os.path.exists(DOWNLOADS_DIR) else set()
    await dl_btn.click()
    await page.wait_for_timeout(1000)
    
    opt_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p')").first
    if await opt_720.count() == 0:
        opt_720 = page.get_by_text("720p").first
        
    success = False
    try:
        async with page.expect_download(timeout=35000) as dl_info:
            await opt_720.click()
        download = await dl_info.value
        temp_p = await download.path()
        shutil.copy2(temp_p, dest_path)
        print(f"SUCCESS: Saved to {dest_path} ({os.path.getsize(dest_path):,} bytes)", flush=True)
        success = True
    except Exception as e:
        print(f"Download notice: {e}. Checking downloads folder fallback...", flush=True)
        await page.wait_for_timeout(5000)
        after_files = set(os.listdir(DOWNLOADS_DIR)) if os.path.exists(DOWNLOADS_DIR) else set()
        new_files = list(after_files - before_files)
        mp4_files = [f for f in new_files if f.endswith(".mp4")]
        if mp4_files:
            latest = max([os.path.join(DOWNLOADS_DIR, f) for f in mp4_files], key=os.path.getmtime)
            shutil.copy2(latest, dest_path)
            print(f"SUCCESS (fallback): Found {latest} -> saved to {dest_path} ({os.path.getsize(dest_path):,} bytes)", flush=True)
            success = True
            
    # Close editor
    done_btn = page.locator("button:has-text('Done'), button[aria-label='Done editing scene']").first
    if await done_btn.count() > 0 and await done_btn.is_visible():
        await done_btn.click()
    else:
        await page.keyboard.press("Escape")
    await page.wait_for_timeout(1500)
    return success

async def main():
    os.makedirs("data/flow_clips", exist_ok=True)
    
    print("=======================================================", flush=True)
    print("AUTONOMOUS GOOGLE VEO 2 BATCH PIPELINE FOR PROJECT AZORIAN", flush=True)
    print("=======================================================", flush=True)

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
        await page.wait_for_timeout(4000)
        
        # Ensure any open drawer is closed
        done_btn = page.locator("button:has-text('Done'), button[aria-label='Done editing scene']").first
        if await done_btn.count() > 0 and await done_btn.is_visible():
            await done_btn.click()
            await page.wait_for_timeout(1000)

        for sc in ALL_SCENES:
            num = sc["num"]
            title = sc["title"]
            prompt = sc["prompt"]
            dest_path = os.path.abspath(f"data/flow_clips/azorian_scene_{num}.mp4")
            tile_idx = num - 1

            print(f"\n>>> PROCESSING SCENE {num}/8: {title} <<<", flush=True)
            
            # Check if file already downloaded
            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1_000_000:
                print(f"[OK] Scene {num} file already exists ({os.path.getsize(dest_path):,} bytes). Skipping.", flush=True)
                continue
                
            current_tiles = await page.locator("flow-video-tile").count()
            print(f"Current tiles on canvas: {current_tiles} (target tile index: {tile_idx})", flush=True)
            
            # If the tile already exists on canvas, just download it
            if current_tiles > tile_idx:
                print(f"Tile {tile_idx} already rendered on canvas. Downloading now...", flush=True)
                ok = await download_tile_at_index(page, tile_idx, dest_path)
                if ok:
                    continue
                    
            # Need to generate tile for this scene
            print(f"Generating Scene {num}: {prompt}", flush=True)
            box = page.locator("div.ProseMirror[role='textbox']").first
            await box.click()
            await page.wait_for_timeout(400)
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await page.wait_for_timeout(300)
            
            await page.keyboard.insert_text(prompt)
            await page.wait_for_timeout(800)
            
            send_btn = page.locator("button:has-text('arrow_forward')").last
            print(f"Submitting Scene {num}...", flush=True)
            await send_btn.click()
            await page.wait_for_timeout(5000)
            
            # Monitor rendering
            start_t = time.time()
            for check_idx in range(35):  # up to ~3 mins
                await page.wait_for_timeout(5000)
                elapsed = int(time.time() - start_t)
                tiles = await page.locator("flow-video-tile").count()
                pendings = await page.locator("flow-pending-tile").count()
                pct_elem = page.locator(".loading-percentage")
                pct = await pct_elem.first.inner_text() if await pct_elem.count() > 0 else "Ready"
                print(f"  [{elapsed}s] Scene {num} | Tiles: {tiles} | Pendings: {pendings} | Progress: {pct}", flush=True)
                
                if pendings == 0 and tiles > tile_idx and elapsed >= 15:
                    print(f"Scene {num} finished rendering in {elapsed}s!", flush=True)
                    break
                    
            await page.wait_for_timeout(2000)
            # Download the newly created tile
            await download_tile_at_index(page, tile_idx, dest_path)
            
        print("\n=======================================================", flush=True)
        print("ALL 8 PROJECT AZORIAN SCENES PROCESSED AND DOWNLOADED!", flush=True)
        print("=======================================================", flush=True)
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(main())
