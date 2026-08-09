/**
 * Shared Playwright E2E Helpers — login, navigation, API interceptors
 */
import { Page, expect } from "@playwright/test";

export const BASE = "http://localhost:3000";
export const API_BASE = "http://localhost:8000/api/v1";

export const ADMIN_EMAIL = "admin@school.edu";
export const ADMIN_PASS = "Admin@1234";

/** Log in via the login page and wait for navigation. */
export async function loginAs(page: Page, email: string, password: string) {
  await page.goto(`${BASE}/login`);
  await page.waitForSelector('input[type="email"]', { timeout: 10_000 });
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL(
    /\/admin|\/teacher|\/student|\/parent|\/accountant|\/librarian|\/counselor/,
    { timeout: 10_000 },
  );
}

/** Log in as admin and wait for admin dashboard. */
export async function loginAsAdmin(page: Page) {
  await loginAs(page, ADMIN_EMAIL, ADMIN_PASS);
  await page.waitForURL("**/admin**");
}

/** Navigate to an admin sub-page and wait for it to load. */
export async function gotoAdminPage(page: Page, path: string) {
  await page.goto(`${BASE}/admin/${path}`);
  await page.waitForSelector("h1, [data-testid='page-title']", { timeout: 10_000 });
}

/**
 * Mocked current academic year. ExamsPage/TimetablePage/ReportsPage gate their data
 * queries on useCurrentAcademicYear(), and the seeded DB has no current year — mock
 * this endpoint so those queries actually fire.
 */
export const MOCK_CURRENT_YEAR = {
  count: 1,
  results: [{ id: 1, name: "2026-27", is_current: true }],
};

/** Intercept GET /students/academic-years/ and fulfill with MOCK_CURRENT_YEAR. */
export async function mockCurrentAcademicYear(page: Page) {
  await page.route(`${API_BASE}/students/academic-years/**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(MOCK_CURRENT_YEAR),
    });
  });
}

/** The user-menu dropdown panel (the w-72 popover directly after its trigger button). */
export function userMenuPanel(page: Page) {
  return page.locator('[data-testid="user-menu-trigger"] + div');
}
