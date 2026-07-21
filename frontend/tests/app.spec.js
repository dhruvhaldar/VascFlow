import { test, expect } from '@playwright/test';

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

test.describe('svFSI Configurator App', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('has correct title and header', async ({ page }) => {
    const header = page.locator('header h1');
    await expect(header).toContainText('svFSI Configurator');
  });

  test('sidebar navigation works', async ({ page }) => {
    await expect(page.locator('.sidebar .tabs-nav button.active')).toContainText('Mesh');
    await expect(page.locator('#panel-mesh')).toContainText('Upload a .vtu, .vtp, or .vtk file');

    await page.getByRole('tab', { name: 'Physics' }).click();
    await expect(page.locator('.sidebar .tabs-nav button.active')).toContainText('Physics');
    await expect(page.locator('.physics-config')).toBeVisible();

    await page.getByRole('tab', { name: 'Boundary Conditions' }).click();
    await expect(page.locator('.sidebar .tabs-nav button.active')).toContainText('Boundary Conditions');
    await expect(page.locator('h3:has-text("Boundary Conditions")')).toBeVisible();

    await page.getByRole('tab', { name: 'General' }).click();
    await expect(page.locator('.sidebar .tabs-nav button.active')).toContainText('General');
    await expect(page.locator('.general-config')).toBeVisible();

    // Test Home and End keys for tab navigation
    await page.keyboard.press('Home');
    await expect(page.locator('.sidebar .tabs-nav button.active')).toContainText('Mesh');
    await expect(page.locator('#panel-mesh')).toContainText('Upload a .vtu, .vtp, or .vtk file');

    await page.keyboard.press('End');
    await expect(page.locator('.sidebar .tabs-nav button.active')).toContainText('General');
    await expect(page.locator('.general-config')).toBeVisible();

    // Test Spatial keys (Up and Down)
    await page.keyboard.press('Home');
    await page.keyboard.press('ArrowDown');
    await expect(page.locator('.sidebar .tabs-nav button.active')).toContainText('Boundary Conditions');

    await page.keyboard.press('ArrowUp');
    await expect(page.locator('.sidebar .tabs-nav button.active')).toContainText('Mesh');

    await page.keyboard.press('ArrowRight');
    await page.keyboard.press('ArrowDown');
    await expect(page.locator('.sidebar .tabs-nav button.active')).toContainText('General');
  });

  test('generate_input API is called and XML response is rendered', async ({ page }) => {
    await page.route('**/generate_input', async route => {
      await route.fulfill({
        headers: { 'Access-Control-Allow-Origin': '*' },
        json: { xml: '<svFSIFile><GeneralSimulationParameters /></svFSIFile>' }
      });
    });

    await page.getByRole('button', { name: /Generate XML/ }).click();
    await expect(page.getByLabel('Generated XML Preview')).toHaveValue(/<svFSIFile>/);
  });

  test('mesh upload, BC management and process_mesh API flow', async ({ page }) => {
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

    await expect(page.locator('.mesh-info')).toContainText('Loaded: dummy_mesh.vtu');
    await expect(page.locator('.mesh-info')).toContainText('Cells: 100, Points: 50');
    await expect(page.locator('.mesh-info')).toContainText('Detected Faces: 2');

    await page.getByRole('tab', { name: 'Boundary Conditions' }).click();

    const faceSelect = page.locator('.add-bc select').nth(0);
    await faceSelect.selectOption('inlet');

    const bcTypeSelect = page.locator('.add-bc select').nth(1);
    await bcTypeSelect.selectOption('Dirichlet');

    const variableInput = page.locator('.add-bc input[placeholder="Variable (e.g. Velocity)"]');
    await variableInput.fill('Velocity');

    const valueInput = page.locator('.add-bc input[type="number"]');
    await valueInput.fill('10.5');

    const profileSelect = page.locator('.add-bc select').nth(2);
    await profileSelect.selectOption('Parabolic');

    const addBcButton = page.locator('button:has-text("Add BC")');
    await addBcButton.click();

    const bcList = page.locator('.bc-editor ul li');
    await expect(bcList).toHaveCount(1);
    await expect(bcList.first()).toContainText('inlet: Dirichlet Velocity=10.5 (Parabolic)');

    await faceSelect.selectOption('outlet');
    await bcTypeSelect.selectOption('Neumann');
    await valueInput.fill('0');
    await profileSelect.selectOption('Flat');
    await addBcButton.click();

    await expect(bcList).toHaveCount(2);
    await expect(bcList.nth(1)).toContainText('outlet: Neumann Velocity=0 (Flat)');

    const removeButton = bcList.first().locator('button');

    page.on('dialog', async dialog => {
      if (dialog.message().includes('inlet')) {
        await dialog.dismiss();
      } else {
        await dialog.accept();
      }
    });

    await removeButton.click();
    await expect(bcList).toHaveCount(2);

    // Let's test the accept branch on the same button for robustness
    await page.evaluate(() => window.confirm = () => true);
    await removeButton.click();

    await expect(bcList).toHaveCount(1);
    await expect(bcList.first()).toContainText('outlet: Neumann Velocity=0 (Flat)');
  });

  test('visualizer requests processed mesh file from static files endpoint', async ({ page }) => {
    await page.route('**/process_mesh', async route => {
      await route.fulfill({ headers: { 'Access-Control-Allow-Origin': '*' }, json: MOCK_MESH_RESPONSE });
    });

    await page.route('**/files/mock_surface.vtp', async route => {
      await route.fulfill({
        headers: { 'Access-Control-Allow-Origin': '*' },
        status: 200,
        contentType: 'application/xml',
        body: `<?xml version="1.0"?>\n<VTKFile type="PolyData" version="0.1" byte_order="LittleEndian"><PolyData><Piece NumberOfPoints="0" NumberOfVerts="0" NumberOfLines="0" NumberOfStrips="0" NumberOfPolys="0"><Points><DataArray type="Float32" NumberOfComponents="3" format="ascii"></DataArray></Points></Piece></PolyData></VTKFile>`
      });
    });

    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.locator('.mesh-upload').click();
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles({
      name: 'dummy_mesh.vtu',
      mimeType: 'application/octet-stream',
      buffer: Buffer.from('dummy data')
    });

    await expect(page.locator('.viewer-header span[role="status"]')).toContainText('Previewing dummy_mesh.vtu');
    await expect(page.getByTestId('viewer-canvas')).toBeVisible();
  });
});
