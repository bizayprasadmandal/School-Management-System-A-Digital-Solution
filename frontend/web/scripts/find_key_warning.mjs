/**
 * Locate the source of 'Each child in a list should have a unique "key" prop'
 * by capturing the warning's component stack on a few admin pages.
 *
 * Run: node scripts/find_key_warning.mjs
 */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const EMAIL = process.env.PROBE_USER || "bizaymndl@gmail.com";
const PASSWORD = process.env.PROBE_PASS || "Admin@1234";
const PAGES = (process.env.PROBE_PAGES || "/admin/students,/admin/library,/admin/cafeteria").split(
  ",",
);

const browser = await chromium.launch();
const page = await browser
  .newContext({ viewport: { width: 1700, height: 1000 } })
  .then((c) => c.newPage());

page.on("console", (m) => {
  const t = m.text();
  if (t.includes('unique "key" prop')) {
    console.log("\n=== KEY WARNING ===", t.slice(0, 80));
    // React passes the component stack as the second console argument
    for (const a of m.args().slice(1)) {
      a.jsonValue()
        .then((v) => console.log("STACK:", String(v).split("\n").slice(0, 10).join("\n")))
        .catch(() => {});
    }
  }
});

await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
await page.waitForSelector("input[type=email]", { timeout: 40000 });
await page.fill("input[type=email]", EMAIL);
await page.fill("input[type=password]", PASSWORD);
await page.click("button[type=submit]");
await page.waitForURL("**/admin**", { timeout: 60000 });
await page.waitForTimeout(2500);

// switch to a school so real data renders
await page.click("button:has-text('All Schools')");
await page.waitForTimeout(800);
await page.fill("input[placeholder*='earch']", "Green Valley");
await page.waitForTimeout(900);
await page.click("text=Green Valley");
await page.waitForTimeout(2000);

for (const p of PAGES) {
  await page.goto(`${BASE}${p}`, { waitUntil: "domcontentloaded" }).catch(() => {});
  await page.waitForTimeout(2500);
  console.log(`visited ${p}`);
}

await browser.close();
console.log("\ndone");
