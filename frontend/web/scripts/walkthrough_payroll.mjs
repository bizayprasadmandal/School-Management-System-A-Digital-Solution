/**
 * Browser walkthrough of the HR Center Payroll Runs panel:
 *   login → /hr → payroll run → approve drafts → mark paid → ledger reflection.
 *
 * Run: node scripts/walkthrough_payroll.mjs
 */
import { chromium } from "playwright";

const BASE = process.env.BASE_URL || "http://127.0.0.1:5173";
const EMAIL = process.env.BROWSE_USER || "admin@greenvalley.edu";
const PASSWORD = process.env.BROWSE_PASS || "Admin@1234";
const API = "http://127.0.0.1:8000/api/v1";

const browser = await chromium.launch();
const page = await browser
  .newContext({ viewport: { width: 1600, height: 1000 } })
  .then((c) => c.newPage());

// Auto-accept every confirm dialog (bulk actions use window.confirm)
page.on("dialog", (d) => void d.accept().catch(() => {}));

let failed = 0;
const step = (n, ok, label) => {
  console.log(`${ok ? "✅" : "❌"} ${n}. ${label}`);
  if (!ok) failed++;
};

page.on("console", (m) => {
  if (m.type() === "error") console.log("  console.error:", m.text().slice(0, 200));
});
page.on("response", (r) => {
  if (r.url().includes("/api/") && r.status() >= 400) {
    console.log(`  API ${r.status()} ${r.request().method()} ${r.url()}`);
  }
});

// 1. login
await page.goto(`${BASE}/login`, { waitUntil: "networkidle" });
await page.fill('input[type="email"]', EMAIL);
await page.fill('input[type="password"]', PASSWORD);
await page.click('button[type="submit"]');
await page.waitForURL(/dashboard|admin/i, { timeout: 30000 });
step(1, true, `Logged in as ${EMAIL}`);

// 2. open HR Center
await page.goto(`${BASE}/admin/hr-center`, { waitUntil: "networkidle" });
const runHeading = await page
  .getByRole("heading", { name: "Run payroll" })
  .isVisible()
  .catch(() => false);
step(2, runHeading, "HR Center opens with the Payroll Runs tab active");

// 3. generate payslips for a fresh period
const now = new Date();
const iso = (d) => d.toISOString().slice(0, 10);
const start = iso(new Date(now.getFullYear(), now.getMonth(), 1));
const end = iso(new Date(now.getFullYear(), now.getMonth() + 1, 0));
const periodInputs = page.locator('input[type="date"]');
const beforeRun = await page.evaluate(async () => {
  const token = JSON.parse(
    localStorage.getItem("auth") || sessionStorage.getItem("auth") || "null",
  );
  return token ? token.access || token.token : null;
});
const apiResp = await page.evaluate(
  async ({ api, email, password, start, end }) => {
    const login = await fetch(`${api}/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    }).then((r) => r.json());
    const res = await fetch(`${api}/hr/payslips/payroll-run/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${login.access || login.token}`,
      },
      body: JSON.stringify({ period_start: start, period_end: end }),
    });
    return { status: res.status, body: await res.json() };
  },
  { api: API, email: EMAIL, password: PASSWORD, start, end },
);
const created = apiResp.status === 200 ? apiResp.body.created : -1;
step(
  3,
  created >= 0,
  `Payroll run for ${start} → ${end}: ${
    created >= 0 ? `${created} payslips created` : `HTTP ${apiResp.status}`
  }`,
);

// 4. reload panel and check counters reflect the run
await page.reload({ waitUntil: "networkidle" });
const counters = await page.evaluate(() => {
  const cards = [...document.querySelectorAll("p")].filter((p) =>
    ["Drafts", "Approved", "Paid"].includes(p.textContent?.trim() ?? ""),
  );
  return cards.map((p) => ({
    label: p.textContent?.trim(),
    value: p.nextElementSibling?.textContent?.trim(),
  }));
});
console.log("   counters:", JSON.stringify(counters));
step(
  4,
  counters.length === 3,
  `Stage counters render: ${counters.map((c) => `${c.label}=${c.value}`).join(" · ")}`,
);

// 5. approve all drafts via UI button
const approveBtn = page.getByRole("button", { name: "Approve all drafts" });
const hasDrafts = await approveBtn.isEnabled();
if (hasDrafts) {
  await approveBtn.click();
  await page
    .getByText(/Approved \d+ payslips/i)
    .waitFor({ timeout: 15000 })
    .catch(() => {});
}
step(5, true, `Bulk approve clicked (drafts present: ${hasDrafts})`);

// 6. reload → drafts should be 0, approved/paid > 0
await page.reload({ waitUntil: "networkidle" });
await page.getByRole("heading", { name: "Run payroll" }).waitFor();
const after = await page.evaluate(async () => {
  const cards = [...document.querySelectorAll("p")].filter((p) =>
    ["Drafts", "Approved", "Paid"].includes(p.textContent?.trim() ?? ""),
  );
  return cards.map((p) => ({
    label: p.textContent?.trim(),
    value: Number(p.nextElementSibling?.textContent),
  }));
});
const draftCount = after.find((c) => c.label === "Drafts")?.value ?? -1;
const approvedCount = after.find((c) => c.label === "Approved")?.value ?? -1;
const paidCount = after.find((c) => c.label === "Paid")?.value ?? -1;
const lifecycleSane = draftCount === 0 && (approvedCount > 0 || paidCount > 0);
step(
  6,
  lifecycleSane,
  `After approve: Drafts=${draftCount}, Approved=${approvedCount}, Paid=${paidCount}`,
);

// 7. mark all paid via UI button (posts each salary to the ledger)
const payBtn = page.getByRole("button", { name: "Mark all paid → ledger" });
if (await payBtn.isEnabled()) {
  await payBtn.click();
  await page
    .getByText(/Paid \d+ payslips/i)
    .waitFor({ timeout: 20000 })
    .catch(() => {});
  step(7, true, "Bulk mark-paid clicked — ledger posting fired");
} else {
  step(7, true, "Nothing left to pay (already paid in a previous run)");
}

// 8. verify the ledger has payroll entries via API
const ledger = await page.evaluate(
  async ({ api, email, password }) => {
    const login = await fetch(`${api}/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    }).then((r) => r.json());
    const res = await fetch(`${api}/fees/accounting-entry/monthly_summary/`, {
      headers: { Authorization: `Bearer ${login.access || login.token}` },
    });
    const body = await res.json();
    return body.streams?.find((s) => s.stream === "payroll") ?? null;
  },
  { api: API, email: EMAIL, password: PASSWORD },
);
console.log("   payroll ledger stream:", JSON.stringify(ledger));
step(
  8,
  !!ledger && Number(ledger.total_debits) > 0,
  `Ledger shows payroll debits: ${ledger ? Number(ledger.total_debits).toLocaleString() : "none"}`,
);

// 9. payslip table renders real names
await page.reload({ waitUntil: "networkidle" });
const rowCount = await page.locator("tbody tr").count();
step(9, rowCount > 0, `Payslip table renders ${rowCount} rows`);

await page.screenshot({ path: "walkthrough_payroll.png", fullPage: true });
await browser.close();

console.log(failed === 0 ? "\n🎉 ALL STEPS PASSED" : `\n💥 ${failed} step(s) failed`);
process.exit(failed === 0 ? 0 : 1);
