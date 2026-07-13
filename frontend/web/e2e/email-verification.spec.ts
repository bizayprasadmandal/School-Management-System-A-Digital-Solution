/**
 * E2E: Email Verification — Full Flow
 *
 * Tests the complete email verification experience:
 *   1. Login page shows verification banner for unverified users
 *   2. Resend verification from the login page
 *   3. Verify-email public page (success state)
 *   4. Verify-email public page (expired/invalid token — error state)
 *   5. In-app VerifyEmailSettingsPage (send verification from settings)
 *   6. Dashboard EmailVerificationBanner (resend + dismiss)
 *   7. User menu dropdown resend flow
 *   8. Settings tab reflects email verification status
 *   9. Navigation from unverified → verified re-enables access
 *
 * Prerequisites: frontend on :3000, backend on :8000, demo data seeded.
 * Run: npx playwright test --headed
 */

import { test, expect } from "@playwright/test";

const BASE = "http://localhost:3000";
const API_BASE = "http://localhost:8000/api/v1";
const ADMIN_EMAIL = "admin@school.edu";
const ADMIN_PASS = "Admin@1234";
const STUDENT_EMAIL = "student@school.edu";
const STUDENT_PASS = "Student@1234";

// ─── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Log in via the login page and wait for navigation completion.
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
 * Open the user menu dropdown by clicking its trigger button.
 */
async function openUserMenu(page) {
  const trigger = page.locator('[data-testid="user-menu-trigger"]');
  await trigger.click();
  await expect(page.getByText("Email Verification")).toBeVisible({ timeout: 3_000 });
}

/**
 * Helper: Set up route interception to make user appear unverified.
 * Sets email_verified=false in the login response.
 */
async function interceptAsUnverified(page) {
  await page.route(`${API_BASE}/auth/login/`, async (route) => {
    const response = await route.fetch();
    const body = await response.json();
    body.user.email_verified = false;
    await route.fulfill({ response, body: JSON.stringify(body) });
  });
}

/**
 * Helper: Intercept the send-verification endpoint to return success
 * without actually trying to send an email.
 */
async function interceptSendVerification(page) {
  await page.route(`${API_BASE}/auth/send-verification/`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        detail: "Verification email sent. Check your inbox (and spam folder).",
      }),
    });
  });
}

/**
 * Helper: Intercept the verify-email endpoint to return success.
 */
async function interceptVerifyEmailSuccess(page) {
  await page.route(`${API_BASE}/auth/verify-email/`, async (route) => {
    const body = JSON.stringify({
      detail: "Email verified successfully.",
      email_verified: true,
    });
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body,
    });
  });
}

/**
 * Helper: Intercept the verify-email endpoint to return an error.
 */
async function interceptVerifyEmailError(page, status = 400, message = "This verification link has expired. Request a new one.") {
  await page.route(`${API_BASE}/auth/verify-email/`, async (route) => {
    const body = JSON.stringify({ detail: message });
    await route.fulfill({
      status,
      contentType: "application/json",
      body,
    });
  });
}

// ─── Tests ────────────────────────────────────────────────────────────────────

