/**
 * Crawl the admin panel as a super admin with a school selected, collecting
 * every API request that returns >=400 so we can see exactly which endpoints
 * fail in school-context mode. Run: node scripts/crawl_superadmin_failures.mjs
 */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const EMAIL = process.env.PROBE_USER || "bizaymndl@gmail.com";
const PASSWORD = process.env.PROBE_PASS || "Admin@1234";

const PAGES = [
  "/admin",
  "/admin/students",
  "/admin/academics",
  "/admin/attendance",
  "/admin/fees",
  "/admin/finance-center",
  "/admin/announcements",
  "/admin/communication-center",
  "/admin/hr-center",
  "/admin/timetable",
  "/admin/reports",
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

const browser = await chromium.launch();
const page = await browser
  .newContext({ viewport: { width: 1600, height: 1000 } })
  .then((c) => c.newPage());

const failures = new Map(); // url -> {status, count}
let schoolHeaderSeen = false;

page.on("request", (r) => {
  if (r.url().includes("/api/v1/") && r.headers()["x-school-id"]) schoolHeaderSeen = true;
});
page.on("response", (r) => {
  if (r.url().includes("/api/v1/") && r.status() >= 400) {
    const key = `${r.status()} ${r.url().replace("http://localhost:8000/api/v1/", "")}`;
    failures.set(key, (failures.get(key) || 0) + 1);
  }
});
page.on("console", (m) => {
  if (m.type() === "error" && !m.text().includes("WebSocket")) {
    // ignore ws noise; real JS errors show up as page failures anyway
  }
});

await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
await page.waitForSelector("input[type=email]", { timeout: 20000 });
await page.fill("input[type=email]", EMAIL);
await page.fill("input[type=password]", PASSWORD);
await page.click("button[type=submit]");
await page.waitForURL("**/admin**", { timeout: 30000 });
await page.waitForTimeout(2000);

// select Bright Future Academy in the switcher
await page.click("button:has-text('All Schools')");
await page.waitForTimeout(800);
await page.fill("input[placeholder*='earch']", "Bright Future");
await page.waitForTimeout(800);
await page.click("text=Bright Future Academy");
await page.waitForTimeout(1500);
console.log("school selected, X-School-ID header seen:", schoolHeaderSeen);

for (const path of PAGES) {
  failures.clear();
  const before = new Set();
  await page.goto(`${BASE}${path}`, { waitUntil: "domcontentloaded" }).catch(() => {});
  await page.waitForTimeout(2200);
  const url404 = [...failures.keys()].filter((k) => k.startsWith("404 "));
  console.log(`\n=== ${path} — ${failures.size ? `${failures.size} failing` : "all OK"} ===`);
  for (const k of [...failures.keys()].slice(0, 8)) console.log("  ", k, `(x${failures.get(k)})`);
}

await browser.close();
console.log("\nDONE");
