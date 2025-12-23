/**
 * E2E Test: Start Coaching Session (User Story 1)
 *
 * Tests the complete flow of starting a new coaching session:
 * 1. Student describes their struggle
 * 2. Form validation works
 * 3. Session is created successfully
 * 4. Coach's first question appears
 * 5. Session ID is generated
 */

import { test, expect } from '@playwright/test';

test.describe('Start Coaching Session', () => {
  test.beforeEach(async ({ page }) => {
    // TODO: Setup authentication (login as test student)
    // await page.goto('/login');
    // await page.fill('[name="email"]', 'test@example.com');
    // await page.fill('[name="password"]', 'testpass');
    // await page.click('button[type="submit"]');

    // Navigate to coaching page
    await page.goto('/coaching');
  });

  test('should show empty form on first visit', async ({ page }) => {
    // Check that form is visible
    await expect(page.locator('textarea[name="topic"]')).toBeVisible();
    await expect(page.locator('button[type="submit"]')).toBeVisible();

    // Check that chat interface is NOT visible yet
    await expect(page.locator('[data-testid="chat-interface"]')).not.toBeVisible();
  });

  test('should validate empty topic', async ({ page }) => {
    // Try to submit without filling topic
    await page.click('button[type="submit"]');

    // Check for validation error
    await expect(page.locator('text=/Please describe your struggle/i')).toBeVisible();
  });

  test('should validate topic length (min 10 chars)', async ({ page }) => {
    // Enter too-short topic
    await page.fill('textarea[name="topic"]', 'Too short');

    await page.click('button[type="submit"]');

    // Check for validation error
    await expect(page.locator('text=/at least 10 characters/i')).toBeVisible();
  });

  test('should validate topic length (max 500 chars)', async ({ page }) => {
    // Enter too-long topic (501 characters)
    const longTopic = 'a'.repeat(501);
    await page.fill('textarea[name="topic"]', longTopic);

    await page.click('button[type="submit"]');

    // Check for validation error
    await expect(page.locator('text=/maximum 500 characters/i')).toBeVisible();
  });

  test('should show loading state while creating session', async ({ page }) => {
    // Fill valid topic
    await page.fill('textarea[name="topic"]', "I don't understand price elasticity");

    // Submit form
    await page.click('button[type="submit"]');

    // Check for loading indicator
    await expect(page.locator('text=/preparing your session/i')).toBeVisible();
  });

  test('should successfully start session and show coach question', async ({ page }) => {
    // Mock the API response (if needed)
    // await page.route('**/api/coaching/tutor-session', async (route) => {
    //   await route.fulfill({
    //     status: 200,
    //     body: JSON.stringify({
    //       session: { id: 'test-session-id', status: 'active', topic: 'test' },
    //       initial_message: { content: 'Can you explain what you understand so far?' }
    //     })
    //   });
    // });

    // Fill valid topic
    await page.fill('textarea[name="topic"]', "I don't understand price elasticity");

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for session to be created (max 5 seconds)
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible({
      timeout: 5000
    });

    // Check that coach's first message appears
    await expect(page.locator('[data-testid="coach-message"]').first()).toBeVisible();

    // Check that form is hidden
    await expect(page.locator('textarea[name="topic"]')).not.toBeVisible();
  });

  test('should handle session creation error', async ({ page }) => {
    // Mock API error
    await page.route('**/api/coaching/tutor-session', async (route) => {
      await route.fulfill({
        status: 500,
        body: JSON.stringify({
          detail: 'Internal server error'
        })
      });
    });

    // Fill valid topic
    await page.fill('textarea[name="topic"]', "I don't understand price elasticity");

    // Submit form
    await page.click('button[type="submit"]');

    // Check for error message
    await expect(page.locator('text=/error/i')).toBeVisible({
      timeout: 5000
    });

    // Check for retry button
    await expect(page.locator('button:has-text("Try again")')).toBeVisible();
  });

  test('should allow retry after error', async ({ page }) => {
    let attemptCount = 0;

    // Mock API to fail first time, succeed second time
    await page.route('**/api/coaching/tutor-session', async (route) => {
      attemptCount++;
      if (attemptCount === 1) {
        await route.fulfill({
          status: 500,
          body: JSON.stringify({ detail: 'Internal server error' })
        });
      } else {
        await route.fulfill({
          status: 200,
          body: JSON.stringify({
            session: { id: 'test-session-id', status: 'active', topic: 'test' },
            initial_message: { content: 'Can you explain what you understand so far?' }
          })
        });
      }
    });

    // Fill valid topic
    await page.fill('textarea[name="topic"]', "I don't understand price elasticity");

    // Submit form
    await page.click('button[type="submit"]');

    // Wait for error
    await expect(page.locator('button:has-text("Try again")')).toBeVisible({
      timeout: 5000
    });

    // Click retry
    await page.click('button:has-text("Try again")');

    // Check that session is created successfully
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible({
      timeout: 5000
    });
  });
});
