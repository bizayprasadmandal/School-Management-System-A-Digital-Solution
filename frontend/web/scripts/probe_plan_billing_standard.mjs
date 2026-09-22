/** Browser probe: standard school sees priced upgrade CTA + pricing cards. */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const EMAIL = process.env.PROBE_USER || "admin@brightfuture.edu";
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
await page.goto(`${BASE}/admin/plan-billing`, { waitUntil: "domcontentloaded" });

await page.waitForFunction(() => document.body.innerText.includes("Feature comparison"), {
  timeout: 30000,
});
const body = await page.evaluate(() => document.body.innerText);
const checks = {
  "pricing cards show monthly rates": body.includes("Rs. 30.00") && body.includes("Rs. 60.00"),
  "free tier shown": body.includes("Free"),
  "annual hint (2 months free)": body.includes("billed yearly"),
  "current-tier highlight": body.includes("current"),
  "CTA carries price": /Upgrade to Premium\s*·\s*Rs\. 60\.00\/student\/mo/.test(body),
};
for (const [k, v] of Object.entries(checks)) console.log(v ? "PASS" : "FAIL", k);

await page.screenshot({ path: "scripts/plan_billing_standard_probe.png", fullPage: true });
await browser.close();
const failed = Object.values(checks).filter((v) => !v).length;
console.log(failed === 0 ? "ALL_CHECKS_PASSED" : `FAILED_CHECKS: ${failed}`);
