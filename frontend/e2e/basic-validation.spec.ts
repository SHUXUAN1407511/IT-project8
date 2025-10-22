import { test, expect } from '@playwright/test';

test('basic app check', async ({ page }) => {
  await page.goto('http://localhost:5174');
  await page.waitForTimeout(3000);
  
  // 检查页面基本元素
  await expect(page.locator('body')).toBeVisible();
  
  // 截图用于分析
  await page.screenshot({ path: 'basic-app-check.png' });
  
  // 检查页面标题
  const title = await page.title();
  console.log('Page title:', title);
  
  // 检查是否有 Vue/React 应用挂载点
  const appElement = page.locator('#app');
  const hasApp = await appElement.count() > 0;
  console.log('Has #app element:', hasApp);
  
  // 检查是否有任何交互元素
  const buttons = await page.locator('button').count();
  const inputs = await page.locator('input').count();
  const links = await page.locator('a').count();
  
  console.log('Interactive elements - Buttons:', buttons, 'Inputs:', inputs, 'Links:', links);
  
  // 测试基本交互
  if (buttons > 0) {
    const firstButton = page.locator('button').first();
    const buttonText = await firstButton.textContent();
    console.log('First button text:', buttonText);
  }
});
