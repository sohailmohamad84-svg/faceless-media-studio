import asyncio
import json
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

PROJECT_FILE = "data/jakarta_flow_project.json"
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DOWNLOADS_DIR = os.path.expandvars(r"C:\Users\Sohail\Downloads")

JAKARTA_SCENES = [
    {
        "num": 1,
        "title": "The Submerged Street Hook",
        "prompt": "Cinematic low tracking shot through a flooded Jakarta street where murky ocean water laps against second-story shop signs, concrete flood walls holding back dark sea, 4k 60fps vertical 9:16"
    },
    {
        "num": 2,
        "title": "3D Groundwater Subsidence Cutaway",
        "prompt": "3D geological cross-section beneath Jakarta streets showing illegal deep water wells draining underground aquifers, porous soil layers collapsing like an empty sponge, 4k 60fps vertical 9:16"
    },
    {
        "num": 3,
        "title": "3D Satellite Elevation DEM",
        "prompt": "3D satellite elevation map over northern Jakarta showing dark blue contour lines sinking below zero-meter sea level, Java Sea towering behind reinforced dikes, 4k 60fps vertical 9:16"
    },
    {
        "num": 4,
        "title": "The Great Garuda Sea Wall Blueprint",
        "prompt": "Holographic 3D blueprint animation of the 25-mile offshore 'Great Garuda' sea wall shaped like a mythical eagle spanning across Jakarta Bay, artificial barrier islands glowing in gold, 4k 60fps vertical 9:16"
    },
    {
        "num": 5,
        "title": "Heavy Rock Revetment Engineering",
        "prompt": "Giant marine crane barges dumping multi-ton interlocking concrete tetrapods into roaring ocean waters along the perimeter of the offshore seawall, 4k 60fps vertical 9:16"
    },
    {
        "num": 6,
        "title": "Moving the Capital into the Jungle",
        "prompt": "3D satellite push from sinking Jakarta over 800 miles across the Java Sea into the dense green rainforests of East Kalimantan where Nusantara smart city is being built, 4k 60fps vertical 9:16"
    },
    {
        "num": 7,
        "title": "Sea Barrier Pumping Station",
        "prompt": "Colossal high-volume Archimedes screw pumps discharging millions of gallons of trapped river water over the sea wall back into the open Java Sea, heavy spray, 4k 60fps vertical 9:16"
    },
    {
        "num": 8,
        "title": "Golden Bay Sunset & Organic CTA",
        "prompt": "Sweeping golden hour drone shot looking out from the sea wall towards the Jakarta skyline reflecting on the glowing ocean, warm cinematic sunset, 4k 60fps vertical 9:16"
    }
]

