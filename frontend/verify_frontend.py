import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        # Mock the API responses
        await page.route("http://localhost:8000/process_mesh", lambda route: route.fulfill(
            headers={"Access-Control-Allow-Origin": "*"},
            json={
                "n_cells": 100,
                "n_points": 50,
                "faces": [{"name": "inlet", "id": 1}],
                "bounds": [0, 1, 0, 1, 0, 1],
                "viz_file": "mock_surface.vtp"
            }
        ))

        await page.route("http://localhost:8000/files/mock_surface.vtp", lambda route: route.fulfill(
            headers={"Access-Control-Allow-Origin": "*"},
            status=200,
            content_type="application/xml",
            body='<?xml version="1.0"?>\n<VTKFile type="PolyData" version="0.1" byte_order="LittleEndian"><PolyData><Piece NumberOfPoints="0" NumberOfVerts="0" NumberOfLines="0" NumberOfStrips="0" NumberOfPolys="0"><Points><DataArray type="Float32" NumberOfComponents="3" format="ascii"></DataArray></Points></Piece></PolyData></VTKFile>'
        ))

        await page.goto("http://localhost:5173")

        # Trigger mesh upload
        async with page.expect_file_chooser() as fc_info:
            await page.locator('input[type="file"]').click()
        file_chooser = await fc_info.value
        await file_chooser.set_files(files=[{"name": "mock_mesh.vtu", "mimeType": "application/octet-stream", "buffer": b"dummy"}])

        # Wait for rendering to complete (simulated)
        await page.wait_for_selector(".viewer-header span:has-text('Previewing mock_mesh.vtu')", timeout=5000)

        await page.screenshot(path="/home/jules/verification/viewer_status.png")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())
