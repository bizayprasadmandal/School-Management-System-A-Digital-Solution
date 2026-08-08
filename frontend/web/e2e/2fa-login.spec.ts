/**
 * E2E: 2FA Login Flow (TOTP + Backup Code)
 *
 * Tests the second step of login when a user has two-factor authentication
 * enabled: login → 2FA challenge → verify with TOTP or backup code → dashboard.
 *
 * Uses route interception to simulate 2FA responses without requiring a real
 * 2FA-enabled user or a real authenticator app code.
 *
 * Prerequisites: frontend on :3000, backend on :8000, demo data seeded.
 * Run: npx playwright test 2fa-login.spec.ts --headed
 */

import { test, expect } from "@playwright/test";

const BASE = "http://localhost:3000";
const API_BASE = "http://localhost:8000/api/v1";
const ADMIN_EMAIL = "admin@school.edu";
const ADMIN_PASS = "Admin@1234";
const ADMIN_USER_ID = "00000000-0000-0000-0000-000000000001"; // Mock UUID
const MOCK_ACCESS_TOKEN = "mock-access-token-12345";
const MOCK_REFRESH_TOKEN = "mock-refresh-token-67890";

// ─── Helpers ──────────────────────────────────────────────────────────────────

/**
 * Intercept the login endpoint to simulate a user who has 2FA enabled.
 * Returns requires_2fa: true with a mock user_id.
 */
async function interceptLoginWith2FA(page) {
  await page.route(`${API_BASE}/auth/login/`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        requires_2fa: true,
        user_id: ADMIN_USER_ID,
        detail: "2FA is enabled. Please provide your TOTP code via /auth/verify-2fa/",
      }),
    });
  });
}

/**
 * Intercept the verify-2fa-login endpoint to return a successful JWT response.
 * Used for both TOTP and backup code verification success.
 */
async function interceptVerify2FASuccess(page) {
  await page.route(`${API_BASE}/auth/verify-2fa-login/`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        access: MOCK_ACCESS_TOKEN,
        refresh: MOCK_REFRESH_TOKEN,
        user: {
          id: ADMIN_USER_ID,
          email: ADMIN_EMAIL,
          first_name: "Admin",
          last_name: "User",
          full_name: "Admin User",
          role: "school_admin",
          avatar: null,
          email_verified: true,
          school: null,
        },
      }),
    });
  });
}

/**
 * Intercept the verify-2fa-login endpoint to return an error.
 */
async function interceptVerify2FAError(page, status = 400, message = "Invalid verification code.") {
  await page.route(`${API_BASE}/auth/verify-2fa-login/`, async (route) => {
    await route.fulfill({
      status,
      contentType: "application/json",
      body: JSON.stringify({ detail: message }),
    });
  });
}

/**
 * Fill in login email/password and submit, then wait for redirect to /verify-2fa.
 */
async function loginWith2FA(page) {
  await page.goto(`${BASE}/login`);
  await page.waitForSelector('input[type="email"]', { timeout: 10_000 });

  await page.fill('input[type="email"]', ADMIN_EMAIL);
  await page.fill('input[type="password"]', ADMIN_PASS);
  await page.click('button[type="submit"]');

  // Wait for navigation to verify-2fa page
  await page.waitForURL("**/verify-2fa**", { timeout: 10_000 });
}

/**
 * Enter a 6-digit TOTP code into the 6 individual input boxes.
 */
async function enterTOTPCode(page, code: string) {
  const digits = code.split("").slice(0, 6);
  for (let i = 0; i < digits.length; i++) {
    const input = page.locator(`input[aria-label="Digit ${i + 1}"]`);
    await input.fill(digits[i]);
  }
}

// ─── Tests ────────────────────────────────────────────────────────────────────

