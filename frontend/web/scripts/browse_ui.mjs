/**
 * Browse the admin UI with seeded data: log in as the demo admin, visit every
 * module page, and report headings, seeded rows, console errors, failed API
 * calls, and error-boundary crashes per page.
 *
 * Run: node scripts/browse_ui.mjs
 */
import { chromium } from "playwright";
import fs from "fs";

const BASE = "http://localhost:5173";
const API = "http://localhost:8000/api/v1";
const EMAIL = process.env.BROWSE_USER || "admin@greenvalley.edu";
const PASS = process.env.BROWSE_PASS || "Admin@1234";

const PAGES = [
  "/admin",
  "/admin/attendance",
  "/admin/attendance-center",
  "/admin/timetable",
  "/admin/gradebook-center",
  "/admin/finance-center",
  "/admin/fees",
  "/admin/library",
  "/admin/behavior",
  "/admin/sports",
  "/admin/health",
  "/admin/alumni",
  "/admin/cafeteria",
  "/admin/hostel",
  "/admin/transportation-center",
  "/admin/inventory-center",
  "/admin/infrastructure",
  "/admin/hr",
  "/admin/admissions-center",
  "/admin/communication",
  "/admin/conferences-center",
  "/admin/reporting-center",
  "/admin/counseling",
  "/admin/students",
  "/admin/student-records",
  "/admin/academics",
  "/admin/exams",
  "/admin/settings",
];

const results = [];

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 1600, height: 1000 } });
const page = await ctx.newPage();

// Collect diagnostics
let consoleErrors = [];
let failedApi = [];
let apiItems = 0; // total JSON list items the page actually received
let apiUrls = [];
page.on("console", (msg) => {
  if (msg.type() === "error") consoleErrors.push(msg.text().slice(0, 220));
});
page.on("response", async (res) => {
  if (
    !res.url().includes("/api/") ||
    !res
      .request()
      .method()
      .match(/^(GET|HEAD)$/)
  )
    return;
  if (res.status() >= 400) {
    failedApi.push(`${res.status()} ${res.url().replace(API, "")}`);
  }
  apiUrls.push(`${res.status()} ${res.url().replace(API, "").split("?")[0]}`);
  try {
    const ct = res.headers()["content-type"] || "";
    if (!ct.includes("application/json")) return;
    const json = await res.json();
    if (Array.isArray(json)) apiItems += json.length;
    else if (json && Array.isArray(json.results)) apiItems += json.results.length;
    else if (json && typeof json === "object" && !Array.isArray(json.results)) apiItems += 1;
  } catch {
    /* non-JSON or stream consumed elsewhere */
  }
});

// ─── Login ──────────────────────────────────────────────────────────────────
await page.goto(`${BASE}/login`, { waitUntil: "load", timeout: 30000 });
await page.waitForSelector('input[type="email"]', { timeout: 15000 });
await page.fill('input[type="email"]', EMAIL);
await page.fill('input[type="password"]', PASS);
await page.click('button[type="submit"]');
try {
  await page.waitForURL(/\/admin/, { timeout: 20000 });
  console.log(`LOGIN OK → ${page.url()}`);
} catch {
  console.log(`LOGIN FAILED — still at ${page.url()}`);
  process.exit(1);
}

// ─── Visit pages ────────────────────────────────────────────────────────────
for (const path of PAGES) {
  consoleErrors = [];
  failedApi = [];
  apiItems = 0;
  apiUrls = [];
  let ok = true;
  let heading = "";
  let crash = "";
  let body = "";
  try {
    await page.goto(`${BASE}${path}`, { waitUntil: "domcontentloaded", timeout: 30000 });
    await page.waitForTimeout(2500);
    const h1 = page.locator("h1").first();
    heading = (await h1.textContent({ timeout: 5000 }).catch(() => "")) || "";
    body =
      (await page
        .locator("body")
        .innerText({ timeout: 5000 })
        .catch(() => "")) || "";
    if (/something went wrong|unexpected error/i.test(body)) {
      crash = (body.match(/[A-Za-z ]*(?:Cannot read|undefined|null)[^\n]*/i) || [
        "unknown crash",
      ])[0];
      ok = false;
    }
  } catch (e) {
    ok = false;
    crash = `navigation error: ${String(e).slice(0, 140)}`;
  }
  const realApiErrors = failedApi.filter(
    (f) => !f.includes("health") && !f.includes("ws") && !f.includes("me/"),
  );
  results.push({
    path,
    ok,
    heading: heading.trim().slice(0, 60),
    crash: crash.slice(0, 120),
    apiItems,
    apiUrls: [...new Set(apiUrls)].slice(0, 12),
    consoleErrors: consoleErrors.slice(0, 3),
    apiErrors: realApiErrors.slice(0, 3),
  });
  const flag = ok ? "✓" : "✗";
  console.log(
    `${flag} ${path.padEnd(28)} h1="${heading.trim().slice(0, 36)}" apiItems=${String(
      apiItems,
    ).padStart(4)}${crash ? "  CRASH: " + crash.slice(0, 70) : ""}${
      realApiErrors.length ? "  api: " + realApiErrors[0] : ""
    }`,
  );
}

// ─── Summary ────────────────────────────────────────────────────────────────
const bad = results.filter((r) => !r.ok);
const thin = results.filter((r) => r.ok && r.apiItems === 0);
console.log("\n================ SUMMARY ================");
console.log(
  `pages: ${results.length}, ok: ${results.length - bad.length}, problems: ${
    bad.length
  }, no-api-data: ${thin.length}`,
);
for (const r of thin) {
  console.log(`  ~ ${r.path} (renders, but received 0 list items from the API)`);
  for (const u of r.apiUrls) console.log(`      ${u}`);
}
for (const r of bad) {
  console.log(`\n✗ ${r.path}`);
  if (r.crash) console.log(`   crash: ${r.crash}`);
  for (const c of r.consoleErrors) console.log(`   console: ${c}`);
  for (const a of r.apiErrors) console.log(`   api: ${a}`);
}

// Screenshots of the most data-heavy pages
fs.mkdirSync("browse-shots", { recursive: true });
for (const p of [
  "/admin",
  "/admin/timetable",
  "/admin/gradebook-center",
  "/admin/fees",
  "/admin/attendance",
  "/admin/inventory-center",
]) {
  await page.goto(`${BASE}${p}`, { waitUntil: "domcontentloaded", timeout: 30000 });
  await page.waitForTimeout(2000);
  const name = p.replace(/\//g, "_") || "home";
  await page.screenshot({ path: `browse-shots/${name}.png`, fullPage: false });
}
console.log("\nscreenshots saved to frontend/web/browse-shots/");
await browser.close();
