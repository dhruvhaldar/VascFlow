from playwright.sync_api import sync_playwright
import time

def verify_frontend():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(record_video_dir="frontend_videos")
        page = context.new_page()

        page.goto("http://localhost:5173")
        time.sleep(2) # wait for page to load

        # Navigate to Boundary Conditions tab
        page.click("button:has-text('Boundary Conditions')")
        time.sleep(1)

        # Hover over the add BC button
        add_bc_btn = page.locator("button:has-text('Add BC')")
        add_bc_btn.hover()
        time.sleep(1)

        # Take screenshot
        page.screenshot(path="frontend_videos/bc_tab_screenshot.png")

        # Close
        context.close()
        browser.close()

if __name__ == "__main__":
    verify_frontend()