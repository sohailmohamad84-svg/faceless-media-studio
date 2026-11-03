import asyncio
import json
import os
from pathlib import Path
from playwright.async_api import async_playwright

ARTIFACT_DIR = Path(r"C:\Users\Sohail\.gemini\antigravity\brain\eb4bd0b7-d463-4e01-b351-a971179e01ed")
CHROME_DATA_DIR = os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData")
CHROME_EXE = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PROJECT_FILE = "data/azorian_flow_project.json"

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
        
        # Find the prompt input
        input_elem = page.locator("textarea, input[type='text'], [contenteditable='true'], [placeholder*='What do you want to create']").first
        print("Input element count:", await input_elem.count())
        box = await input_elem.bounding_box()
        print("Bounding box:", box)
        
        # Click and type
        await input_elem.click()
        await page.wait_for_timeout(500)
        await page.keyboard.type("Underwater cinematic shot in pitch black ocean depth where deep-sea submersible spotlights reveal the crushed black hull of Soviet nuclear missile submarine K-129 resting on the abyssal plain, 4k 60fps vertical 9:16", delay=10)
        await page.wait_for_timeout(1000)
        
        # Take screenshot of typed state
        await page.screenshot(path=str(ARTIFACT_DIR / "azorian_typed_test.png"))
        print("Typed test screenshot saved.")
        
        # Find the submit button
        submit_btn = page.locator("button:has-text('arrow_forward'), button[aria-label*='Send'], button[aria-label*='Submit']").last
        print("Submit button count:", await submit_btn.count())
        s_box = await submit_btn.bounding_box()
        print("Submit bounding box:", s_box)
        
        if s_box:
            await page.mouse.click(s_box["x"] + s_box["width"]/2, s_box["y"] + s_box["height"]/2)
            print("Clicked submit button via mouse coordinates!")
            await page.wait_for_timeout(5000)
            
            # Check for any dialogs, radios, or spinners
            await page.screenshot(path=str(ARTIFACT_DIR / "azorian_after_submit_test.png"))
            print("After submit screenshot saved.")
            
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(main())
