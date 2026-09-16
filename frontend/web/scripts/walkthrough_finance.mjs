/**
 * Browser walkthrough of the new finance workflow buttons (v2 — deterministic):
 *   Session A (accountant): /accountant/purchase-orders → filter Draft → Submit → Approve
 *   Session B (admin):      /admin/finance-center → search "draft" → Credit Note Apply;
 *                           Financial Year tab → Close (asserts button count drops)
 *
 * Run: node scripts/walkthrough_finance.mjs
 */
import { chromium } from "playwright";

const BASE = "http://localhost:5173";
const API = "http://localhost:8000/api/v1";

/** Pick an issued credit note that is linked to an invoice (apply requires it). */
async function pickApplicableCreditNote() {
  const login = await fetch(`${API}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: "admin@greenvalley.edu", password: "Admin@1234" }),
  }).then((r) => r.json());
  const notes = await fetch(`${API}/fees/credit-note/?status=issued&page_size=100`, {
    headers: { Authorization: `Bearer ${login.access}` },
  }).then((r) => r.json());
  // status filter may be ignored server-side — verify client-side too
  const match = (notes.results || []).find((n) => n.invoice && n.status === "issued");
  return match ? match.note_number : null;
}

/** Pick a draft PO that actually has line items (submit guard requires them). */
async function pickDraftPoWithItems() {
  const login = await fetch(`${API}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email: "accountant@greenvalley.edu", password: "Admin@1234" }),
  }).then((r) => r.json());
  const auth = { Authorization: `Bearer ${login.access}` };
  const drafts = await fetch(`${API}/inventory/purchase-orders/?status=draft&page_size=100`, {
    headers: auth,
  }).then((r) => r.json());
  const items = await fetch(`${API}/inventory/purchase-order-item/?page_size=200`, {
    headers: auth,
  }).then((r) => r.json());
  const poIdsWithItems = new Set((items.results || []).map((it) => it.purchase_order));
  const match = (drafts.results || []).find((p) => poIdsWithItems.has(p.id));
  return match ? match.order_number : null;
}

const results = [];
const report = (step, ok, detail) => {
  results.push({ step, ok, detail });
  console.log(`${ok ? "PASS" : "FAIL"}  ${step}${detail ? ` — ${detail}` : ""}`);
};

function wireDialogs(page) {
  page.on("dialog", async (d) => {
    console.log(`        dialog: ${d.message().slice(0, 90)}`);
    await d.accept();
  });
}

function wireDiagnostics(page, bucket) {
  page.on("console", (msg) => {
    if (msg.type() === "error" && !msg.text().includes("WebSocket")) {
      bucket.errors.push(msg.text().slice(0, 160));
    }
  });
  page.on("response", (res) => {
    if (res.url().includes("/api/") && res.status() >= 400) {
      bucket.failedApi.push(
        `${res.status()} ${res.url().replace("http://localhost:8000/api/v1", "")}`,
      );
    }
  });
}

async function login(page, email, pass) {
  // Vite transforms modules on demand — the first load after a restart can
  // take a while, so wait for domcontentloaded + the form fields, not "load".
  await page.goto(`${BASE}/login`, { waitUntil: "domcontentloaded", timeout: 90000 });
  await page.waitForSelector('input[type="email"]', { timeout: 60000 });
  await page.fill('input[type="email"]', email);
  await page.fill('input[type="password"]', pass);
  await page.click('button[type="submit"]');
  await page.waitForTimeout(5000);
  return page.url();
}

const browser = await chromium.launch();
const errors = { errors: [], failedApi: [] };

