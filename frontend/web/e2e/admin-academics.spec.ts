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
    { id: 1, name: "5A", grade_name: "Grade 5", capacity: 35, teacher_name: "Sarah Mitchell", student_count: 28 },
    { id: 2, name: "6B", grade_name: "Grade 6", capacity: 35, teacher_name: "John Davis", student_count: 30 },
  ],
};

const MOCK_EXAMS = {
  count: 3,
  results: [
    { id: "1", name: "Midterm 2024", exam_type_name: "Term Exam", start_date: "2024-06-01", end_date: "2024-06-07", status: "ongoing" },
    { id: "2", name: "Final Exam", exam_type_name: "Term Exam", start_date: "2024-09-01", end_date: "2024-09-14", status: "scheduled" },
    { id: "3", name: "Quiz 1", exam_type_name: "Quiz", start_date: "2024-05-15", end_date: "2024-05-15", status: "completed" },
  ],
};

const MOCK_TIMETABLE = [
  { id: 1, day_of_week: 0, period: 1, subject_name: "Math", teacher_name: "John Davis", start_time: "09:00", end_time: "09:45", room: "101" },
  { id: 2, day_of_week: 0, period: 2, subject_name: "Science", teacher_name: "Sarah Mitchell", start_time: "09:50", end_time: "10:35", room: "102" },
  { id: 3, day_of_week: 1, period: 1, subject_name: "English", teacher_name: "Emily Chen", start_time: "09:00", end_time: "09:45", room: "101" },
];

test.describe("Admin — Attendance Page", () => {

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/students/classrooms/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_CLASSROOMS) });
    });
    await page.route(`${API_BASE}/attendance/**`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ count: 0, results: [] }) });
    });
  });

  test("renders attendance page with classroom selector", async ({ page }) => {
    await gotoAdminPage(page, "attendance");
    await expect(page.getByText(/Attendance/i)).toBeVisible({ timeout: 5_000 });
    // Should have a classroom/date filter
    const classroomSelect = page.locator("select, [role='combobox']").first();
    await expect(classroomSelect).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("5A")).toBeVisible();
  });
});

test.describe("Admin — Exams Page", () => {

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/gradebook/exams/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_EXAMS) });
    });
  });

  test("renders exam list", async ({ page }) => {
    await gotoAdminPage(page, "exams");
    await expect(page.getByText(/Exams/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Midterm 2024")).toBeVisible();
    await expect(page.getByText("Final Exam")).toBeVisible();
  });

  test("shows exam status badges", async ({ page }) => {
    await gotoAdminPage(page, "exams");
    await expect(page.getByText(/Ongoing|scheduled|completed/i).first()).toBeVisible({ timeout: 5_000 });
  });

  test("has create exam button", async ({ page }) => {
    await gotoAdminPage(page, "exams");
    const createBtn = page.locator("a, button").filter({ hasText: /Create|New|Add.*Exam/i }).first();
    await expect(createBtn).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Admin — Timetable Page", () => {

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/students/classrooms/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_CLASSROOMS) });
    });
    await page.route(`${API_BASE}/timetable/slots/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_TIMETABLE) });
    });
  });

  test("renders timetable page with classroom selector", async ({ page }) => {
    await gotoAdminPage(page, "timetable");
    await expect(page.getByText(/Timetable|Schedule/i)).toBeVisible({ timeout: 5_000 });
    // Table or grid should show subjects
    await expect(page.getByText("Math").first()).toBeVisible();
    await expect(page.getByText("Science").first()).toBeVisible();
  });

  test("shows time slots and teacher names", async ({ page }) => {
    await gotoAdminPage(page, "timetable");
    await expect(page.getByText("John Davis")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText(/09:00|9:00 AM/).first()).toBeVisible({ timeout: 5_000 });
  });
});
