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
        
        out_path = ARTIFACT_DIR / "azorian_canvas_inspect.png"
        await page.screenshot(path=str(out_path), full_page=True)
        print(f"Canvas inspect saved: {out_path} ({out_path.stat().st_size:,} bytes)")
        
        # Let's inspect text
        text = await page.inner_text("body")
        print("Page text snippet:\n", text[:500])
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(main())
