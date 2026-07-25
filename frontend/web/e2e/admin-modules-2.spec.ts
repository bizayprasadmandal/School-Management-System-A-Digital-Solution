/**
 * E2E: Admin Module Pages 2 — Transportation, Inventory, Sports, Health,
 *                               Hostel, Cafeteria, Admissions, Alumni
 *
 * These pages primarily use card/modal-based CRUD rather than tables.
 * Tests verify page mounts, data renders, and key UI elements are present.
 *
 * Run: npx playwright test admin-modules-2.spec.ts --headed
 */
import { test, expect } from "@playwright/test";
import { BASE, API_BASE, loginAsAdmin, gotoAdminPage } from "./helpers";

const MOCK_VEHICLES = {
  count: 2,
  results: [
    { id: "1", plate_number: "ABC-123", model: "Toyota Hiace", capacity: 25, driver_name: "Mike Johnson", status: "active" },
    { id: "2", plate_number: "XYZ-789", model: "Nissan Caravan", capacity: 20, driver_name: "Anna Lee", status: "maintenance" },
  ],
};

const MOCK_ITEMS = {
  count: 2,
  results: [
    { id: "1", name: "Whiteboard Markers", category_name: "Supplies", quantity: 50, unit_price: 2.5, low_stock_threshold: 10, is_low_stock: false },
    { id: "2", name: "Printer Paper", category_name: "Supplies", quantity: 5, unit_price: 15.0, low_stock_threshold: 20, is_low_stock: true },
  ],
};

const MOCK_SPORTS = {
  count: 2,
  results: [
    { id: "1", name: "Basketball", coach_name: "Coach Williams", total_members: 12 },
    { id: "2", name: "Soccer", coach_name: "Coach Garcia", total_members: 18 },
  ],
};

const MOCK_HEALTH = {
  count: 2,
  results: [
    { id: "1", student_name: "Alice Johnson", record_type: "checkup", date: "2024-06-01", notes: "Routine checkup" },
    { id: "2", student_name: "Bob Smith", record_type: "medication", date: "2024-06-02", notes: "Allergy medication administered" },
  ],
};

const MOCK_HOSTELS = {
  count: 2,
  results: [
    { id: "1", name: "Boys Hostel A", capacity: 100, occupied: 85, warden_name: "Mr. Brown" },
    { id: "2", name: "Girls Hostel B", capacity: 80, occupied: 72, warden_name: "Ms. Taylor" },
  ],
};

const MOCK_MENUS = {
  count: 2,
  results: [
    { id: "1", name: "Monday Breakfast", meal_type: "breakfast", date: "2024-06-10", items: ["Pancakes", "Orange Juice"] },
    { id: "2", name: "Monday Lunch", meal_type: "lunch", date: "2024-06-10", items: ["Rice", "Chicken Curry"] },
  ],
};

const MOCK_INTAKES = {
  count: 2,
  results: [
    { id: "1", name: "2024 Fall Intake", grade_name: "Grade 1", total_seats: 50, available_seats: 12, status: "open", application_count: 38 },
    { id: "2", name: "2024 Spring Intake", grade_name: "Grade 2", total_seats: 30, available_seats: 0, status: "closed", application_count: 30 },
  ],
};

const MOCK_ALUMNI = {
  count: 2,
  results: [
    { id: "1", full_name: "John Anderson", graduation_year: 2020, current_occupation: "Software Engineer", city: "New York" },
    { id: "2", full_name: "Lisa Chen", graduation_year: 2019, current_occupation: "Doctor", city: "San Francisco" },
  ],
};

// ─── Transportation ──────────────────────────────────────────────────────────────

test.describe("Admin — Transportation Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/transport/vehicles/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_VEHICLES) });
    });
    await page.route(`${API_BASE}/transport/drivers/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ count: 0, results: [] }) });
    });
    await page.route(`${API_BASE}/transport/routes/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ count: 0, results: [] }) });
    });
  });

  test("renders transportation page with vehicles", async ({ page }) => {
    await gotoAdminPage(page, "transport");
    await expect(page.getByText(/Transport/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("ABC-123")).toBeVisible();
    await expect(page.getByText("Toyota Hiace")).toBeVisible();
  });
});

