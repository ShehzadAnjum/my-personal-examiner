/**
 * E2E Test: Chat Conversation (User Story 2)
 *
 * Tests the complete flow of chatting with the AI coach:
 * 1. Start session (prerequisite from User Story 1)
 * 2. See coach's first question
 * 3. Send message to coach
 * 4. Receive coach response
 * 5. Continue conversation
 * 6. Auto-scroll behavior
 * 7. Offline/online handling
 * 8. Message retry on error
 */

import { test, expect } from '@playwright/test';

test.describe('Chat Conversation', () => {
  test.beforeEach(async ({ page }) => {
    // TODO: Setup authentication
    // Navigate to coaching page
    await page.goto('/coaching');

    // Start a session (prerequisite)
    await page.fill('textarea[name="topic"]', "I don't understand price elasticity");
    await page.click('button[type="submit"]');

    // Wait for chat interface to appear
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible({
      timeout: 5000
    });
  });

  test('should display coach first question', async ({ page }) => {
    // Check that first coach message is visible
    const coachMessage = page.locator('[data-testid="coach-message"]').first();
    await expect(coachMessage).toBeVisible();

    // Check message has content
    await expect(coachMessage).not.toBeEmpty();
  });

  test('should display message input', async ({ page }) => {
    // Check that message input is visible
    await expect(page.locator('[data-testid="message-input"]')).toBeVisible();

    // Check that send button is visible
    await expect(page.locator('[data-testid="send-button"]')).toBeVisible();
  });

  test('should send student message', async ({ page }) => {
    // Type message
    await page.fill('[data-testid="message-input"]', 'What is price elasticity?');

    // Send message
    await page.click('[data-testid="send-button"]');

    // Check that student message appears (optimistic update)
    const studentMessage = page.locator('[data-testid="student-message"]').last();
    await expect(studentMessage).toBeVisible();
    await expect(studentMessage).toContainText('What is price elasticity?');

    // Check that message input is cleared
    await expect(page.locator('[data-testid="message-input"]')).toHaveValue('');
  });

  test('should receive coach response after sending message', async ({ page }) => {
    // Send message
    await page.fill('[data-testid="message-input"]', 'What is price elasticity?');
    await page.click('[data-testid="send-button"]');

    // Wait for coach response (max 15 seconds)
    const coachMessages = page.locator('[data-testid="coach-message"]');
    const initialCount = await coachMessages.count();

    // Wait for new coach message
    await expect(async () => {
      const newCount = await coachMessages.count();
      expect(newCount).toBeGreaterThan(initialCount);
    }).toPass({ timeout: 15000 });
  });

  test('should show typing indicator while coach is typing', async ({ page }) => {
    // Send message
    await page.fill('[data-testid="message-input"]', 'What is price elasticity?');
    await page.click('[data-testid="send-button"]');

    // Check for typing indicator (should appear within 2 seconds)
    await expect(page.locator('[data-testid="typing-indicator"]')).toBeVisible({
      timeout: 2000
    });

    // Typing indicator should disappear after coach responds
    await expect(page.locator('[data-testid="typing-indicator"]')).not.toBeVisible({
      timeout: 15000
    });
  });

  test('should display timestamps for messages', async ({ page }) => {
    // Check that messages have timestamps
    const timestamp = page.locator('[data-testid="message-timestamp"]').first();
    await expect(timestamp).toBeVisible();

    // Timestamp should be in readable format (e.g., "2:30 PM")
    const timestampText = await timestamp.textContent();
    expect(timestampText).toMatch(/\d{1,2}:\d{2}/);
  });

  test('should auto-scroll to latest message', async ({ page }) => {
    // Send multiple messages to fill the chat
    for (let i = 0; i < 5; i++) {
      await page.fill('[data-testid="message-input"]', `Message ${i + 1}`);
      await page.click('[data-testid="send-button"]');
      await page.waitForTimeout(500);
    }

    // Check that the latest message is in viewport
    const lastMessage = page.locator('[data-testid="student-message"]').last();
    await expect(lastMessage).toBeInViewport();
  });

  test('should handle message send error with retry', async ({ page }) => {
    // Mock API error
    await page.route('**/api/coaching/session/*/respond', async (route) => {
      await route.fulfill({
        status: 500,
        body: JSON.stringify({ detail: 'Internal server error' })
      });
    });

    // Send message
    await page.fill('[data-testid="message-input"]', 'What is price elasticity?');
    await page.click('[data-testid="send-button"]');

    // Check for error indicator on message
    await expect(page.locator('[data-testid="message-error"]')).toBeVisible({
      timeout: 5000
    });

    // Check for retry button
    await expect(page.locator('[data-testid="retry-message"]')).toBeVisible();
  });

  test('should show offline banner when network is down', async ({ page }) => {
    // Simulate offline
    await page.context().setOffline(true);

    // Check for offline banner
    await expect(page.locator('[data-testid="offline-banner"]')).toBeVisible({
      timeout: 2000
    });

    // Try to send message while offline
    await page.fill('[data-testid="message-input"]', 'Test message');
    await page.click('[data-testid="send-button"]');

    // Message should be queued (show pending indicator)
    await expect(page.locator('[data-testid="message-pending"]')).toBeVisible();

    // Go back online
    await page.context().setOffline(false);

    // Offline banner should disappear
    await expect(page.locator('[data-testid="offline-banner"]')).not.toBeVisible({
      timeout: 5000
    });

    // Pending message should be sent
    await expect(page.locator('[data-testid="message-pending"]')).not.toBeVisible({
      timeout: 5000
    });
  });

  test('should persist chat history on page reload', async ({ page }) => {
    // Send a message
    await page.fill('[data-testid="message-input"]', 'Test persistence');
    await page.click('[data-testid="send-button"]');

    // Wait for message to appear
    await expect(page.locator('text=Test persistence')).toBeVisible();

    // Reload page
    await page.reload();

    // Wait for chat interface
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible({
      timeout: 5000
    });

    // Check that message is still visible
    await expect(page.locator('text=Test persistence')).toBeVisible();
  });

  test('should distinguish between student and coach messages', async ({ page }) => {
    // Check coach message styling
    const coachMessage = page.locator('[data-testid="coach-message"]').first();
    await expect(coachMessage).toBeVisible();

    // Send student message
    await page.fill('[data-testid="message-input"]', 'Student message test');
    await page.click('[data-testid="send-button"]');

    // Check student message styling
    const studentMessage = page.locator('[data-testid="student-message"]').last();
    await expect(studentMessage).toBeVisible();

    // Messages should have different alignment (coach: left, student: right)
    const coachAlign = await coachMessage.evaluate((el) =>
      window.getComputedStyle(el).textAlign || el.closest('[style*="align"]')
    );
    const studentAlign = await studentMessage.evaluate((el) =>
      window.getComputedStyle(el).textAlign || el.closest('[style*="align"]')
    );

    // Verify they're different (visual distinction)
    expect(coachAlign).not.toBe(studentAlign);
  });

  test('should be accessible with keyboard navigation', async ({ page }) => {
    // Focus on message input
    await page.focus('[data-testid="message-input"]');

    // Type message
    await page.keyboard.type('Keyboard navigation test');

    // Press Enter to send (or use keyboard to click send button)
    await page.keyboard.press('Enter');

    // Message should be sent
    await expect(page.locator('text=Keyboard navigation test')).toBeVisible();
  });

  test('should have proper ARIA labels', async ({ page }) => {
    // Check message input has aria-label
    const input = page.locator('[data-testid="message-input"]');
    await expect(input).toHaveAttribute('aria-label', /.+/);

    // Check chat container has role
    const chatContainer = page.locator('[data-testid="chat-interface"]');
    await expect(chatContainer).toHaveAttribute('role');
  });
});
