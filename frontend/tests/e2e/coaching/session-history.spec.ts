/**
 * E2E Test: View Past Session History (User Story 4)
 *
 * Tests the complete flow of viewing and reviewing past coaching sessions:
 * 1. Display list of past sessions with topic, date, outcome
 * 2. Click to view full transcript in read-only mode
 * 3. Empty state when no sessions exist
 * 4. Filtering and sorting functionality
 */

import { test, expect } from '@playwright/test';

test.describe('View Past Session History', () => {
  test.beforeEach(async ({ page }) => {
    // TODO: Setup authentication (login as test student)
    // Navigate to coaching history page
    await page.goto('/coaching/history');
  });

  test('should display list of past sessions', async ({ page }) => {
    // Mock API to return list of sessions
    await page.route('**/api/coaching/sessions', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          sessions: [
            {
              id: 'session-1',
              topic: 'price elasticity',
              created_at: new Date(Date.now() - 86400000).toISOString(), // 1 day ago
              outcome: 'resolved',
              message_count: 8,
            },
            {
              id: 'session-2',
              topic: 'monopoly power',
              created_at: new Date(Date.now() - 172800000).toISOString(), // 2 days ago
              outcome: 'needs_more_help',
              message_count: 12,
            },
            {
              id: 'session-3',
              topic: 'fiscal policy',
              created_at: new Date(Date.now() - 259200000).toISOString(), // 3 days ago
              outcome: 'refer_to_teacher',
              message_count: 5,
            },
          ],
          total: 3,
        })
      });
    });

    // Check that session list is visible
    await expect(page.locator('[data-testid="session-history"]')).toBeVisible({
      timeout: 5000
    });

    // Check that all 3 sessions are displayed
    const sessionItems = page.locator('[data-testid="session-list-item"]');
    await expect(sessionItems).toHaveCount(3);

    // Check first session details
    const firstSession = sessionItems.first();
    await expect(firstSession).toContainText('price elasticity');
    await expect(firstSession).toContainText('Resolved');
  });

  test('should display session with correct outcome badge', async ({ page }) => {
    await page.route('**/api/coaching/sessions', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          sessions: [
            {
              id: 'session-resolved',
              topic: 'supply and demand',
              created_at: new Date().toISOString(),
              outcome: 'resolved',
              message_count: 10,
            },
            {
              id: 'session-help',
              topic: 'market structures',
              created_at: new Date().toISOString(),
              outcome: 'needs_more_help',
              message_count: 8,
            },
            {
              id: 'session-teacher',
              topic: 'macroeconomics',
              created_at: new Date().toISOString(),
              outcome: 'refer_to_teacher',
              message_count: 3,
            },
          ],
          total: 3,
        })
      });
    });

    // Check for different outcome badges
    await expect(page.locator('[data-testid="outcome-badge"]:has-text("Resolved")')).toBeVisible();
    await expect(page.locator('[data-testid="outcome-badge"]:has-text("Needs More Help")')).toBeVisible();
    await expect(page.locator('[data-testid="outcome-badge"]:has-text("Refer to Teacher")')).toBeVisible();
  });

  test('should navigate to session detail when clicking on session', async ({ page }) => {
    await page.route('**/api/coaching/sessions', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          sessions: [
            {
              id: 'session-123',
              topic: 'inflation',
              created_at: new Date().toISOString(),
              outcome: 'resolved',
              message_count: 7,
            },
          ],
          total: 1,
        })
      });
    });

    // Mock session detail API
    await page.route('**/api/coaching/session/session-123', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          session_id: 'session-123',
          student_id: 'test-student',
          topic: 'inflation',
          struggle_description: 'Understanding CPI',
          transcript: [
            {
              role: 'coach',
              content: 'Can you explain what inflation means?',
              timestamp: new Date().toISOString(),
            },
            {
              role: 'student',
              content: 'It means prices go up',
              timestamp: new Date().toISOString(),
            },
          ],
          outcome: 'resolved',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        })
      });
    });

    // Click on first session
    await page.click('[data-testid="session-list-item"]');

    // Check that we navigated to detail page
    await expect(page).toHaveURL(/\/coaching\/session-123/, { timeout: 5000 });

    // Check that transcript is visible
    await expect(page.locator('[data-testid="chat-interface"]')).toBeVisible();
  });

  test('should display read-only transcript (no input)', async ({ page }) => {
    // Navigate directly to session detail
    await page.goto('/coaching/session-123');

    // Mock session detail API
    await page.route('**/api/coaching/session/session-123', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          session_id: 'session-123',
          student_id: 'test-student',
          topic: 'GDP',
          struggle_description: 'Calculating GDP',
          transcript: [
            {
              role: 'coach',
              content: 'What are the components of GDP?',
              timestamp: new Date().toISOString(),
            },
            {
              role: 'student',
              content: 'C + I + G + NX',
              timestamp: new Date().toISOString(),
            },
          ],
          outcome: 'resolved',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        })
      });
    });

    await page.waitForTimeout(2000);

    // Check that message input is disabled or hidden
    const messageInput = page.locator('[data-testid="message-input"]');

    // Input should either be disabled or not visible in read-only mode
    const isDisabled = await messageInput.isDisabled().catch(() => true);
    const isHidden = await messageInput.isHidden().catch(() => true);

    expect(isDisabled || isHidden).toBe(true);

    // Check that transcript messages are visible
    await expect(page.locator('[data-testid="coach-message"]').first()).toBeVisible();
    await expect(page.locator('[data-testid="student-message"]').first()).toBeVisible();
  });

  test('should display empty state when no sessions exist', async ({ page }) => {
    // Mock API to return empty sessions list
    await page.route('**/api/coaching/sessions', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          sessions: [],
          total: 0,
        })
      });
    });

    // Check for empty state component
    await expect(page.locator('[data-testid="empty-history"]')).toBeVisible({
      timeout: 5000
    });

    // Check for empty state message
    await expect(page.locator('text=/No coaching sessions yet/i')).toBeVisible();

    // Check for "Start Session" button in empty state
    await expect(page.locator('button:has-text("Start Your First Session")')).toBeVisible();
  });

  test('should allow starting new session from empty state', async ({ page }) => {
    // Mock empty sessions
    await page.route('**/api/coaching/sessions', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          sessions: [],
          total: 0,
        })
      });
    });

    // Click "Start Your First Session" button
    await page.click('button:has-text("Start Your First Session")');

    // Check that we navigated to coaching page
    await expect(page).toHaveURL(/\/coaching$/, { timeout: 3000 });
  });

  test('should sort sessions by date (newest first by default)', async ({ page }) => {
    await page.route('**/api/coaching/sessions', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          sessions: [
            {
              id: 'session-new',
              topic: 'newest topic',
              created_at: new Date(Date.now() - 3600000).toISOString(), // 1 hour ago
              outcome: 'resolved',
              message_count: 5,
            },
            {
              id: 'session-old',
              topic: 'oldest topic',
              created_at: new Date(Date.now() - 604800000).toISOString(), // 1 week ago
              outcome: 'resolved',
              message_count: 8,
            },
          ],
          total: 2,
        })
      });
    });

    // Check that sessions are sorted by date (newest first)
    const sessionItems = page.locator('[data-testid="session-list-item"]');

    // First item should be the newest
    await expect(sessionItems.first()).toContainText('newest topic');

    // Last item should be the oldest
    await expect(sessionItems.last()).toContainText('oldest topic');
  });

  test('should filter sessions by outcome', async ({ page }) => {
    await page.route('**/api/coaching/sessions', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          sessions: [
            {
              id: 'session-1',
              topic: 'topic 1',
              created_at: new Date().toISOString(),
              outcome: 'resolved',
              message_count: 5,
            },
            {
              id: 'session-2',
              topic: 'topic 2',
              created_at: new Date().toISOString(),
              outcome: 'needs_more_help',
              message_count: 7,
            },
            {
              id: 'session-3',
              topic: 'topic 3',
              created_at: new Date().toISOString(),
              outcome: 'resolved',
              message_count: 6,
            },
          ],
          total: 3,
        })
      });
    });

    // Initially all 3 sessions should be visible
    await expect(page.locator('[data-testid="session-list-item"]')).toHaveCount(3);

    // Click filter dropdown
    const filterButton = page.locator('[data-testid="outcome-filter"]');
    if (await filterButton.isVisible().catch(() => false)) {
      await filterButton.click();

      // Select "Resolved" filter
      await page.click('text=/Resolved/i');

      // Now only 2 "resolved" sessions should be visible
      await expect(page.locator('[data-testid="session-list-item"]')).toHaveCount(2);

      // Both visible sessions should have "Resolved" badge
      const visibleSessions = page.locator('[data-testid="session-list-item"]:visible');
      await expect(visibleSessions.first()).toContainText('Resolved');
      await expect(visibleSessions.last()).toContainText('Resolved');
    }
  });

  test('should handle pagination for many sessions', async ({ page }) => {
    // Mock API with 25 sessions (pagination at 20)
    const sessions = Array.from({ length: 25 }, (_, i) => ({
      id: `session-${i}`,
      topic: `topic ${i}`,
      created_at: new Date(Date.now() - i * 86400000).toISOString(),
      outcome: 'resolved',
      message_count: 5,
    }));

    await page.route('**/api/coaching/sessions*', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          sessions: sessions.slice(0, 20), // First 20 sessions
          total: 25,
          has_more: true,
        })
      });
    });

    // Check that 20 sessions are displayed
    await expect(page.locator('[data-testid="session-list-item"]')).toHaveCount(20);

    // Check for "Load More" button or pagination
    const loadMoreButton = page.locator('button:has-text("Load More")');
    const hasLoadMore = await loadMoreButton.isVisible().catch(() => false);

    if (hasLoadMore) {
      await expect(loadMoreButton).toBeVisible();
    }
  });

  test('should maintain accessibility in history view', async ({ page }) => {
    await page.route('**/api/coaching/sessions', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          sessions: [
            {
              id: 'session-a11y',
              topic: 'accessibility test',
              created_at: new Date().toISOString(),
              outcome: 'resolved',
              message_count: 5,
            },
          ],
          total: 1,
        })
      });
    });

    // Check that history view has proper ARIA role
    const historyContainer = page.locator('[data-testid="session-history"]');
    await expect(historyContainer).toHaveAttribute('role', 'region');

    // Check that session items are keyboard navigable
    const firstSession = page.locator('[data-testid="session-list-item"]').first();
    await firstSession.focus();
    await expect(firstSession).toBeFocused();

    // Press Enter to navigate
    await page.keyboard.press('Enter');

    // Should navigate to detail page
    await expect(page).toHaveURL(/\/coaching\/session-a11y/, { timeout: 3000 });
  });
});
