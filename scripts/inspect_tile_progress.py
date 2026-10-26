import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        tile = page.locator("flow-video-tile").last
        print("Tile innerHTML:", await tile.evaluate("el => el.innerHTML"))
        print("Tile text:", (await tile.inner_text()).strip().replace('\n', ' '))

if __name__ == "__main__":
    asyncio.run(main())
