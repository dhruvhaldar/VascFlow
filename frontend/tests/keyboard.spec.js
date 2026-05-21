import { test, expect } from '@playwright/test';

test.describe('svFSI Configurator Keyboard Shortcuts', () => {
  test('Cmd/Ctrl+Enter triggers XML generation', async ({ page }) => {
    await page.goto('/');

    // Change a setting to make XML outdated
    await page.getByRole('tab', { name: 'Physics' }).click();
    await page.getByPlaceholder('e.g. 1.06').fill('1.1');

    // Set up route to fulfill generate API
    await page.route('http://localhost:8000/generate_input', async route => {
      await route.fulfill({
        headers: { 'Access-Control-Allow-Origin': '*' },
        json: { xml: '<svFSIFile>\n  <Generated>true</Generated>\n</svFSIFile>' }
      });
    });

    // Press Cmd/Ctrl + Enter anywhere on the page
    await page.keyboard.press('Control+Enter');

    // Verify it was generated
    await expect(page.getByLabel('Generated XML Preview')).toHaveValue(/<Generated>true<\/Generated>/);
  });
});
