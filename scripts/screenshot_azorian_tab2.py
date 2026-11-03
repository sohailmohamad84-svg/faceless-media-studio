import asyncio
import sys
from pathlib import Path
from playwright.async_api import async_playwright

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

ARTIFACT_DIR = Path(r"C:\Users\Sohail\.gemini\antigravity\brain\eb4bd0b7-d463-4e01-b351-a971179e01ed")

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1400, "height": 1800})
        await page.goto("http://localhost:8501", timeout=30000)
        await page.wait_for_timeout(4000)
        
        # Click Tab 2
        tab2 = page.locator("button[role='tab']:has-text('Creator Quality & Sign-Off'), [data-baseweb='tab']:has-text('Creator Quality & Sign-Off')").first
        if await tab2.count() > 0:
            await tab2.click()
            await page.wait_for_timeout(2500)
            
        await page.screenshot(path=str(ARTIFACT_DIR / "azorian_dashboard_tab2.png"), full_page=True)
        print("Screenshot saved: azorian_dashboard_tab2.png")
        
        txt = await page.inner_text("body")
        for l in txt.splitlines():
            l = l.strip()
            if any(k in l.lower() for k in ["azorian", "score", "status", "ready", "claw", "gate", "approve", "sign-off", "100/100"]):
                print(l)
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
