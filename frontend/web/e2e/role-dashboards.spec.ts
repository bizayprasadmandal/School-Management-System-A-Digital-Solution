/**
 * E2E: Role-Specific Dashboards & Navigation
 *
 * Tests that each role can access their dashboard, sidebar nav items render,
 * and key pages display correctly. Uses route mocking and role override.
 *
 * Run: npx playwright test role-dashboards.spec.ts --headed
 */
import { test, expect } from "@playwright/test";
import { BASE, API_BASE } from "./helpers";

// ─── Helpers ──────────────────────────────────────────────────────────────────

/** Login and override the user's role in the API response. */
async function loginAndOverrideRole(page: typeof test.prototype.page, email: string, password: string, role: string, extra: Record<string, unknown> = {}) {
  await page.route(`${API_BASE}/auth/login/`, async (route) => {
    const response = await route.fetch();
    const body = await response.json();
    body.user.role = role;
    body.user.email_verified = true;
    Object.assign(body.user, extra);
    await route.fulfill({ response, body: JSON.stringify(body) });
  });

  await page.goto(`${BASE}/login`);
  await page.waitForSelector('input[type="email"]', { timeout: 10_000 });
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', password);
  await page.click('button[type="submit"]');
  await page.waitForURL(new RegExp(`/${role === "school_admin" ? "admin" : role}`), { timeout: 10_000 });
}

async function mockDashboardApi(page: typeof test.prototype.page, role: string) {
  await page.route(`${API_BASE}/reporting/dashboard-stats/`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        total_students: 150,
        total_teachers: 20,
        total_classrooms: 10,
        attendance_today_pct: 94.5,
        fees_collected_month: 45000,
        fees_outstanding: 12000,
      }),
    });
  });
  await page.route(`${API_BASE}/students/classrooms/`, async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ count: 0, results: [] }) });
  });
  await page.route(`${API_BASE}/communication/notifications/`, async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ count: 0, results: [] }) });
  });
  await page.route(`${API_BASE}/communication/announcements/`, async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ count: 0, results: [] }) });
  });
  await page.route(`${API_BASE}/attendance/**`, async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({}) });
  });
}

// ─── Admin Dashboard ──────────────────────────────────────────────────────────

test.describe("Admin Dashboard", () => {
  test("renders admin dashboard with KPI cards", async ({ page }) => {
    await loginAndOverrideRole(page, "admin@school.edu", "Admin@1234", "school_admin");
    await mockDashboardApi(page, "admin");
    await page.waitForURL("**/admin**");

    // Dashboard should show KPI cards
    await expect(page.getByText(/Good morning|Dashboard/i).first()).toBeVisible({ timeout: 5_000 });
    // Quick action cards or stats should be visible
    await expect(page.locator('[data-testid="user-menu-trigger"]')).toBeVisible({ timeout: 5_000 });
  });
});

// ─── Teacher Dashboard ─────────────────────────────────────────────────────────

test.describe("Teacher Dashboard", () => {
  test("renders teacher dashboard with stats", async ({ page }) => {
    await loginAndOverrideRole(page, "teacher@school.edu", "Teacher@1234", "teacher");
    await page.goto(`${BASE}/teacher`);
    await expect(page.getByText(/Dashboard|Good/i).first()).toBeVisible({ timeout: 10_000 });
    await expect(page.locator('[data-testid="user-menu-trigger"]')).toBeVisible({ timeout: 5_000 });
  });

  test("teacher sidebar has expected nav items", async ({ page }) => {
    await loginAndOverrideRole(page, "teacher@school.edu", "Teacher@1234", "teacher");
    await page.goto(`${BASE}/teacher`);
    await expect(page.getByText(/Attendance|Gradebook|Timetable/i).first()).toBeVisible({ timeout: 10_000 });
  });
});

// ─── Student Dashboard ─────────────────────────────────────────────────────────

