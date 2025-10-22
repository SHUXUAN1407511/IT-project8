import { test, expect } from '@playwright/test';

test.describe('User Authentication Flow', () => {
  test('user login with valid credentials', async ({ page }) => {
    await page.goto('http://localhost:5174');
    await expect(page.locator('h1')).toContainText('AI Use Declaration Platform');
    await expect(page.locator('button:has-text("Sign In")')).toBeVisible();
    await page.fill('input[placeholder*="e.g. sc.user"]', 'testuser');
    await page.fill('input[placeholder="Enter password"]', 'password123');
    await page.click('button:has-text("Sign In")');
    await page.waitForTimeout(3000);
    const currentUrl = page.url();
    console.log('After login URL:', currentUrl);
    await page.screenshot({ path: 'after-login.png' });
  });

  test('login form validation', async ({ page }) => {
    await page.goto('http://localhost:5174');
    await page.click('button:has-text("Sign In")');
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'empty-form-validation.png' });
  });

  test('navigate to registration page', async ({ page }) => {
    await page.goto('http://localhost:5174');
    await page.click('a[href="/register"]');
    await page.waitForTimeout(2000);
    const currentUrl = page.url();
    expect(currentUrl).toContain('/register');
    await page.screenshot({ path: 'registration-page.png' });
    const registrationInputs = await page.locator('input').count();
    console.log('Registration page inputs:', registrationInputs);
  });
});

test.describe('Complete User Workflow', () => {
  test('complete user registration and login workflow', async ({ page }) => {
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    const inputs = await page.locator('input').all();
    console.log('Registration form inputs count:', inputs.length);
    if (inputs.length >= 4) {
      await page.fill('input:first-of-type', 'e2e_test_user');
      await page.fill('input:nth-of-type(2)', 'e2e@test.com');
      await page.fill('input:nth-of-type(3)', 'Test123!');
      await page.fill('input:nth-of-type(4)', 'Test123!');
    }
    const registerButton = page.locator('button:has-text("Register"), button:has-text("Sign Up")');
    if (await registerButton.count() > 0) {
      await registerButton.click();
      await page.waitForTimeout(3000);
      await page.screenshot({ path: 'after-registration.png' });
    }
    await page.goto('http://localhost:5174');
    await page.fill('input[placeholder*="e.g. sc.user"]', 'e2e_test_user');
    await page.fill('input[placeholder="Enter password"]', 'Test123!');
    await page.click('button:has-text("Sign In")');
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'final-login-attempt.png' });
  });
});

test.describe('Navigation Flow', () => {
  test('forgot password flow', async ({ page }) => {
    await page.goto('http://localhost:5174');
    await page.click('text=Forgot password?');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'forgot-password-page.png' });
  });
});
