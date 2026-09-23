/**
 * Full audit of EVERY admin page in school mode.
 *
 * Logs in as the super admin, selects a school (default: Green Valley School,
 * which has seeded data), then visits each page and reports:
 *   - failing API calls (>=400) with the endpoint
 *   - main list endpoint counts actually returned
 *   - empty-state / error text visible in the page
 *   - JS console errors
 *
 * Run: node scripts/audit_school_mode_panel.mjs [School Name]
 */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const EMAIL = process.env.PROBE_USER || "bizaymndl@gmail.com";
const PASSWORD = process.env.PROBE_PASS || "Admin@1234";
const SCHOOL = process.argv[2] || "Green Valley School";

const PAGES = [
  ["/admin", "Dashboard"],
  ["/admin/students", "Students"],
  ["/admin/student-records", "Student Records"],
  ["/admin/teachers", "Teachers"],
  ["/admin/classrooms", "Classrooms"],
  ["/admin/academics", "Academics Hub"],
  ["/admin/timetable", "Timetable"],
  ["/admin/attendance", "Attendance"],
  ["/admin/exams", "Examinations"],
  ["/admin/report-cards", "Report Cards"],
  ["/admin/announcements", "Announcements"],
  ["/admin/communication-center", "Communication Center"],
  ["/admin/fees", "Fee Management"],
  ["/admin/finance-center", "Finance Center"],
  ["/admin/hr-center", "HR Center"],
  ["/admin/timetable-center", "Timetable Center"],
  ["/admin/reports", "Reports"],
  ["/admin/reporting-center", "Reporting Center"],
  ["/admin/library", "Library"],
  ["/admin/hostel-center", "Hostel Center"],
  ["/admin/transportation-center", "Transportation Center"],
  ["/admin/inventory-center", "Inventory Center"],
  ["/admin/cafeteria", "Cafeteria"],
  ["/admin/health", "Health Clinic"],
  ["/admin/behavior", "Behavior"],
  ["/admin/counseling", "Counseling"],
  ["/admin/alumni", "Alumni"],
  ["/admin/sports", "Sports"],
  ["/admin/admissions-center", "Admissions Center"],
  ["/admin/conferences-center", "Conferences Center"],
  ["/admin/security-center", "Auth Center"],
  ["/admin/plan-billing", "Plan & Billing"],
];

const EMPTY_PATTERNS = [
  /no .{0,24}(found|yet|available|records|data|results)/i,
  /nothing (here|to show)/i,
  /no data/i,
];

const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: 1600, height: 1000 } });
const page = await context.newPage();

let failures = [];
let counts = new Map();
let consoleErrors = [];

page.on("response", async (r) => {
  if (!r.url().includes("/api/v1/")) return;
  const path = r.url().split("/api/v1/")[1].split("?")[0];
  if (r.status() >= 400) {
    failures.push(`${r.status()} ${path}`);
    return;
  }
  const ct = r.headers()["content-type"] || "";
  if (ct.includes("json")) {
    try {
      const body = await r.json();
      if (body && typeof body.count === "number") counts.set(path, body.count);
    } catch {
      /* ignore */
    }
  }
});
page.on("console", (m) => {
  if (m.type() === "error" && !m.text().includes("WebSocket"))
    consoleErrors.push(m.text().slice(0, 110));
});
page.on("pageerror", (e) => consoleErrors.push(`PAGEERROR ${String(e).slice(0, 110)}`));

// ── login + select school ────────────────────────────────────────────────────
await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
await page.waitForSelector("input[type=email]", { timeout: 30000 });
await page.fill("input[type=email]", EMAIL);
await page.fill("input[type=password]", PASSWORD);
await page.click("button[type=submit]");
await page.waitForURL("**/admin**", { timeout: 40000 });
await page.waitForTimeout(2500);

await page.click("button:has-text('All Schools')");
await page.waitForTimeout(800);
await page.fill("input[placeholder*='earch']", SCHOOL);
await page.waitForTimeout(900);
await page.click(`text=${SCHOOL}`);
await page.waitForTimeout(1500);

const badge = await page.evaluate(() => {
  const el = [...document.querySelectorAll("aside p, aside div")].find((n) =>
    n.textContent?.includes("Active School"),
  );
  return el ? el.innerText.replace(/\n/g, " ") : "no badge";
});
console.log(`SCHOOL CONTEXT: ${badge}\n`);

const results = [];

for (const [path, label] of PAGES) {
  failures = [];
  counts = new Map();
  consoleErrors = [];

  await page.goto(`${BASE}${path}`, { waitUntil: "domcontentloaded" }).catch(() => {});
  // wait for content to settle (polling HMR means first paint can be slower)
  await page.waitForTimeout(3200);

  const text = await page.evaluate(() =>
    (document.querySelector("main") || document.body).innerText.slice(0, 4000),
  );
  const emptyHits = EMPTY_PATTERNS.filter((re) => re.test(text)).map((re) => String(re));
  const hasContent = text.replace(/\s+/g, " ").trim().length > 60;
  const countsObj = Object.fromEntries(counts);

  results.push({
    path,
    label,
    failures: [...new Set(failures)],
    counts: countsObj,
    emptyHits,
    hasContent,
    consoleErrors: [...new Set(consoleErrors)],
  });
}

await browser.close();

// ── report ──────────────────────────────────────────────────────────────────
console.log("=".repeat(100));
console.log("PAGE".padEnd(30), "STATUS".padEnd(12), "NOTES");
console.log("=".repeat(100));

let problems = 0;
for (const r of results) {
  const issues = [];
  if (r.failures.length) issues.push(`API FAIL: ${r.failures.slice(0, 3).join(", ")}`);
  if (!r.hasContent) issues.push("EMPTY PAGE (no content rendered)");
  if (r.emptyHits.length && Object.values(r.counts).every((c) => c === 0))
    issues.push("empty-state + all counts 0");
  if (r.consoleErrors.length) issues.push(`console: ${r.consoleErrors[0]}`);

  const countStr = Object.entries(r.counts)
    .map(([k, v]) => `${k.split("/").slice(-2).join("/")}=${v}`)
    .slice(0, 3)
    .join(" ");

  const status = issues.length ? "PROBLEM" : "ok";
  if (issues.length) problems++;
  console.log(
    r.label.padEnd(30),
    status.padEnd(12),
    (issues.join(" | ") || countStr).slice(0, 150),
  );
}

console.log("=".repeat(100));
console.log(`pages with problems: ${problems}/${results.length}`);
