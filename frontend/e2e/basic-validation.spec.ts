import { test, expect } from '@playwright/test';

test('basic app check', async ({ page }) => {
  await page.goto('http://localhost:5174');
  await page.waitForTimeout(3000);
  
  await expect(page.locator('body')).toBeVisible();
  
  await page.screenshot({ path: 'basic-app-check.png' });
  
  const title = await page.title();
  console.log('Page title:', title);
  
  const appElement = page.locator('#app');
  const hasApp = await appElement.count() > 0;
  console.log('Has #app element:', hasApp);
  
  const buttons = await page.locator('button').count();
  const inputs = await page.locator('input').count();
  const links = await page.locator('a').count();
  
  console.log('Interactive elements - Buttons:', buttons, 'Inputs:', inputs, 'Links:', links);
  
  if (buttons > 0) {
    const firstButton = page.locator('button').first();
    const buttonText = await firstButton.textContent();
    console.log('First button text:', buttonText);
  }
});
