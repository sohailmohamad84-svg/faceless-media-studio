import asyncio
from playwright.async_api import async_playwright

async def check_chat():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        
        # Click All Media to go back to full canvas if needed
        all_media = page.locator("flow-project-nav-list *:has-text('All media')").last
        await all_media.click()
        await page.wait_for_timeout(1000)
        
        # Check all flow-chat-bubble elements
        bubbles = await page.locator("flow-chat-bubble").all()
        print(f"Chat bubbles count: {len(bubbles)}")
        for i, b in enumerate(bubbles):
            txt = (await b.inner_text()).strip().replace('\n', ' ')
            print(f"Bubble {i}: {txt[:80]}")
            
        # Check all video tiles or media in the entire document
        v_tiles = await page.locator("flow-video-tile").all()
        print(f"flow-video-tile count in All Media: {len(v_tiles)}")

if __name__ == "__main__":
    asyncio.run(check_chat())
