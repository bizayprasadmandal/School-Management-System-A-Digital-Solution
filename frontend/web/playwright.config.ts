import { defineConfig, devices } from "@playwright/test";

/**
 * Playwright Configuration — end-to-end tests for EduSphere SMS
 *
 * Requires the frontend dev server (port 5173) and backend (port 8000) to be
 * running.  Start both via `docker compose up` or locally before running tests.
 *
 * Usage:
 *   npx playwright test                # Run all e2e tests
 *   npx playwright test --ui           # UI mode for debugging
 *   npx playwright show-report         # View last HTML report
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: false,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: [["html", { outputFolder: "playwright-report" }], ["list"]],

  use: {
    baseURL: process.env.BASE_URL ?? "http://localhost:5173",
    trace: "on-first-retry",
    screenshot: "only-on-failure",
  },

  projects: [
    {
      name: "chromium",
      use: { ...devices["Desktop Chrome"] },
    },
  ],
});
