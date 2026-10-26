import asyncio
from playwright.async_api import async_playwright

async def inspect():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        print("URL:", page.url)
        print("Title:", await page.title())
        await page.screenshot(path="flow_current_canvas.png")
        
        # Check all flow-video-tile or media elements
        tiles = await page.locator("flow-video-tile").all()
        print("flow-video-tile count:", len(tiles))
        for i, t in enumerate(tiles):
            print(f"Tile {i}: visible={await t.is_visible()}")

        # Check left sidebar Videos list
        video_tab = page.locator("button:has-text('Videos')")
        print("Videos tab count:", await video_tab.count())

if __name__ == "__main__":
    asyncio.run(inspect())
