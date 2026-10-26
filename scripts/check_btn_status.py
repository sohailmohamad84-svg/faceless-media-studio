import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        btn = page.locator("[aria-label*='Download media']").first
        if await btn.count() > 0:
            is_disabled = await btn.get_attribute("disabled")
            enabled = await btn.is_enabled()
            print("Download button disabled attribute:", is_disabled)
            print("Download button enabled:", enabled)
        else:
            print("No download button found")

if __name__ == "__main__":
    asyncio.run(main())
