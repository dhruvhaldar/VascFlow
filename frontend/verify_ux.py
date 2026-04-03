import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Navigate to the local dev server
        await page.goto('http://localhost:5173')

        # Wait for the tabs to load
        await page.wait_for_selector('.tabs-nav')

        # Take screenshot of the initial state showing tabs
        await page.screenshot(path='../screenshots/tabs_initial.png')

        # Focus on the Physics tab to check tabindex styling
        await page.locator('#tab-physics').click()
        await page.wait_for_selector('#panel-physics')
        await page.locator('#panel-physics').focus()
        await page.screenshot(path='../screenshots/tabpanel_focused.png')

        # Upload a dummy mesh via API mock (if applicable) or directly navigate
        # Assuming we can mock response to allow navigating to BCs tab
        await page.route("http://localhost:8000/process_mesh", lambda route: route.fulfill(
            status=200,
            json={
                "n_cells": 100,
                "n_points": 50,
                "faces": [{"name": "inlet", "id": 1}, {"name": "outlet", "id": 2}],
                "viz_file": "dummy.vtp"
            },
            headers={'Access-Control-Allow-Origin': '*'}
        ))

        # Handle BC Tab
        await page.locator('#tab-bcs').click()

        # Mock file upload to bypass empty state
        file_input = page.locator('input[type="file"]')
        if await file_input.count() == 0:
            await page.locator('#tab-mesh').click()
            file_input = page.locator('input[type="file"]')

        import tempfile
        import os
        with tempfile.NamedTemporaryFile(suffix='.vtu', delete=False) as f:
            f.write(b"dummy vtu content")
            temp_path = f.name

        await file_input.set_input_files(temp_path)
        os.remove(temp_path)

        # Wait for BC editor to become active
        await page.locator('#tab-bcs').click()
        await page.wait_for_selector('.add-bc select')

        # Select "inlet" and add BC
        await page.locator('.add-bc select[title="Select Face"]').select_option('inlet')
        await page.locator('.add-bc button').click()

        # Wait for list item to appear and take a screenshot
        await page.wait_for_selector('.bc-editor ul li')
        await page.screenshot(path='../screenshots/bc_remove_button.png')

        await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