test.describe("Email Verification — Login Page Banner", () => {

  test("shows verification banner on login for unverified user", async ({ page }) => {
    await interceptAsUnverified(page);
    await interceptSendVerification(page);

    await page.goto(`${BASE}/login`);
    await page.waitForSelector('input[type="email"]', { timeout: 10_000 });

    await page.fill('input[type="email"]', ADMIN_EMAIL);
    await page.fill('input[type="password"]', ADMIN_PASS);
    await page.click('button[type="submit"]');

    // Should stay on login page with the verification banner visible
    await expect(page.getByText("Email not verified")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Some features are restricted until you verify")).toBeVisible();
  });

  test("resend verification from login banner succeeds", async ({ page }) => {
    await interceptAsUnverified(page);
    await interceptSendVerification(page);

    await page.goto(`${BASE}/login`);
    await page.waitForSelector('input[type="email"]', { timeout: 10_000 });

    await page.fill('input[type="email"]', ADMIN_EMAIL);
    await page.fill('input[type="password"]', ADMIN_PASS);
    await page.click('button[type="submit"]');

    // Wait for banner
    await expect(page.getByText("Email not verified")).toBeVisible({ timeout: 5_000 });

    // Click resend button
    const resendBtn = page.locator("button").filter({ hasText: /Resend verification email/i });
    await expect(resendBtn).toBeVisible();
    await resendBtn.click();

    // Should see success toast
    await expect(page.getByText("Verification email sent! Check your inbox.")).toBeVisible({ timeout: 5_000 });
  });

  test("verified user is redirected away from login page", async ({ page }) => {
    // The demo admin user has email_verified=true by default
    await page.goto(`${BASE}/login`);
    await page.waitForSelector('input[type="email"]', { timeout: 10_000 });

    await page.fill('input[type="email"]', ADMIN_EMAIL);
    await page.fill('input[type="password"]', ADMIN_PASS);
    await page.click('button[type="submit"]');

    // Should navigate to admin dashboard
    await page.waitForURL("**/admin**", { timeout: 10_000 });
    // The verification banner should NOT be visible
    await expect(page.getByText("Email not verified")).not.toBeVisible({ timeout: 2_000 });
  });

});

test.describe("Email Verification — Public Verify-Email Page", () => {

  test("shows success state with valid token", async ({ page }) => {
    await interceptVerifyEmailSuccess(page);

    // Navigate directly to verify-email page with a fake token
    await page.goto(`${BASE}/verify-email/valid-test-token-12345`);

    // Should show the success state
    await expect(page.getByText("Verifying your email…")).toBeVisible({ timeout: 3_000 });
    await expect(page.getByText("Email verified!")).toBeVisible({ timeout: 5_000 });
    await expect(
      page.getByText("Your email address has been confirmed. You can now access all features of the system.")
    ).toBeVisible();

    // Should have a "Sign in to your account" link
    const signInLink = page.getByText("Sign in to your account");
    await expect(signInLink).toBeVisible();
    await expect(signInLink).toHaveAttribute("href", "/login");
  });

  test("shows error state with expired token", async ({ page }) => {
    await interceptVerifyEmailError(page, 400, "This verification link has expired. Request a new one.");

    await page.goto(`${BASE}/verify-email/expired-token-abc`);

    // Should show the error state
    await expect(page.getByText("Verifying your email…")).toBeVisible({ timeout: 3_000 });
    await expect(page.getByText("Verification failed")).toBeVisible({ timeout: 5_000 });
    await expect(
      page.getByText("This verification link has expired. Request a new one.")
    ).toBeVisible();

    // Should have a "Go to login" link
    const loginLink = page.getByText("Go to login");
    await expect(loginLink).toBeVisible();
    await expect(loginLink).toHaveAttribute("href", "/login");
  });

  test("shows error state with missing token", async ({ page }) => {
    // Navigate without a token
    await page.goto(`${BASE}/verify-email/`);

    await expect(page.getByText("Verification failed")).toBeVisible({ timeout: 5_000 });
    await expect(
      page.getByText("No verification token found in the URL.")
    ).toBeVisible();
  });

  test("shows error state with already used token", async ({ page }) => {
    await interceptVerifyEmailError(page, 400, "Invalid or already used verification link.");

    await page.goto(`${BASE}/verify-email/used-token-xyz`);

    await expect(page.getByText("Verification failed")).toBeVisible({ timeout: 5_000 });
    await expect(
      page.getByText("Invalid or already used verification link.")
    ).toBeVisible();
  });

  test("success page links to login", async ({ page }) => {
    await interceptVerifyEmailSuccess(page);

    await page.goto(`${BASE}/verify-email/some-valid-token`);

    // Wait for success state
    await expect(page.getByText("Email verified!")).toBeVisible({ timeout: 5_000 });

    // Click "Sign in to your account"
    await page.getByText("Sign in to your account").click();

    // Should navigate to login page
    await expect(page).toHaveURL(/\/login/, { timeout: 5_000 });
  });

});

test.describe("Email Verification — In-App Settings Page", () => {

  test("shows verified status for verified user", async ({ page }) => {
    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin/verify-email`);

    await expect(page.getByText("Email Verification")).toBeVisible({ timeout: 3_000 });
    await expect(page.getByText("Email verified")).toBeVisible();
    await expect(page.getByText("Verified")).toBeVisible();
    // Should NOT show send button
    await expect(page.getByText("Send verification email")).not.toBeVisible();
    // Should show "all good" message
    await expect(page.getByText("All good — your email is verified.")).toBeVisible();
  });

  test("shows unverified status and allows resend", async ({ page }) => {
    // Intercept login to make user appear unverified
    await interceptAsUnverified(page);
    await interceptSendVerification(page);

    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin/verify-email`);

    // Wait for page to load
    await expect(page.getByText("Email Verification")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Email not verified")).toBeVisible();
    await expect(page.getByText("Unverified")).toBeVisible();

    // Should show the send button
    const sendBtn = page.locator("button").filter({ hasText: /Send verification email/i });
    await expect(sendBtn).toBeVisible();
    await sendBtn.click();

    // Should show sent confirmation
    await expect(page.getByText("Verification email sent!")).toBeVisible({ timeout: 5_000 });
  });

});

test.describe("Email Verification — Dashboard Banner", () => {

  test("shows banner for unverified user on dashboard", async ({ page }) => {
    await interceptAsUnverified(page);
    await interceptSendVerification(page);

    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin`);
    await page.waitForSelector('[data-testid="user-menu-trigger"]', { timeout: 10_000 });

    // The EmailVerificationBanner should be visible on the dashboard
    await expect(page.getByText("Email not verified")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Some features are restricted until you verify your email address.")).toBeVisible();
  });

  test("resend from dashboard banner works", async ({ page }) => {
    await interceptAsUnverified(page);
    await interceptSendVerification(page);

    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin`);
    await page.waitForSelector('[data-testid="user-menu-trigger"]', { timeout: 10_000 });

    // Find the resend button inside the banner (not user menu)
    const resendBtn = page.locator("button").filter({ hasText: /Resend verification email/i }).first();
    await expect(resendBtn).toBeVisible({ timeout: 3_000 });
    await resendBtn.click();

    await expect(page.getByText("Verification email sent! Check your inbox.")).toBeVisible({ timeout: 5_000 });
  });

  test("dismiss banner hides it", async ({ page }) => {
    await interceptAsUnverified(page);

    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin`);
    await page.waitForSelector('[data-testid="user-menu-trigger"]', { timeout: 10_000 });

    // Banner should be visible
    await expect(page.getByText("Email not verified")).toBeVisible({ timeout: 3_000 });

    // Click dismiss (X) button — it has aria-label="Dismiss"
    const dismissBtn = page.locator('button[aria-label="Dismiss"]');
    await expect(dismissBtn).toBeVisible();
    await dismissBtn.click();

    // Banner should disappear
    await expect(page.getByText("Email not verified")).not.toBeVisible({ timeout: 2_000 });
  });

  test("banner not shown for verified user", async ({ page }) => {
    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin`);

    // The demo admin is verified — banner should not appear
    await expect(page.getByText("Email not verified")).not.toBeVisible({ timeout: 3_000 });
  });

});

