import asyncio
import os
import shutil
import time
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACT_DIR = Path(r"C:\Users\Sohail\.gemini\antigravity\brain\eb4bd0b7-d463-4e01-b351-a971179e01ed")
PROJECT_URL = "https://flow.google.com/project/2c6f19c8-b792-4427-b525-40c5f99bed37"
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
DOWNLOADS_DIR = os.path.expandvars(r"C:\Users\Sohail\Downloads")
DEST_PATH = os.path.abspath("data/flow_clips/azorian_scene_2.mp4")

SCENE_2_PROMPT = "3D architectural cutaway of the 618-foot Hughes Glomar Explorer ship, exterior showing deep-sea manganese nodule mining gear, interior cutaway revealing a gigantic secret submarine moon pool inside the hull, 4k 60fps vertical 9:16"

async def main():
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
        await page.goto(PROJECT_URL, timeout=30000)
        await page.wait_for_timeout(3000)
        
        initial_tiles = await page.locator("flow-video-tile").count()
        print(f"Initial tiles before Scene 2: {initial_tiles}")
        
        # Insert Scene 2 prompt
        box = page.locator("div.ProseMirror[role='textbox']").first
        await box.click()
        await page.wait_for_timeout(300)
        
        print("Inserting prompt for Scene 2...")
        await page.keyboard.insert_text(SCENE_2_PROMPT)
        await page.wait_for_timeout(800)
        
        send_btn = page.locator("button:has-text('arrow_forward')").last
        print("Submitting Scene 2...")
        await send_btn.click()
        await page.wait_for_timeout(5000)
        
        # Monitor rendering
        start_t = time.time()
        for i in range(25):
            await page.wait_for_timeout(5000)
            elapsed = int(time.time() - start_t)
            tiles = await page.locator("flow-video-tile").count()
            pendings = await page.locator("flow-pending-tile").count()
            pct_elem = page.locator(".loading-percentage")
            pct = await pct_elem.first.inner_text() if await pct_elem.count() > 0 else "Ready"
            print(f"[{elapsed}s] Tiles: {tiles} | Pendings: {pendings} | Pct: {pct}")
            
            if pendings == 0 and tiles > initial_tiles and elapsed > 15:
                print(f"Scene 2 finished rendering in {elapsed}s!")
                break
                
        now_tiles = await page.locator("flow-video-tile").count()
        print(f"Total tiles now: {now_tiles}")
        
        # Check positions of tiles
        tiles_list = await page.locator("flow-video-tile").all()
        for idx, t in enumerate(tiles_list):
            box = await t.bounding_box()
            print(f"Tile {idx}: bounding_box={box}")
            
        await page.screenshot(path=str(ARTIFACT_DIR / "azorian_scene2_rendered.png"), full_page=True)
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(main())