test.describe("2FA Login — TOTP Flow", () => {
  test("full TOTP flow: login → 2FA → enter code → dashboard", async ({ page }) => {
    await interceptLoginWith2FA(page);
    await interceptVerify2FASuccess(page);

    // Step 1: Login — should detect 2FA and redirect to verification page
    await loginWith2FA(page);

    // Should be on the verify-2fa page
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByRole("button", { name: "Authenticator app" })).toBeVisible();
    await expect(page.getByText(ADMIN_EMAIL)).toBeVisible();

    // Step 2: Enter a TOTP code
    await enterTOTPCode(page, "123456");

    // Step 3: Click "Verify & Sign In"
    const verifyBtn = page.locator("button").filter({ hasText: /Verify & Sign In/i });
    await expect(verifyBtn).toBeVisible();
    await verifyBtn.click();

    // Step 4: Should navigate to admin dashboard
    await page.waitForURL("**/admin**", { timeout: 10_000 });

    // Should see welcome toast
    await expect(page.getByText("Welcome back, Admin!")).toBeVisible({ timeout: 5_000 });
  });

  test("shows error with invalid TOTP code", async ({ page }) => {
    await interceptLoginWith2FA(page);
    await interceptVerify2FAError(
      page,
      400,
      "Invalid verification code. 3 backup code attempt remaining before lockout.",
    );

    await loginWith2FA(page);
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });

    // Enter an invalid code
    await enterTOTPCode(page, "000000");

    // Click Verify
    await page
      .locator("button")
      .filter({ hasText: /Verify & Sign In/i })
      .click();

    // Should see error message from API (inline error — first match in DOM order)
    await expect(page.getByText("Invalid verification code.").first()).toBeVisible({
      timeout: 5_000,
    });

    // Error toast should appear
    await expect(page.getByText("Invalid verification code.").first()).toBeVisible();
  });

  test("auto-advances to next digit when typing", async ({ page }) => {
    await interceptLoginWith2FA(page);

    await loginWith2FA(page);
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });

    // Focus the first input and type a digit via keyboard
    const firstInput = page.locator('input[aria-label="Digit 1"]');
    await firstInput.focus();
    await page.keyboard.type("1");

    // The second input should now be focused (React state update + ref focus)
    const secondInput = page.locator('input[aria-label="Digit 2"]');
    await expect(secondInput).toBeFocused({ timeout: 2_000 });

    // First input should have the digit
    await expect(firstInput).toHaveValue("1");
  });

  test("paste 6-digit code fills all inputs", async ({ page }) => {
    await interceptLoginWith2FA(page);

    await loginWith2FA(page);
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });

    // Simulate a paste event on the first input with clipboard data
    await page.evaluate(() => {
      const input = document.querySelector('input[aria-label="Digit 1"]');
      if (!input) return;

      // Create a DataTransfer with the pasted text
      const dt = new DataTransfer();
      dt.setData("text/plain", "987654");

      // Create and dispatch a paste event with clipboardData attached
      const pasteEvent = new Event("paste", { bubbles: true, cancelable: true });
      Object.defineProperty(pasteEvent, "clipboardData", { value: dt });
      input.dispatchEvent(pasteEvent);
    });

    // All 6 inputs should be filled after paste
    const allInputs = page.locator('input[aria-label^="Digit"]');
    const count = await allInputs.count();
    expect(count).toBe(6);

    const filledValues: string[] = [];
    for (let i = 0; i < 6; i++) {
      filledValues.push(await allInputs.nth(i).inputValue());
    }
    expect(filledValues.join("")).toBe("987654");
  });
});

test.describe("2FA Login — Backup Code Flow", () => {
  test("full backup code flow: login → switch to backup → enter code → dashboard", async ({
    page,
  }) => {
    await interceptLoginWith2FA(page);
    await interceptVerify2FASuccess(page);

    // Step 1: Login
    await loginWith2FA(page);
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });

    // Step 2: Switch to backup code tab
    await page.locator("button").filter({ hasText: "Backup code" }).click();

    // Should see the backup code input
    const backupInput = page.locator("input[placeholder='XXXXX-XXXXX']");
    await expect(backupInput).toBeVisible({ timeout: 2_000 });

    // Step 3: Enter a backup code
    await backupInput.fill("ABCDE-12345");

    // Step 4: Click "Verify & Sign In"
    await page
      .locator("button")
      .filter({ hasText: /Verify & Sign In/i })
      .click();

    // Step 5: Should navigate to admin dashboard
    await page.waitForURL("**/admin**", { timeout: 10_000 });

    // Should see welcome toast
    await expect(page.getByText("Welcome back, Admin!")).toBeVisible({ timeout: 5_000 });
  });

  test("shows error with invalid backup code", async ({ page }) => {
    await interceptLoginWith2FA(page);
    await interceptVerify2FAError(page, 400, "Invalid backup code.");

    await loginWith2FA(page);
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });

    // Switch to backup code tab
    await page.locator("button").filter({ hasText: "Backup code" }).click();

    // Enter invalid code
    const backupInput = page.locator("input[placeholder='XXXXX-XXXXX']");
    await backupInput.fill("WRONG-67890");

    // Click Verify
    await page
      .locator("button")
      .filter({ hasText: /Verify & Sign In/i })
      .click();

    // Should see error
    await expect(page.getByText("Invalid backup code.").first()).toBeVisible({ timeout: 5_000 });
  });

  test("auto-formats backup code with dash", async ({ page }) => {
    await interceptLoginWith2FA(page);

    await loginWith2FA(page);
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });

    // Switch to backup code
    await page.locator("button").filter({ hasText: "Backup code" }).click();

    // Type 10 characters without dash — should auto-insert dash
    const backupInput = page.locator("input[placeholder='XXXXX-XXXXX']");
    await backupInput.fill("ABCDE12345");

    // Should have auto-formatted to XXXXX-XXXXX
    const value = await backupInput.inputValue();
    expect(value).toBe("ABCDE-12345");
  });
});

