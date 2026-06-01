import { test, expect } from '@playwright/test';

test('xml generation error handling', async ({ page }) => {
  await page.route('http://localhost:8000/generate_input', async route => {
    await route.fulfill({
      status: 400,
      headers: { 'Access-Control-Allow-Origin': '*' },
      json: { detail: "Invalid density value" }
    });
  });

  await page.goto('/');
  await page.getByRole('tab', { name: 'Physics' }).click();
  const input = page.locator('input[type="number"]').first();
  await input.fill('0');

  await page.getByRole('button', { name: 'Generate XML' }).click();
  await page.waitForTimeout(500);

  const content = await page.content();
  expect(content.includes('❌ Failed to generate XML')).toBe(true);
  expect(content.includes('Invalid density value')).toBe(true);
});
