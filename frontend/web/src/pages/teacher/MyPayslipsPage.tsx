/**
 * My Payslips — employee self-service page.
 *
 * Lists only the signed-in staff member's own payslips (backend scopes the
 * queryset to employee__user = request.user). Selecting a slip shows the full
 * earnings/deductions breakdown, with a print view (browser → Save as PDF)
 * for the selected slip.
 */
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { api } from "../../api/client";
import { Button } from "../../components/common";
import { useTitle } from "../../hooks";
import { BanknotesIcon, PrinterIcon } from "@heroicons/react/24/outline";

interface MyPayslip {
  id: string;
  period_start?: string;
  period_end?: string;
  status: string;
  basic_salary?: string;
  housing_allowance?: string;
  transport_allowance?: string;
  medical_allowance?: string;
  other_allowances?: string;
  tax_deduction?: string;
  pension_deduction?: string;
  other_deductions?: string;
  gross_pay?: string;
  total_deductions?: string;
  net_pay: string;
  payment_date?: string | null;
  payment_method?: string;
}

function fmtMoney(v: string | number | undefined): string {
  const n = Number(v ?? 0);
  return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

const STATUS_STYLES: Record<string, string> = {
  paid: "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300",
  approved: "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300",
  cancelled: "bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300",
  draft: "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300",
};

const EARNINGS: [string, keyof MyPayslip][] = [
  ["Basic salary", "basic_salary"],
  ["Housing allowance", "housing_allowance"],
  ["Transport allowance", "transport_allowance"],
  ["Medical allowance", "medical_allowance"],
  ["Other allowances", "other_allowances"],
];

const DEDUCTIONS: [string, keyof MyPayslip][] = [
  ["Tax (PAYE)", "tax_deduction"],
  ["Pension", "pension_deduction"],
  ["Other deductions", "other_deductions"],
];

export default function MyPayslipsPage() {
  useTitle("My Payslips");
  const [slips, setSlips] = useState<MyPayslip[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get<{ results?: MyPayslip[] } | MyPayslip[]>("/hr/payslips/", {
        page_size: 100,
        ordering: "-period_start",
      });
      setSlips(Array.isArray(res) ? res : res.results ?? []);
    } catch {
      setError(
        "Could not load your payslips. If you are not enrolled in payroll, you may not have any yet.",
      );
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const selected = useMemo(
    () => slips.find((s) => s.id === selectedId) ?? null,
    [slips, selectedId],
  );

  /** Print view for the selected slip (browser → Save as PDF). */
  const printSlip = () => {
    if (!selected) return;
    const s = selected;
    const w = window.open("", "_blank", "width=800,height=650");
    if (!w) return; // popup blocked
    const num = (v: string | undefined) => fmtMoney(v ?? "0");
    const earnRows = EARNINGS.map(
      ([label, key]) =>
        `<tr><td>${label}</td><td class="num">${num(s[key] as string | undefined)}</td></tr>`,
    ).join("");
    const dedRows = DEDUCTIONS.map(
      ([label, key]) =>
        `<tr><td>${label}</td><td class="num">${num(s[key] as string | undefined)}</td></tr>`,
    ).join("");
    w.document.write(`<!doctype html><html><head><meta charset="utf-8"/>
<title>Payslip ${s.period_start ?? ""} – ${s.period_end ?? ""}</title>
<style>
  body { font-family: -apple-system, Segoe UI, sans-serif; margin: 32px; color: #111; }
  h1 { font-size: 18px; margin: 0 0 2px; }
  p.meta { color: #555; font-size: 12px; margin: 0 0 18px; }
  table { width: 100%; border-collapse: collapse; font-size: 13px; }
  .kv { width: auto; min-width: 55%; margin-bottom: 14px; }
  .kv th { text-align: left; font-size: 12px; color: #444; width: 140px; padding: 4px 8px; border-bottom: 1px solid #eee; }
  .kv td { padding: 4px 8px; border-bottom: 1px solid #eee; }
  .cols { display: flex; gap: 24px; }
  .cols table { flex: 1; }
  th { background: #f4f4f5; text-transform: uppercase; font-size: 11px; letter-spacing: .04em; padding: 6px 8px; text-align: left; }
  th.num, td.num { text-align: right; font-variant-numeric: tabular-nums; }
  td { border-bottom: 1px solid #ddd; padding: 6px 8px; }
  tr.sub td, tr.sub th { font-weight: 700; border-top: 1px solid #111; border-bottom: none; }
  p.net { font-size: 15px; margin-top: 14px; }
</style></head><body>
<h1>Payslip</h1>
<p class="meta">Period ${s.period_start ?? "—"} → ${s.period_end ?? "—"} · ${s.status}${
      s.payment_date ? ` · paid ${s.payment_date} via ${s.payment_method || "—"}` : ""
    }</p>
<table class="kv">
  <tr><th>Gross pay</th><td class="num">${num(s.gross_pay)}</td></tr>
  <tr><th>Total deductions</th><td class="num">${num(s.total_deductions)}</td></tr>
</table>
<div class="cols">
  <table>
    <thead><tr><th colspan="2">Earnings</th></tr></thead>
    <tbody>${earnRows}<tr class="sub"><td>Gross pay</td><td class="num">${num(
      s.gross_pay,
    )}</td></tr></tbody>
  </table>
  <table>
    <thead><tr><th colspan="2">Deductions</th></tr></thead>
    <tbody>${dedRows}<tr class="sub"><td>Total deductions</td><td class="num">${num(
      s.total_deductions,
    )}</td></tr></tbody>
  </table>
</div>
<p class="net">Net pay: <strong>${fmtMoney(s.net_pay)}</strong></p>
</body></html>`);
    w.document.close();
    w.focus();
    w.print();
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">My Payslips</h1>
        <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
          Your pay history. Select a payslip to see the full breakdown, or print it as a PDF.
        </p>
      </div>

      {error && (
        <div
          role="alert"
          className="rounded-xl border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-800 dark:border-rose-700 dark:bg-rose-900/30 dark:text-rose-300"
        >
          {error}
        </div>
      )}

      <div className="grid gap-6 lg:grid-cols-5">
        {/* Slip list */}
        <div
          data-testid="my-payslip-list"
          className="overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-700 lg:col-span-2"
        >
          {loading ? (
            <div className="space-y-3 p-4">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="h-14 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-700"
                />
              ))}
            </div>
          ) : slips.length === 0 ? (
            <p
              data-testid="no-payslips"
              className="px-4 py-10 text-center text-sm text-slate-500 dark:text-slate-400"
            >
              No payslips yet. When payroll is run and you are enrolled, your slips will appear
              here.
            </p>
          ) : (
            <ul className="divide-y divide-slate-100 dark:divide-slate-700">
              {slips.map((s) => (
                <li key={s.id}>
                  <button
                    onClick={() => setSelectedId(s.id)}
                    aria-pressed={selectedId === s.id}
                    className={`flex w-full items-center justify-between gap-3 px-4 py-3 text-left transition ${
                      selectedId === s.id
                        ? "bg-indigo-50 dark:bg-indigo-900/30"
                        : "bg-white hover:bg-slate-50 dark:bg-slate-800 dark:hover:bg-slate-700"
                    }`}
                  >
                    <div>
                      <p className="text-sm font-medium text-slate-900 dark:text-slate-100">
                        {s.period_start ?? "—"} → {s.period_end ?? "—"}
                      </p>
                      <span
                        className={`mt-0.5 inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                          STATUS_STYLES[s.status] ?? STATUS_STYLES.draft
                        }`}
                      >
                        {s.status}
                      </span>
                    </div>
                    <p className="shrink-0 text-sm font-semibold tabular-nums text-slate-900 dark:text-slate-100">
                      {fmtMoney(s.net_pay)}
                    </p>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Detail panel */}
        <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800 lg:col-span-3">
          {selected ? (
            <div data-testid="payslip-detail" className="space-y-5">
              <div className="flex flex-wrap items-start justify-between gap-3">
                <div>
                  <h2 className="text-base font-semibold text-slate-900 dark:text-white">
                    {selected.period_start} → {selected.period_end}
                  </h2>
                  <span
                    className={`mt-1 inline-block rounded-full px-2 py-0.5 text-xs font-medium ${
                      STATUS_STYLES[selected.status] ?? STATUS_STYLES.draft
                    }`}
                  >
                    {selected.status}
                    {selected.payment_date ? ` · paid ${selected.payment_date}` : ""}
                  </span>
                </div>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={printSlip}
                  leftIcon={<PrinterIcon className="h-4 w-4" />}
                  aria-label="Print this payslip"
                >
                  Print / PDF
                </Button>
              </div>

              <div className="grid grid-cols-3 gap-3">
                <div className="rounded-xl bg-slate-50 p-3 dark:bg-slate-700">
                  <p className="text-xs text-slate-500 dark:text-slate-400">Gross</p>
                  <p className="mt-0.5 text-sm font-semibold tabular-nums text-slate-900 dark:text-white">
                    {fmtMoney(selected.gross_pay)}
                  </p>
                </div>
                <div className="rounded-xl bg-slate-50 p-3 dark:bg-slate-700">
                  <p className="text-xs text-slate-500 dark:text-slate-400">Deductions</p>
                  <p className="mt-0.5 text-sm font-semibold tabular-nums text-slate-900 dark:text-white">
                    {fmtMoney(selected.total_deductions)}
                  </p>
                </div>
                <div className="rounded-xl bg-emerald-50 p-3 dark:bg-emerald-900/30">
                  <p className="text-xs text-slate-500 dark:text-slate-400">Net pay</p>
                  <p className="mt-0.5 flex items-center gap-1 text-sm font-semibold tabular-nums text-emerald-700 dark:text-emerald-300">
                    <BanknotesIcon className="h-4 w-4" aria-hidden="true" />
                    {fmtMoney(selected.net_pay)}
                  </p>
                </div>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 dark:border-slate-600">
                      <th className="pb-2 text-left text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
                        Earnings
                      </th>
                      <th className="pb-2 text-right text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
                        Amount
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                    {EARNINGS.map(([label, key]) => (
                      <tr key={key as string}>
                        <td className="py-1.5 text-slate-600 dark:text-slate-300">{label}</td>
                        <td className="py-1.5 text-right tabular-nums text-slate-900 dark:text-slate-100">
                          {fmtMoney(selected[key] as string | undefined)}
                        </td>
                      </tr>
                    ))}
                    <tr className="border-t-2 border-slate-300 dark:border-slate-500">
                      <td className="py-1.5 font-semibold text-slate-900 dark:text-white">
                        Gross pay
                      </td>
                      <td className="py-1.5 text-right font-semibold tabular-nums text-slate-900 dark:text-white">
                        {fmtMoney(selected.gross_pay)}
                      </td>
                    </tr>
                  </tbody>
                </table>

                <table className="min-w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200 dark:border-slate-600">
                      <th className="pb-2 text-left text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
                        Deductions
                      </th>
                      <th className="pb-2 text-right text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400">
                        Amount
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                    {DEDUCTIONS.map(([label, key]) => (
                      <tr key={key as string}>
                        <td className="py-1.5 text-slate-600 dark:text-slate-300">{label}</td>
                        <td className="py-1.5 text-right tabular-nums text-slate-900 dark:text-slate-100">
                          {fmtMoney(selected[key] as string | undefined)}
                        </td>
                      </tr>
                    ))}
                    <tr className="border-t-2 border-slate-300 dark:border-slate-500">
                      <td className="py-1.5 font-semibold text-slate-900 dark:text-white">
                        Total deductions
                      </td>
                      <td className="py-1.5 text-right font-semibold tabular-nums text-slate-900 dark:text-white">
                        {fmtMoney(selected.total_deductions)}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              {selected.payment_method && (
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  Payment method: {selected.payment_method}
                </p>
              )}
            </div>
          ) : (
            <p
              data-testid="no-selection"
              className="py-16 text-center text-sm text-slate-500 dark:text-slate-400"
            >
              Select a payslip on the left to see its breakdown.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
