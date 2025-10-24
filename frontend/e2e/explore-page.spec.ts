import { test, expect } from '@playwright/test';

test('explore page structure', async ({ page }) => {
  await page.goto('http://localhost:5174');
  await page.waitForTimeout(3000);
  
  await page.screenshot({ path: 'explore-homepage.png' });
  
  console.log('=== PAGE ANALYSIS ===');
  console.log('Title:', await page.title());
  
  const buttons = await page.locator('button').all();
  console.log('Buttons found:', buttons.length);
  for (let i = 0; i < buttons.length; i++) {
    const text = await buttons[i].textContent();
    console.log(`Button ${i}:`, text?.substring(0, 50));
  }
  
  const inputs = await page.locator('input').all();
  console.log('Inputs found:', inputs.length);
  for (let i = 0; i < inputs.length; i++) {
    const placeholder = await inputs[i].getAttribute('placeholder');
    const name = await inputs[i].getAttribute('name');
    const type = await inputs[i].getAttribute('type');
    console.log(`Input ${i}: type=${type}, name=${name}, placeholder=${placeholder}`);
  }
  
  const links = await page.locator('a').all();
  console.log('Links found:', links.length);
  for (let i = 0; i < links.length; i++) {
    const href = await links[i].getAttribute('href');
    const text = await links[i].textContent();
    console.log(`Link ${i}: href=${href}, text=${text}`);
  }
  
  const selectors = ['#app', '.login', '.dashboard', '.container', '.main', '.header', '.navigation', '.nav'];
  for (const selector of selectors) {
    const element = page.locator(selector);
    const count = await element.count();
    if (count > 0) {
      console.log(`Selector "${selector}": found ${count} elements`);
    }
  }
  
  const bodyText = await page.locator('body').textContent();
  console.log('Body text sample:', bodyText?.substring(0, 200));
});
