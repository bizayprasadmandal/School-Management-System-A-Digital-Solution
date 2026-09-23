/**
 * Deep walkthrough of the school-mode admin panel: every page AND every tab.
 *
 * For each page it clicks through each tab in the page's tab strip, waiting for
 * the tab's own API calls, and records:
 *   - API calls with status >= 400 (the tab is broken when this happens)
 *   - the primary list endpoint's `count` the tab received
 *   - whether the tab body rendered an empty state or an error message
 *
 * Output: JSON dump (scripts/tab_walk.json) + a summary table on stdout.
 *
 * Run: node scripts/walk_school_panel_tabs.mjs ["Green Valley School"]
 */
import { chromium } from "playwright";
import fs from "fs";

const BASE = "http://localhost:5173";
const EMAIL = process.env.PROBE_USER || "bizaymndl@gmail.com";
const PASSWORD = process.env.PROBE_PASS || "Admin@1234";
const SCHOOL = process.argv[2] || "Green Valley School";

// Optional filter: WALK_PAGES="/admin/hr-center,/admin/cafeteria" limits the run.
const FILTER = (process.env.WALK_PAGES || "")
  .split(",")
  .map((p) => p.trim())
  .filter(Boolean);

const ALL_PAGES = [
  "/admin",
  "/admin/students",
  "/admin/student-records",
  "/admin/teachers",
  "/admin/classrooms",
  "/admin/academics",
  "/admin/timetable",
  "/admin/attendance",
  "/admin/exams",
  "/admin/report-cards",
  "/admin/announcements",
  "/admin/communication-center",
  "/admin/fees",
  "/admin/finance-center",
  "/admin/hr-center",
  "/admin/timetable-center",
  "/admin/reports",
  "/admin/reporting-center",
  "/admin/library",
  "/admin/hostel-center",
  "/admin/transportation-center",
  "/admin/inventory-center",
  "/admin/cafeteria",
  "/admin/health",
  "/admin/behavior",
  "/admin/counseling",
  "/admin/alumni",
  "/admin/sports",
  "/admin/admissions-center",
  "/admin/conferences-center",
  "/admin/security-center",
  "/admin/plan-billing",
];

const PAGES = FILTER.length ? ALL_PAGES.filter((p) => FILTER.includes(p)) : ALL_PAGES;

const EMPTY_RE =
  /no .{0,30}(found|yet|available|records|data|results|items|entries)|nothing (here|to show|yet)|no data/i;
const ERROR_RE =
  /failed to load|something went wrong|could not (load|fetch)|error loading|unable to load|request failed/i;

let buffer = { failures: [], counts: new Map() };
const consoleErrors = new Map();

const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: 1700, height: 1000 } });
const page = await context.newPage();

page.on("response", async (r) => {
  if (!r.url().includes("/api/v1/")) return;
  const path = r.url().split("/api/v1/")[1].split("?")[0];
  if (r.status() >= 400) {
    buffer.failures.push(`${r.status()} ${path}`);
    return;
  }
  const ct = r.headers()["content-type"] || "";
  if (!ct.includes("json")) return;
  try {
    const body = await r.json();
    if (body && typeof body.count === "number") buffer.counts.set(path, body.count);
  } catch {
    /* not json */
  }
});
page.on("console", (m) => {
  if (m.type() === "error" && !m.text().includes("WebSocket")) {
    consoleErrors.set(m.text().slice(0, 120), true);
  }
});
page.on("pageerror", (e) => consoleErrors.set(`PAGEERROR ${String(e).slice(0, 120)}`, true));

// ── login + school switch ────────────────────────────────────────────────────
await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
await page.waitForSelector("input[type=email]", { timeout: 40000 });
await page.fill("input[type=email]", EMAIL);
await page.fill("input[type=password]", PASSWORD);
await page.click("button[type=submit]");
await page.waitForURL("**/admin**", { timeout: 60000 });
await page.waitForTimeout(3000);

await page.click("button:has-text('All Schools')");
await page.waitForTimeout(900);
await page.fill("input[placeholder*='earch']", SCHOOL);
await page.waitForTimeout(1000);
await page.click(`text=${SCHOOL}`);
await page.waitForTimeout(2000);
console.log(`school selected: ${SCHOOL}\n`);

/** Tab strip buttons for the current page (EntitySection pages use `shrink-0`). */
async function tabLabels() {
  return page.evaluate(() =>
    [...document.querySelectorAll("main button")]
      .filter((b) => b.className.includes("shrink-0") && b.innerText.trim())
      .map((b) => b.innerText.trim()),
  );
}

async function snapshot() {
  const info = await page.evaluate(() => {
    const main = document.querySelector("main") || document.body;
    const text = main.innerText.replace(/\s+/g, " ").slice(0, 4000);
    const cards = main.querySelectorAll("li, tr, [data-row], article").length;
    return { text, cards };
  });
  return info;
}

const results = [];

for (const path of PAGES) {
  await page.goto(`${BASE}${path}`, { waitUntil: "domcontentloaded" }).catch(() => {});
  await page.waitForTimeout(2200);

  let tabs = await tabLabels();
  if (!tabs.length) tabs = ["(default view)"];

  for (const label of tabs) {
    buffer = { failures: [], counts: new Map() };
    if (label !== "(default view)") {
      const clicked = await page
        .evaluate((lbl) => {
          const btn = [...document.querySelectorAll("main button")].find(
            (b) => b.className.includes("shrink-0") && b.innerText.trim() === lbl,
          );
          if (!btn) return false;
          btn.click();
          return true;
        }, label)
        .catch(() => false);
      if (!clicked) continue;
    }
    await page.waitForTimeout(1800);

    const snap = await snapshot();
    results.push({
      path,
      tab: label,
      failures: [...new Set(buffer.failures)],
      counts: Object.fromEntries(buffer.counts),
      empty: EMPTY_RE.test(snap.text),
      errorText: (snap.text.match(ERROR_RE) || [])[0] || null,
      cards: snap.cards,
      snippet: snap.text.slice(0, 160),
    });
  }
  console.log(`walked ${path} (${tabs.length} tab(s))`);
}

await browser.close();

const out = { school: SCHOOL, pages: PAGES.length, tabs: results.length, results };
fs.writeFileSync("scripts/tab_walk.json", JSON.stringify(out, null, 2));

// ── report ───────────────────────────────────────────────────────────────────
console.log("\n" + "=".repeat(112));
console.log("PAGE".padEnd(32), "TAB".padEnd(30), "ISSUE");
console.log("=".repeat(112));

let flagged = 0;
const emptyTabs = [];
for (const r of results) {
  const issues = [];
  if (r.failures.length) issues.push(`API ${r.failures.slice(0, 2).join(" / ")}`);
  if (r.errorText) issues.push(`error text: ${r.errorText}`);
  const counts = Object.values(r.counts);
  if (r.empty && counts.every((c) => c === 0)) {
    issues.push("EMPTY (0 rows)");
    emptyTabs.push(`${r.path}#${r.tab}`);
  }
  if (!issues.length) continue;
  flagged++;
  console.log(
    r.path.replace("/admin", "").padEnd(32),
    r.tab.slice(0, 28).padEnd(30),
    issues.join(" | ").slice(0, 60),
  );
}
console.log("=".repeat(112));
console.log(`tabs walked: ${results.length} | flagged: ${flagged}`);
console.log(`empty tabs: ${emptyTabs.length}`);
if (consoleErrors.size) {
  console.log("\nconsole errors:");
  for (const e of consoleErrors.keys()) console.log(" -", e);
}
