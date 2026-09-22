/** Browser probe: /admin/plan-billing renders tier card + matrix + CTA state. */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const EMAIL = process.env.PROBE_USER || "admin@greenvalley.edu";
const PASSWORD = process.env.PROBE_PASS || "Admin@1234";

const browser = await chromium.launch();
const page = await browser
  .newContext({ viewport: { width: 1600, height: 1000 } })
  .then((c) => c.newPage());

await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
await page.waitForSelector("input[type=email], input[name=email]", { timeout: 20000 });
await page.fill("input[type=email], input[name=email]", EMAIL);
await page.fill("input[type=password], input[name=password]", PASSWORD);
await page.click("button[type=submit]");
await page.waitForURL("**/admin", { timeout: 30000 });
await page.waitForTimeout(1500);

// in-app nav to the plan page
await page.goto(`${BASE}/admin/plan-billing`, { waitUntil: "domcontentloaded" });

// wait for real page content (hydration + data)
await page.waitForFunction(() => document.body.innerText.includes("Feature comparison"), {
  timeout: 30000,
});
const body = await page.evaluate(() => document.body.innerText);
const checks = {
  "heading present": body.includes("Plan & Billing") || body.includes("Plan &amp; Billing"),
  "school name shown": body.includes("Green Valley School"),
  "tier badge": /Premium/.test(body),
  "matrix heading": body.includes("Feature comparison"),
  "matrix rows":
    body.includes("Double-entry accounting ledger") && body.includes("Live GPS tracking"),
  "included-in-plan markers": body.includes("included in your plan"),
};
for (const [k, v] of Object.entries(checks)) console.log(v ? "PASS" : "FAIL", k);

// premium school → no upgrade button expected
const upgradeBtn = await page.$('button:has-text("Upgrade to")');
console.log(
  upgradeBtn ? "FAIL upgrade CTA visible on premium" : "PASS no upgrade CTA on premium school",
);

// sidebar nav link exists
const navLink = await page.$('a[href="/admin/plan-billing"]');
console.log(navLink ? "PASS sidebar nav link present" : "FAIL sidebar nav link missing");

await page.screenshot({ path: "scripts/plan_billing_probe.png", fullPage: true });
await browser.close();
const failed = Object.values(checks).filter((v) => !v).length;
console.log(failed === 0 ? "ALL_CHECKS_PASSED" : `FAILED_CHECKS: ${failed}`);
