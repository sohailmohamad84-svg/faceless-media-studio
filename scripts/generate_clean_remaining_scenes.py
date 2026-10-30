import asyncio
import os
import shutil
import time
from pathlib import Path
from playwright.async_api import async_playwright

PROJECT_URL = "https://flow.google.com/project/4636eaaf-c702-4c9a-9c78-a73e4307f511"
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

SCENES_TO_GENERATE = [
    {
        "num": 2,
        "title": "Inlet Spike Translation Cutaway",
        "prompt": (
            "3D architectural mechanical cutaway of the SR-71 Blackbird engine intake nacelle, "
            "showing the sharp pointed conical spike translating 26 inches rearward inside the engine cowl, "
            "slowing Mach 3 air to subsonic speed, technical schematic animation with internal airflow lines, "
            "photorealistic engineering documentary, 4k 60fps vertical 9:16"
        ),
        "dest": "data/flow_clips/sr71_clean_scene_2.mp4"
    },
    {
        "num": 3,
        "title": "Forensic Shockwave Expulsion",
        "prompt": (
            "Forensic aerodynamic simulation of an SR-71 engine inlet unstart: "
            "supersonic normal shockwave violently expelling forward out of the intake cowl into open air, "
            "creating visible white condensation vapor rings and shock collars around the nacelle, "
            "zero explosion, zero fireballs, pure aerodynamic fluid dynamics simulation, 4k 60fps vertical 9:16"
        ),
        "dest": "data/flow_clips/sr71_clean_scene_3.mp4"
    },
    {
        "num": 4,
        "title": "Cockpit Violent Yaw Telemetry",
        "prompt": (
            "Intense visceral first-person cockpit POV inside the SR-71 Blackbird during severe asymmetric yaw, "
            "pilot wearing white David Clark full-pressure suit and gold reflective visor violently slammed sideways against canopy, "
            "vibrating analog cockpit dials and red warning alarms flashing, high-G cockpit camera shake, "
            "cinematic documentary, 4k 60fps vertical 9:16"
        ),
        "dest": "data/flow_clips/sr71_clean_scene_4.mp4"
    },
    {
        "num": 5,
        "title": "J58 Turbo-Ramjet Bypass Bleed Cutaway",
        "prompt": (
            "3D technical cutaway cross-section of the Pratt and Whitney J58 turbo-ramjet engine, "
            "showing six large external bypass bleed pipes ducting high-pressure air directly into the roaring afterburner, "
            "glowing orange heat, rotating turbine blades and internal flame holder, "
            "technical engineering visualization, 4k 60fps vertical 9:16"
        ),
        "dest": "data/flow_clips/sr71_clean_scene_5.mp4"
    },
    {
        "num": 6,
        "title": "Titanium Thermal Expansion",
        "prompt": (
            "Macro tracking shot gliding across the corrugated matte black titanium fuselage skin of the SR-71 Blackbird "
            "heated to 600 degrees Fahrenheit by atmospheric friction, titanium panels expanding to seal loose joints, "
            "intense atmospheric heat shimmer distortion rising from the dark metal, 4k 60fps vertical 9:16"
        ),
        "dest": "data/flow_clips/sr71_clean_scene_6.mp4"
    }
]

async def run_batch_generation():
    print("Launching persistent Chrome for batch clean generation...")
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
        
        for sc in SCENES_TO_GENERATE:
            num = sc["num"]
            title = sc["title"]
            prompt = sc["prompt"]
            dest = Path(sc["dest"])
            dest.parent.mkdir(parents=True, exist_ok=True)
            
            print(f"\n=======================================================")
            print(f"STARTING SCENE {num}: {title}")
            print(f"=======================================================")
            
            # Close any open viewer or dialog
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(1000)
            
            curr_tiles = await page.locator("flow-video-tile").count()
            print(f"Current tiles on canvas: {curr_tiles}")
            
            # Type prompt
            prompt_box = page.locator("[contenteditable='true']").first
            await prompt_box.scroll_into_view_if_needed()
            await prompt_box.click()
            await page.wait_for_timeout(300)
            await page.keyboard.insert_text(prompt)
            await page.wait_for_timeout(1000)
            
            send_btn = page.locator("button[aria-label='Start generation'], button:has-text('arrow_forward')").last
            print(f"Submitting prompt for Scene {num}...")
            await send_btn.click()
            await page.wait_for_timeout(3000)
            
            # Handle approval if dialog appears
            radios = page.locator("div[role='radio']:not([aria-disabled='true'])")
            if await radios.count() > 0:
                always_btn = page.locator("div[role='radio']:not([aria-disabled='true']):has-text('Always approve')")
                if await always_btn.count() > 0:
                    print("Clicking 'Always approve'...")
                    await always_btn.first.click()
                else:
                    print("Clicking 'Approve'...")
                    await radios.first.click()
                await page.wait_for_timeout(2000)
                
            print(f"Waiting for Scene {num} tile to appear and finish rendering...")
            start_t = time.time()
            target_idx = curr_tiles # Next tile index
            
            # Wait for tile creation & completion
            for poll in range(50):
                await page.wait_for_timeout(5000)
                tiles_now = await page.locator("flow-video-tile").count()
                pendings = await page.locator("flow-pending-tile").count()
                pct_elem = page.locator(".loading-percentage")
                pct = await pct_elem.first.inner_text() if await pct_elem.count() > 0 else "N/A"
                elapsed = int(time.time() - start_t)
                print(f"  [{elapsed}s] Total tiles: {tiles_now} (expected >={target_idx+1}) | Pendings: {pendings} | Pct: {pct}")
                
                if tiles_now >= (target_idx + 1) and pendings == 0 and pct in ["Ready", "N/A"] and elapsed > 10:
                    print(f"Scene {num} (Tile {target_idx}) finished rendering in {elapsed}s!")
                    break
                    
            await page.wait_for_timeout(2000)
            
            # Download the tile
            print(f"Downloading Scene {num} from Tile {target_idx}...")
            target_tile = page.locator("flow-video-tile").nth(target_idx)
            await target_tile.scroll_into_view_if_needed()
            await page.wait_for_timeout(1000)
            
            box = await target_tile.bounding_box()
            if box:
                await page.mouse.click(box["x"] + box["width"]/2, box["y"] + box["height"]/2)
                await page.wait_for_timeout(2000)
                
            dl = page.locator("button[aria-label='Download media'], button:has-text('download')").first
            if await dl.count() > 0 and await dl.is_enabled():
                await dl.click()
                await page.wait_for_timeout(1000)
                opt = page.get_by_text("720p").first
                async with page.expect_download(timeout=35000) as d_info:
                    await opt.click()
                d = await d_info.value
                await d.save_as(str(dest))
                print(f"SUCCESS: Scene {num} downloaded: {dest.stat().st_size:,} bytes")
                
                # Extract preview frame
                frame_out = f"scratch/clean_scene_{num}_2s.jpg"
                cmd = ["ffmpeg", "-y", "-ss", "2.0", "-i", str(dest), "-vframes", "1", frame_out]
                __import__("subprocess").run(cmd, stdout=__import__("subprocess").DEVNULL, stderr=__import__("subprocess").DEVNULL)
                print(f"Extracted preview frame -> {frame_out}")
            else:
                print(f"ERROR: Download button not found for Scene {num}!")
                
            await page.keyboard.press("Escape")
            await page.wait_for_timeout(1500)
            
        print("\n=======================================================")
        print("ALL SCENES 2 THROUGH 6 GENERATION & DOWNLOAD COMPLETE!")
        print("=======================================================")
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(run_batch_generation())
