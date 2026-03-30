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
    await expect(header).toHaveText('svFSI Configurator');
  });

  test('sidebar navigation works', async ({ page }) => {
    await expect(page.locator('.sidebar nav button.active')).toHaveText('Mesh');
    await expect(page.locator('.config-panel')).toContainText('Upload a .vtu or .vtp file');

    await page.click('text="Physics"');
    await expect(page.locator('.sidebar nav button.active')).toHaveText('Physics');
    await expect(page.locator('.physics-config')).toBeVisible();

    await page.click('text="Boundary Conditions"');
    await expect(page.locator('.sidebar nav button.active')).toHaveText('Boundary Conditions');
    await expect(page.locator('h3:has-text("Boundary Conditions")')).toBeVisible();

    await page.click('text="General"');
    await expect(page.locator('.sidebar nav button.active')).toHaveText('General');
    await expect(page.locator('.general-config')).toBeVisible();
  });

  test('generate_input API is called and XML response is rendered', async ({ page }) => {
    await page.route('http://localhost:8000/generate_input', async route => {
      await route.fulfill({
        headers: {
          'Access-Control-Allow-Origin': '*'
        },
        json: { xml: '<svFSIFile><GeneralSimulationParameters /></svFSIFile>' }
      });
    });

    await page.getByRole('button', { name: 'Generate XML' }).click();
    await expect(page.getByLabel('Generated XML Preview')).toHaveValue(/<svFSIFile>/);
  });

  test('mesh upload, BC management and process_mesh API flow', async ({ page }) => {
    await page.route('http://localhost:8000/process_mesh', async route => {
      await route.fulfill({
        headers: {
          'Access-Control-Allow-Origin': '*'
        },
        json: MOCK_MESH_RESPONSE
      });
    });

    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.locator('input[type="file"]').click();
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles({
      name: 'dummy_mesh.vtu',
      mimeType: 'application/octet-stream',
      buffer: Buffer.from('dummy data')
    });

    await expect(page.locator('.mesh-info')).toContainText('Loaded: dummy_mesh.vtu');
    await expect(page.locator('.mesh-info')).toContainText('Cells: 100, Points: 50');
    await expect(page.locator('.mesh-info')).toContainText('Detected Faces: 2');

    await page.click('text="Boundary Conditions"');

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
    await removeButton.click();

    await expect(bcList).toHaveCount(1);
    await expect(bcList.first()).toContainText('outlet: Neumann Velocity=0 (Flat)');
  });

  test('visualizer requests processed mesh file from static files endpoint', async ({ page }) => {
    await page.route('http://localhost:8000/process_mesh', async route => {
      await route.fulfill({
        headers: {
          'Access-Control-Allow-Origin': '*'
        },
        json: MOCK_MESH_RESPONSE
      });
    });

    await page.route('http://localhost:8000/files/mock_surface.vtp', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'application/xml',
        body: `<?xml version="1.0"?>\n<VTKFile type="PolyData" version="0.1" byte_order="LittleEndian"><PolyData><Piece NumberOfPoints="0" NumberOfVerts="0" NumberOfLines="0" NumberOfStrips="0" NumberOfPolys="0"><Points><DataArray type="Float32" NumberOfComponents="3" format="ascii"></DataArray></Points></Piece></PolyData></VTKFile>`
      });
    });

    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.locator('input[type="file"]').click();
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles({
      name: 'dummy_mesh.vtu',
      mimeType: 'application/octet-stream',
      buffer: Buffer.from('dummy data')
    });

    await expect(page.locator('.viewer-header span')).toContainText('Previewing mock_surface.vtp');
    await expect(page.getByTestId('viewer-canvas')).toBeVisible();
  });
});
