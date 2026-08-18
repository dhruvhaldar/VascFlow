from playwright.sync_api import sync_playwright
import time
import os

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://localhost:5173')

    # 1. Upload the mock mesh
    file_input = page.locator('input[type="file"]')
    file_input.set_input_files('/tmp/cube.vtp')

    # Wait for processing and BC tab to be active
    # The MeshUpload component shows text like "Loaded: cube.vtp" or "Detected Faces:"
    page.wait_for_selector('text="Loaded: cube.vtp"', timeout=10000)

    # Click BC tab
    page.get_by_role('tab', name='Boundary Conditions').click()

    # Wait for the select dropdown to appear
    page.wait_for_selector('.add-bc select')
    face_select = page.locator('.add-bc select').first
    options = face_select.locator('option').all()

    option_values = []
    for opt in options:
        val = opt.get_attribute('value')
        if val and val != "":
            option_values.append(val)

    print(f"Found faces to assign: {option_values}")

    # 3. Assign a BC for each face
    for face_val in option_values:
        print(f"Assigning BC to face: {face_val}")
        # Select face
        face_select.select_option(value=face_val)

        # Fill variable
        page.locator('input[placeholder="Variable (e.g. Velocity)"]').fill('Velocity')

        # Fill value
        page.locator('input[placeholder="e.g. 10.5"]').fill('10')

        # Click Add BC
        page.get_by_role('button', name='Add BC').click()
        time.sleep(0.5) # Wait for state to update

    # 4. Verify the success container appears
    print("Waiting for success container...")
    page.wait_for_selector('.all-faces-assigned', timeout=5000)

    # Take screenshot
    os.makedirs('/home/jules/verification/screenshots', exist_ok=True)
    page.screenshot(path='/home/jules/verification/screenshots/bc-success.png')
    print("Screenshot saved to /home/jules/verification/screenshots/bc-success.png")

    browser.close()
