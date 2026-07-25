/**
 * E2E: Admin Module Pages 1 — Library, Behavior, Events, HR
 *
 * Run: npx playwright test admin-modules-1.spec.ts --headed
 */
import { test, expect } from "@playwright/test";
import { BASE, API_BASE, loginAsAdmin, gotoAdminPage } from "./helpers";

const MOCK_BOOKS = {
  count: 3,
  results: [
    { id: "1", title: "To Kill a Mockingbird", author: "Harper Lee", isbn: "9780061120084", available_copies: 3, total_copies: 5 },
    { id: "2", title: "1984", author: "George Orwell", isbn: "9780451524935", available_copies: 2, total_copies: 2 },
    { id: "3", title: "The Great Gatsby", author: "F. Scott Fitzgerald", isbn: "9780743273565", available_copies: 0, total_copies: 1 },
  ],
};

const MOCK_INCIDENTS = {
  count: 2,
  results: [
    { id: "1", student_name: "Bob Smith", incident_type: "disruption", severity: "medium", date: "2024-06-10", status: "resolved" },
    { id: "2", student_name: "Charlie Brown", incident_type: "tardy", severity: "low", date: "2024-06-11", status: "pending" },
  ],
};

const MOCK_EVENTS = {
  count: 3,
  results: [
    { id: "1", title: "Science Fair", event_type: "cultural", start_date: "2024-07-01", end_date: "2024-07-02", is_school_wide: true },
    { id: "2", title: "Sports Day", event_type: "sports", start_date: "2024-08-15", end_date: "2024-08-15", is_school_wide: true },
    { id: "3", title: "Parent-Teacher Meeting", event_type: "ptm", start_date: "2024-06-20", end_date: "2024-06-20", is_school_wide: true },
  ],
};

const MOCK_EMPLOYEES = {
  count: 2,
  results: [
    { id: "1", full_name: "Jane Doe", employee_id: "EMP001", department_name: "Administration", designation: "Accountant", is_active: true },
    { id: "2", full_name: "Mark Smith", employee_id: "EMP002", department_name: "Maintenance", designation: "Custodian", is_active: true },
  ],
};

test.describe("Admin — Library Page", () => {

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/library/books/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_BOOKS) });
    });
  });

  test("renders book catalog", async ({ page }) => {
    await gotoAdminPage(page, "library");
    await expect(page.getByText(/Library|Books/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("To Kill a Mockingbird")).toBeVisible();
    await expect(page.getByText("Harper Lee")).toBeVisible();
  });

  test("shows available copies info", async ({ page }) => {
    await gotoAdminPage(page, "library");
    await expect(page.getByText(/Available|Copies|3|2/i).first()).toBeVisible({ timeout: 5_000 });
  });

  test("has search input", async ({ page }) => {
    await gotoAdminPage(page, "library");
    const searchInput = page.locator('input[type="search"], input[placeholder*="Search"]').first();
    await expect(searchInput).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Admin — Behavior Page", () => {

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/behavior/incidents/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_INCIDENTS) });
    });
  });

  test("renders behavior incidents list", async ({ page }) => {
    await gotoAdminPage(page, "behavior");
    await expect(page.getByText(/Behavior|Incident/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Bob Smith")).toBeVisible();
    await expect(page.getByText("disruption")).toBeVisible();
  });

  test("shows severity and status badges", async ({ page }) => {
    await gotoAdminPage(page, "behavior");
    await expect(page.getByText(/medium|low|resolved|pending/i).first()).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Admin — Events Calendar Page", () => {

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/timetable/events/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_EVENTS) });
    });
  });

  test("renders events list", async ({ page }) => {
    await gotoAdminPage(page, "events");
    await expect(page.getByText(/Events|Calendar/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Science Fair")).toBeVisible();
    await expect(page.getByText("Sports Day")).toBeVisible();
  });

  test("shows create event button", async ({ page }) => {
    await gotoAdminPage(page, "events");
    const createBtn = page.locator("button, a").filter({ hasText: /Create|New|Add.*Event/i }).first();
    await expect(createBtn).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Admin — HR Page", () => {

  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/hr/employees/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_EMPLOYEES) });
    });
  });

  test("renders employees list", async ({ page }) => {
    await gotoAdminPage(page, "hr");
    await expect(page.getByText(/HR|Employee|Human Resource/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Jane Doe")).toBeVisible();
    await expect(page.getByText("EMP001")).toBeVisible();
  });

  test("shows department info", async ({ page }) => {
    await gotoAdminPage(page, "hr");
    await expect(page.getByText("Administration")).toBeVisible({ timeout: 5_000 });
  });
});