test.describe("Email Verification — Topbar Badge + Sidebar", () => {

  test("shows email verification badge in topbar for unverified user", async ({ page }) => {
    await interceptAsUnverified(page);

    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin`);
    await page.waitForSelector('[data-testid="user-menu-trigger"]', { timeout: 10_000 });

    // The mail icon badge in the topbar should be visible
    const topbarBadge = page.locator('header button[title*="Email not verified"]');
    await expect(topbarBadge).toBeVisible({ timeout: 3_000 });
  });

  test("topbar badge navigates to verify-email page", async ({ page }) => {
    await interceptAsUnverified(page);

    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin`);
    await page.waitForSelector('[data-testid="user-menu-trigger"]', { timeout: 10_000 });

    // Click the topbar badge
    const topbarBadge = page.locator('header button[title*="Email not verified"]');
    await expect(topbarBadge).toBeVisible({ timeout: 3_000 });
    await topbarBadge.click();

    // Should navigate to verify-email settings page
    await page.waitForURL("**/admin/verify-email**", { timeout: 10_000 });
    await expect(page.getByText("Email Verification")).toBeVisible();
  });

  test("sidebar avatar shows amber dot for unverified user", async ({ page }) => {
    await interceptAsUnverified(page);

    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin`);
    await page.waitForSelector('[data-testid="user-menu-trigger"]', { timeout: 10_000 });

    // The amber dot in the sidebar near the user name should be visible
    // It's a button with title="Verify now" and an amber background
    const verifyDot = page.locator('button[title="Verify now"]');
    await expect(verifyDot).toBeVisible({ timeout: 3_000 });
  });

  test("sidebar avatar shows green dot for verified user", async ({ page }) => {
    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin`);

    // The green dot has title="Email verified"
    const verifiedDot = page.locator('span[title="Email verified"]');
    // The green dot is a span (not a button since it's not clickable)
    // Actually, for verified users in AdminLayout, it's a span with title="Email verified"
    await expect(verifiedDot.first()).toBeVisible({ timeout: 3_000 });
  });

});

