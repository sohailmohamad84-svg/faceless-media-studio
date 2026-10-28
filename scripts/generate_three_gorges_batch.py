"""Autonomous Google Flow Batch Generator for Three Gorges Dam.
Generates Scenes 2 through 8 sequentially on the dedicated project canvas.
"""
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

PROJECT_URL = "https://flow.google.com/project/abffc76f-a50f-4cca-b4c6-7605f64e41e5"
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DOWNLOADS_DIR = os.path.expandvars(r"C:\Users\Sohail\Downloads")

THREE_GORGES_SCENES = [
    {
        "num": 1,
        "title": "The Massive Spillway Hook",
        "prompt": "Low-angle cinematic drone shot facing the colossal concrete wall of Three Gorges Dam with massive floodgates blasting violent roaring white water into the gorge, heavy mist and rainbow distortion, 4k 60fps vertical 9:16"
    },
    {
        "num": 2,
        "title": "Planetary Physics & Moment of Inertia",
        "prompt": "3D holographic view of planet Earth spinning in deep space, glowing vector lines showing Earth's rotational axis shifting slightly as a glowing red mass concentrates in central China, 4k 60fps vertical 9:16"
    },
    {
        "num": 3,
        "title": "Spinning Figure Skater Analogy",
        "prompt": "Visual split simulation comparing a spinning figure skater extending arms to a spinning globe elevating billions of tons of water away from its core, motion vectors, 4k 60fps vertical 9:16"
    },
    {
        "num": 4,
        "title": "3D Internal Turbine Cutaway",
        "prompt": "3D architectural cross-section cutaway deep inside the dam wall revealing thirty-two colossal Francis hydro-turbines spinning in roaring high-pressure water, glowing copper magnetic coils, 4k 60fps vertical 9:16"
    },
    {
        "num": 5,
        "title": "Ship Elevator Engineering Marvel",
        "prompt": "Macro tracking shot of the world's largest vertical ship lift, raising a 3,000-ton container barge 370 feet straight up inside a steel elevator shaft on massive counterweight cables, 4k 60fps vertical 9:16"
    },
    {
        "num": 6,
        "title": "Seismic Stress & Crustal Fault Lines",
        "prompt": "3D geological fault line simulation showing immense tectonic pressure underneath the reservoir bed with micro-fractures glowing red in continental crust rock, 4k 60fps vertical 9:16"
    },
    {
        "num": 7,
        "title": "Flood Defense Shockwave",
        "prompt": "High-speed tracking shot of rushing monsoon flood currents crashing into reinforced concrete dissipation baffles, water exploding into towering spray, 4k 60fps vertical 9:16"
    },
    {
        "num": 8,
        "title": "Golden Dam Crest Panorama & CTA",
        "prompt": "Stunning golden hour panoramic drone shot rising over the crest of the dam, calm mountain reservoir stretching hundreds of miles into misty limestone peaks, warm sunlight, 4k 60fps vertical 9:16"
    }
]

