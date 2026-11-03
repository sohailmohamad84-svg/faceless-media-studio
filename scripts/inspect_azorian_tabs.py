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
        
        # Check sessions menu or click on "Sunken Soviet Submarine"
        session_header = page.locator("*:has-text('Sunken Soviet Submarine')").first
        print("Session header text:", await session_header.inner_text() if await session_header.count() > 0 else "None")
        
        # Click on "Scenes" in left sidebar
        scenes_tab = page.locator("button:has-text('Scenes'), [aria-label*='Scenes']").first
        if await scenes_tab.count() > 0:
            print("Clicking Scenes tab...")
            await scenes_tab.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path=str(ARTIFACT_DIR / "azorian_scenes_tab.png"))
            
        # Click on "All media" in left sidebar
        all_media = page.locator("button:has-text('All media'), [aria-label*='All media']").first
        if await all_media.count() > 0:
            print("Clicking All media tab...")
            await all_media.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path=str(ARTIFACT_DIR / "azorian_all_media_tab.png"))
            
        # Inspect what is inside the chat area
        chat_msgs = await page.locator(".message, .chat-message, [role='log'], .message-content, flow-chat-message").all()
        print("Chat messages count:", len(chat_msgs))
        for idx, m in enumerate(chat_msgs):
            print(f"  Msg {idx}: {(await m.inner_text())[:150]}")
            
        await ctx.close()

if __name__ == "__main__":
    asyncio.run(main())
