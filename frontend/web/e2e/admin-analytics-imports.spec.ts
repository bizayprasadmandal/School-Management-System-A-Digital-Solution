/**
 * E2E: Admin Analytics Panels, CSV Import Wizards & Grade-Change Approvals
 *
 * Covers the analytics panels on the admin dashboard (at-risk students,
 * enrollment funnel, fee forecast), the reusable CSV import wizard flow
 * (students / teachers / attendance), and the pending grade-change
 * approvals queue on the Exams page.
 *
 * Run: npx playwright test admin-analytics-imports.spec.ts
 */
import { test, expect } from "@playwright/test";
import { API_BASE, loginAsAdmin, gotoAdminPage, mockCurrentAcademicYear } from "./helpers";

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const MOCK_DASHBOARD_STATS = {
  total_students: 150,
  total_teachers: 20,
  total_classrooms: 10,
  attendance_today_pct: 94.5,
  fees_collected_month: 45000,
  fees_outstanding: 12000,
  student_delta_pct: 2.1,
  attendance_delta_pct: -1.4,
  attendance_week: [
    { day: "Mon", present: 94.0, absent: 6.0 },
    { day: "Tue", present: 91.0, absent: 9.0 },
    { day: "Wed", present: 96.0, absent: 4.0 },
  ],
  grade_distribution: [
    { name: "A+", value: 18 },
    { name: "A", value: 24 },
    { name: "B", value: 31 },
  ],
};

const MOCK_AT_RISK = {
  threshold_attendance_pct: 80,
  window_days: 30,
  count: 1,
  students: [
    {
      student_id: "s1",
      student_name: "Jane Doe",
      admission_number: "ADM-001",
      classroom: "Grade 5 - A",
      attendance_pct: 61,
      absent_days: 4,
      avg_percentage: 71.2,
      reasons: ["low_attendance", "low_academics"],
    },
  ],
};

const MOCK_FUNNEL = {
  intake_id: null,
  total_applications: 25,
  funnel: [
    { stage: "submitted", count: 25 },
    { stage: "under_review", count: 18 },
    { stage: "shortlisted", count: 12 },
    { stage: "accepted", count: 8 },
    { stage: "enrolled", count: 5 },
    { stage: "rejected", count: 3 },
    { stage: "waitlisted", count: 2 },
  ],
  conversion: { submitted_to_accepted: 32, accepted_to_enrolled: 62.5 },
};

const MOCK_FORECAST = {
  today: "2024-06-15",
  overdue_total: 82000,
  forecast_90d: [
    { window_start: "2024-06-15", window_end: "2024-07-14", expected: 120000, already_paid: 30000 },
    { window_start: "2024-07-15", window_end: "2024-08-13", expected: 95000, already_paid: 0 },
  ],
  history_3m: [
    { month: "2024-03", collected: 410000 },
    { month: "2024-04", collected: 388000 },
    { month: "2024-05", collected: 445000 },
  ],
};

const MOCK_PROPOSALS = {
  count: 1,
  results: [
    {
      id: "p1",
      student: "stu-1",
      student_name: "Alice Johnson",
      admission_number: "ADM-007",
      exam_schedule: 3,
      subject: "Mathematics",
      exam: "Midterm 2024",
      max_marks: 100,
      action: "update",
      status: "proposed",
      marks_obtained_new: 88,
      marks_obtained_current: 74,
      is_absent_new: false,
      remarks_new: "Rechecked answer sheet",
      reason: "Answer sheet recheck found an error",
      proposed_by: "teacher-1",
      proposed_at: "2024-06-01T09:00:00Z",
      reviewed_by: null,
      reviewed_at: null,
      review_notes: "",
    },
  ],
};

const EMPTY_LIST = { count: 0, results: [], next: null, previous: null };

/** Register the shared admin-dashboard analytics mocks (analytics tests only). */
async function mockAnalyticsApi(page: typeof test.prototype.page) {
  await page.route(`${API_BASE}/**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(EMPTY_LIST),
    });
  });
  await page.route(`${API_BASE}/reporting/dashboard-stats/`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(MOCK_DASHBOARD_STATS),
    });
  });
  await page.route(`${API_BASE}/reporting/at-risk-students/**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(MOCK_AT_RISK),
    });
  });
  await page.route(`${API_BASE}/reporting/enrollment-funnel/**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(MOCK_FUNNEL),
    });
  });
  await page.route(`${API_BASE}/reporting/fee-forecast/**`, async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify(MOCK_FORECAST),
    });
  });
}

/**
 * Run a CSV import through the reusable ImportCsvModal:
 * opens the modal, switches to Paste Data, fills the CSV textarea,
 * mocks the POST endpoint, and clicks Import Data.
 */
async function runCsvImport(
  page: typeof test.prototype.page,
  opts: { endpoint: string; csv: string },
) {
  let importCalled = false;
  await page.route(`${API_BASE}${opts.endpoint}`, async (route) => {
    importCalled = true;
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({ imported: 2, errors: [] }),
    });
  });

  await page
    .getByRole("button", { name: /Import CSV/i })
    .first()
    .click();
  // Modal opens — wait for its heading (scoped to role so the page's
  // "Import CSV" button doesn't create a strict-mode collision)
  await expect(page.getByRole("heading", { name: "Import CSV" })).toBeVisible({
    timeout: 5_000,
  });
  await page.getByRole("button", { name: "Paste Data" }).click();
  const textarea = page.locator("textarea[placeholder*='Paste CSV data']");
  await textarea.fill(opts.csv);
  await page.getByRole("button", { name: "Import Data" }).click();
  await expect(page.getByText("Successfully imported 2 records!")).toBeVisible({
    timeout: 5_000,
  });
  expect(importCalled).toBe(true);
}

