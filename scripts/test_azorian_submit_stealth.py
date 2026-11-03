import asyncio
import os
import time
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACT_DIR = Path(r"C:\Users\Sohail\.gemini\antigravity\brain\eb4bd0b7-d463-4e01-b351-a971179e01ed")
PROJECT_URL = "https://flow.google.com/project/2c6f19c8-b792-4427-b525-40c5f99bed37"
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

AZORIAN_SCENE_1_PROMPT = "Underwater cinematic shot in pitch black ocean depth where deep-sea submersible spotlights reveal the crushed black hull of Soviet nuclear missile submarine K-129 resting on the abyssal plain, 4k 60fps vertical 9:16"

async def main():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_DATA_DIR,
            executable_path=CHROME_EXE,
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            ignore_default_args=["--enable-automation"]
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
        await page.goto(PROJECT_URL, timeout=30000)
        await page.wait_for_timeout(3000)
        
        # Verify prompt box
        box = page.locator("div.ProseMirror[role='textbox']").first
        await box.click()
        await page.wait_for_timeout(500)
        
        print("Inserting prompt for Scene 1...")
        await page.keyboard.insert_text(AZORIAN_SCENE_1_PROMPT)
        await page.wait_for_timeout(1000)
        
        send_btn = page.locator("button:has-text('arrow_forward')").last
        print("Clicking Start Generation...")
        await send_btn.click()
        await page.wait_for_timeout(5000)
        
        await page.screenshot(path=str(ARTIFACT_DIR / "azorian_scene1_submitted.png"), full_page=True)
        print("Saved screenshot azorian_scene1_submitted.png")
        
        # Monitor for up to 90 seconds
        start_t = time.time()
        for i in range(18):
            await page.wait_for_timeout(5000)
            elapsed = int(time.time() - start_t)
            stop_btn = page.locator("button:has-text('Stop'), [aria-label*='Stop']")
            is_generating = (await stop_btn.count() > 0 and await stop_btn.first.is_visible())
            tiles = await page.locator("flow-video-tile").count()
            pendings = await page.locator("flow-pending-tile").count()
            pct_elem = page.locator(".loading-percentage")
            pct = await pct_elem.first.inner_text() if await pct_elem.count() > 0 else ""
            print(f"[{elapsed}s] Generating: {is_generating} | Tiles: {tiles} | Pendings: {pendings} | Pct: {pct}")
            
            if tiles > 0:
                print("SUCCESS: Video tile generated!")
                break
                
        await page.screenshot(path=str(ARTIFACT_DIR / "azorian_scene1_result.png"), full_page=True)
        print("Saved screenshot azorian_scene1_result.png")
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(main())
