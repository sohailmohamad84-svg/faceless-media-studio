import asyncio
from playwright.async_api import async_playwright

async def check_videos_tab():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        
        # Click "videocam Videos"
        vid_btn = page.locator("flow-project-nav-list *:has-text('Videos')").last
        print("Clicking Videos nav item...", flush=True)
        await vid_btn.click()
        await page.wait_for_timeout(2000)
        
        await page.screenshot(path="flow_videos_view.png")
        print("Screenshot saved to flow_videos_view.png", flush=True)
        
        # Check all cards / items in the view
        tiles = await page.locator("flow-video-tile, [class*='tile'], [class*='card']").all()
        print(f"Tiles found: {len(tiles)}", flush=True)
        
        # Check all download buttons
        dl_btns = await page.locator("[aria-label*='Download'], button:has-text('download')").all()
        print(f"Download buttons found: {len(dl_btns)}", flush=True)
        for i, b in enumerate(dl_btns):
            print(f"  DL btn {i}: label='{await b.get_attribute('aria-label')}' text='{await b.inner_text()}' visible={await b.is_visible()}")

if __name__ == "__main__":
    asyncio.run(check_videos_tab())