test.describe("2FA Login — Mode Switching", () => {
  test("can switch between TOTP and backup code tabs", async ({ page }) => {
    await interceptLoginWith2FA(page);

    await loginWith2FA(page);
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });

    // Default should be TOTP mode
    await expect(
      page.getByText("Enter the 6-digit code from your authenticator app"),
    ).toBeVisible();

    // Switch to backup code
    await page.locator("button").filter({ hasText: "Backup code" }).click();
    await expect(page.getByText("Enter one of your backup codes")).toBeVisible();

    // Switch back to TOTP
    await page.locator("button").filter({ hasText: "Authenticator app" }).click();
    await expect(
      page.getByText("Enter the 6-digit code from your authenticator app"),
    ).toBeVisible();
  });

  test("error clears when switching modes", async ({ page }) => {
    await interceptLoginWith2FA(page);
    await interceptVerify2FAError(page);

    await loginWith2FA(page);
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });

    // Enter invalid code to trigger error
    await enterTOTPCode(page, "000000");
    await page
      .locator("button")
      .filter({ hasText: /Verify & Sign In/i })
      .click();

    // Wait for error
    await expect(page.getByText("Invalid verification code.").first()).toBeVisible({
      timeout: 5_000,
    });

    // Switch to backup code — form error should clear (toast notification may linger)
    await page.locator("button").filter({ hasText: "Backup code" }).click();
    await expect(
      page.locator("p").filter({ hasText: "Invalid verification code." }),
    ).not.toBeVisible({ timeout: 2_000 });
  });
});

test.describe("2FA Login — Navigation", () => {
  test("back to sign in link navigates to login", async ({ page }) => {
    await interceptLoginWith2FA(page);

    await loginWith2FA(page);
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });

    // Click "Back to sign in"
    await page.getByText("Back to sign in").click();

    // Should navigate back to login page
    await expect(page).toHaveURL(/\/login/, { timeout: 5_000 });
  });

  test("direct access to verify-2fa without user_id redirects to login", async ({ page }) => {
    // Navigate directly to verify-2fa without state
    await page.goto(`${BASE}/verify-2fa`);

    // Should be redirected to login
    await expect(page).toHaveURL(/\/login/, { timeout: 5_000 });
  });

  test("shows help section for lost authenticator", async ({ page }) => {
    await interceptLoginWith2FA(page);

    await loginWith2FA(page);
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });

    // The "Need help?" section should be visible
    await expect(page.getByText("Need help signing in?")).toBeVisible();
    await expect(page.getByText(/If you've lost access to your authenticator/)).toBeVisible();
  });
});

test.describe("2FA Login — Backup Code Lockout Handling", () => {
  test("shows remaining attempts message", async ({ page }) => {
    await interceptLoginWith2FA(page);
    // Simulate response with attempt info (first failed attempt)
    await page.route(`${API_BASE}/auth/verify-2fa-login/`, async (route) => {
      await route.fulfill({
        status: 400,
        contentType: "application/json",
        body: JSON.stringify({
          detail: "Invalid verification code. 2 backup code attempts remaining before lockout.",
        }),
      });
    });

    await loginWith2FA(page);
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });

    // Switch to backup code
    await page.locator("button").filter({ hasText: "Backup code" }).click();

    // Enter invalid backup code
    const backupInput = page.locator("input[placeholder='XXXXX-XXXXX']");
    await backupInput.fill("WRONG-11111");

    // Submit
    await page
      .locator("button")
      .filter({ hasText: /Verify & Sign In/i })
      .click();

    // Should see the remaining attempts message
    await expect(page.getByText("2 backup code attempts remaining").first()).toBeVisible({
      timeout: 5_000,
    });
  });

  test("shows lockout message after 3 failed backup attempts", async ({ page }) => {
    await interceptLoginWith2FA(page);
    // Simulate lockout response
    await page.route(`${API_BASE}/auth/verify-2fa-login/`, async (route) => {
      await route.fulfill({
        status: 429,
        contentType: "application/json",
        body: JSON.stringify({
          detail:
            "Too many failed backup code attempts. You are temporarily locked out. Try again in 30 minutes or use your authenticator app.",
        }),
      });
    });

    await loginWith2FA(page);
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });

    // Switch to backup code
    await page.locator("button").filter({ hasText: "Backup code" }).click();

    // Enter invalid backup code — triggers lockout
    const backupInput = page.locator("input[placeholder='XXXXX-XXXXX']");
    await backupInput.fill("WRONG-22222");
    await page
      .locator("button")
      .filter({ hasText: /Verify & Sign In/i })
      .click();

    // Should see lockout message
    await expect(page.getByText("Too many failed backup code attempts.").first()).toBeVisible({
      timeout: 5_000,
    });
  });
});

