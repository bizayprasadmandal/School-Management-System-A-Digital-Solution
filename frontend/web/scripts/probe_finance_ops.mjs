/** Probe: the Finance & Operations section renders on the admin dashboard. */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";

const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1600, height: 1000 } });

// Real form login — the same path the finance walkthrough uses.
await page.goto(`${BASE}/login`);
await page.fill('input[type="email"]', "admin@greenvalley.edu");
await page.fill('input[type="password"]', "Admin@1234");
await page.click('button[type="submit"]');
await page.waitForURL("**/admin", { timeout: 15000 });
await page.waitForTimeout(4500);

console.log("URL:", page.url());
console.log("GREETING:", await page.getByText(/Good morning/).count());
console.log("KPI:", await page.getByText("Total Students").count());
page.on(
  "console",
  (m) => m.type() === "error" && console.log("CONSOLE_ERR:", m.text().slice(0, 200)),
);

const checks = {
  "Money This Month": await page.getByText("Money This Month").count(),
  "Operations Health": await page.getByText("Operations Health").count(),
  "Payroll committed": await page.getByText("Payroll committed").count(),
  "Outstanding invoices": await page.getByText("Outstanding invoices").count(),
  "Stock alerts": await page.getByText("Stock alerts").count(),
  "Fleet vehicles": await page.getByText("Fleet vehicles").count(),
};
console.log("CHECKS:", checks);
const ok = Object.values(checks).every((c) => c > 0);
console.log(ok ? "ALL_SECTIONS_VISIBLE" : "MISSING_SECTIONS");
await page.screenshot({ path: "scripts/dashboard_finance_ops.png", fullPage: false });
await browser.close();
process.exit(ok ? 0 : 1);