// ─── Inventory ──────────────────────────────────────────────────────────────────

test.describe("Admin — Inventory Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/inventory/items/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_ITEMS) });
    });
    await page.route(`${API_BASE}/inventory/categories/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ count: 0, results: [] }) });
    });
  });

  test("renders inventory page with items", async ({ page }) => {
    await gotoAdminPage(page, "inventory");
    await expect(page.getByText(/Inventory|Store/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Whiteboard Markers")).toBeVisible();
    await expect(page.getByText("Printer Paper")).toBeVisible();
  });
});

// ─── Sports ─────────────────────────────────────────────────────────────────────

test.describe("Admin — Sports Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/sports/sports/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_SPORTS) });
    });
  });

  test("renders sports page", async ({ page }) => {
    await gotoAdminPage(page, "sports");
    await expect(page.getByText(/Sports|Athletic/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Basketball")).toBeVisible();
    await expect(page.getByText("Soccer")).toBeVisible();
  });
});

// ─── Health ────────────────────────────────────────────────────────────────────

test.describe("Admin — Health Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/health/records/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_HEALTH) });
    });
  });

  test("renders health page", async ({ page }) => {
    await gotoAdminPage(page, "health");
    await expect(page.getByText(/Health|Clinic/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Alice Johnson")).toBeVisible();
  });
});

// ─── Hostel ────────────────────────────────────────────────────────────────────

test.describe("Admin — Hostel Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/hostel/hostels/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_HOSTELS) });
    });
  });

  test("renders hostel page", async ({ page }) => {
    await gotoAdminPage(page, "hostel");
    await expect(page.getByText(/Hostel|Accommodation/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Boys Hostel A")).toBeVisible();
    await expect(page.getByText("Girls Hostel B")).toBeVisible();
  });
});

// ─── Cafeteria ──────────────────────────────────────────────────────────────────

test.describe("Admin — Cafeteria Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/cafeteria/menus/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_MENUS) });
    });
    await page.route(`${API_BASE}/cafeteria/plans/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ count: 0, results: [] }) });
    });
    await page.route(`${API_BASE}/cafeteria/bookings/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ count: 0, results: [] }) });
    });
  });

  test("renders cafeteria page", async ({ page }) => {
    await gotoAdminPage(page, "cafeteria");
    await expect(page.getByText(/Cafeteria|Meal|Menu/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("Monday Breakfast")).toBeVisible();
  });
});

// ─── Admissions ─────────────────────────────────────────────────────────────────

test.describe("Admin — Admissions Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/admissions/intakes/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_INTAKES) });
    });
    await page.route(`${API_BASE}/admissions/applications/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify({ count: 0, results: [] }) });
    });
  });

  test("renders admissions page", async ({ page }) => {
    await gotoAdminPage(page, "admissions");
    await expect(page.getByText(/Admissions/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("2024 Fall Intake")).toBeVisible();
  });
});

// ─── Alumni ────────────────────────────────────────────────────────────────────

test.describe("Admin — Alumni Page", () => {
  test.beforeEach(async ({ page }) => {
    await loginAsAdmin(page);
    await page.route(`${API_BASE}/alumni/profiles/`, async (route) => {
      await route.fulfill({ status: 200, contentType: "application/json", body: JSON.stringify(MOCK_ALUMNI) });
    });
  });

  test("renders alumni page", async ({ page }) => {
    await gotoAdminPage(page, "alumni");
    await expect(page.getByText(/Alumni/i)).toBeVisible({ timeout: 5_000 });
    await expect(page.getByText("John Anderson")).toBeVisible();
    await expect(page.getByText("Software Engineer")).toBeVisible();
  });
});