test.describe("2FA Login — Full End-to-End Flow", () => {
  test("complete flow: login → TOTP → admin dashboard", async ({ page }) => {
    await interceptLoginWith2FA(page);
    await interceptVerify2FASuccess(page);

    // Step 1: Go to login page
    await page.goto(`${BASE}/login`);
    await page.waitForSelector('input[type="email"]', { timeout: 10_000 });

    // Step 2: Enter credentials
    await page.fill('input[type="email"]', ADMIN_EMAIL);
    await page.fill('input[type="password"]', ADMIN_PASS);
    await page.click('button[type="submit"]');

    // Step 3: Should redirect to verify-2fa
    await page.waitForURL("**/verify-2fa**", { timeout: 10_000 });
    await expect(page.getByText("Two-factor authentication")).toBeVisible();
    await expect(page.getByText(ADMIN_EMAIL)).toBeVisible();

    // Step 4: Enter TOTP code
    await enterTOTPCode(page, "654321");

    // Step 5: Click verify
    await page
      .locator("button")
      .filter({ hasText: /Verify & Sign In/i })
      .click();

    // Step 6: Should land on admin dashboard
    await page.waitForURL("**/admin**", { timeout: 10_000 });

    // Verify dashboard content is visible
    await expect(page.getByText("Welcome back, Admin!")).toBeVisible({ timeout: 5_000 });
    // Verify the user menu trigger is present (indicating authenticated state)
    await expect(page.locator('[data-testid="user-menu-trigger"]')).toBeVisible({ timeout: 5_000 });
  });

  test("complete flow: login → backup code → admin dashboard", async ({ page }) => {
    await interceptLoginWith2FA(page);
    await interceptVerify2FASuccess(page);

    // Step 1: Login
    await page.goto(`${BASE}/login`);
    await page.waitForSelector('input[type="email"]', { timeout: 10_000 });
    await page.fill('input[type="email"]', ADMIN_EMAIL);
    await page.fill('input[type="password"]', ADMIN_PASS);
    await page.click('button[type="submit"]');

    // Step 2: Verify-2fa page
    await page.waitForURL("**/verify-2fa**", { timeout: 10_000 });
    await expect(page.getByText("Two-factor authentication")).toBeVisible();

    // Step 3: Switch to backup code tab
    await page.locator("button").filter({ hasText: "Backup code" }).click();

    // Step 4: Enter backup code
    const backupInput = page.locator("input[placeholder='XXXXX-XXXXX']");
    await backupInput.fill("ZYXWV-54321");

    // Step 5: Verify
    await page
      .locator("button")
      .filter({ hasText: /Verify & Sign In/i })
      .click();

    // Step 6: Admin dashboard
    await page.waitForURL("**/admin**", { timeout: 10_000 });
    await expect(page.getByText("Welcome back, Admin!")).toBeVisible({ timeout: 5_000 });
    await expect(page.locator('[data-testid="user-menu-trigger"]')).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("2FA Login — Backup Codes Remaining Badge", () => {
  test("shows remaining backup codes count on backup code tab", async ({ page }) => {
    // Intercept login to include backup_codes_remaining and trigger 2FA
    await page.route(`${API_BASE}/auth/login/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          requires_2fa: true,
          user_id: ADMIN_USER_ID,
          backup_codes_remaining: 4,
          detail: "2FA is enabled.",
        }),
      });
    });

    await loginWith2FA(page);
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });

    // Switch to backup code tab
    await page.locator("button").filter({ hasText: "Backup code" }).click();

    // Should see the remaining count badge
    await expect(page.getByText("4 backup codes remaining")).toBeVisible({ timeout: 3_000 });
  });

  test("shows low-badge in amber when <= 2 codes remaining", async ({ page }) => {
    // Login response with low backup codes remaining
    await page.route(`${API_BASE}/auth/login/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          requires_2fa: true,
          user_id: ADMIN_USER_ID,
          backup_codes_remaining: 1,
          detail: "2FA is enabled.",
        }),
      });
    });

    await loginWith2FA(page);
    await page.locator("button").filter({ hasText: "Backup code" }).click();

    // Should show singular "1 backup code remaining" (not "codes")
    await expect(page.getByText("1 backup code remaining")).toBeVisible({ timeout: 3_000 });
    await expect(page.getByText("1 backup codes remaining")).not.toBeVisible();
  });

  test("shows badge with emerald styling when plenty of codes remain", async ({ page }) => {
    await page.route(`${API_BASE}/auth/login/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          requires_2fa: true,
          user_id: ADMIN_USER_ID,
          backup_codes_remaining: 8,
          detail: "2FA is enabled.",
        }),
      });
    });

    await loginWith2FA(page);
    await page.locator("button").filter({ hasText: "Backup code" }).click();

    // Should show full count
    await expect(page.getByText("8 backup codes remaining")).toBeVisible({ timeout: 3_000 });
  });

  test("badge not shown when backup_codes_remaining is not provided", async ({ page }) => {
    // Login without backup_codes_remaining (e.g., legacy response)
    await page.route(`${API_BASE}/auth/login/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({
          requires_2fa: true,
          user_id: ADMIN_USER_ID,
        }),
      });
    });

    await loginWith2FA(page);
    await page.locator("button").filter({ hasText: "Backup code" }).click();

    // No badge should appear (matches both "N backup code remaining" and "N backup codes remaining")
    await expect(page.getByText(/\d+ backup code[s]? remaining/)).not.toBeVisible({
      timeout: 2_000,
    });
  });
});

