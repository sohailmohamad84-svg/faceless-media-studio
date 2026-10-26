import asyncio
import json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp("http://localhost:9222")
        context = browser.contexts[0]
        page = context.pages[0]
        
        # Let's inspect the entire DOM structure around canvas and chat
        # Check all custom elements or divs with role or class
        elements_info = await page.evaluate("""() => {
            const results = [];
            // find all images or canvas or video elements
            const media = document.querySelectorAll('img, video, canvas');
            for (let m of media) {
                results.push({
                    tag: m.tagName,
                    src: m.src || m.getAttribute('src') || '',
                    width: m.clientWidth,
                    height: m.clientHeight,
                    alt: m.alt || ''
                });
            }
            return results;
        }""")
        print("Media elements:", json.dumps(elements_info, indent=2))
        
        # Check if there are cards or nodes in canvas
        nodes = await page.evaluate("""() => {
            const cards = [];
            document.querySelectorAll('[data-node-id], [class*=\"node\"], [class*=\"card\"], [class*=\"item\"]').forEach(el => {
                if (el.innerText && el.innerText.length > 5) {
                    cards.push({
                        className: el.className,
                        text: el.innerText.substring(0, 100)
                    });
                }
            });
            return cards.slice(0, 20);
        }""")
        print(f"Cards/Nodes ({len(nodes)}):")
        for n in nodes[:10]:
            print("  ", n)

if __name__ == "__main__":
    asyncio.run(main())
