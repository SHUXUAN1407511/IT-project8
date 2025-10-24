import { test, expect } from '@playwright/test';

test.describe('User Authentication Flow', () => {
  test('user login with valid credentials', async ({ page }) => {
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(2000);
    
    const usernameInput = page.locator('input[placeholder="e.g. sc.user"]');
    const passwordInput = page.locator('input[placeholder="Enter password"]');
    const loginButton = page.locator('button:has-text("Sign In")');
    
    await expect(usernameInput).toBeVisible();
    await expect(passwordInput).toBeVisible();
    await expect(loginButton).toBeVisible();
    
    await usernameInput.fill('testuser');
    await passwordInput.fill('password123');
    await loginButton.click();
    
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'after-login.png' });
  });

  test('login form validation', async ({ page }) => {
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(1000);
    
    const loginButton = page.locator('button:has-text("Sign In")');
    await loginButton.click();
    
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'empty-form-validation.png' });
  });

  test('navigate to registration page', async ({ page }) => {
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(1000);
    
    const registerLink = page.locator('a[href="/register"]');
    await registerLink.click();
    
    await page.waitForTimeout(2000);
    await expect(page).toHaveURL('http://localhost:5174/register');
    await page.screenshot({ path: 'registration-page.png' });
  });
});

test.describe('Registration Without Role Selection', () => {
  test('fill registration form without role', async ({ page }) => {
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    
    await page.fill('input[placeholder="Choose a username"]', 'test_user_no_role');
    await page.fill('input[placeholder="Create a password"]', 'Test123!');
    await page.fill('input[placeholder="Re-enter password"]', 'Test123!');
    
    const registerButton = page.locator('button:has-text("Register")');
    await registerButton.click();
    
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'registration-no-role.png' });
  });

  test('test registration with different approach', async ({ page }) => {
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    
    await page.fill('input[placeholder="Choose a username"]', 'simple_user');
    await page.fill('input[placeholder="Create a password"]', 'Simple123');
    await page.fill('input[placeholder="Re-enter password"]', 'Simple123');
    
    await page.screenshot({ path: 'simple-registration.png' });
    
    const errorMessages = await page.locator('.error-message, .el-message, .el-form-item__error').all();
    console.log('Error messages found:', errorMessages.length);
  });
});

test.describe('Navigation Flow', () => {
  test('forgot password flow', async ({ page }) => {
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(1000);
    
    const forgotPasswordLink = page.locator('text=Forgot password?');
    await forgotPasswordLink.click();
    
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'forgot-password-page.png' });
  });
});

test.describe('Basic Form Tests', () => {
  test('test login with different users', async ({ page }) => {
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(1000);
    
    const testUsers = [
      { username: 'admin', password: 'admin123' },
      { username: 'teacher', password: 'teacher123' },
      { username: 'student', password: 'student123' }
    ];
    
    for (const user of testUsers) {
      await page.fill('input[placeholder="e.g. sc.user"]', user.username);
      await page.fill('input[placeholder="Enter password"]', user.password);
      await page.click('button:has-text("Sign In")');
      
      await page.waitForTimeout(2000);
      await page.screenshot({ path: `login-${user.username}.png` });
      
      await page.goto('http://localhost:5174');
      await page.waitForTimeout(1000);
    }
  });

  test('explore registration form structure', async ({ page }) => {
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    
    const allInputs = await page.locator('input').all();
    console.log('Total inputs on registration page:', allInputs.length);
    
    for (let i = 0; i < allInputs.length; i++) {
      const input = allInputs[i];
      const placeholder = await input.getAttribute('placeholder');
      const type = await input.getAttribute('type');
      const role = await input.getAttribute('role');
      const id = await input.getAttribute('id');
      
      console.log(`Input ${i}: type=${type}, role=${role}, placeholder=${placeholder}, id=${id}`);
    }
    
    const selectWrapper = page.locator('.el-select, [class*="select"]').first();
    if (await selectWrapper.count() > 0) {
      await selectWrapper.click();
      await page.waitForTimeout(1000);
      await page.screenshot({ path: 'select-clicked.png' });
    }
    
    const dropdownOptions = await page.locator('.el-select-dropdown__item, [class*="option"]').all();
    console.log('Dropdown options found:', dropdownOptions.length);
  });
});
