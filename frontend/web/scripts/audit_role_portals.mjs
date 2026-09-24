/**
 * Role-portal audit: walk every page of a role's portal as a demo user and
 * capture failing API calls (>=400) plus in-page error text.
 *
 * Usage:
 *   ROLE=parent node scripts/audit_role_portals.mjs
 *   ROLE=student ROLE_USER=student@school.edu ROLE_PASS=Student@1234 node scripts/audit_role_portals.mjs
 */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const ROLE = process.env.ROLE || "parent";

const USERS = {
  parent: {
    email: process.env.ROLE_USER || "parent@school.edu",
    pass: process.env.ROLE_PASS || "Parent@1234",
    prefix: "/parent",
  },
  student: {
    email: process.env.ROLE_USER || "student@school.edu",
    pass: process.env.ROLE_PASS || "Student@1234",
    prefix: "/student",
  },
  teacher: {
    email: process.env.ROLE_USER || "teacher@school.edu",
    pass: process.env.ROLE_PASS || "Teacher@1234",
    prefix: "/teacher",
  },
};
const user = USERS[ROLE];
const afterLogin = `**/${ROLE}**`;

const PAGES = (process.env.AUDIT_PAGES || "")
  .split(",")
  .map((p) => p.trim())
  .filter(Boolean);

const browser = await chromium.launch();
const context = await browser.newContext({ viewport: { width: 1700, height: 1000 } });
const page = await context.newPage();

const failures = new Map(); // page -> Set of "status path"
const errorText = new Map(); // page -> first error snippet

let current = "(login)";
page.on("response", (r) => {
  if (!r.url().includes("/api/v1/")) return;
  if (r.status() >= 400) {
    if (!failures.has(current)) failures.set(current, new Set());
    const path = r.url().split("/api/v1/")[1].split("?")[0];
    failures.get(current).add(`${r.status()} ${path}`);
  }
});
page.on("console", (m) => {
  if (m.type() === "error" && m.text().includes("WebSocket")) return;
});

await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
await page.waitForSelector("input[type=email]", { timeout: 40000 });
await page.fill("input[type=email]", user.email);
await page.fill("input[type=password]", user.pass);
await page.click("button[type=submit]");
await page.waitForURL(afterLogin, { timeout: 60000 }).catch(() => {});
await page.waitForTimeout(4500);

// discover routes from the sidebar/nav links pointing at the role prefix
const links = await page.evaluate((prefix) => {
  return [...document.querySelectorAll('a[href^="' + prefix + '"]')]
    .map((a) => a.getAttribute("href"))
    .filter((h, i, arr) => h && arr.indexOf(h) === i);
}, user.prefix);

const pages = PAGES.length ? PAGES : links;
console.log(`${ROLE} portal: ${pages.length} pages to audit\n`);

for (const p of pages) {
  current = p;
  await page.goto(`${BASE}${p}`, { waitUntil: "domcontentloaded" }).catch(() => {});
  await page.waitForTimeout(2200);
  const text = await page.evaluate(() => {
    const main = document.querySelector("main") || document.body;
    return main.innerText.replace(/\s+/g, " ").slice(0, 2500);
  });
  const m = text.match(
    /failed to load|something went wrong|could not (load|fetch)|error loading|unable to load|request failed/i,
  );
  if (m) errorText.set(p, m[0]);
  console.log(`visited ${p}${m ? "  ERROR-TEXT: " + m[0] : ""}`);
}

await browser.close();

console.log("\n" + "=".repeat(80));
let flagged = 0;
for (const [p, fs] of failures) {
  console.log(`${p}: ${[...fs].join(", ")}`);
  flagged++;
}
for (const [p, t] of errorText) {
  if (!failures.has(p)) console.log(`${p}: error text (${t})`);
  flagged++;
}
console.log("=".repeat(80));
console.log(`pages: ${pages.length} | flagged: ${flagged}`);
