from playwright.sync_api import sync_playwright
from pathlib import Path

ARTIFACT_DIR = Path(r"C:\Users\Sohail\.gemini\antigravity\brain\eb4bd0b7-d463-4e01-b351-a971179e01ed")

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1360, 'height': 1100})
        page.goto('http://localhost:8501/')
        page.wait_for_timeout(6000)
        tabs = page.locator("[role='tab']").all()
        print(f"Tabs count: {len(tabs)}")
        if len(tabs) > 1:
            tabs[1].click()
            page.wait_for_timeout(3000)
            
            # Select Boeing 747 in the selectbox
            select_box = page.locator("div[data-baseweb='select']").first
            if select_box.count() > 0:
                select_box.click()
                page.wait_for_timeout(1000)
                opt = page.locator("li[role='option']:has-text('Boeing 747')").first
                if opt.count() > 0:
                    opt.click()
                    page.wait_for_timeout(3000)

            out_path = ARTIFACT_DIR / "boeing_dashboard_local_tab2.png"
            page.screenshot(path=str(out_path), full_page=False)
            print(f"Saved boeing_dashboard_local_tab2.png ({out_path.stat().st_size:,} bytes)")
        browser.close()

if __name__ == "__main__":
    main()
