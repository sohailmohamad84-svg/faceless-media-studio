import asyncio
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

DOWNLOADS_DIR = "C:\\Users\\Sohail\\Downloads"

SCENES = [
    {
        "num": 3,
        "title": "Silicon Valley Hype vs Cryo Reality",
        "prompt": "Cinematic split-screen documentary style: left side showing an experimental vacuum hyperloop steel tube buckling under atmospheric pressure, right side showing a high-tech Japanese cryogenic laboratory testing superconducting coils glowing with cold blue light, 4k 60fps vertical 9:16"
    },
    {
        "num": 4,
        "title": "3D Architectural Cutaway Bogie Cross-Section",
        "prompt": "Architectural 3D cutaway cross-section of a Maglev train bogie and concrete guideway sidewall, transparent metal chassis revealing niobium-titanium superconducting coils inside liquid helium tanks, glowing magnetic flux lines repelling the track and lifting the train four inches high, technical engineering visualization, 4k 60fps vertical 9:16"
    },
    {
        "num": 5,
        "title": "Linear Synchronous Motor Propulsion",
        "prompt": "3D animated technical schematic inside the concrete guideway walls, alternating electromagnetic coils pulsing in synchronized blue and orange light wave packets pulling the train forward at high velocity, cinematic motion graphic, 4k 60fps vertical 9:16"
    },
    {
        "num": 6,
        "title": "Subterranean Mountain Tunnel Boring",
        "prompt": "Heavy industrial underground construction shot inside a deep Alpine mountain tunnel, massive tunnel boring machine cutterhead spinning against solid granite rock with high pressure water mist, industrial floodlights, muddy bedrock, cinematic documentary, 4k 60fps vertical 9:16"
    },
    {
        "num": 7,
        "title": "Cockpit Telemetry at 375 MPH",
        "prompt": "Futuristic high-tech train driver console view looking through the cockpit window down an illuminated guideway, digital HUD telemetry overlay showing 603 km/h 375 MPH with zero vibration, lush Japanese landscape blurring by, photorealistic, 4k 60fps vertical 9:16"
    },
    {
        "num": 8,
        "title": "Epic Alpine Viaduct River Finish",
        "prompt": "Cinematic wide aerial drone shot of the gleaming silver aerodynamic Maglev bullet train bursting out of an Alpine mountain portal onto a soaring viaduct over a crystal clear river gorge, morning sun reflecting off the fuselage, epic documentary finish, 4k 60fps vertical 9:16"
    }
]

async def run_batch():
    os.makedirs("data/flow_clips", exist_ok=True)
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        
        for sc in SCENES:
            num = sc["num"]
            title = sc["title"]
            prompt = sc["prompt"]
            dest_path = os.path.abspath(f"data/flow_clips/maglev_scene_{num}.mp4")
            
            if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000000:
                print(f"Skipping Scene {num} - already exists ({os.path.getsize(dest_path)} bytes)", flush=True)
                continue
                
            print(f"\n=======================================================", flush=True)
            print(f"🎬 SCENE {num}/8: {title}", flush=True)
            print(f"Prompt: {prompt}", flush=True)
            print(f"=======================================================", flush=True)
            
            initial_tiles = await page.locator("flow-video-tile").count()
            print(f"Current tiles: {initial_tiles}", flush=True)
            
            # Fill prompt
            prompt_box = page.locator("[contenteditable='true']").last
            await prompt_box.click()
            await page.wait_for_timeout(400)
            await prompt_box.fill(prompt)
            await page.wait_for_timeout(800)
            
            # Click submit
            send_btn = page.locator("button:has-text('arrow_forward')").last
            print("Submitting prompt to Flow canvas...", flush=True)
            await send_btn.click()
            await page.wait_for_timeout(3000)
            
            # Approve if needed
            approve_btn = page.locator("button:has-text('Always approve'), button:has-text('Approve')")
            if await approve_btn.count() > 0 and await approve_btn.first.is_visible():
                print("Clicking approval button...", flush=True)
                await approve_btn.first.click()
                await page.wait_for_timeout(2000)
                
            # Wait for tile count to increase
            print("Waiting for generation tile to register...", flush=True)
            tile_added = False
            for _ in range(20):
                await page.wait_for_timeout(2000)
                now_tiles = await page.locator("flow-video-tile").count()
                if now_tiles > initial_tiles:
                    tile_added = True
                    print(f"New tile registered! Total: {now_tiles}", flush=True)
                    break
                    
            if not tile_added:
                print(f"Warning: Tile count did not increase for Scene {num}. Checking chat...", flush=True)
            
            # Now poll the latest tile until generation finishes
            print("Polling generation progress...", flush=True)
            start_gen = time.time()
            gen_done = False
            
            for _ in range(60): # up to 5 minutes
                await page.wait_for_timeout(5000)
                latest_tile = page.locator("flow-video-tile").last
                
                # Check if pending tile still exists inside latest tile
                pending = await latest_tile.locator("flow-pending-tile").count()
                
                # Also select the tile to check download button
                try:
                    await latest_tile.click()
                except Exception:
                    pass
                
                dl_btn = page.locator("[aria-label*='Download media'], button:has-text('download')").first
                is_enabled = False
                if await dl_btn.count() > 0:
                    is_enabled = await dl_btn.is_enabled()
                    
                elapsed = int(time.time() - start_gen)
                print(f"  [{elapsed}s] Pending: {pending > 0} | DL Enabled: {is_enabled}", flush=True)
                
                if pending == 0 and is_enabled:
                    print(f"🎉 Scene {num} finished rendering in {elapsed}s!", flush=True)
                    gen_done = True
                    break
                    
            if not gen_done:
                print(f"❌ Scene {num} generation timed out or failed. Skipping to next.", flush=True)
                continue
                
            # Download 720p
            before_files = set(os.listdir(DOWNLOADS_DIR))
            dl_btn = page.locator("[aria-label*='Download media'], button:has-text('download')").first
            await dl_btn.click()
            await page.wait_for_timeout(1200)
            
            opt_720 = page.locator("[role='menuitem']:has-text('720p')").first
            await opt_720.click()
            
            print(f"Downloading clip for Scene {num}...", flush=True)
            dl_file = None
            for _ in range(30):
                await page.wait_for_timeout(1000)
                now_files = set(os.listdir(DOWNLOADS_DIR))
                diff = now_files - before_files
                for f in diff:
                    if f.endswith(".mp4") and not f.endswith(".crdownload"):
                        dl_file = os.path.join(DOWNLOADS_DIR, f)
                        break
                if dl_file:
                    break
                    
            if dl_file and os.path.exists(dl_file):
                shutil.copy2(dl_file, dest_path)
                print(f"✅ Scene {num} saved to {dest_path} (Size: {os.path.getsize(dest_path)} bytes)", flush=True)
            else:
                print(f"❌ Failed to download Scene {num}.", flush=True)
                
            # Brief pause before next prompt
            await page.wait_for_timeout(3000)

if __name__ == "__main__":
    asyncio.run(run_batch())
