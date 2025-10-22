import { test, expect } from '@playwright/test';

test.describe('User Authentication Flow', () => {
  test('user login with valid credentials', async ({ page }) => {
    await page.goto('http://localhost:5174');
    await expect(page.locator('h1')).toContainText('AI Use Declaration Platform');
    await page.fill('input[placeholder="e.g. sc.user"]', 'testuser');
    await page.fill('input[placeholder="Enter password"]', 'password123');
    await page.click('button:has-text("Sign In")');
    await page.waitForTimeout(3000);
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
    await expect(page).toHaveURL('http://localhost:5174/register');
    await page.screenshot({ path: 'registration-page.png' });
  });
});

test.describe('Complete User Workflow', () => {
  test('complete user registration and login workflow', async ({ page }) => {
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    
    await page.fill('input[placeholder="Choose a username"]', 'e2e_test_user');
    await page.fill('input[placeholder="Create a password"]', 'Test123!');
    await page.fill('input[placeholder="Re-enter password"]', 'Test123!');
    await page.fill('input:not([placeholder])', 'e2e@test.com');
    
    const registerButton = page.locator('button:has-text("Register"), button:has-text("Sign Up")');
    await registerButton.click();
    
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'after-registration.png' });
    
    await page.goto('http://localhost:5174');
    await page.fill('input[placeholder="e.g. sc.user"]', 'e2e_test_user');
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

test.describe('Registration Form Tests', () => {
  test('fill complete registration form', async ({ page }) => {
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    
    await page.fill('input[placeholder="Choose a username"]', 'new_test_user');
    await page.fill('input[placeholder="Create a password"]', 'SecurePass123!');
    await page.fill('input[placeholder="Re-enter password"]', 'SecurePass123!');
    await page.fill('input:not([placeholder])', 'newuser@example.com');
    
    await page.screenshot({ path: 'filled-registration-form.png' });
    
    const registerButton = page.locator('button:has-text("Register")');
    if (await registerButton.count() > 0) {
      await registerButton.click();
      await page.waitForTimeout(3000);
      await page.screenshot({ path: 'registration-submitted.png' });
    }
  });

  test('password mismatch validation', async ({ page }) => {
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    
    await page.fill('input[placeholder="Choose a username"]', 'testuser');
    await page.fill('input[placeholder="Create a password"]', 'Password123');
    await page.fill('input[placeholder="Re-enter password"]', 'DifferentPassword');
    await page.fill('input:not([placeholder])', 'test@example.com');
    
    const registerButton = page.locator('button:has-text("Register")');
    await registerButton.click();
    
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'password-mismatch.png' });
  });
});
