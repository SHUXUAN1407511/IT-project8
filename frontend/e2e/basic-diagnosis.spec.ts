import { test, expect } from '@playwright/test';

test('basic page diagnosis', async ({ page }) => {
  await page.goto('http://localhost:5174/register');
  await page.waitForTimeout(5000); // 更长等待时间
  
  console.log('=== BASIC PAGE DIAGNOSIS ===');
  console.log('Current URL:', page.url());
  console.log('Page title:', await page.title());
  
  // 检查页面内容
  const bodyText = await page.textContent('body');
  console.log('Body text sample:', bodyText?.substring(0, 500));
  
  // 检查所有按钮
  const allButtons = await page.locator('button').all();
  console.log('Total buttons found:', allButtons.length);
  
  for (let i = 0; i < allButtons.length; i++) {
    const button = allButtons[i];
    const text = await button.textContent();
    const isVisible = await button.isVisible();
    console.log(`Button ${i}: text="${text}", visible=${isVisible}`);
  }
  
  // 检查所有包含"Register"文本的元素
  const registerElements = await page.locator('text=Register').all();
  console.log('Elements with "Register" text:', registerElements.length);
  
  for (let i = 0; i < registerElements.length; i++) {
    const element = registerElements[i];
    const tagName = await element.evaluate(el => el.tagName);
    const text = await element.textContent();
    console.log(`Register element ${i}: <${tagName}> "${text}"`);
  }
  
  // 截图当前页面
  await page.screenshot({ path: 'basic-diagnosis.png', fullPage: true });
});

test('check if registration page loads correctly', async ({ page }) => {
  await page.goto('http://localhost:5174/register');
  await page.waitForTimeout(3000);
  
  // 检查是否有输入框
  const inputs = await page.locator('input').all();
  console.log('Inputs on registration page:', inputs.length);
  
  // 检查是否有表单
  const forms = await page.locator('form').all();
  console.log('Forms found:', forms.length);
  
  // 检查是否有任何提交按钮
  const submitButtons = await page.locator('button[type="submit"], input[type="submit"]').all();
  console.log('Submit buttons:', submitButtons.length);
  
  // 检查页面是否包含注册相关文本
  const pageContent = await page.textContent('body');
  const hasRegisterText = pageContent?.toLowerCase().includes('register');
  const hasSignUpText = pageContent?.toLowerCase().includes('sign up');
  
  console.log('Has "register" text:', hasRegisterText);
  console.log('Has "sign up" text:', hasSignUpText);
  
  await page.screenshot({ path: 'registration-load-check.png' });
});

test('test alternative registration flows', async ({ page }) => {
  await page.goto('http://localhost:5174');
  await page.waitForTimeout(2000);
  
  // 检查登录页面是否有注册链接
  const registerLinks = await page.locator('a').all();
  let registerLinkFound = false;
  
  for (const link of registerLinks) {
    const href = await link.getAttribute('href');
    const text = await link.textContent();
    if (href?.includes('register') || text?.toLowerCase().includes('register')) {
      console.log('Found register link:', { href, text });
      registerLinkFound = true;
      
      // 点击注册链接
      await link.click();
      await page.waitForTimeout(3000);
      
      console.log('After click URL:', page.url());
      await page.screenshot({ path: 'after-register-click.png' });
      break;
    }
  }
  
  if (!registerLinkFound) {
    console.log('No register link found on login page');
  }
});
