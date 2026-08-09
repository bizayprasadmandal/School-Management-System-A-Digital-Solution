/**
 * E2E: Admin Finances — Fees, Reports
 *
 * Tests fee invoice list, payment recording, and financial reports.
 *
 * Run: npx playwright test admin-finances.spec.ts --headed
 */
import { test, expect } from "@playwright/test";
import { BASE, API_BASE, loginAsAdmin, gotoAdminPage, mockCurrentAcademicYear } from "./helpers";

const MOCK_INVOICES = {
  count: 3,
  results: [
    {
      id: "1",
      invoice_number: "INV-001",
      student: "Alice Johnson",
      due_date: "2024-06-15",
      total_amount: 5000,
      paid_amount: 5000,
      outstanding_amount: 0,
      status: "paid",
    },
    {
      id: "2",
      invoice_number: "INV-002",
      student: "Bob Smith",
      due_date: "2024-05-01",
      total_amount: 5000,
      paid_amount: 2000,
      outstanding_amount: 3000,
      status: "partial",
    },
    {
      id: "3",
      invoice_number: "INV-003",
      student: "Charlie Brown",
      due_date: "2024-04-01",
      total_amount: 5000,
      paid_amount: 0,
      outstanding_amount: 5000,
      status: "overdue",
    },
  ],
};

const MOCK_FEE_CATEGORIES = [
  {
    id: 1,
    name: "Tuition",
    description: "Monthly tuition fee",
    is_mandatory: true,
    recurrence: "monthly",
  },
  {
    id: 2,
    name: "Transport",
    description: "Transport fee",
    is_mandatory: false,
    recurrence: "monthly",
  },
];

const MOCK_FEE_STRUCTURES = {
  count: 2,
  results: [
    {
      id: 1,
      grade_name: "Grade 5",
      category_name: "Tuition",
      amount: 5000,
      due_day: 10,
      is_active: true,
    },
    {
      id: 2,
      grade_name: "Grade 5",
      category_name: "Transport",
      amount: 2000,
      due_day: 10,
      is_active: true,
    },
  ],
};

const MOCK_SCHOLARSHIPS = {
  count: 1,
  results: [
    {
      id: "1",
      student_name: "Alice Johnson",
      name: "Merit Scholarship",
      discount_type: "percent",
      discount_value: 25,
      is_active: true,
    },
  ],
};

const MOCK_FEE_REPORT = {
  total_invoiced: 15000,
  total_collected: 7000,
  total_outstanding: 8000,
  total_overdue: 5000,
  collection_rate: 46.7,
  // Bar chart reads dataKey="amount" — missing values crash recharts (Cannot read 'toFixed')
  by_status: [
    { status: "paid", amount: 7000, total: 7000, count: 1 },
    { status: "partial", amount: 3000, total: 3000, count: 1 },
    { status: "overdue", amount: 5000, total: 5000, count: 1 },
  ],
  monthly: [
    { month: "Jan", invoiced: 5000, collected: 5000, outstanding: 0 },
    { month: "Feb", invoiced: 5000, collected: 2000, outstanding: 3000 },
  ],
  recent_payments: [
    {
      id: "1",
      receipt_number: "RCP-001",
      invoice_number: "INV-001",
      student_name: "Alice Johnson",
      amount: 5000,
      payment_method: "cash",
      status: "successful",
      paid_at: "2024-06-15T10:00:00Z",
    },
  ],
};

test.describe("Admin — Fees Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/fees/invoices/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_INVOICES),
      });
    });
    await page.route(`${API_BASE}/fees/categories/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_FEE_CATEGORIES),
      });
    });
    await page.route(`${API_BASE}/fees/structures/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_FEE_STRUCTURES),
      });
    });
    await page.route(`${API_BASE}/fees/scholarships/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_SCHOLARSHIPS),
      });
    });
    await page.route(`${API_BASE}/reporting/fee-report/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_FEE_REPORT),
      });
    });
  });

  test("renders fees page with invoice list", async ({ page }) => {
    await gotoAdminPage(page, "fees");
    await expect(page.getByRole("heading", { name: "Fee Management" })).toBeVisible({
      timeout: 5_000,
    });
    await expect(page.getByText("INV-001")).toBeVisible();
    await expect(page.getByText("INV-002")).toBeVisible();
    await expect(page.getByText("Alice Johnson")).toBeVisible();
  });

  test("shows summary cards", async ({ page }) => {
    await gotoAdminPage(page, "fees");
    await expect(page.getByText(/Total Invoiced|Collected|Outstanding/i).first()).toBeVisible({
      timeout: 5_000,
    });
  });

  test("switches to categories tab", async ({ page }) => {
    await gotoAdminPage(page, "fees");
    const catTab = page
      .locator("button")
      .filter({ hasText: /Categories/i })
      .first();
    await expect(catTab).toBeVisible({ timeout: 5_000 });
    await catTab.click();
    // "Tuition" appears in category cards, descriptions ("Monthly tuition fee") and structure rows
    await expect(page.getByText("Tuition").first()).toBeVisible({ timeout: 5_000 });
  });

  test("switches to scholarships tab", async ({ page }) => {
    await gotoAdminPage(page, "fees");
    const scholarTab = page
      .locator("button")
      .filter({ hasText: /Scholarships/i })
      .first();
    await expect(scholarTab).toBeVisible({ timeout: 5_000 });
    await scholarTab.click();
    await expect(page.getByText("Merit Scholarship")).toBeVisible({ timeout: 5_000 });
  });

  test("has export button", async ({ page }) => {
    await gotoAdminPage(page, "fees");
    const exportBtn = page
      .locator("button, a")
      .filter({ hasText: /Export|CSV/i })
      .first();
    await expect(exportBtn).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Admin — Reports Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    // The fee-report query is gated on useCurrentAcademicYear() — the seeded DB has
    // no current year, so mock one or the query never fires.
    await mockCurrentAcademicYear(page);
    // The page fetches three different reporting endpoints; each needs its own shape.
    // (dashboard-stats without attendance_today_pct crashes percent() → "Cannot read 'toFixed'")
    const MOCK_DASH_STATS = {
      total_students: 120,
      total_teachers: 8,
      attendance_today_pct: 92.5,
      fees_collected_month: 7000,
      total_classrooms: 6,
      fees_outstanding: 8000,
    };
    await page.route(`${API_BASE}/reporting/**`, async (route) => {
      const url = route.request().url();
      let body: unknown = MOCK_FEE_REPORT;
      if (url.includes("dashboard-stats")) body = MOCK_DASH_STATS;
      else if (url.includes("attendance-report")) body = { daily: [] };
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(body),
      });
    });
  });

  test("renders reports page with summary cards", async ({ page }) => {
    await gotoAdminPage(page, "reports");
    await expect(page.getByRole("heading", { name: /Reports|Financial/i })).toBeVisible({
      timeout: 5_000,
    });
    // Should show some numeric data
    await expect(page.getByText(/15|\$|7,000|8,000/).first()).toBeVisible({ timeout: 5_000 });
  });

  test("shows collection rate", async ({ page }) => {
    await gotoAdminPage(page, "reports");
    await expect(page.getByText(/Collection Rate|46/i).first()).toBeVisible({ timeout: 5_000 });
  });
});