async def generate_three_gorges_batch():
    os.makedirs("data/flow_clips", exist_ok=True)
    print("=======================================================", flush=True)
    print("STARTING THREE GORGES DAM VEO GENERATION BATCH", flush=True)
    print(f"Canvas URL: {PROJECT_URL}", flush=True)
    print("=======================================================", flush=True)

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_DATA_DIR,
            executable_path=CHROME_EXE,
            headless=True,
            accept_downloads=True
        )
        page = context.pages[0] if context.pages else await context.new_page()
        
        print("Navigating to Three Gorges project canvas...", flush=True)
        await page.goto(PROJECT_URL, timeout=35000)
        await page.wait_for_timeout(5000)

        # Ensure active approval state if prompt already submitted
        active_radios = page.locator("div[role='radio']:not([aria-disabled='true'])")
        if await active_radios.count() > 0:
            always_btn = page.locator("div[role='radio']:not([aria-disabled='true']):has-text('Always approve')")
            if await always_btn.count() > 0:
                print("Clicking active 'Always approve'...", flush=True)
                await always_btn.first.click()
            else:
                print("Clicking active 'Approve'...", flush=True)
                await active_radios.first.click()
            await page.wait_for_timeout(3000)

        for sc in THREE_GORGES_SCENES:
            num = sc["num"]
            title = sc["title"]
            prompt = sc["prompt"]
            dest1 = os.path.abspath(f"data/flow_clips/threegorges_scene_{num}.mp4")
            dest2 = os.path.abspath(f"data/flow_clips/three_gorges_scene_{num}.mp4")

            if (os.path.exists(dest1) and os.path.getsize(dest1) > 1_000_000) or (os.path.exists(dest2) and os.path.getsize(dest2) > 1_000_000):
                if not os.path.exists(dest1) and os.path.exists(dest2):
                    shutil.copyfile(dest2, dest1)
                elif not os.path.exists(dest2) and os.path.exists(dest1):
                    shutil.copyfile(dest1, dest2)
                print(f"\n[OK] Scene {num} already downloaded ({os.path.getsize(dest1):,} bytes). Skipping.", flush=True)
                continue

            print(f"\n=======================================================", flush=True)
            print(f"SCENE {num}/8: {title}", flush=True)
            print(f"Prompt: {prompt}", flush=True)
            print(f"=======================================================", flush=True)

            initial_tiles = await page.locator("flow-video-tile").count()
            print(f"Current canvas video tiles: {initial_tiles}", flush=True)

            # 1. Type prompt via keyboard insertion into ProseMirror
            prompt_box = page.locator("[contenteditable='true']").first
            await prompt_box.click()
            await page.wait_for_timeout(400)
            await page.keyboard.insert_text(prompt)
            await page.wait_for_timeout(1000)

            # 2. Click send button
            send_btn = page.locator("button[aria-label='Start generation'], button:has-text('arrow_forward')").last
            print(f"Submitting Scene {num} prompt to Flow canvas...", flush=True)
            await send_btn.click()
            await page.wait_for_timeout(4000)

            # 3. Check for approval radio option
            for check_app in range(6):
                radios = page.locator("div[role='radio']:not([aria-disabled='true'])")
                if await radios.count() > 0:
                    always_btn = page.locator("div[role='radio']:not([aria-disabled='true']):has-text('Always approve')")
                    if await always_btn.count() > 0:
                        print("Clicking 'Always approve'...", flush=True)
                        await always_btn.first.click()
                    else:
                        print("Clicking 'Approve'...", flush=True)
                        await radios.first.click()
                    await page.wait_for_timeout(3000)
                    break
                await page.wait_for_timeout(2000)

            # 4. Wait for tile count to increment
            print("Waiting for generation tile to register on canvas...", flush=True)
            tile_registered = False
            for _ in range(15):
                await page.wait_for_timeout(2000)
                now_tiles = await page.locator("flow-video-tile").count()
                if now_tiles > initial_tiles:
                    tile_registered = True
                    print(f"New video tile created! Canvas total: {now_tiles}", flush=True)
                    break

            if not tile_registered:
                print("Notice: Tile count not yet incremented, checking canvas state...", flush=True)

            # 5. Poll newest tile for generation completion
            print(f"Rendering Veo clip for Scene {num} in Google Flow...", flush=True)
            start_t = time.time()
            gen_done = False

            for check_idx in range(60):  # up to 5 minutes
                await page.wait_for_timeout(5000)
                elapsed = int(time.time() - start_t)

                stop_count = await page.locator("button:has-text('Stop'), button[aria-label='Stop']").count()
                tiles_all = page.locator("flow-video-tile")
                current_tile_count = await tiles_all.count()
                
                pending_count = 1
                if current_tile_count > initial_tiles:
                    target_tile = tiles_all.last
                    pending_count = await target_tile.locator("flow-pending-tile").count()

                print(f"  [{elapsed}s] CanvasTiles: {current_tile_count} | Pending: {pending_count} | StopBtn: {stop_count}", flush=True)

                if current_tile_count > initial_tiles and pending_count == 0 and stop_count == 0 and elapsed >= 20:
                    print(f"Generation completed for Scene {num} in {elapsed}s!", flush=True)
                    gen_done = True
                    break

            # 6. Download 720p clip
            await page.wait_for_timeout(2000)
            target_tile = page.locator("flow-video-tile").last
            await target_tile.scroll_into_view_if_needed()
            await target_tile.click()
            await page.wait_for_timeout(1500)

            before_files = set(os.listdir(DOWNLOADS_DIR)) if os.path.exists(DOWNLOADS_DIR) else set()
            try:
                dl_btn = page.locator("[aria-label*='Download media'], button:has-text('download')").first
                if await dl_btn.count() == 0:
                    await target_tile.click()
                    await page.wait_for_timeout(1500)
                    dl_btn = page.locator("[aria-label*='Download media'], button:has-text('download')").first

                if await dl_btn.count() > 0:
                    await dl_btn.click()
                    await page.wait_for_timeout(1000)

                    opt_720 = page.get_by_text("720p").first
                    print(f"Triggering 720p download for Scene {num}...", flush=True)

                    try:
                        async with page.expect_download(timeout=35000) as dl_info:
                            await opt_720.click()
                        download = await dl_info.value
                        await download.save_as(dest1)
                        shutil.copyfile(dest1, dest2)
                        print(f"Saved Scene {num} directly to {dest1} ({os.path.getsize(dest1):,} bytes)", flush=True)
                    except Exception as dl_err:
                        print(f"Direct download event error ({dl_err}). Checking Downloads directory...", flush=True)
                        found_file = None
                        for _ in range(25):
                            await page.wait_for_timeout(1000)
                            now_files = set(os.listdir(DOWNLOADS_DIR))
                            diff = now_files - before_files
                            for f in diff:
                                if f.endswith(".mp4") and not f.endswith(".crdownload"):
                                    found_file = os.path.join(DOWNLOADS_DIR, f)
                                    break
                            if found_file:
                                break
                        if found_file and os.path.exists(found_file):
                            shutil.copyfile(found_file, dest1)
                            shutil.copyfile(dest1, dest2)
                            print(f"Recovered Scene {num} from Downloads folder ({os.path.getsize(dest1):,} bytes)", flush=True)
                        else:
                            print(f"Could not find download file for Scene {num}", flush=True)
                else:
                    print(f"Download button not visible for Scene {num}!")
            except Exception as e:
                print(f"Error during Scene {num} download interaction: {e}", flush=True)

            # 7. Press Escape and pause before next scene
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(3000)

        await page.screenshot(path="three_gorges_batch_final.png")
        await context.close()

    print("\n=======================================================", flush=True)
    print("THREE GORGES BATCH COMPLETED. Verifying downloaded clips:", flush=True)
    all_present = True
    for sc in THREE_GORGES_SCENES:
        num = sc["num"]
        p = Path(f"data/flow_clips/three_gorges_scene_{num}.mp4")
        if p.exists() and p.stat().st_size > 1_000_000:
            print(f"  - Scene {num} ({sc['title']}): {p.stat().st_size:,} bytes [OK]")
        else:
            print(f"  - Scene {num} ({sc['title']}): MISSING or invalid! [FAIL]")
            all_present = False
    print("=======================================================", flush=True)
    return all_present

if __name__ == "__main__":
    success = asyncio.run(generate_three_gorges_batch())
    if not success:
        sys.exit(1)
