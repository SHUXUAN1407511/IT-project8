import { test, expect } from '@playwright/test';

test.describe('Complete User Workflow', () => {
  test('complete user registration and template creation workflow', async ({ page }) => {
    await page.goto('/');
    
    await page.click('a[href*="/register"]');
    await page.fill('input[name="username"]', 'e2e_test_user');
    await page.fill('input[name="email"]', 'e2e@test.com');
    await page.fill('input[name="password"]', 'Test123!');
    await page.fill('input[name="confirmPassword"]', 'Test123!');
    await page.selectOption('select[name="role"]', 'tutor');
    await page.click('button[type="submit"]');
    
    await page.waitForURL('**/dashboard');
    await expect(page.locator('h1')).toContainText('Dashboard');
    
    await page.click('a[href*="/templates"]');
    await page.click('button:has-text("Create New Template")');
    
    await page.fill('input[name="templateName"]', 'E2E Test Assignment');
    await page.selectOption('select[name="course"]', 'CS101');
    await page.selectOption('select[name="aiLevel"]', 'R2');
    await page.fill('textarea[name="description"]', 'This is an automated test assignment');
    await page.fill('textarea[name="requirements"]', 'Complete all sections with proper AI declaration');
    
    await page.click('button:has-text("Create Template")');
    await expect(page.locator('.success-toast')).toContainText('Template created successfully');
    
    await page.click('a[href*="/assignments"]');
    await expect(page.locator('.assignment-list')).toContainText('E2E Test Assignment');
  });
});

test.describe('Admin Management Flow', () => {
  test('admin user management workflow', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('input[name="username"]', 'admin');
    await page.fill('input[name="password"]', 'admin123');
    await page.click('button[type="submit"]');
    
    await page.waitForURL('**/admin');
    await page.click('a[href*="/admin/users"]');
    
    await page.click('button:has-text("Add User")');
    await page.fill('input[name="newUsername"]', 'new_tutor_user');
    await page.fill('input[name="newEmail"]', 'tutor@university.edu');
    await page.selectOption('select[name="newRole"]', 'tutor');
    await page.click('button:has-text("Create User")');
    
    await expect(page.locator('.user-table')).toContainText('new_tutor_user');
    
    await page.click('a[href*="/admin/courses"]');
    await page.click('button:has-text("Add Course")');
    
    await page.fill('input[name="courseCode"]', 'TEST101');
    await page.fill('input[name="courseName"]', 'Test Course');
    await page.selectOption('select[name="semester"]', '2025S1');
    await page.selectOption('select[name="coordinator"]', 'admin');
    await page.click('button:has-text("Create Course")');
    
    await expect(page.locator('.course-table')).toContainText('TEST101');
  });
});

test.describe('AI Scale Integration Flow', () => {
  test('student submits assignment with AI declaration', async ({ page }) => {
    await page.goto('/login');
    
    await page.fill('input[name="username"]', 'student1');
    await page.fill('input[name="password"]', 'student123');
    await page.click('button[type="submit"]');
    
    await page.waitForURL('**/dashboard');
    await page.click('a[href*="/my-assignments"]');
    
    await page.click('.assignment-item:first-child');
    await page.click('button:has-text("Start Assignment")');
    
    await page.fill('textarea[name="answer"]', 'This is my assignment submission.');
    await page.selectOption('select[name="aiUsageLevel"]', 'R2');
    await page.fill('textarea[name="aiDeclaration"]', 'I used AI for research assistance but wrote the final content myself.');
    
    await page.click('button:has-text("Submit Assignment")');
    await expect(page.locator('.submission-success')).toContainText('Assignment submitted successfully');
    
    await page.click('a[href*="/submissions"]');
    await expect(page.locator('.submission-history')).toContainText('R2');
  });
});
