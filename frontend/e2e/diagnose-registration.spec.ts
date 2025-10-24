import { test, expect } from '@playwright/test';

test('diagnose registration form state', async ({ page }) => {
  await page.goto('http://localhost:5174/register');
  await page.waitForTimeout(2000);
  
  console.log('=== REGISTRATION FORM DIAGNOSIS ===');
  
  const registerButton = page.locator('button:has-text("Register")');
  const isDisabled = await registerButton.isDisabled();
  const isVisible = await registerButton.isVisible();
  const buttonText = await registerButton.textContent();
  
  console.log('Register button - Disabled:', isDisabled, 'Visible:', isVisible, 'Text:', buttonText);
  
  const buttonAttributes = await registerButton.evaluate((el) => {
    const attrs = {};
    for (const attr of el.attributes) {
      attrs[attr.name] = attr.value;
    }
    return attrs;
  });
  console.log('Button attributes:', buttonAttributes);
  
  await page.fill('input[placeholder="Choose a username"]', 'testuser');
  await page.fill('input[placeholder="Create a password"]', 'Test123!');
  await page.fill('input[placeholder="Re-enter password"]', 'Test123!');
  
  const selectWrapper = page.locator('.el-select').first();
  await selectWrapper.click();
  await page.waitForTimeout(1000);
  
  const options = await page.locator('.el-select-dropdown__item').all();
  console.log('Available roles:', options.length);
  
  for (let i = 0; i < options.length; i++) {
    const roleText = await options[i].textContent();
    console.log(`Role ${i}:`, roleText);
  }
  
  await options[0].click();
  await page.waitForTimeout(1000);
  
  const isDisabledAfter = await registerButton.isDisabled();
  console.log('Register button after form fill - Disabled:', isDisabledAfter);
  
  const errorElements = await page.locator('.el-form-item__error, .error, [class*="error"]').all();
  console.log('Validation errors found:', errorElements.length);
  
  for (let i = 0; i < errorElements.length; i++) {
    const errorText = await errorElements[i].textContent();
    console.log(`Error ${i}:`, errorText);
  }
  
  const inputs = await page.locator('input').all();
  for (let i = 0; i < inputs.length; i++) {
    const value = await inputs[i].inputValue();
    const placeholder = await inputs[i].getAttribute('placeholder');
    console.log(`Input ${i} (${placeholder}):`, value);
  }
  
  await page.screenshot({ path: 'registration-diagnosis.png' });
  
  if (isDisabledAfter) {
    console.log('Button is still disabled. Trying force click...');
    await registerButton.click({ force: true });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'force-click-result.png' });
  }
});
