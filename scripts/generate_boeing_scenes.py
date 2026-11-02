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

PROJECT_FILE = "data/boeing_flow_project.json"
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DOWNLOADS_DIR = os.path.expandvars(r"C:\Users\Sohail\Downloads")

BOEING_SCENES = [
    {
        "num": 1,
        "title": "The Iconic Silhouette Hook",
        "prompt": "Dramatic low-angle tracking shot of a Boeing 747-400 rotating off runway at sunset, four giant turbofan engines roaring with golden exhaust haze, distinctive upper deck hump catching warm light, 4k 60fps vertical 9:16"
    },
    {
        "num": 2,
        "title": "Supersonic Obsolescence Fear",
        "prompt": "Split screen comparing a sleek Concorde supersonic airliner slicing through Mach clouds to a widebody 747 subsonic airliner, glowing Mach numbers, 4k 60fps vertical 9:16"
    },
    {
        "num": 3,
        "title": "3D Swing-Up Nose Cargo Cutaway",
        "prompt": "3D architectural cutaway of the 747 nose swinging completely upward on massive hinges, allowing two semi-truck shipping containers to drive straight down the main cargo deck, 4k 60fps vertical 9:16"
    },
    {
        "num": 4,
        "title": "Area Rule Aerodynamics",
        "prompt": "Wind tunnel aerodynamic visualization showing Whitcomb area-rule airflow smoothing around the 747 cockpit hump, air pressure streamlines curving without drag penalties, 4k 60fps vertical 9:16"
    },
    {
        "num": 5,
        "title": "The Incredible Boeing Everett Factory",
        "prompt": "Colossal indoor drone tracking shot inside Boeing's Everett Factory, the largest building by volume in the world, with three 747 fuselages under construction under massive yellow bridge cranes, 4k 60fps vertical 9:16"
    },
    {
        "num": 6,
        "title": "Supersonic Failure & The 747 Triumph",
        "prompt": "3D global cartography showing sonic boom ban flight restrictions over land, forcing supersonic airliners off lucrative continental routes while 747s conquer global skies, 4k 60fps vertical 9:16"
    },
    {
        "num": 7,
        "title": "Main Deck Military Cargo Ingestion",
        "prompt": "Time-lapse of heavy mechanized military pallets and jet engines sliding effortlessly into the gaping open nose of a 747 freighter under airport floodlights, 4k 60fps vertical 9:16"
    },
    {
        "num": 8,
        "title": "Queen of the Skies Sunset & Organic CTA",
        "prompt": "Majestic golden hour shot of a Boeing 747 soaring into pink clouds at sunset, sun glinting off the upper deck windows, cinematic warm lighting, 4k 60fps vertical 9:16"
    }
]

