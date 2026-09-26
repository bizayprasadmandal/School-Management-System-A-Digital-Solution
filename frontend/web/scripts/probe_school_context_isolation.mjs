/**
 * Browser probe: a super admin's switched school must not outlive the session.
 *
 * Reproduces the leak that made a school admin's panel show the previous super
 * admin's school: sign in as super admin → pick a school → sign out → sign in
 * as a school admin, then assert the panel is scoped to *their own* school and
 * the stray platform-only controls are gone.
 *
 * Run: node scripts/probe_school_context_isolation.mjs
 * Exits non-zero if any check fails.
 */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const SUPER = {
  email: process.env.PROBE_USER || "bizaymndl@gmail.com",
  pass: process.env.PROBE_PASS || "Admin@1234",
};
const SCHOOL_ADMIN = { email: "admin@greenvalley.edu", pass: "Admin@1234" };
const SWITCH_TO = "Bright Future Academy";
const OWN_SCHOOL = "Green Valley School";

const browser = await chromium.launch();
const page = await browser
  .newContext({ viewport: { width: 1600, height: 1000 } })
  .then((c) => c.newPage());

async function login({ email, pass }) {
  await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("input[type=email]", { timeout: 20000 });
  await page.fill("input[type=email]", email);
  await page.fill("input[type=password]", pass);
  await page.click("button[type=submit]");
  await page.waitForURL("**/admin**", { timeout: 30000 });
  await page.waitForTimeout(4000);
}

const storedContext = () =>
  page.evaluate(() => localStorage.getItem("sms-school-context") ?? "none");
const asideText = () => page.evaluate(() => document.querySelector("aside")?.innerText ?? "");
const mainText = () => page.evaluate(() => document.querySelector("main")?.innerText ?? "");

const results = {};

// ── 1. super admin picks a school ────────────────────────────────────────────
await login(SUPER);
await page.waitForFunction(() => document.body.innerText.includes("Platform Dashboard"), {
  timeout: 30000,
});
const header = page.locator("header");
await header.locator("button").filter({ hasText: "All Schools" }).first().click();
await page.waitForTimeout(800);
await page.locator("input[placeholder='Search schools...']").fill(SWITCH_TO);
await page.waitForTimeout(1000);
await header.getByText(SWITCH_TO, { exact: true }).first().click();
await page.waitForTimeout(3000);
let ctx = await storedContext();
results["super admin selection is persisted"] = ctx.includes(SWITCH_TO);

// ── 2. sign out clears it ────────────────────────────────────────────────────
await page.click('aside button[aria-label="Sign out"]');
await page.waitForURL("**/login**", { timeout: 20000 });
await page.waitForTimeout(1500);
ctx = await storedContext();
results["sign-out clears the stored school context"] =
  ctx === "none" || /"activeSchool"\s*:\s*null/.test(ctx);

// ── 3. school admin signs in ─────────────────────────────────────────────────
await login(SCHOOL_ADMIN);
const aside = await asideText();
const main = await mainText();
results["school admin sees their own school, not the switched one"] =
  aside.includes(OWN_SCHOOL) && !aside.includes(SWITCH_TO);
results["no stray platform-only 'exit' control"] = !aside.includes("Active School · exit");
results["school admin panel renders content"] = main.length > 60;

// ── 4. platform route is not silently reachable from the school panel ────────
await page.goto(`${BASE}/admin/platform`, { waitUntil: "domcontentloaded" });
await page.waitForTimeout(5000);
const platformMain = await mainText();
results["school admin platform route is blocked (no dead-end error page)"] = !platformMain.includes(
  "Failed to load platform data.",
);

await browser.close();

let failed = 0;
for (const [name, ok] of Object.entries(results)) {
  console.log(ok ? "PASS" : "FAIL", name);
  if (!ok) failed++;
}
console.log(failed === 0 ? "ALL_CHECKS_PASSED" : `FAILED_CHECKS: ${failed}`);
process.exit(failed === 0 ? 0 : 1);
