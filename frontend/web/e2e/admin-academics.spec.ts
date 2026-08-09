/**
 * E2E: Admin Academics — Attendance, Exams, Timetable
 *
 * Tests page rendering, data display, filters, and key interactions.
 *
 * Run: npx playwright test admin-academics.spec.ts --headed
 */
import { test, expect } from "@playwright/test";
import { BASE, API_BASE, loginAsAdmin, gotoAdminPage } from "./helpers";

const MOCK_CLASSROOMS = {
  count: 2,
  results: [
    {
      id: 1,
      name: "5A",
      grade_name: "Grade 5",
      capacity: 35,
      teacher_name: "Sarah Mitchell",
      student_count: 28,
    },
    {
      id: 2,
      name: "6B",
      grade_name: "Grade 6",
      capacity: 35,
      teacher_name: "John Davis",
      student_count: 30,
    },
  ],
};

// The seeded DB has no current academic year, but ExamsPage/TimetablePage gate their
// queries on useCurrentAcademicYear() — mock it so those queries actually fire.
const MOCK_CURRENT_YEAR = {
  count: 1,
  results: [{ id: 1, name: "2026-27", is_current: true }],
};

const MOCK_EXAMS = {
  count: 3,
  results: [
    {
      id: "1",
      name: "Midterm 2024",
      exam_type_name: "Term Exam",
      start_date: "2024-06-01",
      end_date: "2024-06-07",
      status: "ongoing",
    },
    {
      id: "2",
      name: "Final Exam",
      exam_type_name: "Term Exam",
      start_date: "2024-09-01",
      end_date: "2024-09-14",
      status: "scheduled",
    },
    {
      id: "3",
      name: "Quiz 1",
      exam_type_name: "Quiz",
      start_date: "2024-05-15",
      end_date: "2024-05-15",
      status: "completed",
    },
  ],
};

// TimetablePage fetches /timetable/slots/weekly/ keyed by day name (Monday..Saturday)
// and only after a classroom is selected (enabled: !!classroomId && !!academicYear?.id).
const MOCK_TIMETABLE_WEEKLY: Record<string, any[]> = {
  Monday: [
    {
      subject_name: "Math",
      period_name: "Period 1",
      start_time: "09:00",
      end_time: "09:45",
      teacher_name: "John Davis",
      classroom_name: "5A",
      room: "101",
    },
    {
      subject_name: "Science",
      period_name: "Period 2",
      start_time: "09:50",
      end_time: "10:35",
      teacher_name: "Sarah Mitchell",
      classroom_name: "5A",
      room: "102",
    },
  ],
  Tuesday: [
    {
      subject_name: "English",
      period_name: "Period 1",
      start_time: "09:00",
      end_time: "09:45",
      teacher_name: "Emily Chen",
      classroom_name: "5A",
      room: "101",
    },
  ],
};

test.describe("Admin — Attendance Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    // useClassrooms() always appends ?page=1 — glob the URL
    await page.route(`${API_BASE}/students/classrooms/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_CLASSROOMS),
      });
    });
    await page.route(`${API_BASE}/attendance/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ count: 0, results: [] }),
      });
    });
  });

  test("renders attendance page with classroom selector", async ({ page }) => {
    await gotoAdminPage(page, "attendance");
    await expect(page.getByRole("heading", { name: "Attendance" })).toBeVisible({ timeout: 5_000 });
    // Should have a classroom/date filter
    const classroomSelect = page.locator("select, [role='combobox']").first();
    await expect(classroomSelect).toBeVisible({ timeout: 5_000 });
    // Options live inside a native <select> (not independently "visible"), so assert on the select's text
    await expect(classroomSelect).toContainText("Grade 5 5A");
  });
});

test.describe("Admin — Exams Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/students/academic-years/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_CURRENT_YEAR),
      });
    });
    await page.route(`${API_BASE}/gradebook/exams/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_EXAMS),
      });
    });
  });

  test("renders exam list", async ({ page }) => {
    await gotoAdminPage(page, "exams");
    // Page heading is "Examinations" — pin the heading role to avoid the nav-link collision
    await expect(page.getByRole("heading", { name: /Exam/i })).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Midterm 2024")).toBeVisible();
    await expect(page.getByText("Final Exam")).toBeVisible();
  });

  test("shows exam status badges", async ({ page }) => {
    await gotoAdminPage(page, "exams");
    await expect(page.getByText(/Ongoing|scheduled|completed/i).first()).toBeVisible({
      timeout: 5_000,
    });
  });

  test("has create exam button", async ({ page }) => {
    await gotoAdminPage(page, "exams");
    const createBtn = page
      .locator("a, button")
      .filter({ hasText: /Create|New|Add.*Exam/i })
      .first();
    await expect(createBtn).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Admin — Timetable Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/students/academic-years/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_CURRENT_YEAR),
      });
    });
    // useClassrooms() always appends ?page=1 — glob the URL
    await page.route(`${API_BASE}/students/classrooms/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_CLASSROOMS),
      });
    });
    await page.route(`${API_BASE}/timetable/slots/weekly/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_TIMETABLE_WEEKLY),
      });
    });
  });

  test("renders timetable page with classroom selector", async ({ page }) => {
    await gotoAdminPage(page, "timetable");
    await expect(page.getByRole("heading", { name: "Timetable" })).toBeVisible({ timeout: 5_000 });
    // Weekly slots only load after picking a classroom
    await page.getByLabel("Select Classroom").selectOption({ label: "Grade 5 5A" });
    // Table or grid should show subjects
    await expect(page.getByText("Math").first()).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Science").first()).toBeVisible();
  });

  test("shows time slots and teacher names", async ({ page }) => {
    await gotoAdminPage(page, "timetable");
    await page.getByLabel("Select Classroom").selectOption({ label: "Grade 5 5A" });
    await expect(page.getByText("John Davis")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText(/09:00|9:00 AM/).first()).toBeVisible({ timeout: 5_000 });
  });
});
