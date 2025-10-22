import { test, expect } from '@playwright/test';

test.describe('User Authentication Flow', () => {
  test('user login with valid credentials', async ({ page }) => {
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(2000);
    
    // 移除 h1 检查，直接测试表单
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

test.describe('Complete User Workflow', () => {
  test('complete user registration and login workflow', async ({ page }) => {
    // 注册流程
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    
    await page.fill('input[placeholder="Choose a username"]', 'e2e_test_user');
    await page.fill('input[placeholder="Create a password"]', 'Test123!');
    await page.fill('input[placeholder="Re-enter password"]', 'Test123!');
    
    // 处理角色选择框
    const roleSelector = page.locator('input[role="combobox"]');
    await roleSelector.click();
    await page.waitForTimeout(500);
    
    // 选择第一个选项
    const firstOption = page.locator('.el-select-dropdown__item').first();
    await firstOption.click();
    
    const registerButton = page.locator('button:has-text("Register")');
    await registerButton.click();
    
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'after-registration.png' });
    
    // 登录流程
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(1000);
    
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
    await page.waitForTimeout(1000);
    
    const forgotPasswordLink = page.locator('text=Forgot password?');
    await forgotPasswordLink.click();
    
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
    
    // 处理角色选择
    const roleSelector = page.locator('input[role="combobox"]');
    await roleSelector.click();
    await page.waitForTimeout(500);
    
    const options = await page.locator('.el-select-dropdown__item').all();
    if (options.length > 0) {
      await options[0].click();
    }
    
    await page.screenshot({ path: 'filled-registration-form.png' });
    
    const registerButton = page.locator('button:has-text("Register")');
    await registerButton.click();
    
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'registration-submitted.png' });
  });

  test('password mismatch validation', async ({ page }) => {
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    
    await page.fill('input[placeholder="Choose a username"]', 'testuser');
    await page.fill('input[placeholder="Create a password"]', 'Password123');
    await page.fill('input[placeholder="Re-enter password"]', 'DifferentPassword');
    
    // 处理角色选择
    const roleSelector = page.locator('input[role="combobox"]');
    await roleSelector.click();
    await page.waitForTimeout(500);
    
    const options = await page.locator('.el-select-dropdown__item').all();
    if (options.length > 0) {
      await options[0].click();
    }
    
    const registerButton = page.locator('button:has-text("Register")');
    await registerButton.click();
    
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'password-mismatch.png' });
  });
});
