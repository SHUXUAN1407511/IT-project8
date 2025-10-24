import { test, expect } from '@playwright/test';

test('diagnose current page structure', async ({ page }) => {
  await page.goto('http://localhost:5174');
  await page.waitForTimeout(3000);
  
  console.log('=== CURRENT PAGE DIAGNOSIS ===');
  console.log('URL:', page.url());
  console.log('Title:', await page.title());
  
  const allElements = await page.locator('*').all();
  console.log('Total elements:', allElements.length);
  
  const headings = await page.locator('h1, h2, h3, h4, h5, h6').all();
  console.log('Headings found:', headings.length);
  for (let i = 0; i < headings.length; i++) {
    const text = await headings[i].textContent();
    console.log(`Heading ${i}:`, text);
  }
  
  const inputs = await page.locator('input').all();
  console.log('Inputs found:', inputs.length);
  for (let i = 0; i < inputs.length; i++) {
    const type = await inputs[i].getAttribute('type');
    const placeholder = await inputs[i].getAttribute('placeholder');
    const name = await inputs[i].getAttribute('name');
    const id = await inputs[i].getAttribute('id');
    console.log(`Input ${i}: type=${type}, placeholder=${placeholder}, name=${name}, id=${id}`);
  }
  
  const buttons = await page.locator('button').all();
  console.log('Buttons found:', buttons.length);
  for (let i = 0; i < buttons.length; i++) {
    const text = await buttons[i].textContent();
    console.log(`Button ${i}:`, text);
  }
  
  const links = await page.locator('a').all();
  console.log('Links found:', links.length);
  for (let i = 0; i < links.length; i++) {
    const href = await links[i].getAttribute('href');
    const text = await links[i].textContent();
    console.log(`Link ${i}: href=${href}, text=${text}`);
  }
  
  await page.screenshot({ path: 'current-page-diagnosis.png' });
  
  await page.goto('http://localhost:5174/register');
  await page.waitForTimeout(2000);
  console.log('=== REGISTRATION PAGE ===');
  console.log('Registration URL:', page.url());
  
  const regInputs = await page.locator('input').all();
  console.log('Registration inputs:', regInputs.length);
  for (let i = 0; i < regInputs.length; i++) {
    const type = await regInputs[i].getAttribute('type');
    const placeholder = await regInputs[i].getAttribute('placeholder');
    console.log(`Reg Input ${i}: type=${type}, placeholder=${placeholder}`);
  }
  
  await page.screenshot({ path: 'current-registration-page.png' });
});
