import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

async def create_clean_project():
    print("Launching Chrome to create brand-new clean Google Flow project...")
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_DATA_DIR,
            executable_path=CHROME_EXE,
            headless=True
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto("https://flow.google.com/", timeout=40000)
        await page.wait_for_timeout(4000)
        
        # Look for New project button
        new_btn = page.locator("button:has-text('New project'), [aria-label*='New project']").first
        if await new_btn.count() == 0:
            print("Could not find New project button! Current URL:", page.url)
            await page.screenshot(path="scratch/flow_new_btn_debug.png")
            await ctx.close()
            return None
            
        print("Clicking '+ New project' button...")
        await new_btn.click()
        await page.wait_for_timeout(5000)
        
        new_url = page.url
        print(f"Created new project! URL: {new_url}")
        
        # Now set aspect ratio to 9:16
        print("Configuring 9:16 vertical aspect ratio...")
        tune_btn = page.locator("button:has-text('tune'), [aria-label*='tune'], [aria-label*='Settings']").last
        if await tune_btn.count() > 0:
            await tune_btn.click()
            await page.wait_for_timeout(1500)
            ratio_916 = page.locator("button:has-text('9:16'), [aria-label*='9:16'], mat-button-toggle:has-text('9:16')").first
            if await ratio_916.count() > 0:
                await ratio_916.click()
                print("Successfully selected 9:16 aspect ratio!")
                await page.wait_for_timeout(1000)
            else:
                print("Warning: 9:16 toggle button not found inside tune popup.")
            await page.keyboard.press("Escape")
        else:
            print("Warning: Tune button not found.")
            
        await page.wait_for_timeout(1000)
        
        # Verify 0 tiles exist on this fresh canvas
        tiles_count = await page.locator("flow-video-tile").count()
        print(f"Verified initial tile count on fresh canvas: {tiles_count} tiles.")
        
        out_info = {
            "project_url": new_url,
            "created_at": "2026-10-30",
            "topic": "sr71_blackbird_unstart"
        }
        Path("data/sr71_clean_flow_project.json").write_text(json.dumps(out_info, indent=2))
        print("Saved project info to data/sr71_clean_flow_project.json")
        
        await ctx.close()
        return new_url

if __name__ == "__main__":
    asyncio.run(create_clean_project())