// ─── Admin Dashboard Analytics ─────────────────────────────────────────────────

test.describe("Admin — Analytics panels", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await mockAnalyticsApi(page);
  });

  test("renders at-risk students, enrollment funnel and fee forecast", async ({ page }) => {
    await page.waitForURL("**/admin**");
    await expect(page.getByText("At-Risk Students")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Jane Doe")).toBeVisible();
    await expect(page.getByText("1 flagged")).toBeVisible();
    await expect(page.getByText("Enrollment Funnel")).toBeVisible();
    await expect(page.getByText("Submitted → Accepted")).toBeVisible();
    await expect(page.getByText("32%")).toBeVisible();
    await expect(page.getByText("$82K overdue")).toBeVisible();
    await expect(page.getByText("90-day forecast")).toBeVisible();
  });

  test("renders attendance trend and grade distribution chart headings", async ({ page }) => {
    await page.waitForURL("**/admin**");
    await expect(page.getByText("This Week's Attendance")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Grade Distribution")).toBeVisible();
  });

  test("shows empty states when analytics return no data", async ({ page }) => {
    await page.route(`${API_BASE}/reporting/at-risk-students/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ ...MOCK_AT_RISK, count: 0, students: [] }),
      });
    });
    await page.route(`${API_BASE}/reporting/enrollment-funnel/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ ...MOCK_FUNNEL, total_applications: 0, funnel: [] }),
      });
    });
    await page.waitForURL("**/admin**");
    await expect(page.getByText("🎉 No students currently flagged")).toBeVisible({
      timeout: 5_000,
    });
    await expect(page.getByText("No applications yet")).toBeVisible();
  });
});

// ─── CSV Import Wizards ────────────────────────────────────────────────────────

test.describe("Admin — CSV import wizards", () => {
  const STUDENT_CSV =
    "full_name,email,admission_number,classroom_name,gender\nRavi Sharma,ravi@example.com,STU1001,5-A,Male\n";

  test("imports students via the CSV paste flow", async ({ page }) => {
    await loginAsAdmin(page);
    await gotoAdminPage(page, "students");
    await runCsvImport(page, { endpoint: "/students/import-csv/", csv: STUDENT_CSV });
  });

  test("imports teachers via the CSV paste flow", async ({ page }) => {
    await loginAsAdmin(page);
    await gotoAdminPage(page, "teachers");
    await runCsvImport(page, {
      endpoint: "/academics/teacher-profiles/import-csv/",
      csv: "full_name,email,phone\nSita Gurung,sita@example.com,9800000000\n",
    });
  });

  test("imports attendance via the CSV paste flow", async ({ page }) => {
    await loginAsAdmin(page);
    await gotoAdminPage(page, "attendance");
    await runCsvImport(page, {
      endpoint: "/attendance/import-csv/",
      csv: "admission_number,date,status,remarks\nSTU1001,2024-06-10,P,\n",
    });
  });
});

// ─── Grade-Change Approvals Queue ──────────────────────────────────────────────

test.describe("Admin — Grade-change approvals queue", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    // Catch-all first so later-specific routes take precedence and unknown
    // page queries (exams list, academic year, etc.) never 401-logout.
    await page.route(`${API_BASE}/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(EMPTY_LIST),
      });
    });
    await mockCurrentAcademicYear(page);
    await page.route(`${API_BASE}/gradebook/proposals/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_PROPOSALS),
      });
    });
  });

  test("shows pending grade-change proposals awaiting review", async ({ page }) => {
    await gotoAdminPage(page, "exams");
    await expect(page.getByText("Pending Grade Changes")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Alice Johnson")).toBeVisible();
    await expect(page.getByText(/Mathematics/)).toBeVisible();
    await expect(page.getByText("1 awaiting review")).toBeVisible();
    // Current → new marks shown
    await expect(page.getByText("74")).toBeVisible();
    await expect(page.getByText("88")).toBeVisible();
  });

  test("approves a pending grade change", async ({ page }) => {
    let approveCalled = false;
    await page.route(`${API_BASE}/gradebook/proposals/p1/approve/`, async (route) => {
      approveCalled = true;
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ status: "approved" }),
      });
    });
    await gotoAdminPage(page, "exams");
    await expect(page.getByText("Alice Johnson")).toBeVisible({ timeout: 5_000 });
    await page.getByRole("button", { name: "Approve" }).click();
    await expect(page.getByText("Approved change for Alice Johnson")).toBeVisible({
      timeout: 5_000,
    });
    expect(approveCalled).toBe(true);
  });
});
