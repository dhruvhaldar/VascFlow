import { test, expect } from '@playwright/test';

test('skip link works', async ({ page }) => {
  await page.goto('/');
  await page.keyboard.press('Tab');
  const skipLink = page.locator('.skip-link');
  await expect(skipLink).toBeFocused();
  await page.keyboard.press('Enter');
  await expect(page.locator('#main-content')).toBeFocused();
});
