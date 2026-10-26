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

async def generate_and_download_scene(scene_num, prompt):
    print(f"\n=======================================================", flush=True)
    print(f"🎬 STARTING SCENE {scene_num}: {prompt[:60]}...", flush=True)
    print(f"=======================================================", flush=True)
    
    os.makedirs("data/flow_clips", exist_ok=True)
    dest_path = os.path.abspath(f"data/flow_clips/maglev_scene_{scene_num}.mp4")
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        
        # 1. Count existing video tiles
        initial_tiles = await page.locator("flow-video-tile").count()
        print(f"Current video tiles before submission: {initial_tiles}", flush=True)
        
        # 2. Find prompt box
        prompt_box = page.locator("[contenteditable='true']").last
        await prompt_box.click()
        await page.wait_for_timeout(500)
        
        # Clear existing text if any
        await prompt_box.fill("")
        await prompt_box.fill(prompt)
        await page.wait_for_timeout(1000)
        
        # 3. Click send button
        send_btn = page.locator("button:has-text('arrow_forward')").last
        print("Clicking submit button...", flush=True)
        await send_btn.click()
        await page.wait_for_timeout(3000)
        
        # 4. Check if confirmation / approve button appears
        approve_btn = page.locator("button:has-text('Always approve'), button:has-text('Approve')")
        if await approve_btn.count() > 0 and await approve_btn.first.is_visible():
            print("Approval required. Clicking 'Always approve' / 'Approve'...", flush=True)
            await approve_btn.first.click()
            await page.wait_for_timeout(2000)
        
        # 5. Monitor for new flow-video-tile
        print("Waiting for generation to finish (polling flow-video-tile count)...", flush=True)
        max_wait = 300  # up to 5 minutes
        start_time = time.time()
        new_tile_found = False
        
        while time.time() - start_time < max_wait:
            await page.wait_for_timeout(5000)
            current_tiles = await page.locator("flow-video-tile").count()
            elapsed = int(time.time() - start_time)
            
            # Check for error or queuing message
            chat_text = await page.evaluate("() => document.body.innerText")
            last_lines = [l.strip() for l in chat_text.split('\n') if l.strip()][-5:]
            status_line = " | ".join(last_lines)
            
            print(f"[{elapsed}s] Tiles: {current_tiles}/{initial_tiles+1} | Status: {status_line[:80]}", flush=True)
            
            if current_tiles > initial_tiles:
                print(f"🎉 New video tile detected! Total tiles: {current_tiles}", flush=True)
                new_tile_found = True
                break
                
        if not new_tile_found:
            print("⚠️ Timeout waiting for new video tile. Taking screenshot...", flush=True)
            await page.screenshot(path=f"flow_timeout_scene_{scene_num}.png")
            return False
            
        # 6. Click on the latest tile to select it
        print("Selecting new video tile...", flush=True)
        latest_tile = page.locator("flow-video-tile").last
        await latest_tile.click()
        await page.wait_for_timeout(1500)
        
        # 7. Click download button
        dl_btn = page.locator("[aria-label*='Download media'], button:has-text('download')").first
        if await dl_btn.count() == 0:
            print("Download button not found! Taking screenshot...", flush=True)
            await page.screenshot(path=f"flow_no_dl_scene_{scene_num}.png")
            return False
            
        before_files = set(os.listdir(DOWNLOADS_DIR))
        print("Clicking download button to open quality menu...", flush=True)
        await dl_btn.click()
        await page.wait_for_timeout(1000)
        
        # 8. Click 720p Original size
        opt_720 = page.locator("[role='menuitem']:has-text('720p')").first
        if await opt_720.count() == 0:
            print("720p option not found in menu!", flush=True)
            return False
            
        print("Clicking '720p Original size'...", flush=True)
        await opt_720.click()
        
        # 9. Wait for file in downloads
        print(f"Waiting for download in {DOWNLOADS_DIR}...", flush=True)
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
            print(f"✅ Scene {scene_num} successfully saved to: {dest_path} (Size: {os.path.getsize(dest_path)} bytes)", flush=True)
            return True
        else:
            print("⚠️ Download failed or timed out.", flush=True)
            return False

if __name__ == "__main__":
    prompt_scene2 = "Cinematic 3D satellite digital elevation model flyover over the jagged snowcapped mountains of the Japanese Southern Alps, glowing neon cyan route line tunneling straight through granite peaks from Tokyo to Osaka, photorealistic cartography, 4k 60fps vertical 9:16"
    asyncio.run(generate_and_download_scene(2, prompt_scene2))
