import asyncio
import json
from playwright.async_api import async_playwright

async def inspect_all_tiles():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        
        tiles = await page.locator("flow-video-tile").all()
        print(f"Total flow-video-tile elements: {len(tiles)}")
        
        for i, tile in enumerate(tiles):
            # check images, videos, or text in each tile
            imgs = await tile.locator("img").all()
            img_srcs = [await img.get_attribute("src") for img in imgs]
            txt = (await tile.inner_text()).strip().replace("\n", " ")
            print(f"Tile {i+1}: text='{txt[:60]}...' | imgs={len(imgs)} | src={img_srcs}")

if __name__ == "__main__":
    asyncio.run(inspect_all_tiles())
