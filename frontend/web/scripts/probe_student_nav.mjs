/** Debug: capture the login network response + console/page errors. */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const EMAIL = process.env.PROBE_USER || "student056@demo.edusphere.school";
const PASS = process.env.PROBE_PASS || "Student@1234";

const browser = await chromium.launch();
const page = await browser
  .newContext({ viewport: { width: 1700, height: 1000 } })
  .then((c) => c.newPage());

page.on("response", async (r) => {
  if (r.url().includes("/api/v1/auth/login")) {
    console.log("LOGIN RESP:", r.status(), r.url());
    try {
      console.log((await r.text()).slice(0, 300));
    } catch {}
  }
});
page.on("console", (m) => {
  if (m.type() === "error") console.log("CONSOLE:", m.text().slice(0, 200));
});
page.on("pageerror", (e) => console.log("PAGEERROR:", String(e).slice(0, 200)));

await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded" });
await page.waitForSelector("input[type=email]", { timeout: 40000 });
await page.fill("input[type=email]", EMAIL);
await page.fill("input[type=password]", PASS);
await page.click("button[type=submit]");
await page.waitForTimeout(8000);

console.log("URL after:", page.url());
await browser.close();
