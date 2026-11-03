import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACT_DIR = Path(r"C:\Users\Sohail\.gemini\antigravity\brain\eb4bd0b7-d463-4e01-b351-a971179e01ed")
PROJECT_FILE = "data/azorian_flow_project.json"
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

async def main():
    with open(PROJECT_FILE, "r") as f:
        proj_data = json.load(f)
    project_url = proj_data["project_url"]

    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=CHROME_DATA_DIR,
            executable_path=CHROME_EXE,
            headless=True
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.goto(project_url, timeout=30000)
        await page.wait_for_timeout(3000)
        
        # 1. Click prompt box
        prompt_box = page.locator("div.ProseMirror[role='textbox'], div[aria-label*='What do you want to create']").first
        print("Prompt box count:", await prompt_box.count())
        await prompt_box.click()
        await page.wait_for_timeout(500)
        
        test_prompt = "Underwater cinematic shot in pitch black ocean depth where deep-sea submersible spotlights reveal the crushed black hull of Soviet nuclear missile submarine K-129 resting on the abyssal plain, 4k 60fps vertical 9:16"
        await page.keyboard.type(test_prompt, delay=5)
        await page.wait_for_timeout(1000)
        
        # Check send buttons
        send_btn = page.locator("button:has-text('arrow_forward')").last
        print("Send button visible:", await send_btn.is_visible(), "enabled:", await send_btn.is_enabled())
        s_box = await send_btn.bounding_box()
        print("Send button box:", s_box)
        
        # Click send or press Enter
        print("Clicking send button...")
        await send_btn.click()
        await page.wait_for_timeout(3000)
        
        # Check if an approval dialog appeared
        radios = page.locator("div[role='radio']:not([aria-disabled='true'])")
        print("Radio count:", await radios.count())
        if await radios.count() > 0:
            always_btn = page.locator("div[role='radio']:not([aria-disabled='true']):has-text('Always approve')")
            if await always_btn.count() > 0:
                print("Clicking Always approve...")
                await always_btn.first.click()
            else:
                print("Clicking first radio...")
                await radios.first.click()
            await page.wait_for_timeout(2000)
            
        await page.screenshot(path=str(ARTIFACT_DIR / "azorian_generation_started.png"))
        print("Screenshot saved: azorian_generation_started.png")
        
        # Check canvas tiles and spinners
        tiles = await page.locator("flow-video-tile").count()
        pendings = await page.locator("flow-pending-tile").count()
        print(f"Canvas state after submit: tiles={tiles}, pendings={pendings}")
        
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(main())
