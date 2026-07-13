/**
 * E2E: User Menu Dropdown — Verification Status & Resend
 *
 * Tests that:
 * 1. The user menu opens when clicking the avatar
 * 2. The email verification status badge is displayed
 * 3. Verified users see "Verified" status
 * 4. Unverified users (mocked) see the "Resend" button and can click it
 * 5. Clicking "Resend" shows success feedback
 * 6. Clicking outside closes the dropdown
 *
 * Prerequisites: frontend on :3000, backend on :8000, demo data seeded.
 * Run: npx playwright test --headed
 */

import { test, expect } from "@playwright/test";

const BASE = "http://localhost:3000";
const API_BASE = "http://localhost:8000/api/v1";
const ADMIN_EMAIL = "admin@school.edu";
const ADMIN_PASS = "Admin@1234";

/**
 * Helper: Log in via the login page and wait for the dashboard to load.
 */
async function loginAs(page, email: string, password: string) {
  await page.goto(`${BASE}/login`);
  await page.waitForSelector('input[type="email"]', { timeout: 10_000 });

  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  await page.click('button[type="submit"]');

  // Wait for navigation away from login page
  await page.waitForURL(/\/admin|\/teacher|\/student|\/parent/, { timeout: 10_000 });
}

/**
 * Helper: Open the user menu dropdown by clicking its trigger button.
 */
async function openUserMenu(page) {
  const trigger = page.locator('[data-testid="user-menu-trigger"]');
  await trigger.click();
  await expect(page.getByText("Email Verification")).toBeVisible({ timeout: 3_000 });
}

test.describe("User Menu Dropdown — Email Verification", () => {

  test("opens the dropdown and shows user info", async ({ page }) => {
    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.waitForURL("**/admin**");
    await openUserMenu(page);

    await expect(page.getByText("Email Verification")).toBeVisible();
    await expect(page.getByText("Sign out")).toBeVisible();
  });

  test("shows verified status for verified user", async ({ page }) => {
    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.waitForURL("**/admin**");
    await openUserMenu(page);

    // The demo admin user is pre-verified, so the badge shows "Verified"
    await expect(page.getByText("Verified")).toBeVisible();
    await expect(page.getByText("Your email is verified.")).toBeVisible({ timeout: 3_000 });
  });

  test("closes dropdown when clicking outside", async ({ page }) => {
    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.waitForURL("**/admin**");
    await openUserMenu(page);

    // Click on the main content area to close the dropdown
    await page.locator("main").first().click({ position: { x: 50, y: 50 } });

    // The dropdown should close — the panel should no longer be visible
    await expect(page.getByText("Email Verification")).not.toBeVisible({ timeout: 2_000 });
  });

  test("navigates to settings via View Profile", async ({ page }) => {
    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.waitForURL("**/admin**");
    await openUserMenu(page);

    await page.getByText("View Profile").click();
    await page.waitForURL("**/admin/settings?tab=security**", { timeout: 10_000 });
  });

  test("shows resend button for unverified user and confirms send", async ({ page }) => {
    // Intercept the login response to make the admin appear unverified.
    // This allows testing the UI flow without needing a real unverified user.
    await page.route(`${API_BASE}/auth/login/`, async (route) => {
      const response = await route.fetch();
      const body = await response.json();
      // Override email_verified to false so the UI shows the "Resend" flow
      body.user.email_verified = false;
      await route.fulfill({ response, body: JSON.stringify(body) });
    });

    // Intercept the send-verification endpoint to return success without
    // actually sending an email.
    await page.route(`${API_BASE}/auth/send-verification/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ detail: "Verification email sent. Check your inbox (and spam folder)." }),
      });
    });

    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    // The login page keeps unverified users on /login with a verification banner.
    // Navigate directly to the admin dashboard — the auth store already has the
    // tokens from the successful login call.
    await page.goto(`${BASE}/admin`);
    await page.waitForSelector('[data-testid="user-menu-trigger"]', { timeout: 10_000 });

    await openUserMenu(page);

    // Should now see "Not Verified" because we mocked the login response
    await expect(page.getByText("Not Verified")).toBeVisible({ timeout: 3_000 });

    // Should see the "Resend" button
    const resendBtn = page.locator("button").filter({ hasText: /Resend/i });
    await expect(resendBtn).toBeVisible();

    // Click "Resend" — the intercepted endpoint returns success
    await resendBtn.click();

    // The component shows "Verification email sent!" after a successful send
    await expect(page.getByText("Verification email sent!")).toBeVisible({ timeout: 5_000 });
  });
});
