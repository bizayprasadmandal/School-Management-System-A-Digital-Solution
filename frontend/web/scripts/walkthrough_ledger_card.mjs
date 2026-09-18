/**
 * Read-only browser walkthrough of the Ledger Summary card:
 *   login as admin → /admin/finance-center → Accounting Entry tab
 *   → assert the card shows this month, totals matching the live API,
 *     and one row per posting stream (debits vs credits).
 *
 * Run: node scripts/walkthrough_ledger_card.mjs
 */
import { chromium } from "playwright";

const BASE = "http://127.0.0.1:5173"; // IPv4 explicitly — Windows resolves localhost→::1 first, and another dev app shadows [::1]:5173
const API = "http://127.0.0.1:8000/api/v1";

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
  .newContext({ viewport: { width: 1600, height: 1000 }, acceptDownloads: true })
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
const cardVisible = await card
  .waitFor({ timeout: 15000 })
  .then(() => true)
  .catch(() => false);
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
  const streamRows = await card.locator("span.w-40, [data-testid^='drill-']").count();
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

  /* Range toggle: switching to 12m refetches and re-renders the series */
  await card.locator('button:has-text("12m")').first().click();
  const twelve = await card
    .locator('[data-sparkline][title*="Last 12 months"]')
    .first()
    .waitFor({ timeout: 15000 })
    .then(() => true)
    .catch(() => false);
  report("11 range toggle switches sparklines to 12 months", twelve);
  await card.locator('button:has-text("6m")').first().click();
  await card
    .locator('[data-sparkline][title*="Last 6 months"]')
    .first()
    .waitFor({ timeout: 15000 })
    .catch(() => {});

  /* CSV export downloads and contains stream rows */
  const [download] = await Promise.all([
    page.waitForEvent("download", { timeout: 15000 }).catch(() => null),
    card.locator('[data-testid="export-csv"]').click(),
  ]);
  if (download) {
    const path = await download.path();
    const { readFile } = await import("fs/promises");
    const csv = await readFile(path, "utf8");
    const csvOk =
      csv.includes("stream,credits,debits,entry_count") &&
      csv.includes(`${summary.streams[0].stream},`);
    report("12 CSV export downloads with stream rows", csvOk, download.suggestedFilename());
  } else {
    report("12 CSV export downloads with stream rows", false, "no download event");
  }

  /* Drill-down: clicking a stream label filters the Accounting Entry list below */
  const drillSel = '[data-testid="drill-' + (summary.streams[0]?.stream ?? "") + '"]';
  const drillBtn = page.locator(drillSel).first();
  if ((await drillBtn.count()) > 0) {
    await drillBtn.click();
    const searchInput = page.locator('input[type="search"]').first();
    const searchVal = await searchInput
      .waitFor({ timeout: 10000 })
      .then(() => searchInput.inputValue())
      .catch(() => "");
    report(
      `13 stream drill-down filters the entry list (${summary.streams[0]?.stream})`,
      searchVal === (summary.streams[0]?.stream ?? ""),
      `search="${searchVal}"`,
    );
  } else {
    report("13 stream drill-down filters the entry list", false, "no drill button found");
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
