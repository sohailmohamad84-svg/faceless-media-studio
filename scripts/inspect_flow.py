import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0]
        
        print("Page URL:", page.url)
        print("Page Title:", await page.title())
        
        # Take a screenshot
        await page.screenshot(path="flow_state_full.png")
        print("Screenshot saved to flow_state_full.png")
        
        # Get all text
        text = await page.evaluate("() => document.body.innerText")
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        print(f"Total lines: {len(lines)}")
        for l in lines:
            if any(k in l.lower() for k in ["queue", "generat", "video", "wait", "credit", "percent", "download", "scene", "maglev", "l0"]):
                print("->", l)

if __name__ == "__main__":
    asyncio.run(main())
