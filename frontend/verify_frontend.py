from playwright.sync_api import sync_playwright
import os
import glob

def run_cuj(page):
    # Navigate to the app
    page.goto("http://localhost:4173")
    page.wait_for_timeout(1000)

    # 1. Start on Mesh tab, check title
    page.screenshot(path="screenshots/01_mesh_tab.png")
    title_mesh = page.title()
    print(f"Title on Mesh tab: {title_mesh}")
    page.wait_for_timeout(500)

    # 2. Navigate to Physics tab, check title
    page.get_by_role("tab", name="Physics").click()
    page.wait_for_timeout(1000)
    page.screenshot(path="screenshots/02_physics_tab.png")
    title_physics = page.title()
    print(f"Title on Physics tab: {title_physics}")
    page.wait_for_timeout(500)

    # 3. Navigate to Boundary Conditions tab, check title
    page.get_by_role("tab", name="Boundary Conditions").click()
    page.wait_for_timeout(1000)
    page.screenshot(path="screenshots/03_bc_tab.png")
    title_bc = page.title()
    print(f"Title on BC tab: {title_bc}")
    page.wait_for_timeout(500)

    # 4. Navigate to General tab, check title
    page.get_by_role("tab", name="General").click()
    page.wait_for_timeout(1000)
    page.screenshot(path="screenshots/04_general_tab.png")
    title_general = page.title()
    print(f"Title on General tab: {title_general}")
    page.wait_for_timeout(1000)

    # Final assertion to ensure they are actually changing
    assert "Mesh" in title_mesh
    assert "Physics" in title_physics
    assert "Boundary Conditions" in title_bc
    assert "General" in title_general

if __name__ == "__main__":
    os.makedirs("screenshots", exist_ok=True)
    os.makedirs("frontend_videos", exist_ok=True)

    # Clear old videos
    for f in glob.glob("frontend_videos/*.webm"):
        os.remove(f)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="frontend_videos"
        )
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()
            browser.close()

    videos = glob.glob("frontend_videos/*.webm")
    if videos:
        print(f"Video saved to {videos[0]}")
