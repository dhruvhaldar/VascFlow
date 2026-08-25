import { test, expect } from '@playwright/test';

test('boundary conditions form is hidden and replaced by success message when all faces assigned', async ({ page }) => {
    await page.goto('/');

    const MOCK_MESH_RESPONSE = {
        n_cells: 100,
        n_points: 50,
        faces: [
            { name: 'inlet', id: 1 },
            { name: 'outlet', id: 2 }
        ],
        bounds: [0, 1, 0, 1, 0, 1],
        viz_file: 'mock_surface.vtp'
    };

    await page.route('**/process_mesh', async route => {
        await route.fulfill({ headers: { 'Access-Control-Allow-Origin': '*' }, json: MOCK_MESH_RESPONSE });
    });

    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.locator('.mesh-upload').click();
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles({
        name: 'dummy_mesh.vtu',
        mimeType: 'application/octet-stream',
        buffer: Buffer.from('dummy data')
    });

    await page.getByRole('tab', { name: 'Boundary Conditions' }).click();

    // Add first BC
    await page.locator('.add-bc select').nth(0).selectOption('inlet');
    await page.locator('.add-bc input[placeholder="Variable (e.g. Velocity)"]').fill('Velocity');
    await page.locator('.add-bc input[type="number"]').fill('10');
    await page.locator('button:has-text("Add BC")').click();

    // Check form still visible
    await expect(page.locator('.add-bc')).toBeVisible();

    // Add second (final) BC
    await page.locator('.add-bc select').nth(0).selectOption('outlet');
    await page.locator('.add-bc input[type="number"]').fill('0');
    await page.locator('button:has-text("Add BC")').click();

    // Form should be gone, success message should appear and be focused
    await expect(page.locator('.add-bc')).not.toBeVisible();
    await expect(page.locator('.empty-state:has-text("All available faces have been assigned a boundary condition.")')).toBeVisible();
    await expect(page.locator('.empty-state:has-text("All available faces have been assigned a boundary condition.")')).toBeFocused();

    // Remove one BC, form should come back
    page.once('dialog', dialog => dialog.accept());
    await page.locator('.remove-btn').first().click();

    await expect(page.locator('.add-bc')).toBeVisible();
    await expect(page.locator('.empty-state:has-text("All available faces have been assigned a boundary condition.")')).not.toBeVisible();
});
