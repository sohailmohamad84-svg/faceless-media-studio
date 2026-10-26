import asyncio
from playwright.async_api import async_playwright

async def inspect_grid():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        page = browser.contexts[0].pages[0]
        
        # Inspect flow-grid-tile-container
        grid = page.locator("flow-grid-tile-container")
        print("Grid count:", await grid.count())
        if await grid.count() > 0:
            html = await grid.evaluate("el => el.innerHTML")
            print("Grid innerHTML length:", len(html))
            
            # Find all child tags of grid
            children = await grid.evaluate("""el => {
                return Array.from(el.children).map(c => ({
                    tag: c.tagName,
                    className: c.className,
                    text: c.innerText.substring(0, 80).replace(/\\n/g, ' ')
                }));
            }""")
            print(f"Grid children count: {len(children)}")
            for idx, c in enumerate(children):
                print(f"  Child {idx}: <{c['tag']}> class='{c['className']}' text='{c['text']}'")

if __name__ == "__main__":
    asyncio.run(inspect_grid())
