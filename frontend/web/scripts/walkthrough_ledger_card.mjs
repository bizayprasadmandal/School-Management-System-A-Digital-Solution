/**
 * Read-only browser walkthrough of the Ledger Summary card:
 *   login as admin → /admin/finance-center → Accounting Entry tab
 *   → assert the card shows this month, totals matching the live API,
 *     and one row per posting stream (debits vs credits).
 *
 * Run: node scripts/walkthrough_ledger_card.mjs
 */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const API = "http://localhost:8000/api/v1";

const results = [];
const report = (step, ok, detail) => {
  results.push({ step, ok, detail });
  console.log(`${ok ? "PASS" : "FAIL"}  ${step}${detail ? ` — ${detail}` : ""}`);
};

const month = new Date().toISOString().slice(0, 7);
const money = (v) =>
  `Rs. ${parseFloat(v).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;

/* Expected values straight from the live API. */
const login = await fetch(`${API}/auth/login/`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ email: "admin@greenvalley.edu", password: "Admin@1234" }),
}).then((r) => r.json());
const summary = await fetch(`${API}/fees/accounting-entry/monthly_summary/`, {
  headers: { Authorization: `Bearer ${login.access}` },
}).then((r) => r.json());
const trend = await fetch(`${API}/fees/accounting-entry/monthly_trend/`, {
  headers: { Authorization: `Bearer ${login.access}` },
}).then((r) => r.json());
console.log(
  `api summary: month=${summary.month} streams=${summary.streams?.length} ` +
    `credits=${summary.total_credits} debits=${summary.total_debits}`,
);
console.log(`api trend: months=${trend.months?.length} streams=${trend.streams?.length}`);

const browser = await chromium.launch();
const errors = { errors: [], failedApi: [] };
const page = await browser
  .newContext({ viewport: { width: 1600, height: 1000 } })
  .then((c) => c.newPage());
page.on("console", (m) => {
  if (m.type() === "error" && !m.text().includes("WebSocket"))
    errors.errors.push(m.text().slice(0, 160));
});
page.on("response", (res) => {
  if (res.url().includes("/api/") && res.status() >= 400)
    errors.failedApi.push(`${res.status()} ${res.url().replace(API, "")}`);
});

/* Login through the UI */
await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded", timeout: 90000 });
await page.waitForSelector('input[type="email"]', { timeout: 60000 });
await page.fill('input[type="email"]', "admin@greenvalley.edu");
await page.fill('input[type="password"]', "Admin@1234");
await page.click('button[type="submit"]');
await page.waitForTimeout(5000);
report("1 login as admin", /admin/.test(page.url()), page.url());

/* Finance Center → Accounting Entry tab */
await page.goto(`${BASE}/admin/finance-center`, { waitUntil: "domcontentloaded", timeout: 90000 });
await page.waitForTimeout(6000);
const heading = await page
  .locator("h1")
  .first()
  .textContent()
  .catch(() => "");
report("2 Finance Center loads", /finance/i.test(heading || ""), (heading || "").trim());

await page.locator('button:has-text("Accounting Entry")').first().click();
const card = page.locator('[data-testid="ledger-summary"]');
const cardVisible = await card.isVisible({ timeout: 15000 }).catch(() => false);
report("3 Ledger summary card visible on Accounting Entry tab", cardVisible);

if (cardVisible) {
  const cardText = await card.innerText();

  /* Month heading */
  const monthOk =
    cardText.includes(`Ledger this month (${month})`) || cardText.includes(`(${month})`);
  report(`4 card shows this month (${month})`, monthOk);

  /* Totals match the live API */
  const totalsOk =
    cardText.includes(money(summary.total_credits)) &&
    cardText.includes(money(summary.total_debits));
  report(
    "5 card totals match live API (credits + debits)",
    totalsOk,
    `credits=${money(summary.total_credits)} debits=${money(summary.total_debits)}`,
  );

  const netShown = cardText.includes(`Net ${money(summary.net)}`);
  report("6 net figure shown", netShown, money(summary.net));

  /* One row per stream, credits/debits amounts rendered */
  const streamRows = await card.locator("span.w-40").count();
  report(
    `7 stream rows rendered (${summary.streams.length} expected)`,
    streamRows === summary.streams.length,
    `rendered=${streamRows}`,
  );

  /* First stream's credit value appears (friendly label + amount) */
  const first = summary.streams[0];
  if (first) {
    const amountOk =
      cardText.includes(money(first.total_credits)) || cardText.includes(money(first.total_debits));
    report(
      `8 first stream (${first.stream}) values rendered`,
      amountOk,
      `cr=${money(first.total_credits)} dr=${money(first.total_debits)}`,
    );
  }

  /* Trend sparklines: two mini-charts (credits + debits) per stream */
  const sparkCount = await card.locator("[data-sparkline]").count();
  report(
    `9 trend sparklines rendered (${trend.streams.length} streams → ${
      trend.streams.length * 2
    } expected)`,
    sparkCount === trend.streams.length * 2,
    `rendered=${sparkCount}`,
  );
  const trendStream = trend.streams[0];
  if (trendStream) {
    const sparkTitle = await card
      .locator('[data-sparkline][title*="Last 6 months"]')
      .first()
      .getAttribute("title")
      .catch(() => "");
    // Tooltip renders floats without trailing zeroes — compare numerically
    const lastCr = String(parseFloat(trendStream.credits.at(-1)) || 0);
    const lastDr = String(parseFloat(trendStream.debits.at(-1)) || 0);
    const seriesOk = sparkTitle?.includes(`, ${lastCr}`) || sparkTitle?.includes(`, ${lastDr}`);
    report(
      `10 sparkline tooltip carries the live 6-month series (${trendStream.stream})`,
      !!seriesOk,
      (sparkTitle || "").slice(0, 80),
    );
  }

  /* Screenshot for the record */
  await card.screenshot({ path: "scripts/ledger_card_live.png" });
  console.log("screenshot: scripts/ledger_card_live.png");
}

await browser.close();

console.log("\n════ diagnostics ════");
console.log("console errors:", errors.errors.length ? errors.errors.slice(0, 5) : "none");
console.log(
  "failed API calls:",
  errors.failedApi.length ? [...new Set(errors.failedApi)].slice(0, 8) : "none",
);

const failed = results.filter((r) => !r.ok);
console.log(`\n${results.length - failed.length}/${results.length} steps passed`);
if (failed.length) {
  console.log("FAILED steps:", failed.map((f) => f.step).join(", "));
  process.exit(1);
}
