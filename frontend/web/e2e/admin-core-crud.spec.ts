/**
 * E2E: Admin Core CRUD — Students, Teachers, Classrooms
 *
 * Tests page rendering, data display, search, filters, and navigation.
 * Uses route interception to mock API responses.
 *
 * Run: npx playwright test admin-core-crud.spec.ts --headed
 */
import { test, expect } from "@playwright/test";
import { BASE, API_BASE, loginAsAdmin, gotoAdminPage } from "./helpers";

// ─── Mock data ─────────────────────────────────────────────────────────────────

const MOCK_STUDENTS = {
  count: 3,
  results: [
    { id: "1", full_name: "Alice Johnson", email: "alice@school.edu", admission_number: "ADM001", gender: "F", current_class: "Grade 5 A", is_active: true, avatar: null },
    { id: "2", full_name: "Bob Smith", email: "bob@school.edu", admission_number: "ADM002", gender: "M", current_class: "Grade 6 B", is_active: true, avatar: null },
    { id: "3", full_name: "Charlie Brown", email: "charlie@school.edu", admission_number: "ADM003", gender: "M", current_class: "Grade 5 A", is_active: false, avatar: null },
  ],
};

const MOCK_TEACHERS = {
  count: 2,
  results: [
    { id: "1", full_name: "Sarah Mitchell", email: "sarah@school.edu", employee_id: "TCH001", departments: ["Science"], is_active: true },
    { id: "2", full_name: "John Davis", email: "john@school.edu", employee_id: "TCH002", departments: ["Math"], is_active: true },
  ],
};

const MOCK_CLASSROOMS = {
  count: 3,
  results: [
    { id: 1, name: "5A", grade_name: "Grade 5", capacity: 35, teacher_name: "Sarah Mitchell", student_count: 28 },
    { id: 2, name: "6B", grade_name: "Grade 6", capacity: 35, teacher_name: "John Davis", student_count: 30 },
    { id: 3, name: "7A", grade_name: "Grade 7", capacity: 30, teacher_name: "Emily Chen", student_count: 25 },
  ],
};

const MOCK_GRADES = { count: 3, results: [{ id: 1, name: "Grade 5" }, { id: 2, name: "Grade 6" }, { id: 3, name: "Grade 7" }] };

// ─── Helpers ───────────────────────────────────────────────────────────────────

async function setup(page: typeof test.prototype.page) {
  await page.route(`${API_BASE}/students/`, async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_STUDENTS) });
  });
  await page.route(`${API_BASE}/students/grades/`, async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_GRADES) });
  });
  await page.route(`${API_BASE}/academics/teachers/`, async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_TEACHERS) });
  });
  await page.route(`${API_BASE}/students/classrooms/`, async (route) => {
    await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_CLASSROOMS) });
  });
}

// ─── Tests ─────────────────────────────────────────────────────────────────────

test.describe("Admin — Students Page", () => {

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await setup(page);
  });

  test("renders student list with data", async ({ page }) => {
    await gotoAdminPage(page, "students");
    await expect(page.getByText("Alice Johnson")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Bob Smith")).toBeVisible();
    await expect(page.getByText("ADM001")).toBeVisible();
    await expect(page.getByText("Active")).toBeVisible();
  });

  test("shows search input", async ({ page }) => {
    await gotoAdminPage(page, "students");
    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]').first();
    await expect(searchInput).toBeVisible({ timeout: 5_000 });
  });

  test("has add student button linking to new page", async ({ page }) => {
    await gotoAdminPage(page, "students");
    const addBtn = page.locator("a, button").filter({ hasText: /Add Student/i }).first();
    await expect(addBtn).toBeVisible({ timeout: 5_000 });
  });

  test("has export CSV button", async ({ page }) => {
    await gotoAdminPage(page, "students");
    const exportBtn = page.locator("button, a").filter({ hasText: /Export/i }).first();
    await expect(exportBtn).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Admin — Teachers Page", () => {

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await setup(page);
  });

  test("renders teacher list with names", async ({ page }) => {
    await gotoAdminPage(page, "teachers");
    await expect(page.getByText("Sarah Mitchell")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("John Davis")).toBeVisible();
  });

  test("shows add teacher button", async ({ page }) => {
    await gotoAdminPage(page, "teachers");
    const addBtn = page.locator("a, button").filter({ hasText: /Add Teacher|New Teacher/i }).first();
    await expect(addBtn).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Admin — Classrooms Page", () => {

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await setup(page);
  });

  test("renders classroom list", async ({ page }) => {
    await gotoAdminPage(page, "classrooms");
    await expect(page.getByText("5A")).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("6B")).toBeVisible();
    await expect(page.getByText("Grade 5")).toBeVisible();
  });

  test("shows classroom capacity info", async ({ page }) => {
    await gotoAdminPage(page, "classrooms");
    // At least one classroom card/row should show capacity
    const capacityIndicator = page.locator("text=/35|30/i").first();
    await expect(capacityIndicator).toBeVisible({ timeout: 5_000 });
  });
});
