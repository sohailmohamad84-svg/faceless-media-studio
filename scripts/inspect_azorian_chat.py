import asyncio
import os
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        ctx = await p.chromium.launch_persistent_context(
            user_data_dir=os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\AutomationData"),
            executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            ignore_default_args=["--enable-automation"]
        )
        page = ctx.pages[0] if ctx.pages else await ctx.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined });")
        await page.goto("https://flow.google.com/project/2c6f19c8-b792-4427-b525-40c5f99bed37", timeout=30000)
        await page.wait_for_timeout(3000)
        
        body_text = await page.inner_text("body")
        lines = [l.strip() for l in body_text.splitlines() if l.strip()]
        print("Total lines in page:", len(lines))
        for i, l in enumerate(lines):
            print(f"{i}: {l}")

        await ctx.close()

if __name__ == "__main__":
    asyncio.run(inspect())