async def run_pipeline():
    os.makedirs("data/flow_clips", exist_ok=True)
    
    with open(PROJECT_FILE, "r") as f:
        proj_data = json.load(f)
    project_url = proj_data["project_url"]
    
    print("=======================================================", flush=True)
    print(f"STARTING VEO 2 GENERATION FOR JAKARTA SINKING SEAWALL", flush=True)
    print(f"Canvas URL: {project_url}", flush=True)
    print("=======================================================", flush=True)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_DATA_DIR,
            executable_path=CHROME_EXE,
            headless=True,
            accept_downloads=True
        )
        page = context.pages[0] if context.pages else await context.new_page()
        await page.goto(project_url, timeout=40000)
        await page.wait_for_timeout(5000)

        # Check existing tiles
        initial_tiles = await page.locator("flow-video-tile").count()
        print(f"Initial canvas video tiles: {initial_tiles}", flush=True)

        # Submit all 8 scenes sequentially
        for sc in JAKARTA_SCENES:
            num = sc["num"]
            title = sc["title"]
            prompt = sc["prompt"]
            dest_path = os.path.abspath(f"data/flow_clips/jakarta_scene_{num}.mp4")

            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1_000_000:
                print(f"[OK] Scene {num} already downloaded ({os.path.getsize(dest_path):,} bytes). Skipping submission.", flush=True)
                continue

            print(f"\n--- Submitting Scene {num}/8: {title} ---", flush=True)
            print(f"Prompt: {prompt}", flush=True)

            # Close side drawer if open
            done_btn = page.locator("button[aria-label='Done editing scene'], button:has-text('Done')")
            if await done_btn.count() > 0 and await done_btn.first.is_visible():
                await done_btn.first.click()
                await page.wait_for_timeout(1000)

            # Locate prompt input
            prompt_box = page.locator("[contenteditable='true']").first
            await prompt_box.click()
            await page.wait_for_timeout(300)
            await page.keyboard.insert_text(prompt)
            await page.wait_for_timeout(800)

            # Click send button
            send_btn = page.locator("button[aria-label='Start generation'], button:has-text('arrow_forward')").last
            await send_btn.click()
            print("Clicked Start Generation...", flush=True)
            await page.wait_for_timeout(3000)

            # Check for approval dialog
            for _ in range(5):
                radios = page.locator("div[role='radio']:not([aria-disabled='true'])")
                if await radios.count() > 0:
                    always_btn = page.locator("div[role='radio']:not([aria-disabled='true']):has-text('Always approve')")
                    if await always_btn.count() > 0:
                        print("Clicking 'Always approve'...", flush=True)
                        await always_btn.first.click()
                    else:
                        print("Clicking 'Approve'...", flush=True)
                        await radios.first.click()
                    await page.wait_for_timeout(2000)
                    break
                await page.wait_for_timeout(1000)

            await page.wait_for_timeout(2000)

        # Now monitor until all 8 tiles are rendered
        print("\n=======================================================", flush=True)
        print("MONITORING VEO 2 RENDERING ON CANVAS...", flush=True)
        print("=======================================================", flush=True)
        
        start_t = time.time()
        for poll in range(90):  # up to 7.5 mins
            await page.wait_for_timeout(5000)
            elapsed = int(time.time() - start_t)
            
            tiles = await page.locator("flow-video-tile").count()
            pendings = await page.locator("flow-pending-tile").count()
            stop_btn = await page.locator("button:has-text('Stop'), button[aria-label='Stop']").count()

            print(f"[{elapsed}s] Video Tiles: {tiles}/8 | Pending: {pendings} | Active Generation: {stop_btn > 0}", flush=True)

            if tiles >= 8 and pendings == 0 and stop_btn == 0 and elapsed >= 30:
                print(f"All 8 Veo scenes rendered successfully in {elapsed}s!", flush=True)
                break

        # Download all 8 tiles
        print("\n=======================================================", flush=True)
        print("DOWNLOADING ALL 8 SCENES FROM CANVAS...", flush=True)
        print("=======================================================", flush=True)

        tiles_elements = page.locator("flow-video-tile")
        total_tiles = await tiles_elements.count()
        print(f"Found {total_tiles} video tiles on canvas.", flush=True)

        # In Google Flow, newest tiles appear at index 0 or in creation order
        # Let's download each tile
        for idx in range(min(total_tiles, 8)):
            # Scene numbers correspond to tiles
            # Let's ensure scene_num maps appropriately
            scene_num = idx + 1
            dest_path = os.path.abspath(f"data/flow_clips/jakarta_scene_{scene_num}.mp4")

            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1_000_000:
                print(f"Scene {scene_num} already downloaded ({os.path.getsize(dest_path):,} bytes). Skipping.", flush=True)
                continue

            print(f"\n--- Downloading Tile {idx+1}/{total_tiles} -> Scene {scene_num} ---", flush=True)
            target = tiles_elements.nth(idx)
            box = await target.bounding_box()
            if box:
                await page.mouse.click(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                await page.wait_for_timeout(2000)

            dl_btn = page.locator("button[aria-label='Download media'], button:has-text('download')").first
            for _ in range(10):
                if await dl_btn.count() > 0 and await dl_btn.is_enabled():
                    break
                await page.wait_for_timeout(1000)

            if await dl_btn.count() == 0:
                print(f"Warning: Download button not visible for tile {idx+1}", flush=True)
                continue

            before_files = set(os.listdir(DOWNLOADS_DIR)) if os.path.exists(DOWNLOADS_DIR) else set()
            await dl_btn.click()
            await page.wait_for_timeout(1000)

            opt_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p')").first
            if await opt_720.count() == 0:
                opt_720 = page.get_by_text("720p").first

            try:
                async with page.expect_download(timeout=30000) as dl_info:
                    await opt_720.click()
                download = await dl_info.value
                await download.save_as(dest_path)
                print(f"SUCCESS: Saved Scene {scene_num} to {dest_path} ({os.path.getsize(dest_path):,} bytes)", flush=True)
            except Exception as ex:
                print(f"Direct download event notice: {ex}. Checking Downloads folder...", flush=True)
                found = None
                for _ in range(20):
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
                    shutil.copy2(found, dest_path)
                    print(f"SUCCESS (fallback): Saved {found} -> {dest_path} ({os.path.getsize(dest_path):,} bytes)", flush=True)
                else:
                    print(f"FAILED to download Scene {scene_num}", flush=True)

            await page.keyboard.press("Escape")
            await page.wait_for_timeout(1500)

        await context.close()

    print("\n=======================================================", flush=True)
    print("VERIFICATION OF ALL 8 JAKARTA CLIPS ON DISK:", flush=True)
    verified = 0
    for s in range(1, 9):
        p = Path(f"data/flow_clips/jakarta_scene_{s}.mp4")
        if p.exists() and p.stat().st_size > 1_000_000:
            print(f"  [OK] Scene {s}: {p.stat().st_size:,} bytes")
            verified += 1
        else:
            print(f"  [MISSING/CORRUPT] Scene {s}")
    print(f"Verified {verified}/8 clips successfully.")
    print("=======================================================", flush=True)

if __name__ == "__main__":
    asyncio.run(run_pipeline())
