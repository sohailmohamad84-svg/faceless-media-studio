import asyncio
import json
import sys
from playwright.async_api import async_playwright

async def inspect_dl():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0]
        
        btn = page.locator("[aria-label*='Download media'], button:has-text('download')").first
        if await btn.count() == 0:
            print("No download button found!", flush=True)
            return
            
        print("Download button visible:", await btn.is_visible(), flush=True)
        print("Download button HTML:", await btn.evaluate("el => el.outerHTML"), flush=True)
        print("Download button attributes:", await btn.evaluate("el => Array.from(el.attributes).map(a => `${a.name}=${a.value}`)"), flush=True)

        # Let's inspect any click listeners or what happens when clicked
        # Let's also check if there is an <a download> element or if clicking opens a menu
        print("Clicking download button...", flush=True)
        await btn.click()
        await page.wait_for_timeout(2000)
        await page.screenshot(path="flow_after_dl_click.png")
        print("Screenshot taken: flow_after_dl_click.png", flush=True)
        
        # Check if a menu popped up (e.g. 720p, 1080p, MP4, etc.)
        menu_items = await page.locator("[role='menuitem'], [class*='menu'] button, [class*='mat-mdc-menu-item']").all()
        print(f"Menu items after click: {len(menu_items)}", flush=True)
        for m in menu_items:
            print("Menu item:", (await m.inner_text()).strip(), flush=True)

if __name__ == "__main__":
    asyncio.run(inspect_dl())
