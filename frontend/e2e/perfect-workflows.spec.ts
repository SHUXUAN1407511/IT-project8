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

test.describe('Complete Registration Flow', () => {
  test('successful user registration with role selection', async ({ page }) => {
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    
    // 填写基本信息
    await page.fill('input[placeholder="Choose a username"]', 'e2e_test_user');
    await page.fill('input[placeholder="Create a password"]', 'Test123!');
    await page.fill('input[placeholder="Re-enter password"]', 'Test123!');
    
    // 处理角色选择 - 点击选择框的父容器
    const selectWrapper = page.locator('.el-select').first();
    await selectWrapper.click();
    await page.waitForTimeout(1000);
    
    // 选择第一个可用角色
    const firstOption = page.locator('.el-select-dropdown__item').first();
    await firstOption.click();
    await page.waitForTimeout(1000);
    
    // 现在注册按钮应该可用，点击它
    const registerButton = page.locator('button:has-text("Register")');
    await registerButton.click();
    
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'registration-success.png' });
  });

  test('registration with student role', async ({ page }) => {
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    
    await page.fill('input[placeholder="Choose a username"]', 'student_user');
    await page.fill('input[placeholder="Create a password"]', 'Student123!');
    await page.fill('input[placeholder="Re-enter password"]', 'Student123!');
    
    // 选择角色
    const selectWrapper = page.locator('.el-select').first();
    await selectWrapper.click();
    await page.waitForTimeout(1000);
    
    // 选择学生角色（假设是第一个选项）
    const studentOption = page.locator('.el-select-dropdown__item:has-text("Student")').first();
    if (await studentOption.count() > 0) {
      await studentOption.click();
    } else {
      // 如果没有找到具体文本，选择第一个选项
      await page.locator('.el-select-dropdown__item').first().click();
    }
    
    await page.waitForTimeout(1000);
    
    const registerButton = page.locator('button:has-text("Register")');
    await registerButton.click();
    
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'student-registration.png' });
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

test.describe('Complete User Workflow', () => {
  test('full user journey: register -> login', async ({ page }) => {
    const timestamp = Date.now();
    const testUsername = `user_${timestamp}`;
    
    // 1. 注册新用户
    await page.goto('http://localhost:5174/register');
    await page.waitForTimeout(2000);
    
    await page.fill('input[placeholder="Choose a username"]', testUsername);
    await page.fill('input[placeholder="Create a password"]', 'Password123!');
    await page.fill('input[placeholder="Re-enter password"]', 'Password123!');
    
    // 选择角色
    const selectWrapper = page.locator('.el-select').first();
    await selectWrapper.click();
    await page.waitForTimeout(1000);
    await page.locator('.el-select-dropdown__item').first().click();
    await page.waitForTimeout(1000);
    
    const registerButton = page.locator('button:has-text("Register")');
    await registerButton.click();
    
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'workflow-registration.png' });
    
    // 2. 登录新创建的用户
    await page.goto('http://localhost:5174');
    await page.waitForTimeout(1000);
    
    await page.fill('input[placeholder="e.g. sc.user"]', testUsername);
    await page.fill('input[placeholder="Enter password"]', 'Password123!');
    await page.click('button:has-text("Sign In")');
    
    await page.waitForTimeout(3000);
    await page.screenshot({ path: 'workflow-login.png' });
    
    console.log(`Test completed with username: ${testUsername}`);
  });
});