async def download_current_tile(page, dest_path, num):
    print(f"Downloading active tile for Scene {num}...", flush=True)
    target_tile = page.locator("flow-video-tile").first
    box = await target_tile.bounding_box()
    if box:
        await page.mouse.click(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
        await page.wait_for_timeout(2000)

    dl_btn = page.locator("button[aria-label='Download media'], button:has-text('download')").first
    for _ in range(12):
        if await dl_btn.count() > 0 and await dl_btn.is_enabled():
            print("Download button is active!", flush=True)
            break
        print("Waiting for download button to enable...", flush=True)
        await page.wait_for_timeout(2000)

    before_files = set(os.listdir(DOWNLOADS_DIR)) if os.path.exists(DOWNLOADS_DIR) else set()
    await dl_btn.click()
    await page.wait_for_timeout(1000)

    opt_720 = page.locator("button:has-text('720p'), [role='menuitem']:has-text('720p')").first
    if await opt_720.count() == 0:
        opt_720 = page.get_by_text("720p").first

    try:
        async with page.expect_download(timeout=35000) as dl_info:
            await opt_720.click()
        download = await dl_info.value
        await download.save_as(dest_path)
        print(f"SUCCESS: Scene {num} saved to {dest_path} ({os.path.getsize(dest_path):,} bytes)", flush=True)
    except Exception as ex:
        print(f"Playwright download event notice: {ex}. Checking downloads dir...", flush=True)
        await page.wait_for_timeout(4000)
        after_files = set(os.listdir(DOWNLOADS_DIR)) if os.path.exists(DOWNLOADS_DIR) else set()
        new_files = list(after_files - before_files)
        mp4_files = [f for f in new_files if f.endswith(".mp4")]
        if mp4_files:
            latest = max([os.path.join(DOWNLOADS_DIR, f) for f in mp4_files], key=os.path.getmtime)
            shutil.copy2(latest, dest_path)
            print(f"SUCCESS (fallback): Found {latest} -> saved to {dest_path} ({os.path.getsize(dest_path):,} bytes)", flush=True)
        else:
            print(f"ERROR: Could not capture downloaded video file for Scene {num}", flush=True)

    # Close side drawer/editor
    close_btn = page.locator("button[aria-label='Done editing scene'], button:has-text('Done'), button[aria-label='Close']").first
    if await close_btn.count() > 0 and await close_btn.is_visible():
        await close_btn.click()
        await page.wait_for_timeout(1500)
    await page.keyboard.press("Escape")
    await page.wait_for_timeout(1000)

async def generate_boeing_clips():
    os.makedirs("data/flow_clips", exist_ok=True)
    
    with open(PROJECT_FILE, "r") as f:
        proj_data = json.load(f)
    project_url = proj_data["project_url"]

    print("=======================================================", flush=True)
    print("STARTING AUTONOMOUS GOOGLE FLOW BATCH FOR BOEING 747", flush=True)
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

        # Close editor if open
        done_btn = page.locator("button[aria-label='Done editing scene'], button:has-text('Done')")
        if await done_btn.count() > 0 and await done_btn.first.is_visible():
            await done_btn.first.click()
            await page.wait_for_timeout(1500)

        for sc in BOEING_SCENES:
            num = sc["num"]
            title = sc["title"]
            prompt = sc["prompt"]
            dest_path = os.path.abspath(f"data/flow_clips/boeing747_scene_{num}.mp4")

            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1_000_000:
                print(f"[OK] Scene {num} already downloaded ({os.path.getsize(dest_path):,} bytes). Skipping.", flush=True)
                continue

            current_tiles = await page.locator("flow-video-tile").count()
            
            # If tile for this scene is already rendered on canvas
            if current_tiles >= num:
                print(f"Scene {num} tile already rendered on canvas (total tiles: {current_tiles}). Downloading immediately...", flush=True)
                await download_current_tile(page, dest_path, num)
                continue

            print(f"\n=======================================================", flush=True)
            print(f"GENERATING SCENE {num}/8: {title}", flush=True)
            print(f"Prompt: {prompt}", flush=True)
            print(f"=======================================================", flush=True)

            initial_tiles = await page.locator("flow-video-tile").count()
            print(f"Initial canvas tiles: {initial_tiles}", flush=True)

            # Ensure drawer is closed
            done_btn = page.locator("button[aria-label='Done editing scene'], button:has-text('Done')")
            if await done_btn.count() > 0 and await done_btn.first.is_visible():
                await done_btn.first.click()
                await page.wait_for_timeout(1000)

            # 1. Type prompt into prompt box
            prompt_box = page.locator("[contenteditable='true']").first
            await prompt_box.click()
            await page.wait_for_timeout(300)
            # Select all and clear any residual text
            await page.keyboard.press("Control+A")
            await page.keyboard.press("Backspace")
            await page.wait_for_timeout(300)
            await page.keyboard.insert_text(prompt)
            await page.wait_for_timeout(800)

            # 2. Click send button
            send_btn = page.locator("button[aria-label='Start generation'], button:has-text('arrow_forward')").last
            print("Clicking Start Generation...", flush=True)
            await send_btn.click()
            await page.wait_for_timeout(3000)

            # 3. Handle approval radio if shown
            for _ in range(8):
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

            # 4. Wait for new tile or pending tile
            print("Waiting for generation to begin on canvas...", flush=True)
            for _ in range(20):
                await page.wait_for_timeout(1500)
                pendings = await page.locator("flow-pending-tile").count()
                now_tiles = await page.locator("flow-video-tile").count()
                if pendings > 0 or now_tiles > initial_tiles:
                    print(f"Generation active! (tiles={now_tiles}, pending={pendings})", flush=True)
                    break

            # 5. Monitor rendering
            print(f"Rendering Scene {num} in Google Flow...", flush=True)
            start_t = time.time()
            for _ in range(60):  # up to 5 mins
                await page.wait_for_timeout(5000)
                elapsed = int(time.time() - start_t)
                pendings = await page.locator("flow-pending-tile").count()
                now_tiles = await page.locator("flow-video-tile").count()
                pct_elem = page.locator(".loading-percentage")
                pct = await pct_elem.first.inner_text() if await pct_elem.count() > 0 else "Ready"
                print(f"  [{elapsed}s] Tiles: {now_tiles} | Pendings: {pendings} | Status: {pct}", flush=True)

                if pendings == 0 and now_tiles > initial_tiles and elapsed >= 15:
                    print(f"Scene {num} finished rendering in {elapsed}s!", flush=True)
                    break

            await page.wait_for_timeout(3000)

            # 6. Download the tile
            await download_current_tile(page, dest_path, num)

        print("\n=======================================================", flush=True)
        print("ALL 8 BOEING 747 SCENES PROCESSED SUCCESSFULLY!", flush=True)
        print("=======================================================", flush=True)
        await context.close()

if __name__ == "__main__":
    asyncio.run(generate_boeing_clips())
