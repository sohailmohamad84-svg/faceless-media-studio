import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0]
        
        # Find the image with alt or src containing flow-content
        target_img = page.locator('img[src*="flow-content.google"]').first
        count = await target_img.count()
        print(f"Target img count: {count}")
        
        if count > 0:
            # Let's inspect its parent elements
            info = await target_img.evaluate("""el => {
                let curr = el;
                let path = [];
                for (let i = 0; i < 5; i++) {
                    if (!curr) break;
                    path.push({
                        tag: curr.tagName,
                        className: curr.className,
                        innerHTML: curr.innerHTML.substring(0, 300)
                    });
                    curr = curr.parentElement;
                }
                return path;
            }""")
            print("Parent hierarchy:")
            for p_info in info:
                print(f"<{p_info['tag']}> {p_info['className']}")
            
            # Click on the image to open details / player
            print("Clicking thumbnail...")
            await target_img.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path="flow_after_click_thumb.png")
            
            # Check if any new dialog or video player opened
            new_videos = await page.locator("video").all()
            print(f"Video elements after click: {len(new_videos)}")
            for v in new_videos:
                print("Video src:", await v.get_attribute("src"))
                
            # Check for download button
            dl_buttons = await page.locator("button:has-text('download'), [aria-label*='Download'], [aria-label*='download']").all()
            print(f"Download buttons found: {len(dl_buttons)}")
            for b in dl_buttons:
                print("Download button text:", await b.inner_text(), "aria-label:", await b.get_attribute("aria-label"))

if __name__ == "__main__":
    asyncio.run(main())
