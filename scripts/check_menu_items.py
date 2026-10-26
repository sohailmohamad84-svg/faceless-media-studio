import asyncio
import sys
from playwright.async_api import async_playwright

async def inspect_menu():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        
        # Check all menu panels or role=menu
        menus = await page.locator("[role='menu'], [class*='mat-mdc-menu-panel']").all()
        print(f"Found {len(menus)} menu panels", flush=True)
        for m in menus:
            items = await m.locator("[role='menuitem'], button").all()
            print(f"Panel items ({len(items)}):", flush=True)
            for it in items:
                print("  item text:", (await it.inner_text()).strip().replace('\n', ' '), flush=True)
                print("  item HTML:", await it.evaluate("el => el.outerHTML"), flush=True)

if __name__ == "__main__":
    asyncio.run(inspect_menu())
