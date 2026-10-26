import asyncio
import os
from playwright.async_api import async_playwright

async def download_clip():
    os.makedirs("data/flow_clips", exist_ok=True)
    target_path = os.path.abspath("data/flow_clips/maglev_scene_1.mp4")
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0]
        
        dl_button = page.locator("[aria-label*='Download media'], button:has-text('download')").first
        
        # Start waiting for the download
        print("Waiting for download event...")
        async with page.expect_download(timeout=30000) as download_info:
            await dl_button.click()
            
        download = await download_info.value
        print("Download suggested filename:", download.suggested_filename)
        await download.save_as(target_path)
        print(f"Successfully saved to {target_path} (Size: {os.path.getsize(target_path)} bytes)")

if __name__ == "__main__":
    asyncio.run(download_clip())