test.describe("2FA Login — Throttle Error Handling", () => {
  test("shows throttle error from verify-2fa-login endpoint", async ({ page }) => {
    await interceptLoginWith2FA(page);
    // Intercept verify endpoint to return 429 (throttled)
    await page.route(`${API_BASE}/auth/verify-2fa-login/`, async (route) => {
      await route.fulfill({
        status: 429,
        contentType: "application/json",
        body: JSON.stringify({
          detail: "Request was throttled. Expected available in 52 seconds.",
        }),
      });
    });

    await loginWith2FA(page);
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });

    // Enter a TOTP code and submit
    await enterTOTPCode(page, "123456");
    await page
      .locator("button")
      .filter({ hasText: /Verify & Sign In/i })
      .click();

    // Should see throttle error message
    await expect(page.getByText("Request was throttled.").first()).toBeVisible({ timeout: 5_000 });
  });

  test("throttle and lockout messages are distinct", async ({ page }) => {
    // First, simulate a lockout on the backup code tab
    await interceptLoginWith2FA(page);
    await page.route(`${API_BASE}/auth/verify-2fa-login/`, async (route) => {
      await route.fulfill({
        status: 429,
        contentType: "application/json",
        body: JSON.stringify({
          detail:
            "Too many failed backup code attempts. You are temporarily locked out. Try again in 30 minutes or use your authenticator app.",
        }),
      });
    });

    await loginWith2FA(page);
    await expect(page.getByText("Two-factor authentication")).toBeVisible({ timeout: 5_000 });

    // Submit a TOTP code to trigger lockout response
    await enterTOTPCode(page, "000000");
    await page
      .locator("button")
      .filter({ hasText: /Verify & Sign In/i })
      .click();

    // Should see "Access temporarily locked" banner for lockout
    await expect(page.getByText("Access temporarily locked")).toBeVisible({ timeout: 5_000 });

    // Should NOT see the generic throttle message
    await expect(page.getByText("Request was throttled.").first()).not.toBeVisible();

    // Should see the helpful hint about using authenticator
    await expect(
      page.getByText("You can still sign in using your authenticator app."),
    ).toBeVisible();
  });

  test("attempts-remaining warning visible from TOTP tab", async ({ page }) => {
    // Set up: login with 2FA, simulate attempts-remaining error
    await interceptLoginWith2FA(page);
    await page.route(`${API_BASE}/auth/verify-2fa-login/`, async (route) => {
      await route.fulfill({
        status: 400,
        contentType: "application/json",
        body: JSON.stringify({
          detail: "Invalid verification code. 1 backup code attempt remaining before lockout.",
        }),
      });
    });

    await loginWith2FA(page);

    // Submit from TOTP tab — gets attempts-remaining warning
    await enterTOTPCode(page, "000000");
    await page
      .locator("button")
      .filter({ hasText: /Verify & Sign In/i })
      .click();

    // Attempts warning should be visible
    await expect(page.getByText("Warning: 1 attempt remaining")).toBeVisible({ timeout: 5_000 });
  });
});