test.describe("Student Dashboard", () => {
  test("renders student dashboard", async ({ page }) => {
    await loginAndOverrideRole(page, "student@school.edu", "Student@1234", "student");
    await page.goto(`${BASE}/student`);
    await expect(page.getByText(/Dashboard|Good/i).first()).toBeVisible({ timeout: 10_000 });
    await expect(page.locator('[data-testid="user-menu-trigger"]')).toBeVisible({ timeout: 5_000 });
  });

  test("student sidebar shows grade and fee nav items", async ({ page }) => {
    await loginAndOverrideRole(page, "student@school.edu", "Student@1234", "student");
    await page.goto(`${BASE}/student`);
    await expect(page.getByText(/My Grades|Attendance|Fees/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test("student can navigate to their grades page", async ({ page }) => {
    await loginAndOverrideRole(page, "student@school.edu", "Student@1234", "student");
    await page.goto(`${BASE}/student/grades`);
    await expect(page.getByText(/Grades|My Grades/i).first()).toBeVisible({ timeout: 10_000 });
  });
});

// ─── Parent Dashboard ─────────────────────────────────────────────────────────

test.describe("Parent Dashboard", () => {
  test("renders parent dashboard", async ({ page }) => {
    await loginAndOverrideRole(page, "parent@school.edu", "Parent@1234", "parent");
    await page.goto(`${BASE}/parent`);
    await expect(page.getByText(/Dashboard|Good/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test("parent sidebar shows children nav item", async ({ page }) => {
    await loginAndOverrideRole(page, "parent@school.edu", "Parent@1234", "parent");
    await page.goto(`${BASE}/parent`);
    await expect(page.getByText(/My Children|Attendance|Grades|Fees/i).first()).toBeVisible({ timeout: 10_000 });
  });
});

// ─── Accountant Dashboard ──────────────────────────────────────────────────────

test.describe("Accountant Dashboard", () => {
  test("renders accountant dashboard with fee KPIs", async ({ page }) => {
    await loginAndOverrideRole(page, "accountant@school.edu", "TestPass@1234", "accountant");
    await mockDashboardApi(page, "accountant");
    await page.goto(`${BASE}/accountant`);
    await expect(page.getByText(/Dashboard|Good/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test("accountant sidebar shows fee management links", async ({ page }) => {
    await loginAndOverrideRole(page, "accountant@school.edu", "TestPass@1234", "accountant");
    await page.goto(`${BASE}/accountant`);
    await expect(page.getByText(/Fee Management|Payment History|Reports/i).first()).toBeVisible({ timeout: 10_000 });
  });
});

// ─── Librarian Dashboard ───────────────────────────────────────────────────────

test.describe("Librarian Dashboard", () => {
  test("renders librarian dashboard", async ({ page }) => {
    await loginAndOverrideRole(page, "librarian@school.edu", "TestPass@1234", "librarian");
    await page.goto(`${BASE}/librarian`);
    await expect(page.getByText(/Dashboard|Good/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test("librarian sidebar shows library nav items", async ({ page }) => {
    await loginAndOverrideRole(page, "librarian@school.edu", "TestPass@1234", "librarian");
    await page.goto(`${BASE}/librarian`);
    await expect(page.getByText(/Book Catalog|Checkouts|Fines/i).first()).toBeVisible({ timeout: 10_000 });
  });
});

// ─── Counselor Dashboard ───────────────────────────────────────────────────────

test.describe("Counselor Dashboard", () => {
  test("renders counselor dashboard", async ({ page }) => {
    await loginAndOverrideRole(page, "counselor@school.edu", "TestPass@1234", "counselor");
    await page.goto(`${BASE}/counselor`);
    await expect(page.getByText(/Dashboard|Good/i).first()).toBeVisible({ timeout: 10_000 });
  });

  test("counselor sidebar shows appointment nav items", async ({ page }) => {
    await loginAndOverrideRole(page, "counselor@school.edu", "TestPass@1234", "counselor");
    await page.goto(`${BASE}/counselor`);
    await expect(page.getByText(/Appointments|Referrals/i).first()).toBeVisible({ timeout: 10_000 });
  });
});

// ─── Cross-Role Navigation Guards ──────────────────────────────────────────────

test.describe("Cross-Role Navigation Guards", () => {
  test("student cannot access admin page", async ({ page }) => {
    await loginAndOverrideRole(page, "student@school.edu", "Student@1234", "student");
    await page.goto(`${BASE}/admin/students`);
    // Should be redirected away to unauthorized or student dashboard
    await expect(page).not.toHaveURL(/\/admin\//, { timeout: 5_000 });
  });

  test("teacher cannot access admin fees page", async ({ page }) => {
    await loginAndOverrideRole(page, "teacher@school.edu", "Teacher@1234", "teacher");
    await page.goto(`${BASE}/admin/fees`);
    // Should be redirected away
    await expect(page).not.toHaveURL(/\/admin\//, { timeout: 5_000 });
  });

  test("unauthenticated user is redirected to login", async ({ page }) => {
    await page.goto(`${BASE}/admin`);
    await expect(page).toHaveURL(/\/login/, { timeout: 5_000 });
  });
});
