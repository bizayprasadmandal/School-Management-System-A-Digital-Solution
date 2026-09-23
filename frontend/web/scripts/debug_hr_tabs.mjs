/** Debug: why does the HR Center tab walk collect no tabs? */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const browser = await chromium.launch();
const page = await browser
  .newContext({ viewport: { width: 1700, height: 1000 } })
  .then((c) => c.newPage());

await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
await page.waitForSelector("input[type=email]", { timeout: 40000 });
await page.fill("input[type=email]", "bizaymndl@gmail.com");
await page.fill("input[type=password]", "Admin@1234");
await page.click("button[type=submit]");
await page.waitForURL("**/admin**", { timeout: 60000 });
await page.waitForTimeout(3000);
await page.click("button:has-text('All Schools')");
await page.waitForTimeout(900);
await page.fill("input[placeholder*='earch']", "Green Valley School");
await page.waitForTimeout(1000);
await page.click("text=Green Valley School");
await page.waitForTimeout(2000);

await page.goto(`${BASE}/admin/hr-center`, { waitUntil: "domcontentloaded" });
for (const wait of [3000, 3000, 4000]) {
  await page.waitForTimeout(wait);
  const info = await page.evaluate(() => {
    const main = document.querySelector("main");
    const all = [...document.querySelectorAll("main button")];
    const strip = all.filter((b) => b.className.includes("shrink-0") && b.innerText.trim());
    return {
      hasMain: !!main,
      mainText: (main?.innerText || "").slice(0, 120).replace(/\n/g, " | "),
      totalButtons: all.length,
      stripCount: strip.length,
      first5: strip.slice(0, 5).map((b) => b.innerText.trim()),
      hasOldDashboardTab: strip.some((b) => b.innerText.trim() === "H R Dashboard Metrics"),
    };
  });
  console.log(JSON.stringify(info, null, 1));
}

// try clicking the 3rd strip button
const clicked = await page.evaluate(() => {
  const strip = [...document.querySelectorAll("main button")].filter(
    (b) => b.className.includes("shrink-0") && b.innerText.trim(),
  );
  const btn = strip[2];
  if (!btn) return "no button";
  btn.click();
  return btn.innerText.trim();
});
console.log("clicked:", clicked);
await page.waitForTimeout(2500);
const after = await page.evaluate(() =>
  (document.querySelector("main")?.innerText || "").slice(0, 200),
);
console.log("after:", after.replace(/\n/g, " | "));

await browser.close();
