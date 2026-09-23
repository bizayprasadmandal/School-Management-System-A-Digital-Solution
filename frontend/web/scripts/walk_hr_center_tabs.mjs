/**
 * HR Center tab sweep — clicks every tab and records any API failure.
 *
 * Dedicated because the generic walker occasionally loses this page (it is the
 * largest tab strip in the app): this version waits for hydration before
 * reading the strip and logs the exact endpoint each tab calls.
 *
 * Run: node scripts/walk_hr_center_tabs.mjs ["Green Valley School"]
 */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const SCHOOL = process.argv[2] || "Green Valley School";

let failures = [];
const browser = await chromium.launch();
const page = await browser
  .newContext({ viewport: { width: 1700, height: 1000 } })
  .then((c) => c.newPage());

page.on("response", (r) => {
  if (!r.url().includes("/api/v1/")) return;
  if (r.status() >= 400)
    failures.push(`${r.status()} ${r.url().split("/api/v1/")[1].split("?")[0]}`);
});

await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
await page.waitForSelector("input[type=email]", { timeout: 40000 });
await page.fill("input[type=email]", "bizaymndl@gmail.com");
await page.fill("input[type=password]", "Admin@1234");
await page.click("button[type=submit]");
await page.waitForURL("**/admin**", { timeout: 60000 });
await page.waitForTimeout(3000);
await page.click("button:has-text('All Schools')");
await page.waitForTimeout(900);
await page.fill("input[placeholder*='earch']", SCHOOL);
await page.waitForTimeout(1000);
await page.click(`text=${SCHOOL}`);
await page.waitForTimeout(2000);

await page.goto(`${BASE}/admin/hr-center`, { waitUntil: "domcontentloaded" });
await page.waitForSelector("button:has-text('Payroll Runs')", { timeout: 40000 });
await page.waitForTimeout(2500);

const labels = await page.evaluate(() =>
  [...document.querySelectorAll("main button")]
    .filter((b) => b.className.includes("shrink-0") && b.innerText.trim())
    .map((b) => b.innerText.trim()),
);
console.log(`HR Center tabs: ${labels.length}\n`);

let flagged = 0;
for (const [i, label] of labels.entries()) {
  failures = [];
  await page.evaluate((lbl) => {
    const btn = [...document.querySelectorAll("main button")].find(
      (b) => b.className.includes("shrink-0") && b.innerText.trim() === lbl,
    );
    btn?.click();
  }, label);
  await page.waitForTimeout(1500);
  const text = await page.evaluate(() =>
    (document.querySelector("main")?.innerText || "").slice(0, 3000),
  );
  const empty = /no .{0,30}(found|yet|records|data|results)/i.test(text);
  const uniq = [...new Set(failures)];
  if (uniq.length || empty) {
    flagged++;
    console.log(
      `${(i + 1).toString().padStart(2)}. ${label.padEnd(28)} ${uniq.join(",") || "EMPTY"}`,
    );
  }
}
console.log(`\ntabs: ${labels.length} | flagged: ${flagged}`);
await browser.close();
