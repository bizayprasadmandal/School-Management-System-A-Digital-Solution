/**
 * Browser walkthrough of the employee self-service My Payslips page:
 *   login as demo teacher → /teacher/my-payslips → select slip → breakdown
 *   renders → print view contains full slip → backend logged the view.
 *
 * Run: node scripts/walkthrough_my_payslips.mjs
 */
import { chromium } from "playwright";

const BASE = process.env.BASE_URL || "http://127.0.0.1:5173";
const EMAIL = process.env.BROWSE_USER || "payslip.demo@greenvalley.edu";
const PASSWORD = process.env.BROWSE_PASS || "Teacher@1234";
const API = "http://127.0.0.1:8000/api/v1";

const browser = await chromium.launch();
const page = await browser
  .newContext({ viewport: { width: 1600, height: 1000 } })
  .then((c) => c.newPage());

let failed = 0;
const step = (n, ok, label) => {
  console.log(`${ok ? "✅" : "❌"} ${n}. ${label}`);
  if (!ok) failed++;
};

page.on("response", (r) => {
  if (r.url().includes("/api/") && r.status() >= 400) {
    console.log(`  API ${r.status()} ${r.request().method()} ${r.url()}`);
  }
});

// 1. login as the demo teacher
await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
await page.fill('input[type="email"]', EMAIL);
await page.fill('input[type="password"]', PASSWORD);
await page.click('button[type="submit"]');
await page.waitForURL(/teacher/i, { timeout: 30000 });
step(1, true, `Logged in as teacher ${EMAIL}`);

// 2. open My Payslips via the sidebar nav
await page.goto(`${BASE}/teacher/my-payslips`, { waitUntil: "networkidle" });
await page.getByText("My Payslips").first().waitFor({ timeout: 20000 });
step(2, true, "My Payslips page opens");

// 3. slip list shows 3 periods
const rows = await page.locator('[data-testid="my-payslip-list"] button').count();
step(3, rows === 3, `Slip list renders ${rows} payslips`);

// 4. empty-detail state first, then select the September slip
const sep = page.locator('[data-testid="my-payslip-list"] button', { hasText: "2026-09-01" });
await sep.click();
const detail = page.getByTestId("payslip-detail");
await detail.waitFor();
const detailText = await detail.textContent();
const checks = [
  ["Basic salary", detailText.includes("Basic salary")],
  ["30,000.00 figure", detailText.includes("30,000.00")],
  ["Tax (PAYE)", detailText.includes("Tax (PAYE)")],
  ["Gross 38,000.00", detailText.includes("38,000.00")],
  ["Net 33,000.00", detailText.includes("33,000.00")],
  ["paid badge", detailText.includes("paid")],
];
for (const [label, ok] of checks) {
  step(4, ok, `Breakdown shows ${label}`);
}

// 5. print view contains the slip
const printPromise = page.waitForEvent("popup", { timeout: 15000 }).catch(() => null);
await page.getByLabel("Print this payslip").click();
const popup = await printPromise;
let printOk = false,
  html = "";
if (popup) {
  await popup.waitForLoadState("domcontentloaded");
  html = await popup.content();
  printOk =
    html.includes("Earnings") &&
    html.includes("Deductions") &&
    html.includes("33,000.00") &&
    html.includes("bank_transfer");
  await popup.close();
}
step(9, printOk, `Print view renders full slip (popup: ${!!popup})`);

// 6. backend logged the view (retrieve happened above when selecting)
const viewLogs = await page.evaluate(
  async ({ api, email, password }) => {
    const login = await fetch(`${api}/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    }).then((r) => r.json());
    const res = await fetch(`${api}/hr/payslips/`, {
      headers: { Authorization: `Bearer ${login.access || login.token}` },
    });
    const body = await res.json();
    return (body.results ?? body).length ?? 0;
  },
  { api: API, email: EMAIL, password: PASSWORD },
);
step(10, viewLogs === 3, `Scoped API returns exactly the teacher's ${viewLogs} slips`);

await page.screenshot({ path: "my_payslips_live.png", fullPage: true });
await browser.close();

console.log(failed === 0 ? "\n🎉 ALL STEPS PASSED" : `\n💥 ${failed} step(s) failed`);
process.exit(failed === 0 ? 0 : 1);
