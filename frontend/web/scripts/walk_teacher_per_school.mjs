/**
 * Teacher-portal browser walk, one school at a time.
 *
 * Mode A (form login):  node scripts/walk_teacher_per_school.mjs <email> <password>
 * Mode B (token injection, for demo accounts with emails the login form
 *        can't submit): node scripts/walk_teacher_per_school.mjs --token <file-with-jwt>
 *
 * Visits the teacher pages, records per-page API counts / failures / text
 * volume, and prints a PASS/FAIL line per page.
 */
import { chromium } from "playwright";
import fs from "fs";

const BASE = "http://localhost:5173";
const EMAIL = process.argv[2];
const PASSWORD = process.argv[3];
const TOKEN_FILE = process.argv[2] === "--token" ? process.argv[3] : null;

const PAGES = [
  "/teacher",
  "/teacher/assignments",
  "/teacher/lesson-plans",
  "/teacher/gradebook",
  "/teacher/attendance",
  "/teacher/my-payslips",
  "/teacher/messages",
  "/teacher/conferences",
];

const browser = await chromium.launch();
const page = await browser
  .newContext({ viewport: { width: 1700, height: 1000 } })
  .then((c) => c.newPage());

if (TOKEN_FILE) {
  const token = fs.readFileSync(TOKEN_FILE, "utf8").trim();
  await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
  // Fetch the user profile so the auth store's `user` (route guards read it)
  // is populated, not just the tokens.
  const me = await page.evaluate(async (t) => {
    const r = await fetch("http://localhost:8000/api/v1/auth/me/", {
      headers: { Authorization: `Bearer ${t}` },
    });
    return r.ok ? await r.json() : null;
  }, token);
  await page.evaluate(
    ([t, user]) => {
      localStorage.setItem(
        "sms-auth",
        JSON.stringify({
          state: { tokens: { access: t }, user, isAuthenticated: true },
          version: 0,
        }),
      );
    },
    [token, me],
  );
  await page.reload({ waitUntil: "domcontentloaded" });
  await page.waitForTimeout(4000);
  // Warm-up: after token injection the first navigation races SPA hydration.
  await page.goto(`${BASE}/teacher`, { waitUntil: "domcontentloaded" }).catch(() => {});
  await page.waitForTimeout(6000);
} else {
  await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
  await page.waitForSelector("input[type=email]", { timeout: 40000 });
  await page.fill("input[type=email]", EMAIL);
  await page.fill("input[type=password]", PASSWORD);
  await page.click("button[type=submit]");
  await page.waitForURL("**/teacher**", { timeout: 60000 }).catch(() => {});
  await page.waitForTimeout(4000);
}

const who = await page.evaluate(() => {
  try {
    const s = JSON.parse(localStorage.getItem("sms-auth") || "{}");
    return {
      role: s.state?.user?.role,
      name: s.state?.user?.first_name,
      authed: s.state?.isAuthenticated,
    };
  } catch {
    return {};
  }
});
console.log(
  `session: role=${who.role} name=${who.name} authed=${who.authed}` +
    (TOKEN_FILE ? " (token-injected)" : ` (${EMAIL})`),
);
if (!who.authed) {
  console.error("NOT AUTHENTICATED — aborting walk");
  await browser.close();
  process.exit(1);
}

const results = [];

for (const p of PAGES) {
  const apiCounts = new Map();
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
  const dataEndpoints = entries.filter(([k]) => !/^[45]/.test(k));
  const zeroRows = dataEndpoints.filter(([, v]) => v === 0);
  const failures = entries.filter(([k]) => /^[45]/.test(k));
  const withData = dataEndpoints.filter(([, v]) => v > 0).length;
  const empty =
    (dataEndpoints.length === 0 || zeroRows.length === dataEndpoints.length) && textLen < 400;
  const pass = !empty && failures.length === 0;

  results.push({ p, pass, textLen, withData, failures });
  console.log(
    `${pass ? "PASS " : "FAIL "}${p}  text=${textLen}  data-eps=${withData}/${entries.length}` +
      (failures.length ? `  FAIL:[${failures.map(([k]) => k).join(", ")}]` : "") +
      (zeroRows.length && !pass ? `  zero:[${zeroRows.map(([k]) => k).join(", ")}]` : ""),
  );
}

await browser.close();

const failed = results.filter((r) => !r.pass);
console.log("\n" + "=".repeat(70));
console.log(
  `pages: ${results.length} | passed: ${results.length - failed.length}` +
    (failed.length ? ` | FAILED: ${failed.map((r) => r.p).join(", ")}` : " — ALL PASS"),
);
