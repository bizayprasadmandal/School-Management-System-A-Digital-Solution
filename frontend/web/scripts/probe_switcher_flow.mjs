/**
 * Reproduce the super-admin switcher flow end to end:
 * login → pick school in switcher → click Students → watch network.
 *
 * Logs every /api/v1 request with its X-School-ID header and the students
 * response count. Run: node scripts/probe_switcher_flow.mjs
 */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const EMAIL = process.env.PROBE_USER || "bizaymndl@gmail.com";
const PASSWORD = process.env.PROBE_PASS || "Admin@1234";

const browser = await chromium.launch();
const page = await browser
  .newContext({ viewport: { width: 1600, height: 1000 } })
  .then((c) => c.newPage());

const requests = [];
page.on("request", (r) => {
  if (r.url().includes("/api/v1/")) {
    requests.push({ url: r.url(), schoolHeader: r.headers()["x-school-id"] ?? null });
  }
});
page.on("response", async (r) => {
  if (r.url().includes("/api/v1/students/?") || r.url().endsWith("/api/v1/students/")) {
    let count = null;
    try {
      const body = await r.json();
      count = body.count;
    } catch {
      /* non-JSON */
    }
    console.log(">> students response:", r.status(), "count:", count);
  }
});

await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
await page.waitForSelector("input[type=email], input[name=email]", { timeout: 20000 });
await page.fill("input[type=email], input[name=email]", EMAIL);
await page.fill("input[type=password], input[name=password]", PASSWORD);
await page.click("button[type=submit]");
await page.waitForURL("**/admin**", { timeout: 30000 });
await page.waitForTimeout(2000);

// open the school switcher and pick Bright Future Academy
await page.click("header button:has-text('All Schools'), button:has-text('All Schools')");
await page.waitForTimeout(800);
await page.fill("input[placeholder*='earch']", "Bright Future");
await page.waitForTimeout(800);
const option = await page.waitForSelector("text=Bright Future Academy", { timeout: 10000 });
await option.click();
await page.waitForTimeout(1500);

const switcherText = await page.evaluate(() => {
  const btn = [...document.querySelectorAll("button")].find(
    (b) => b.textContent.includes("Bright Future") || b.textContent.includes("All Schools"),
  );
  return btn ? btn.innerText : "switcher not found";
});
console.log(">> switcher now shows:", JSON.stringify(switcherText));

// navigate to Students via the sidebar (expand Academics group if collapsed)
const studentsLink = await page.$('a[href="/admin/students"]');
if (!studentsLink) {
  await page.click('aside button:has-text("Academics")');
  await page.waitForTimeout(500);
}
await page.click('a[href="/admin/students"]');
await page.waitForTimeout(2500);

const bodyText = await page.evaluate(() => document.body.innerText.slice(0, 600));
console.log(">> students page snippet:", JSON.stringify(bodyText.slice(0, 300)));

console.log("\n=== API requests after login ===");
for (const r of requests) {
  if (r.url.includes("/students") || r.url.includes("students?")) {
    console.log(
      `[students] X-School-ID=${r.schoolHeader ? r.schoolHeader.slice(0, 8) : "none"} ${r.url.slice(
        0,
        90,
      )}`,
    );
  }
}
const studentsReqs = requests.filter((r) => r.url.includes("/students"));
console.log(`\nTotal /students requests: ${studentsReqs.length}`);
console.log(`With X-School-ID header: ${studentsReqs.filter((r) => r.schoolHeader).length}`);

await browser.close();
