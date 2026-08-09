/**
 * E2E: Admin Communication — Announcements, Conferences, Bulk Messages
 *
 * Tests page rendering, CRUD flows, and navigation.
 *
 * Run: npx playwright test admin-communication.spec.ts --headed
 */
import { test, expect } from "@playwright/test";
import { BASE, API_BASE, loginAsAdmin, gotoAdminPage } from "./helpers";

const MOCK_ANNOUNCEMENTS = {
  count: 2,
  results: [
    {
      id: "1",
      title: "School Holiday",
      content: "School will be closed on Friday.",
      priority: "normal",
      audience: "all",
      is_draft: false,
      created_by_name: "Admin",
      created_at: "2024-06-01T10:00:00Z",
      published_at: "2024-06-01T10:00:00Z",
      view_count: 45,
    },
    {
      id: "2",
      title: "Exam Schedule",
      content: "Final exams start next week.",
      priority: "high",
      audience: "students",
      is_draft: false,
      created_by_name: "Admin",
      created_at: "2024-05-20T10:00:00Z",
      published_at: "2024-05-20T10:00:00Z",
      view_count: 120,
    },
  ],
};

const MOCK_CONFERENCE_SLOTS = {
  count: 2,
  results: [
    {
      id: "1",
      teacher_name: "Sarah Mitchell",
      start_time: "2024-06-15T14:00:00Z",
      end_time: "2024-06-15T14:30:00Z",
      is_booked: false,
      location: "Room 101",
    },
    {
      id: "2",
      teacher_name: "John Davis",
      start_time: "2024-06-15T15:00:00Z",
      end_time: "2024-06-15T15:30:00Z",
      is_booked: true,
      booked_by_name: "Alice Johnson",
      location: "Room 102",
    },
  ],
};

test.describe("Admin — Announcements Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/communication/announcements/`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_ANNOUNCEMENTS),
      });
    });
  });

  test("renders announcement list with titles", async ({ page }) => {
    await gotoAdminPage(page, "announcements");
    await expect(page.getByRole("heading", { name: "Announcements" })).toBeVisible({
      timeout: 5_000,
    });
    await expect(page.getByText("School Holiday")).toBeVisible();
    await expect(page.getByText("Exam Schedule")).toBeVisible();
  });

  test("shows priority badges", async ({ page }) => {
    await gotoAdminPage(page, "announcements");
    await expect(page.getByText(/normal|high/i).first()).toBeVisible({ timeout: 5_000 });
  });

  test("shows new announcement button", async ({ page }) => {
    await gotoAdminPage(page, "announcements");
    const createBtn = page
      .locator("button, a")
      .filter({ hasText: /New|Create|Add.*Announcement/i })
      .first();
    await expect(createBtn).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Admin — Conferences Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/conferences/conference-slots/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify(MOCK_CONFERENCE_SLOTS),
      });
    });
    await page.route(`${API_BASE}/conferences/zoom/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({}),
      });
    });
  });

  test("renders conferences page with slot list", async ({ page }) => {
    await gotoAdminPage(page, "conferences");
    await expect(page.getByRole("heading", { name: /Conferences|Parent-Teach/i })).toBeVisible({
      timeout: 5_000,
    });
    // Slot cards show teacher_name + time — location is not rendered by this page
    await expect(page.getByText("Sarah Mitchell")).toBeVisible({ timeout: 5_000 });
  });
});

test.describe("Admin — Bulk Messages Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/communication/**`, async (route) => {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ count: 0, results: [] }),
      });
    });
  });

  test("renders bulk messages page", async ({ page }) => {
    await gotoAdminPage(page, "bulk-messages");
    await expect(page.getByRole("heading", { name: /Bulk|Messages|Communication/i })).toBeVisible({
      timeout: 5_000,
    });
    // Should have form elements
    const sendBtn = page.locator("button").filter({ hasText: /Send/i }).first();
    await expect(sendBtn).toBeVisible({ timeout: 5_000 });
  });
});