test.describe("Email Verification — User Menu Dropdown", () => {

  test("shows verified status for verified user in dropdown", async ({ page }) => {
    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.waitForURL("**/admin**");
    await openUserMenu(page);

    await expect(page.getByText("Verified")).toBeVisible();
    await expect(page.getByText("Your email is verified.")).toBeVisible({ timeout: 3_000 });
  });

  test("shows unverified status and resend button", async ({ page }) => {
    await interceptAsUnverified(page);
    await interceptSendVerification(page);

    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin`);
    await page.waitForSelector('[data-testid="user-menu-trigger"]', { timeout: 10_000 });
    await openUserMenu(page);

    await expect(page.getByText("Not Verified")).toBeVisible({ timeout: 3_000 });
    await expect(page.getByText("Verify your email to unlock all features.")).toBeVisible();

    // Click the Resend button inside the dropdown
    const resendBtn = page.locator("button").filter({ hasText: /^Resend$/ });
    await expect(resendBtn).toBeVisible();
    await resendBtn.click();

    // Should show the sent confirmation within the dropdown
    await expect(page.getByText("Verification email sent! Check your inbox.")).toBeVisible({ timeout: 5_000 });
  });

  test("settings link in dropdown navigates to verify-email page", async ({ page }) => {
    await interceptAsUnverified(page);

    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin`);
    await page.waitForSelector('[data-testid="user-menu-trigger"]', { timeout: 10_000 });
    await openUserMenu(page);

    // Click "Settings" link
    const settingsLink = page.getByText("Settings");
    await expect(settingsLink).toBeVisible();
    await settingsLink.click();

    // Should navigate to verify-email page
    await page.waitForURL("**/admin/verify-email**", { timeout: 10_000 });
    await expect(page.getByText("Email Verification")).toBeVisible();
  });

});

