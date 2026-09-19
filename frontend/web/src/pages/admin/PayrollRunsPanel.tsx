/**
 * Payroll Runs — actionable panel covering the full payroll lifecycle:
 *   run (generate drafts) → approve → mark-paid (posts each salary to the ledger).
 *
 * Renders inside HRCenterPage as a special tab. Talks directly to the
 * payroll actions: POST /hr/payslips/payroll-run/, bulk-approve/, bulk-mark-paid/.
 */
import React, { useCallback, useEffect, useState } from "react";
import { api } from "../../api/client";
import { Button } from "../../components/common";
import { BanknotesIcon, CheckBadgeIcon, PlayIcon } from "@heroicons/react/24/outline";

interface PayslipRow {
  id: number;
  employee_name?: string;
  status: string;
  net_pay: string;
  period_start?: string;
  period_end?: string;
  department_name?: string | null;
  gross_pay?: string;
}

interface RunSummary {
  created: number;
  existing: number;
  total_gross: string;
  total_net: string;
  payslips: { employee_name?: string; net_pay: string }[];
}

function fmtMoney(v: string | number | undefined): string {
  const n = Number(v ?? 0);
  return n.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/** Upcoming month: first day → last day, for the run-form defaults. */
function defaultPeriod(): { start: string; end: string } {
  const now = new Date();
  const start = new Date(now.getFullYear(), now.getMonth() + 1, 1);
  const end = new Date(now.getFullYear(), now.getMonth() + 2, 0);
  const iso = (d: Date) => d.toISOString().slice(0, 10);
  return { start: iso(start), end: iso(end) };
}

export default function PayrollRunsPanel() {
  const dp = defaultPeriod();
  const [periodStart, setPeriodStart] = useState(dp.start);
  const [periodEnd, setPeriodEnd] = useState(dp.end);
  const [running, setRunning] = useState(false);
  const [summary, setSummary] = useState<RunSummary | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [slips, setSlips] = useState<PayslipRow[]>([]);

  const loadSlips = useCallback(async () => {
    try {
      const res = await api.get<{ results?: PayslipRow[] } | PayslipRow[]>("/hr/payslips/", {
        page_size: 200,
        ordering: "-period_start,id",
      });
      const rows = Array.isArray(res) ? res : res.results ?? [];
      setSlips(rows);
    } catch {
      /* tab not permitted for this user — leave list empty */
    }
  }, []);

  useEffect(() => {
    void loadSlips();
  }, [loadSlips]);

  const runPayroll = async () => {
    setRunning(true);
    setError(null);
    setMessage(null);
    try {
      const res = await api.post<RunSummary>("/hr/payslips/payroll-run/", {
        period_start: periodStart,
        period_end: periodEnd,
      });
      setSummary(res);
      setMessage(
        `Run complete: ${res.created} created, ${res.existing} already existed · gross ${fmtMoney(
          res.total_gross,
        )} · net ${fmtMoney(res.total_net)}`,
      );
      await loadSlips();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Payroll run failed");
    } finally {
      setRunning(false);
    }
  };

  const bulkApprove = async () => {
    setError(null);
    setMessage(null);
    try {
      const ids = slips.filter((s) => s.status === "draft").map((s) => s.id);
      if (ids.length === 0) {
        setError("No draft payslips to approve.");
        return;
      }
      const res = await api.post<{ approved: number; skipped: number }>(
        "/hr/payslips/bulk-approve/",
        { ids },
      );
      setMessage(
        `Approved ${res.approved} payslips${res.skipped ? ` · ${res.skipped} skipped` : ""}.`,
      );
      await loadSlips();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Bulk approve failed");
    }
  };

  const bulkMarkPaid = async () => {
    setError(null);
    setMessage(null);
    try {
      const ids = slips.filter((s) => s.status === "approved").map((s) => s.id);
      if (ids.length === 0) {
        setError("No approved payslips to pay.");
        return;
      }
      if (
        !confirm(
          `Mark ${ids.length} approved payslip(s) as paid? Each payment posts the salary expense to the ledger.`,
        )
      ) {
        return;
      }
      const res = await api.post<{ paid: number; skipped: number }>(
        "/hr/payslips/bulk-mark-paid/",
        { ids, payment_date: new Date().toISOString().slice(0, 10) },
      );
      setMessage(
        `Paid ${res.paid} payslips — salary expense posted to the ledger.${
          res.skipped ? ` ${res.skipped} skipped.` : ""
        }`,
      );
      await loadSlips();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Bulk mark-paid failed");
    }
  };

  const drafts = slips.filter((s) => s.status === "draft").length;
  const approved = slips.filter((s) => s.status === "approved").length;
  const paid = slips.filter((s) => s.status === "paid").length;

  /** Per-department net/gross totals + headcount, grouped from the loaded slips. */
  const byDepartment = (() => {
    const map = new Map<
      string,
      { net: number; gross: number; count: number; statusCounts: Record<string, number> }
    >();
    for (const s of slips) {
      const key = s.department_name?.trim() || "Unassigned";
      const cur =
        map.get(key) ?? map.set(key, { net: 0, gross: 0, count: 0, statusCounts: {} }).get(key)!;
      cur.net += Number(s.net_pay ?? 0);
      cur.gross += Number(s.gross_pay ?? 0);
      cur.count += 1;
      cur.statusCounts[s.status] = (cur.statusCounts[s.status] ?? 0) + 1;
    }
    return [...map.entries()].sort((a, b) => b[1].net - a[1].net);
  })();

  return (
    <div className="space-y-6">
      {/* Run form */}
      <div className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800">
        <h3 className="text-base font-semibold text-slate-900 dark:text-white">Run payroll</h3>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Generates draft payslips for every active salary. Re-running the same period backfills
          only new employees — safe to repeat.
        </p>
        <div className="mt-4 flex flex-wrap items-end gap-4">
          <label className="block">
            <span className="mb-1 block text-xs font-medium text-slate-500 dark:text-slate-400">
              Period start
            </span>
            <input
              type="date"
              aria-label="Period start"
              value={periodStart}
              onChange={(e) => setPeriodStart(e.target.value)}
              className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
            />
          </label>
          <label className="block">
            <span className="mb-1 block text-xs font-medium text-slate-500 dark:text-slate-400">
              Period end
            </span>
            <input
              type="date"
              aria-label="Period end"
              value={periodEnd}
              onChange={(e) => setPeriodEnd(e.target.value)}
              className="rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm text-slate-900 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100"
            />
          </label>
          <Button
            variant="primary"
            onClick={runPayroll}
            disabled={running}
            leftIcon={<PlayIcon className="h-4 w-4" />}
          >
            {running ? "Running…" : "Generate payslips"}
          </Button>
        </div>
      </div>

      {/* Status feedback */}
      {message && (
        <div
          role="status"
          className="rounded-xl border border-emerald-300 bg-emerald-50 px-4 py-3 text-sm text-emerald-800 dark:border-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-300"
        >
          {message}
        </div>
      )}
      {error && (
        <div
          role="alert"
          className="rounded-xl border border-rose-300 bg-rose-50 px-4 py-3 text-sm text-rose-800 dark:border-rose-700 dark:bg-rose-900/30 dark:text-rose-300"
        >
          {error}
        </div>
      )}

      {/* Run summary */}
      {summary && (
        <div
          data-testid="run-summary"
          className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800"
        >
          <h3 className="text-base font-semibold text-slate-900 dark:text-white">Run summary</h3>
          <dl className="mt-3 grid grid-cols-2 gap-4 sm:grid-cols-4">
            <div>
              <dt className="text-xs text-slate-500 dark:text-slate-400">Created</dt>
              <dd className="text-lg font-semibold text-slate-900 dark:text-white">
                {summary.created}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-slate-500 dark:text-slate-400">Already existed</dt>
              <dd className="text-lg font-semibold text-slate-900 dark:text-white">
                {summary.existing}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-slate-500 dark:text-slate-400">Total gross</dt>
              <dd className="text-lg font-semibold text-slate-900 dark:text-white">
                {fmtMoney(summary.total_gross)}
              </dd>
            </div>
            <div>
              <dt className="text-xs text-slate-500 dark:text-slate-400">Total net</dt>
              <dd className="text-lg font-semibold text-slate-900 dark:text-white">
                {fmtMoney(summary.total_net)}
              </dd>
            </div>
          </dl>
        </div>
      )}

      {/* Stage counters + lifecycle actions */}
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
          <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Drafts
          </p>
          <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">{drafts}</p>
          <Button
            variant="secondary"
            size="sm"
            className="mt-3"
            onClick={bulkApprove}
            disabled={drafts === 0}
            leftIcon={<CheckBadgeIcon className="h-4 w-4" />}
          >
            Approve all drafts
          </Button>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
          <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">
            Approved
          </p>
          <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">{approved}</p>
          <Button
            variant="primary"
            size="sm"
            className="mt-3"
            onClick={bulkMarkPaid}
            disabled={approved === 0}
            leftIcon={<BanknotesIcon className="h-4 w-4" />}
          >
            Mark all paid → ledger
          </Button>
        </div>
        <div className="rounded-2xl border border-slate-200 bg-white p-5 dark:border-slate-700 dark:bg-slate-800">
          <p className="text-xs uppercase tracking-wide text-slate-500 dark:text-slate-400">Paid</p>
          <p className="mt-1 text-2xl font-bold text-slate-900 dark:text-white">{paid}</p>
        </div>
      </div>

      {/* Per-department breakdown */}
      {byDepartment.length > 0 && (
        <div
          data-testid="department-breakdown"
          className="rounded-2xl border border-slate-200 bg-white p-6 dark:border-slate-700 dark:bg-slate-800"
        >
          <h3 className="text-base font-semibold text-slate-900 dark:text-white">
            Payroll by department
          </h3>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Net totals across all loaded payslips, grouped by each employee&apos;s department.
          </p>
          <div className="mt-4 space-y-3">
            {byDepartment.map(([name, agg]) => {
              const total = byDepartment.reduce((acc, [, a]) => acc + a.net, 0);
              const pct = total > 0 ? Math.round((agg.net / total) * 100) : 0;
              return (
                <div key={name}>
                  <div className="flex items-baseline justify-between gap-4 text-sm">
                    <span className="font-medium text-slate-900 dark:text-slate-100">{name}</span>
                    <span className="tabular-nums text-slate-500 dark:text-slate-400">
                      {agg.count} {agg.count === 1 ? "payslip" : "payslips"} ·{" "}
                      <span className="font-semibold text-slate-900 dark:text-slate-100">
                        {fmtMoney(agg.net)}
                      </span>
                      {agg.gross > 0 && (
                        <span className="text-slate-400 dark:text-slate-500">
                          {" "}
                          gross {fmtMoney(agg.gross)}
                        </span>
                      )}
                    </span>
                  </div>
                  <div className="mt-1.5 h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
                    <div
                      className="h-full rounded-full bg-indigo-500 transition-all"
                      style={{ width: `${Math.max(pct, 1)}%` }}
                      role="meter"
                      aria-label={`${name} share of payroll`}
                      aria-valuenow={pct}
                      aria-valuemin={0}
                      aria-valuemax={100}
                    />
                  </div>
                  <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">
                    {pct}% ·{" "}
                    {Object.entries(agg.statusCounts)
                      .map(([st, n]) => `${n} ${st}`)
                      .join(", ")}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Per-slip breakdown */}
      <div className="overflow-hidden rounded-2xl border border-slate-200 dark:border-slate-700">
        <table className="min-w-full divide-y divide-slate-200 text-sm dark:divide-slate-700">
          <thead className="bg-slate-50 dark:bg-slate-800">
            <tr>
              {["Employee", "Period", "Status", "Net pay"].map((h) => (
                <th
                  key={h}
                  className="px-4 py-2.5 text-left text-xs font-medium uppercase tracking-wide text-slate-500 dark:text-slate-400"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100 bg-white dark:divide-slate-700 dark:bg-slate-800">
            {slips.length === 0 ? (
              <tr>
                <td
                  colSpan={4}
                  data-testid="no-slips"
                  className="px-4 py-8 text-center text-slate-500 dark:text-slate-400"
                >
                  No payslips yet — run payroll above to generate them.
                </td>
              </tr>
            ) : (
              slips.map((s) => (
                <tr key={s.id}>
                  <td className="px-4 py-2.5 text-slate-900 dark:text-slate-100">
                    {s.employee_name ?? `#${s.id}`}
                  </td>
                  <td className="px-4 py-2.5 text-slate-500 dark:text-slate-400">
                    {s.period_start ?? "—"} → {s.period_end ?? "—"}
                  </td>
                  <td className="px-4 py-2.5">
                    <span
                      className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        s.status === "paid"
                          ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300"
                          : s.status === "approved"
                            ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300"
                            : s.status === "cancelled"
                              ? "bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300"
                              : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
                      }`}
                    >
                      {s.status}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-right tabular-nums text-slate-900 dark:text-slate-100">
                    {fmtMoney(s.net_pay)}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
