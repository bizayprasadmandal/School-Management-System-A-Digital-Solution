import { chromium } from "playwright";
const BASE = "http://localhost:5173";
const EMAIL = process.env.ROLE_USER || "teacher@school.edu";
const PASS = process.env.ROLE_PASS || "Teacher@1234";

const browser = await chromium.launch();
const page = await browser.newContext({ viewport: { width: 1700, height: 1000 } }).then(c => c.newPage());
page.on("response", (r) => {
  if (r.url().includes("/api/v1/auth")) console.log("AUTH:", r.status(), r.url().split("/api/v1/")[1]);
});
page.on("console", (m) => { if (m.type() === "error") console.log("CONSOLE:", m.text().slice(0, 160)); });

await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
await page.waitForSelector("input[type=email]", { timeout: 40000 });
await page.fill("input[type=email]", EMAIL);
await page.fill("input[type=password]", PASS);
await page.click("button[type=submit]");
await page.waitForTimeout(6000);
console.log("URL:", page.url());
console.log("TEXT:", (await page.evaluate(() => document.body.innerText.replace(/\s+/g, " ").slice(0, 300))));
await browser.close();
