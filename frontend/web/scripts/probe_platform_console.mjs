/** Browser probe: super admin platform mode — platform nav, revenue & audit pages. */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const EMAIL = process.env.PROBE_USER || "bizaymndl@gmail.com";
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
await page.waitForURL("**/admin**", { timeout: 30000 });
await page.waitForTimeout(2000);

const results = {};

// 1. platform-mode sidebar: platform items present, school sections absent
await page.waitForFunction(() => document.body.innerText.includes("Platform Dashboard"), {
  timeout: 30000,
});
let navText = await page.evaluate(() => document.querySelector("aside")?.innerText ?? "");
results["platform nav shown"] =
  navText.includes("Tenants") &&
  navText.includes("Governance") &&
  navText.includes("Platform Dashboard");
results["school sections hidden in platform mode"] =
  !navText.includes("Student Life") && !navText.includes("Finance & Operations");

// 2. revenue page renders
await page.goto(`${BASE}/admin/platform/revenue`, { waitUntil: "domcontentloaded" });
await page.waitForFunction(() => document.body.innerText.includes("Platform MRR"), {
  timeout: 30000,
});
navText = await page.evaluate(() => document.body.innerText);
results["revenue page: totals + table"] =
  navText.includes("Platform ARR") && navText.includes("EduSphere Demo Academy");
results["Tenants group auto-expands on active route"] = navText.includes("Revenue & Plans");

// 3. audit page renders with cross-school rows
await page.goto(`${BASE}/admin/platform/audit`, { waitUntil: "domcontentloaded" });
await page.waitForFunction(() => document.body.innerText.includes("Cross-school trail"), {
  timeout: 30000,
});
await page.waitForTimeout(1200);
navText = await page.evaluate(() => document.body.innerText);
results["audit page renders table"] =
  !navText.includes("No audit entries match") || navText.includes("plan_tier_change");

await page.screenshot({ path: "scripts/platform_console_probe.png", fullPage: true });
await browser.close();

let failed = 0;
for (const [k, v] of Object.entries(results)) {
  console.log(v ? "PASS" : "FAIL", k);
  if (!v) failed++;
}
console.log(failed === 0 ? "ALL_CHECKS_PASSED" : `FAILED_CHECKS: ${failed}`);
