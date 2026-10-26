import asyncio
from playwright.async_api import async_playwright

async def check_nav():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        
        # Check all items in nav list
        nav_items = await page.locator("flow-project-nav-list [role='listitem'], mat-nav-list a, mat-nav-list button").all()
        print(f"Nav items count: {len(nav_items)}")
        for it in nav_items:
            print("  Nav item:", (await it.inner_text()).strip().replace('\n', ' '))
            
        # Also check cdk-virtual-scroll-viewport
        viewport = page.locator("cdk-virtual-scroll-viewport")
        print("Viewport count:", await viewport.count())
        if await viewport.count() > 0:
            # Check scroll height
            scroll_info = await viewport.evaluate("el => ({scrollHeight: el.scrollHeight, clientHeight: el.clientHeight, scrollTop: el.scrollTop})")
            print("Viewport scroll info:", scroll_info)

if __name__ == "__main__":
    asyncio.run(check_nav())
