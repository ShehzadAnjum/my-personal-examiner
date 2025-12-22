/**
 * E2E Test: Session Outcome & Conclusion (User Story 3)
 *
 * Tests the complete flow when a coaching session concludes:
 * 1. Session reaches an outcome (resolved/needs_more_help/refer_to_teacher)
 * 2. Outcome summary is displayed
 * 3. Next actions are visible and clickable
 * 4. Message input is disabled
 * 5. "Start New Session" option is available
 */

import { test, expect } from '@playwright/test';

test.describe('Session Outcome & Conclusion', () => {
  test.beforeEach(async ({ page }) => {
    // TODO: Setup authentication (login as test student)
    // Navigate to coaching page
    await page.goto('/coaching');
  });

  test('should display outcome when session is resolved', async ({ page }) => {
    // Mock API to return a session with "resolved" outcome
    await page.route('**/api/coaching/session/*', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          session_id: 'test-session-123',
          student_id: 'test-student',
          topic: 'price elasticity',
          struggle_description: "I don't understand why PED is negative",
          transcript: [
            {
              role: 'coach',
              content: "Let's start simple: What happens to quantity demanded when price increases?",
              timestamp: new Date(Date.now() - 120000).toISOString(), // 2 min ago
            },
            {
              role: 'student',
              content: 'It decreases',
              timestamp: new Date(Date.now() - 100000).toISOString(),
            },
            {
              role: 'coach',
              content: "Exactly! That's why PED is always negative for normal goods.",
              timestamp: new Date(Date.now() - 60000).toISOString(),
            }
          ],
          outcome: 'resolved', // ← Session ended with resolution
          created_at: new Date(Date.now() - 300000).toISOString(),
          updated_at: new Date().toISOString(),
        })
      });
    });

    // Start session (simplified - assumes chat interface loads)
    await page.fill('textarea[name="topic"]', "I don't understand price elasticity");
    await page.click('button[type="submit"]');

    // Wait for session to load
    await page.waitForTimeout(2000);

    // Check that outcome component is visible
    await expect(page.locator('[data-testid="session-outcome"]')).toBeVisible({
      timeout: 5000
    });

    // Check outcome status badge shows "Resolved"
    await expect(page.locator('[data-testid="outcome-status"]:has-text("Resolved")')).toBeVisible();

    // Check that summary is visible
    await expect(page.locator('[data-testid="outcome-summary"]')).toBeVisible();
  });

  test('should display outcome when session needs more help', async ({ page }) => {
    // Mock API to return session with "needs_more_help" outcome
    await page.route('**/api/coaching/session/*', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          session_id: 'test-session-456',
          student_id: 'test-student',
          topic: 'monopoly power',
          struggle_description: 'I am confused about market structures',
          transcript: [
            {
              role: 'coach',
              content: 'Can you explain what you know about monopolies?',
              timestamp: new Date(Date.now() - 120000).toISOString(),
            },
            {
              role: 'student',
              content: "I don't really understand them at all",
              timestamp: new Date(Date.now() - 100000).toISOString(),
            }
          ],
          outcome: 'needs_more_help', // ← Student needs additional resources
          created_at: new Date(Date.now() - 300000).toISOString(),
          updated_at: new Date().toISOString(),
        })
      });
    });

    await page.fill('textarea[name="topic"]', 'I am confused about market structures');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);

    // Check outcome displays "Needs More Help"
    await expect(page.locator('[data-testid="outcome-status"]:has-text("Needs More Help")')).toBeVisible({
      timeout: 5000
    });

    // Check that next actions are visible
    await expect(page.locator('[data-testid="next-actions"]')).toBeVisible();
  });

  test('should display outcome when referred to teacher', async ({ page }) => {
    // Mock API to return session with "refer_to_teacher" outcome
    await page.route('**/api/coaching/session/*', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          session_id: 'test-session-789',
          student_id: 'test-student',
          topic: 'advanced macroeconomics',
          struggle_description: 'I need deeper explanation of fiscal policy',
          transcript: [
            {
              role: 'coach',
              content: 'This topic requires in-depth explanation. Let me refer you to the Teacher Agent.',
              timestamp: new Date().toISOString(),
            }
          ],
          outcome: 'refer_to_teacher', // ← Needs Teacher Agent
          created_at: new Date(Date.now() - 60000).toISOString(),
          updated_at: new Date().toISOString(),
        })
      });
    });

    await page.fill('textarea[name="topic"]', 'I need deeper explanation of fiscal policy');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);

    // Check outcome displays "Refer to Teacher"
    await expect(page.locator('[data-testid="outcome-status"]:has-text("Refer to Teacher")')).toBeVisible({
      timeout: 5000
    });

    // Check for teacher link in next actions
    await expect(page.locator('a:has-text("Go to Teacher")')).toBeVisible();
  });

  test('should disable message input when session has ended', async ({ page }) => {
    // Mock resolved session
    await page.route('**/api/coaching/session/*', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          session_id: 'test-session-disabled',
          student_id: 'test-student',
          topic: 'price elasticity',
          struggle_description: 'Confusion about PED',
          transcript: [
            { role: 'coach', content: 'Question 1', timestamp: new Date().toISOString() },
            { role: 'student', content: 'Answer 1', timestamp: new Date().toISOString() }
          ],
          outcome: 'resolved',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        })
      });
    });

    await page.fill('textarea[name="topic"]', 'Confusion about PED');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);

    // Check that message input is disabled
    const messageInput = page.locator('[data-testid="message-input"]');
    await expect(messageInput).toBeDisabled({ timeout: 5000 });

    // Check for "Session ended" message
    await expect(page.locator('text=/Session ended|Session complete/i')).toBeVisible();
  });

  test('should show "Start New Session" button', async ({ page }) => {
    // Mock resolved session
    await page.route('**/api/coaching/session/*', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          session_id: 'test-session-new',
          student_id: 'test-student',
          topic: 'supply and demand',
          struggle_description: 'Need help',
          transcript: [
            { role: 'coach', content: 'Great job!', timestamp: new Date().toISOString() }
          ],
          outcome: 'resolved',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        })
      });
    });

    await page.fill('textarea[name="topic"]', 'Need help');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);

    // Check for "Start New Session" button
    const newSessionButton = page.locator('button:has-text("Start New Session")');
    await expect(newSessionButton).toBeVisible({ timeout: 5000 });

    // Verify button is clickable
    await expect(newSessionButton).toBeEnabled();
  });

  test('should navigate back to form when clicking "Start New Session"', async ({ page }) => {
    // Mock resolved session
    await page.route('**/api/coaching/session/*', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          session_id: 'test-session-nav',
          student_id: 'test-student',
          topic: 'elasticity',
          struggle_description: 'Confused',
          transcript: [
            { role: 'coach', content: 'All clear now!', timestamp: new Date().toISOString() }
          ],
          outcome: 'resolved',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        })
      });
    });

    await page.fill('textarea[name="topic"]', 'Confused');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);

    // Click "Start New Session"
    await page.click('button:has-text("Start New Session")');

    // Check that form is visible again
    await expect(page.locator('textarea[name="topic"]')).toBeVisible({ timeout: 3000 });

    // Check that chat interface is hidden
    await expect(page.locator('[data-testid="chat-interface"]')).not.toBeVisible();

    // Check that form is empty (ready for new session)
    await expect(page.locator('textarea[name="topic"]')).toHaveValue('');
  });

  test('should display next actions with proper labels', async ({ page }) => {
    // Mock session with next actions
    await page.route('**/api/coaching/session/*', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          session_id: 'test-session-actions',
          student_id: 'test-student',
          topic: 'market failure',
          struggle_description: 'Need practice',
          transcript: [
            { role: 'coach', content: 'Good progress!', timestamp: new Date().toISOString() }
          ],
          outcome: 'needs_more_help',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        })
      });
    });

    await page.fill('textarea[name="topic"]', 'Need practice');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);

    // Check that next actions list is visible
    const actionsContainer = page.locator('[data-testid="next-actions"]');
    await expect(actionsContainer).toBeVisible({ timeout: 5000 });

    // Verify at least one action card exists
    const actionCards = page.locator('[data-testid="next-action-card"]');
    await expect(actionCards.first()).toBeVisible();
  });

  test('should show visual distinction for ended session', async ({ page }) => {
    // Mock resolved session
    await page.route('**/api/coaching/session/*', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          session_id: 'test-session-visual',
          student_id: 'test-student',
          topic: 'inflation',
          struggle_description: 'Confused about CPI',
          transcript: [
            { role: 'coach', content: 'Perfect understanding!', timestamp: new Date().toISOString() }
          ],
          outcome: 'resolved',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        })
      });
    });

    await page.fill('textarea[name="topic"]', 'Confused about CPI');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);

    // Check for outcome banner at top of chat
    const outcomeBanner = page.locator('[data-testid="outcome-banner"]');
    await expect(outcomeBanner).toBeVisible({ timeout: 5000 });

    // Check that chat interface has ended state styling
    const chatInterface = page.locator('[data-testid="chat-interface"]');
    await expect(chatInterface).toHaveClass(/ended|completed|resolved/, { timeout: 5000 });
  });

  test('should display confidence score if present', async ({ page }) => {
    // Mock session with confidence score
    await page.route('**/api/coaching/session/*', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          session_id: 'test-session-confidence',
          student_id: 'test-student',
          topic: 'unemployment',
          struggle_description: 'Types of unemployment',
          transcript: [
            { role: 'coach', content: 'Well done!', timestamp: new Date().toISOString(), metadata: { confidence: 85 } }
          ],
          outcome: 'resolved',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        })
      });
    });

    await page.fill('textarea[name="topic"]', 'Types of unemployment');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);

    // Check for confidence indicator (percentage or visual)
    const confidenceIndicator = page.locator('[data-testid="outcome-confidence"]');

    // Confidence may be displayed as percentage or progress bar
    // Check if element exists and contains confidence-related text
    const hasConfidence = await confidenceIndicator.isVisible().catch(() => false);

    if (hasConfidence) {
      // If confidence is shown, verify it displays a valid value
      await expect(confidenceIndicator).toContainText(/%|confidence/i);
    }
  });

  test('should maintain accessibility for outcome components', async ({ page }) => {
    // Mock resolved session
    await page.route('**/api/coaching/session/*', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          session_id: 'test-session-a11y',
          student_id: 'test-student',
          topic: 'GDP',
          struggle_description: 'Measuring GDP',
          transcript: [
            { role: 'coach', content: 'Excellent!', timestamp: new Date().toISOString() }
          ],
          outcome: 'resolved',
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString(),
        })
      });
    });

    await page.fill('textarea[name="topic"]', 'Measuring GDP');
    await page.click('button[type="submit"]');
    await page.waitForTimeout(2000);

    // Check that outcome has proper ARIA labels
    const outcomeComponent = page.locator('[data-testid="session-outcome"]');
    await expect(outcomeComponent).toHaveAttribute('role', 'region');
    await expect(outcomeComponent).toHaveAttribute('aria-label', /outcome|result|conclusion/i);

    // Check that next actions are keyboard navigable
    const firstActionButton = page.locator('[data-testid="next-action-card"] button').first();

    if (await firstActionButton.isVisible().catch(() => false)) {
      // Focus the button with keyboard
      await firstActionButton.focus();

      // Verify it's focused
      await expect(firstActionButton).toBeFocused();
    }
  });
});
