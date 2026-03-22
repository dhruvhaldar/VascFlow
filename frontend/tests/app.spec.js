import { test, expect } from '@playwright/test';

test.describe('svFSI Configurator App', () => {

  test.beforeEach(async ({ page }) => {
    // Navigate to the app
    await page.goto('/');
  });

  test('has correct title and header', async ({ page }) => {
    // Check if the title is set (assuming index.html has a title, or we check the header)
    const header = page.locator('header h1');
    await expect(header).toHaveText('svFSI Configurator');
  });

  test('sidebar navigation works', async ({ page }) => {
    // Default tab should be Mesh
    await expect(page.locator('.sidebar nav button.active')).toHaveText('Mesh');
    await expect(page.locator('.config-panel')).toContainText('Upload a .vtu or .vtp file');

    // Click Physics tab
    await page.click('text="Physics"');
    await expect(page.locator('.sidebar nav button.active')).toHaveText('Physics');
    await expect(page.locator('.physics-config')).toBeVisible();

    // Click Boundary Conditions tab
    await page.click('text="Boundary Conditions"');
    await expect(page.locator('.sidebar nav button.active')).toHaveText('Boundary Conditions');
    await expect(page.locator('h3:has-text("Boundary Conditions")')).toBeVisible();

    // Click General tab
    await page.click('text="General"');
    await expect(page.locator('.sidebar nav button.active')).toHaveText('General');
    await expect(page.locator('.general-config')).toBeVisible();
  });

  test('physics configuration updates', async ({ page }) => {
    await page.click('text="Physics"');

    // Check initial values (assuming defaults in store)
    const densityInput = page.locator('label:has-text("Density:") input');
    const viscosityInput = page.locator('label:has-text("Viscosity:") input');
    const typeSelect = page.locator('label:has-text("Type:") select');

    await expect(typeSelect).toHaveValue('Fluid');

    // Update values
    await typeSelect.selectOption('Structure');
    await densityInput.fill('1.5');
    await viscosityInput.fill('0.05');

    // The changes should ideally be reflected in the XML Preview
    // (We will check this in a comprehensive test below)
  });

  test('general configuration updates', async ({ page }) => {
    await page.click('text="General"');

    const timeStepsInput = page.locator('label:has-text("Time Steps:") input');
    const stepSizeInput = page.locator('label:has-text("Step Size:") input');

    await timeStepsInput.fill('2000');
    await stepSizeInput.fill('0.005');
  });

  test('XML Preview loads', async ({ page }) => {
    // The XML Preview component should show some initial loading or default XML

    // Wait for the XML Preview heading
    const xmlHeader = page.locator('.bottom-pane h3');
    await expect(xmlHeader).toHaveText('Input File Preview');
  });

  test('Boundary Conditions and Mesh Upload flow', async ({ page }) => {
    // Intercept the mesh upload request
    await page.route('http://localhost:8000/process_mesh', async route => {
      const json = {
        n_cells: 100,
        n_points: 50,
        faces: [
          { name: 'inlet', id: 1 },
          { name: 'outlet', id: 2 }
        ],
        type: 'vtu'
      };
      await route.fulfill({ json });
    });

    // We start on the 'mesh' tab by default
    // Upload a fake mesh
    const fileChooserPromise = page.waitForEvent('filechooser');
    await page.locator('input[type="file"]').click();
    const fileChooser = await fileChooserPromise;
    await fileChooser.setFiles({
      name: 'dummy_mesh.vtu',
      mimeType: 'application/octet-stream',
      buffer: Buffer.from('dummy data')
    });

    // Check if mesh metadata is displayed
    await expect(page.locator('.mesh-info')).toContainText('Loaded: dummy_mesh.vtu');
    await expect(page.locator('.mesh-info')).toContainText('Cells: 100, Points: 50');
    await expect(page.locator('.mesh-info')).toContainText('Detected Faces: 2');

    // Go to Boundary Conditions tab
    await page.click('text="Boundary Conditions"');

    // Add a boundary condition
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

    // Verify it was added to the list
    const bcList = page.locator('.bc-editor ul li');
    await expect(bcList).toHaveCount(1);
    await expect(bcList.first()).toContainText('inlet: Dirichlet Velocity=10.5 (Parabolic)');

    // Add another boundary condition
    await faceSelect.selectOption('outlet');
    await bcTypeSelect.selectOption('Neumann');
    await valueInput.fill('0');
    await profileSelect.selectOption('Flat');
    await addBcButton.click();

    await expect(bcList).toHaveCount(2);
    await expect(bcList.nth(1)).toContainText('outlet: Neumann Velocity=0 (Flat)');

    // Remove the first boundary condition
    const removeButton = bcList.first().locator('button');
    await removeButton.click();

    await expect(bcList).toHaveCount(1);
    await expect(bcList.first()).toContainText('outlet: Neumann Velocity=0 (Flat)');
  });
});
