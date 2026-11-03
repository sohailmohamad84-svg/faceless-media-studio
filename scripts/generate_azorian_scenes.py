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

PROJECT_FILE = "data/azorian_flow_project.json"
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DOWNLOADS_DIR = os.path.expandvars(r"C:\Users\Sohail\Downloads")

AZORIAN_SCENES = [
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

async def generate_azorian_clips():
    os.makedirs("data/flow_clips", exist_ok=True)
    
    with open(PROJECT_FILE, "r") as f:
        proj_data = json.load(f)
    project_url = proj_data["project_url"]

    print("=======================================================", flush=True)
    print("STARTING AUTONOMOUS GOOGLE FLOW BATCH FOR PROJECT AZORIAN", flush=True)
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

        for sc in AZORIAN_SCENES:
            num = sc["num"]
            title = sc["title"]
            prompt = sc["prompt"]
            dest_path = os.path.abspath(f"data/flow_clips/azorian_scene_{num}.mp4")

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
        print("ALL 8 PROJECT AZORIAN SCENES PROCESSED SUCCESSFULLY!", flush=True)
        print("=======================================================", flush=True)
        await context.close()

if __name__ == "__main__":
    asyncio.run(generate_azorian_clips())
