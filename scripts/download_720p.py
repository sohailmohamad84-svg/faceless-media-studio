import asyncio
import os
import time
from playwright.async_api import async_playwright

async def trigger_download():
    downloads_dir = "C:\\Users\\Sohail\\Downloads"
    before_files = set(os.listdir(downloads_dir))
    
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        
        # Click "720p Original size" button in menu
        item = page.locator("[role='menuitem']:has-text('720p')").first
        if await item.count() == 0:
            print("720p menu item not found!")
            return
            
        print("Clicking '720p Original size'...")
        await item.click()
        
    # Now monitor Downloads folder for up to 30 seconds
    print("Waiting for file to appear in Downloads folder...")
    new_file = None
    for _ in range(30):
        time.sleep(1)
        current_files = set(os.listdir(downloads_dir))
        added = current_files - before_files
        # Check for completed mp4 (not .crdownload)
        for f in added:
            if f.endswith(".mp4") and not f.endswith(".crdownload"):
                new_file = os.path.join(downloads_dir, f)
                break
        if new_file:
            break
            
    if new_file:
        print(f"Downloaded file: {new_file} (Size: {os.path.getsize(new_file)} bytes)")
        dest = os.path.abspath("data/flow_clips/maglev_scene_1.mp4")
        os.makedirs("data/flow_clips", exist_ok=True)
        import shutil
        shutil.copy2(new_file, dest)
        print(f"Copied to: {dest}")
    else:
        print("Download did not complete in 30s. Checking downloads folder:")
        print(os.listdir(downloads_dir)[:10])

if __name__ == "__main__":
    asyncio.run(trigger_download())
