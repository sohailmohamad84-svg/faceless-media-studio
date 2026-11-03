import asyncio
import os
import time
from playwright.async_api import async_playwright

PROJECT_URL = "https://flow.google.com/project/2c6f19c8-b792-4427-b525-40c5f99bed37"
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

async def check():
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
        
        tiles = await page.locator("flow-video-tile").count()
        pendings = await page.locator("flow-pending-tile").count()
        stop_btn = page.locator("button:has-text('Stop'), [aria-label*='Stop']")
        is_generating = (await stop_btn.count() > 0 and await stop_btn.first.is_visible())
        
        pct_elem = page.locator(".loading-percentage")
        pct = await pct_elem.first.inner_text() if await pct_elem.count() > 0 else "Ready"
        
        print(f"Status: Generating={is_generating} | Tiles={tiles} | Pendings={pendings} | Pct={pct}")
        await page.screenshot(path="azorian_tile1_status.png")
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(check())
