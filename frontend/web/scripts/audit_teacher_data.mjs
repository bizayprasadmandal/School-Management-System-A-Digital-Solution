/**
 * Teacher-portal data audit: walk every page, capture API response counts
 * (rows actually returned) and main-text length, flagging pages where every
 * data endpoint returned 0 rows or the page rendered almost nothing.
 *
 * Run: ROLE=teacher ROLE_USER=... ROLE_PASS=... node scripts/audit_teacher_data.mjs
 */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const EMAIL = process.env.ROLE_USER || "teacher@school.edu";
const PASS = process.env.ROLE_PASS || "Teacher@1234";

const PAGES = (
  process.env.AUDIT_PAGES ||
  "/teacher,/teacher/attendance,/teacher/gradebook,/teacher/assignments,/teacher/timetable,/teacher/messages,/teacher/lesson-plans,/teacher/conferences,/teacher/settings,/teacher/health,/teacher/library,/teacher/sports,/teacher/behavior,/teacher/counseling,/teacher/my-payslips"
)
  .split(",")
  .map((p) => p.trim())
  .filter(Boolean);

const browser = await chromium.launch();
const page = await browser
  .newContext({ viewport: { width: 1700, height: 1000 } })
  .then((c) => c.newPage());

// login
await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
await page.waitForSelector("input[type=email]", { timeout: 40000 });
await page.fill("input[type=email]", EMAIL);
await page.fill("input[type=password]", PASS);
await page.click("button[type=submit]");
await page.waitForURL("**/teacher**", { timeout: 60000 }).catch(() => {});
await page.waitForTimeout(4000);

const results = [];

for (const p of PAGES) {
  const apiCounts = new Map(); // path -> row count
  const onResp = async (r) => {
    if (!r.url().includes("/api/v1/")) return;
    const path = r.url().split("/api/v1/")[1].split("?")[0];
    if (r.status() >= 400) {
      apiCounts.set(`${r.status()} ${path}`, -1);
      return;
    }
    try {
      const ct = r.headers()["content-type"] || "";
      if (!ct.includes("json")) return;
      const body = await r.json();
      const n = Array.isArray(body)
        ? body.length
        : typeof body.count === "number"
          ? body.count
          : body.results
            ? body.results.length
            : null;
      if (n !== null) apiCounts.set(path, n);
    } catch {}
  };
  page.on("response", onResp);

  await page.goto(`${BASE}${p}`, { waitUntil: "domcontentloaded" }).catch(() => {});
  await page.waitForTimeout(2500);

  const textLen = await page.evaluate(() => {
    const main = document.querySelector("main") || document.body;
    return main.innerText.replace(/\s+/g, " ").trim().length;
  });

  page.off("response", onResp);

  const entries = [...apiCounts.entries()];
  const dataEndpoints = entries.filter(([k]) => !k.startsWith("4") && !k.startsWith("5"));
  const zeroRows = dataEndpoints.filter(([, v]) => v === 0);
  const failures = entries.filter(([k]) => /^4|^5/.test(k));
  const empty =
    (dataEndpoints.length === 0 || zeroRows.length === dataEndpoints.length) &&
    textLen < 400;

  results.push({ p, textLen, zeroRows, failures, empty, endpoints: entries.length });
  console.log(
    `${empty ? "EMPTY " : "ok    "}${p}  text=${textLen}  endpoints=${entries.length}` +
      (zeroRows.length ? `  zero:[${zeroRows.map(([k]) => k).join(", ")}]` : "") +
      (failures.length ? `  FAIL:[${failures.map(([k]) => k).join(", ")}]` : ""),
  );
}

await browser.close();

const empties = results.filter((r) => r.empty);
console.log("\n" + "=".repeat(80));
console.log(
  `pages: ${results.length} | empty: ${empties.length} | ` +
    empties.map((r) => r.p).join(", "),
);
