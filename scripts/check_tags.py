import asyncio
from playwright.async_api import async_playwright

async def check():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        
        # Check all custom tags on page
        tags = await page.evaluate("""() => {
            const allTags = {};
            document.querySelectorAll('*').forEach(el => {
                if (el.tagName.includes('-')) {
                    allTags[el.tagName] = (allTags[el.tagName] || 0) + 1;
                }
            });
            return allTags;
        }""")
        print("Custom tags:", tags)
        
        # Check all images on page
        imgs = await page.evaluate("""() => {
            return Array.from(document.querySelectorAll('img')).map(i => ({
                src: i.src.substring(0, 80),
                alt: i.alt,
                w: i.clientWidth,
                h: i.clientHeight
            }));
        }""")
        print(f"Total images: {len(imgs)}")
        for img in imgs:
            print("  IMG:", img)

if __name__ == "__main__":
    asyncio.run(check())
