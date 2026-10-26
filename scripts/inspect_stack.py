import asyncio
from playwright.async_api import async_playwright

async def inspect_stack():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        
        stack = page.locator("flow-tile-container").first
        print("Stack text:", (await stack.inner_text()).replace('\n', ' '))
        print("Clicking stack to expand...")
        await stack.click()
        await page.wait_for_timeout(2000)
        
        await page.screenshot(path="flow_stack_expanded.png")
        print("Saved flow_stack_expanded.png")
        
        # Now check video tiles inside expanded stack
        v_tiles = await page.locator("flow-video-tile").all()
        print(f"Video tiles inside expanded stack: {len(v_tiles)}")
        for i, vt in enumerate(v_tiles):
            txt = (await vt.inner_text()).replace('\n', ' ')
            img = await vt.locator("img").first
            src = await img.get_attribute("src") if await img.count() > 0 else "no img"
            print(f"  Tile {i+1}: text='{txt[:60]}' | img={src[:60]}")

if __name__ == "__main__":
    asyncio.run(inspect_stack())