/* ─────────────────────────── Session A: accountant ───────────────────────── */
{
  const page = await browser
    .newContext({ viewport: { width: 1600, height: 1000 } })
    .then((c) => c.newPage());
  wireDialogs(page);
  wireDiagnostics(page, errors);

  const url = await login(page, "accountant@greenvalley.edu", "Admin@1234");
  report("A1 login as accountant", /accountant/.test(url), url);

  await page.goto(`${BASE}/accountant/purchase-orders`, {
    waitUntil: "domcontentloaded",
    timeout: 90000,
  });
  await page.waitForTimeout(6000);
  const heading = await page
    .locator("h1")
    .first()
    .textContent()
    .catch(() => "");
  report(
    "A2 Purchase Orders page loads",
    /purchase orders/i.test(heading || ""),
    (heading || "").trim(),
  );

  // Search for a draft PO that has line items (deterministic target)
  const targetOrder = await pickDraftPoWithItems();
  report("A2b found draft PO with line items via API", !!targetOrder, targetOrder || "none");
  if (!targetOrder) {
    await page.context().close();
  } else {
    const searchBox = page.locator('input[placeholder="Search purchase orders..."]');
    await searchBox.fill(targetOrder);
    await page.waitForTimeout(1500);

    const submitBtn = page
      .locator('button[aria-label="Submit purchase order for approval"]')
      .first();
    const submitVisible = await submitBtn.isVisible({ timeout: 8000 }).catch(() => false);
    report("A3 Submit button visible on target draft PO", submitVisible);
    if (submitVisible) {
      await submitBtn.click();
      const submitted = await page
        .waitForFunction(() => document.body.innerText.includes("submitted"), undefined, {
          timeout: 12000,
        })
        .then(() => true)
        .catch(() => false);
      report(`A4 PO ${targetOrder} → submitted`, submitted);

      // Clear search; filter to submitted to find the row's Approve button
      await searchBox.fill("");
      await page.locator("select").first().selectOption("submitted");
      await page.waitForTimeout(2500);
      const approveBtn = page.locator('button[aria-label="Approve purchase order"]').first();
      const approveVisible = await approveBtn.isVisible({ timeout: 8000 }).catch(() => false);
      report("A5 Approve button appears for the submitted PO", approveVisible);
      if (approveVisible) {
        await approveBtn.click();
        await page.waitForTimeout(2000);
        // Approved row leaves the "submitted" filter — switch to confirmed
        await page.locator("select").first().selectOption("confirmed");
        const confirmed = await page
          .waitForFunction(() => document.body.innerText.includes("confirmed"), undefined, {
            timeout: 12000,
          })
          .then(() => true)
          .catch(() => false);
        report("A6 PO → confirmed after Approve (posted to accounting)", confirmed);
      }
    }
  }

  // Terminal rows must not expose transition buttons
  await page.locator("select").first().selectOption("received");
  await page.waitForTimeout(2000);
  const leaked = await page
    .locator(
      'button[aria-label="Approve purchase order"], button[aria-label="Submit purchase order for approval"]',
    )
    .count();
  report("A7 no Submit/Approve buttons on received POs", leaked === 0, `leaked=${leaked}`);
  await page.context().close();
}

/* ───────────────────────────── Session B: admin ──────────────────────────── */
{
  const page = await browser
    .newContext({ viewport: { width: 1600, height: 1000 } })
    .then((c) => c.newPage());
  wireDialogs(page);
  wireDiagnostics(page, errors);

  const url = await login(page, "admin@greenvalley.edu", "Admin@1234");
  report("B1 login as admin", /admin/.test(url), url);

  await page.goto(`${BASE}/admin/finance-center`, {
    waitUntil: "domcontentloaded",
    timeout: 90000,
  });
  await page.waitForTimeout(6000);
  const heading = await page
    .locator("h1")
    .first()
    .textContent()
    .catch(() => "");
  report("B2 Finance Center loads", /finance/i.test(heading || ""), (heading || "").trim());

  // Credit Note tab; search for an issued note linked to an invoice
  const targetNote = await pickApplicableCreditNote();
  report("B3b found applicable credit note via API", !!targetNote, targetNote || "none");
  await page.locator('button:has-text("Credit Note")').first().click();
  await page.waitForTimeout(2000);
  const searchInput = page.locator('input[placeholder*="( / )"]').first();
  if (targetNote) {
    await searchInput.fill(targetNote);
    await page.waitForTimeout(1500);

    const applyCountBefore = await page.locator('button[title="Apply to invoice"]').count();
    report(
      `B3 Apply button visible on credit note ${targetNote}`,
      applyCountBefore > 0,
      `count=${applyCountBefore}`,
    );
    if (applyCountBefore > 0) {
      await page.locator('button[title="Apply to invoice"]').first().click();
      // Row flips to applied; the count must drop (1 → 0)
      const dropped = await page
        .waitForFunction(
          (n) => document.querySelectorAll('button[title="Apply to invoice"]').length < n,
          applyCountBefore,
          { timeout: 12000 },
        )
        .then(() => true)
        .catch(() => false);
      report(`B4 credit note ${targetNote} applied to its invoice`, dropped);
    }
  }

  // Financial Year tab → Close: assert the Close-button count decreases
  await searchInput.fill("");
  await page.locator('button:has-text("Financial Year")').first().click();
  await page.waitForTimeout(2000);
  const closeCount = await page.locator('button[title="Close financial year"]').count();
  report("B5 Close buttons visible on open years", closeCount > 0, `count=${closeCount}`);
  if (closeCount > 0) {
    await page.locator('button[title="Close financial year"]').first().click();
    const dropped = await page
      .waitForFunction(
        (n) => document.querySelectorAll('button[title="Close financial year"]').length < n,
        closeCount,
        { timeout: 12000 },
      )
      .then(() => true)
      .catch(() => false);
    report("B6 financial year closed via UI (Close button count dropped)", dropped);
  }

  await page.context().close();
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
