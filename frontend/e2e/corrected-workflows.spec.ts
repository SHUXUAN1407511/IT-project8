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

  test('successful user registration', async ({ page }) => {
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    
    // 填写注册表单
    await page.fill('input[placeholder="Choose a username"]', 'testuser_' + Date.now());
    await page.fill('input[placeholder="Create a password"]', 'Test123!');
    await page.fill('input[placeholder="Re-enter password"]', 'Test123!');
    
    // 选择角色
    const selectWrapper = page.locator('.el-select').first();
    await selectWrapper.click();
    await page.waitForTimeout(1000);
    
    // 选择第一个角色（Administrator）
    await page.locator('.el-select-dropdown__item:has-text("Administrator")').first().click();
    await page.waitForTimeout(1000);
    
    // 点击创建账户按钮
    const createAccountButton = page.locator('button:has-text("Create Account")');
    await createAccountButton.click();
    
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'registration-success.png' });
  });

  test('registration with different roles', async ({ page }) => {
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    
    const timestamp = Date.now();
    
    // 测试 Subject Coordinator 角色
    await page.fill('input[placeholder="Choose a username"]', 'coordinator_' + timestamp);
    await page.fill('input[placeholder="Create a password"]', 'Coordinator123!');
    await page.fill('input[placeholder="Re-enter password"]', 'Coordinator123!');
    
    const selectWrapper = page.locator('.el-select').first();
    await selectWrapper.click();
    await page.waitForTimeout(1000);
    
    await page.locator('.el-select-dropdown__item:has-text("Subject Coordinator")').first().click();
    await page.waitForTimeout(1000);
    
    await page.locator('button:has-text("Create Account")').click();
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'coordinator-registration.png' });
  });

  test('registration form validation', async ({ page }) => {
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    
    // 尝试空表单提交
    await page.locator('button:has-text("Create Account")').click();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: 'empty-form-validation.png' });
    
    // 测试密码不匹配
    await page.fill('input[placeholder="Choose a username"]', 'testuser');
    await page.fill('input[placeholder="Create a password"]', 'Password123');
    await page.fill('input[placeholder="Re-enter password"]', 'DifferentPassword');
    
    await page.locator('.el-select').first().click();
    await page.waitForTimeout(1000);
    await page.locator('.el-select-dropdown__item:has-text("Tutor")').first().click();
    await page.waitForTimeout(1000);
    
    await page.locator('button:has-text("Create Account")').click();
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'password-mismatch.png' });
  });
});

test.describe('Navigation Flow', () => {
  test('complete navigation workflow', async ({ page }) => {
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(1000);
    
    // 去注册页面
    await page.click('a[href="/register"]');
    await page.waitForTimeout(2000);
    await expect(page).toHaveURL('http://localhost:5174/register');
    
    // 返回登录页面
    await page.click('text=Back to sign in');
    await page.waitForTimeout(2000);
    await expect(page).toHaveURL('http://localhost:5174');
    
    await page.screenshot({ path: 'navigation-workflow.png' });
  });

  test('forgot password flow', async ({ page }) => {
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(1000);
    
    await page.click('text=Forgot password?');
    await page.waitForTimeout(2000);
    await page.screenshot({ path: 'forgot-password.png' });
  });
});

test.describe('Complete User Journey', () => {
  test('full user journey: register -> login', async ({ page }) => {
    const timestamp = Date.now();
    const testUsername = `journey_user_${timestamp}`;
    const testPassword = 'Journey123!';
    
    console.log(`Testing with username: ${testUsername}`);
    
    // 1. 注册新用户
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    
    await page.fill('input[placeholder="Choose a username"]', testUsername);
    await page.fill('input[placeholder="Create a password"]', testPassword);
    await page.fill('input[placeholder="Re-enter password"]', testPassword);
    
    // 选择角色
    await page.locator('.el-select').first().click();
    await page.waitForTimeout(1000);
    await page.locator('.el-select-dropdown__item:has-text("Tutor")').first().click();
    await page.waitForTimeout(1000);
    
    await page.locator('button:has-text("Create Account")').click();
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'journey-registration.png' });
    
    // 2. 登录新创建的用户
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(1000);
    
    await page.fill('input[placeholder="e.g. sc.user"]', testUsername);
    await page.fill('input[placeholder="Enter password"]', testPassword);
    await page.click('button:has-text("Sign In")');
    
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'journey-login.png' });
    
    console.log('User journey completed successfully');
  });
});
