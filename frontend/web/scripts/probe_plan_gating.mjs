/**
 * Browser probe of the plan-gating UI:
 *   Session A (premium admin):  header PlanBadge shows "premium", dashboard
 *     shows ledger + analytics content, transport tracking tab renders data.
 *   Session B (standard admin): badge shows "standard", dashboard analytics
 *     cards are replaced by the upgrade prompt, ledger tab shows lock notice,
 *     transport tracking tab shows lock notice (and skips the fetch).
 *
 * Run: node scripts/probe_plan_gating.mjs
 */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const SESSIONS = [
  { name: "PREMIUM", email: "admin@greenvalley.edu", password: "Admin@1234" },
  { name: "STANDARD", email: "admin@brightfuture.edu", password: "Admin@1234" },
];

const results = [];
const check = (name, ok, detail = "") => {
  results.push({ name, ok, detail });
  console.log(`${ok ? "PASS" : "FAIL"}  ${name}${detail ? ` — ${detail}` : ""}`);
};

const browser = await chromium.launch();

for (const session of SESSIONS) {
  console.log(`\n=== ${session.name}: ${session.email} ===`);
  const page = await browser
    .newContext({ viewport: { width: 1600, height: 1000 } })
    .then((c) => c.newPage());
  const consoleErrors = [];
  page.on("pageerror", (e) => consoleErrors.push(String(e)));

  // ── real form login ──
  await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
  await page.fill('input[type="email"]', session.email);
  await page.fill('input[type="password"]', session.password);
  await page.click('button[type="submit"]');
  await page.waitForURL("**/admin", { timeout: 15_000 });

  // ── 1. badge in header (wait for plan sync) ──
  const badge = page.locator('[title^="Current plan:"]');
  let badgeText = "(none)";
  try {
    await badge.first().waitFor({ state: "visible", timeout: 10_000 });
    await page
      .waitForFunction(
        (want) => document.querySelector('[title^="Current plan:"]')?.textContent?.trim() === want,
        session.name.toLowerCase(),
        { timeout: 10_000 },
      )
      .catch(() => {});
    badgeText = (await badge.first().textContent())?.trim() ?? "(none)";
  } catch {
    /* badge never appeared */
  }
  check(
    `${session.name} badge shows tier`,
    badgeText?.toLowerCase() === session.name.toLowerCase(),
    `badge="${badgeText}"`,
  );

  // ── 2. dashboard analytics section ──
  await page.waitForTimeout(1000);
  const analyticsLockCount = await page.getByText("requires a plan upgrade").count();
  const atRiskHeading = await page.locator("h2", { hasText: "At-Risk Students" }).count();
  if (session.name === "PREMIUM") {
    check(`${session.name} analytics rendered`, atRiskHeading > 0 && analyticsLockCount === 0);
  } else {
    check(
      `${session.name} analytics replaced by upgrade prompt`,
      analyticsLockCount > 0 && atRiskHeading === 0,
      `${analyticsLockCount} lock notice(s)`,
    );
  }

  // ── 3. finance center ledger tab ──
  await page.goto(`${BASE}/admin/finance-center?tab=accounting-entry`, {
    waitUntil: "networkidle",
  });
  await page.waitForTimeout(1200);
  const ledgerLock = await page.getByText("requires a plan upgrade").count();
  const ledgerHeader = await page.getByText(/Monthly Debits vs Credits|debits/i).count();
  if (session.name === "PREMIUM") {
    check(`${session.name} ledger renders`, ledgerHeader > 0 && ledgerLock === 0);
  } else {
    check(`${session.name} ledger locked`, ledgerLock > 0);
  }

  // ── 4. transport tracking tab ──
  // NOTE: "Transportation Center" is also a sidebar nav label, so element waits
  // match too early — poll the body text for the lock notice instead.
  await page.goto(`${BASE}/admin/transportation-center?tab=bus-tracking`, {
    waitUntil: "domcontentloaded",
  });
  let transportLock = 0;
  try {
    await page.waitForFunction(
      (txt) => document.body.innerText.includes(txt),
      "requires a plan upgrade",
      { timeout: 15_000 },
    );
    transportLock = 1;
  } catch {
    transportLock = await page.getByText("requires a plan upgrade").count();
  }
  if (session.name === "PREMIUM") {
    const rows = await page.locator(".grid > div").count();
    check(`${session.name} bus-tracking renders`, transportLock === 0, `${rows} cards`);
  } else {
    const heading = await page.locator("h1, h2").allTextContents();
    const body = (await page.locator("main, body").first().textContent())?.slice(0, 300);
    console.log(`  [diag] headings: ${heading.slice(0, 8).join(" | ")}`);
    console.log(`  [diag] body: ${body?.replace(/\s+/g, " ")}`);
    check(`${session.name} bus-tracking locked`, transportLock > 0);
  }

  if (consoleErrors.length) {
    console.log(`  (page errors: ${consoleErrors.slice(0, 3).join(" | ")})`);
  }
  await page.close();
}

await browser.close();

const failed = results.filter((r) => !r.ok);
console.log(`\n${results.length - failed.length}/${results.length} checks passed`);
process.exit(failed.length ? 1 : 0);
