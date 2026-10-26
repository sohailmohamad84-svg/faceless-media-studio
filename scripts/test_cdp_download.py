import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0]
        
        # Configure CDP session to allow downloads
        cdp = await context.new_cdp_session(page)
        await cdp.send("Browser.setDownloadBehavior", {
            "behavior": "allow",
            "downloadPath": "C:\\Users\\Sohail\\Antigravity\\faceless-media-studio\\data\\flow_clips",
            "eventsEnabled": True
        })
        
        # Track all network requests when clicking download
        requests = []
        page.on("request", lambda r: requests.append(r.url) if any(x in r.url for x in [".mp4", "download", "blob", "flow-content", "video"]) else None)
        
        dl_button = page.locator("[aria-label*='Download media'], button:has-text('download')").first
        print("Clicking download button...")
        await dl_button.click()
        
        await page.wait_for_timeout(5000)
        
        print("Relevant network requests caught:")
        for r in requests:
            print("  ", r[:150])

if __name__ == "__main__":
    asyncio.run(main())
