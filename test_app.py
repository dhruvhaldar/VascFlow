from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("http://localhost:5173")
    page.wait_for_timeout(2000)
    page.screenshot(path="screenshot1.png")

    # Click BCs tab
    page.locator("text=Boundary Conditions").click()
    page.wait_for_timeout(1000)
    page.screenshot(path="screenshot2.png")

    browser.close()