test.describe("Email Verification — Settings Page Security Tab", () => {

  test("security tab shows email verification status", async ({ page }) => {
    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin/settings`);

    // Click Security tab
    const securityTab = page.getByText("Security");
    await expect(securityTab).toBeVisible();
    await securityTab.click();

    // Should show email section
    await expect(page.getByText("Account Security")).toBeVisible({ timeout: 3_000 });
    await expect(page.getByText("Email Verification")).toBeVisible();
    await expect(page.getByText("Verified")).toBeVisible();
  });

  test("security tab shows unverified status with send action", async ({ page }) => {
    await interceptAsUnverified(page);
    await interceptSendVerification(page);

    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin/settings`);

    // Click Security tab
    const securityTab = page.getByText("Security");
    await expect(securityTab).toBeVisible();
    await securityTab.click();

    // Should show "Not Verified" status
    await expect(page.getByText("Not Verified")).toBeVisible({ timeout: 3_000 });
    await expect(page.getByText("Verify your email to unlock all features")).toBeVisible();

    // Click the "Send verification email" button from EmailVerificationActions
    // This is in the email verification card within the Security tab
    const sendBtn = page.locator("button").filter({ hasText: /Send verification email/i });
    await expect(sendBtn).toBeVisible();
    await sendBtn.click();

    // Should show confirmation
    const sentIndicator = page.locator("span").filter({ hasText: "Email sent!" });
    await expect(sentIndicator).toBeVisible({ timeout: 5_000 });
  });

  test("security tab shows 2FA and other account info", async ({ page }) => {
    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin/settings`);

    // Click Security tab
    await page.getByText("Security").click();

    // Should show account information
    await expect(page.getByText("Account Information")).toBeVisible({ timeout: 3_000 });
    await expect(page.getByText("Two-Factor Auth")).toBeVisible();
  });

});

test.describe("Email Verification — Notification on Login", () => {

  test("unverified user receives in-app notification on login", async ({ page }) => {
    await interceptAsUnverified(page);

    await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
    await page.goto(`${BASE}/admin`);
    await page.waitForSelector('[data-testid="user-menu-trigger"]', { timeout: 10_000 });

    // The banner should show with the notification title
    await expect(page.getByText("Email not verified")).toBeVisible({ timeout: 3_000 });
  });

});

test.describe("Email Verification — Full End-to-End Flow", () => {

  test("complete flow: login as unverified → verify email → access dashboard", async ({ page }) => {
    // Step 1: Intercept login to create an unverified user session
    await interceptAsUnverified(page);
    await interceptSendVerification(page);
    await interceptVerifyEmailSuccess(page);

    // Step 2: Login — should show verification banner on login page
    await page.goto(`${BASE}/login`);
    await page.fill('input[type="email"]', ADMIN_EMAIL);
    await page.fill('input[type="password"]', ADMIN_PASS);
    await page.click('button[type="submit"]');

    // Should stay on login page with banner
    await expect(page.getByText("Email not verified")).toBeVisible({ timeout: 5_000 });

    // Step 3: Navigate to verify-email page with a token (simulating clicking email link)
    await page.goto(`${BASE}/verify-email/success-token-abc`);

    // Should see success
    await expect(page.getByText("Email verified!")).toBeVisible({ timeout: 5_000 });

    // Step 4: Navigate to login page and log in
    await page.goto(`${BASE}/login`);
    await page.fill('input[type="email"]', ADMIN_EMAIL);
    await page.fill('input[type="password"]', ADMIN_PASS);
    await page.click('button[type="submit"]');

    // Now the user should be redirected to the admin dashboard
    await page.waitForURL("**/admin**", { timeout: 10_000 });

    // Step 5: Verify no verification banner on dashboard
    await expect(page.getByText("Email not verified")).not.toBeVisible({ timeout: 3_000 });
  });

});

test.describe("Email Verification — Teacher Role", () => {

  test("teacher sees verification banner when unverified", async ({ page }) => {
    // Intercept login for a teacher user
    await page.route(`${API_BASE}/auth/login/`, async (route) => {
      const response = await route.fetch();
      const body = await response.json();
      body.user.role = "teacher";
      body.user.email_verified = false;
      await route.fulfill({ response, body: JSON.stringify(body) });
    });
    await interceptSendVerification(page);

    // Login with teacher credentials (using student credentials as base)
    await page.goto(`${BASE}/login`);
    await page.fill('input[type="email"]', STUDENT_EMAIL);
    await page.fill('input[type="password"]', STUDENT_PASS);
    await page.click('button[type="submit"]');

    // Navigate to teacher dashboard
    await page.goto(`${BASE}/teacher`);

    // Should show the verification banner
    await expect(page.getByText("Email not verified")).toBeVisible({ timeout: 5_000 });
  });

  test("teacher verify-email page renders", async ({ page }) => {
    // Use the student demo user who has student role
    await page.route(`${API_BASE}/auth/login/`, async (route) => {
      const response = await route.fetch();
      const body = await response.json();
      body.user.role = "teacher";
      body.user.email_verified = false;
      await route.fulfill({ response, body: JSON.stringify(body) });
    });

    await page.goto(`${BASE}/login`);
    await page.fill('input[type="email"]', STUDENT_EMAIL);
    await page.fill('input[type="password"]', STUDENT_PASS);
    await page.click('button[type="submit"]');

    await page.goto(`${BASE}/teacher/verify-email`);
    await expect(page.getByText("Email Verification")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Email not verified")).toBeVisible();
  });

});
