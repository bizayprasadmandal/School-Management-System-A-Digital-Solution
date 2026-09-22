/**
 * LedgerSummaryCard — monthly debits-vs-credits per posting stream.
 *
 * Reads the fees module's shared ledger (`monthly_summary` +
 * `monthly_trend`) and renders: month totals with deltas vs last month,
 * a 3/6/12-month sparkline per stream, entry counts, and CSV export.
 * Used on the admin dashboard and the Finance Center's Accounting Entry
 * tab; when `onDrillDown` is provided the stream labels become buttons.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { useFeatureLocked } from "../../store/authStore";
import { FeatureLockNotice } from "./PlanGate";

export interface LedgerStream {
  stream: string;
  total_debits: string;
  total_credits: string;
  entry_count: number;
  prev_debits?: string;
  prev_credits?: string;
}

export interface LedgerTrendStream {
  stream: string;
  credits: string[];
  debits: string[];
}

export interface LedgerTrend {
  months: string[];
  streams: LedgerTrendStream[];
}

export interface LedgerSummary {
  month: string;
  prev_month?: string;
  streams: LedgerStream[];
  prev_total_debits?: string;
  prev_total_credits?: string;
  prev_net?: string;
  total_debits: string;
  total_credits: string;
  net: string;
}

export const STREAM_LABELS: Record<string, string> = {
  payment: "Fee Payments",
  transport: "Transport Fees",
  hostel: "Hostel Fees",
  hostel_fee_payment: "Hostel Fees",
  cafeteria_pos: "Cafeteria POS",
  cafeteria_payment: "Cafeteria Online",
  cafeteria_refund: "Cafeteria Refunds",
  depreciation: "Depreciation",
  purchase_order: "Purchase Orders",
  supplier_payment: "Supplier Payments",
  refund: "Fee Refunds",
  manual: "Manual Entries",
  payroll: "Payroll",
  unclassified: "Unclassified",
};

const CURRENCY = "Rs. ";

/** Month-over-month arrow: ↑/↓ vs last month, coloured by direction. */
export function Delta({
  current,
  previous,
  invert = false,
}: {
  current: string;
  previous?: string;
  invert?: boolean;
}) {
  if (previous === undefined) return null;
  const cur = parseFloat(current) || 0;
  const prev = parseFloat(previous) || 0;
  if (prev === 0) {
    if (cur === 0) return null;
    return (
      <span
        className="ml-1 text-[10px] font-medium text-slate-400 dark:text-slate-500"
        title="No activity last month"
      >
        new
      </span>
    );
  }
  const pct = Math.round(((cur - prev) / prev) * 100);
  if (pct === 0) return null;
  const up = pct > 0;
  // For debits, a rise is unfavourable (red); for credits/net, a rise is good.
  const good = invert ? !up : up;
  return (
    <span
      className={`ml-1 text-[10px] font-semibold ${
        good ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
      }`}
      title={`vs ${money(previous)} last month`}
    >
      {up ? "↑" : "↓"}
      {Math.abs(pct)}%
    </span>
  );
}

/** Tiny trailing-months bar chart for one stream (credits or debits). */
export function Sparkline({ values, tone }: { values?: string[]; tone: "green" | "red" }) {
  if (!values || values.length === 0) return null;
  const nums = values.map((v) => parseFloat(v) || 0);
  const max = Math.max(...nums);
  return (
    <div
      data-sparkline
      className="flex h-2 items-end gap-px"
      title={`Last ${nums.length} months (${tone === "green" ? "credits" : "debits"}): ${nums.join(
        ", ",
      )}`}
    >
      {nums.map((n, i) => (
        <div
          key={i}
          className={`w-1 rounded-full ${tone === "green" ? "bg-green-500" : "bg-red-500"} ${
            n > 0 ? "" : "opacity-20"
          }`}
          style={{ height: `${n > 0 ? Math.max(Math.round((n / max) * 8), 2) : 1}px` }}
        />
      ))}
    </div>
  );
}

/**
 * Spike detection: flag a stream whose current-month debits more than double
 * its average over the preceding trend months (min 100 to skip noise).
 * Returns the average for the tooltip, or null when the stream is calm.
 */
export function debitSpike(debits: string, priorDebits?: string[]): number | null {
  if (!priorDebits || priorDebits.length === 0) return null;
  const prior = priorDebits.map((v) => parseFloat(v) || 0);
  const avg = prior.reduce((a, b) => a + b, 0) / prior.length;
  if (avg < 1) return null; // noise floor: ignore streams that were ~always zero
  const cur = parseFloat(debits) || 0;
  return cur > 2 * avg ? Math.round(avg * 100) / 100 : null;
}

/** Amber warning shown on a stream row when this month's debits spike. */
export function DebitSpikeBadge({
  stream,
  debits,
  priorDebits,
}: {
  stream: string;
  debits: string;
  priorDebits?: string[];
}) {
  const avg = debitSpike(debits, priorDebits);
  if (avg === null) return null;
  return (
    <span
      data-testid={`spike-${stream}`}
      className="shrink-0 rounded-full bg-amber-100 px-1.5 py-0.5 text-[10px] font-semibold text-amber-700 dark:bg-amber-900/50 dark:text-amber-300"
      title={`Unusual debit spike — avg ${money(avg)}/month over the trailing months`}
    >
      ⚠ spike
    </span>
  );
}

export function money(v: string | number) {
  const n = typeof v === "string" ? parseFloat(v) : v;
  return `${CURRENCY}${(isFinite(n) ? n : 0).toLocaleString(undefined, {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  })}`;
}

export default function LedgerSummaryCard({
  onDrillDown,
}: {
  onDrillDown?: (stream: string) => void;
}) {
  // Premium gate (`accounting_ledger`): fail-open until plan_features loads,
  // then the backend's own 403 stays the hard enforcement.
  const ledgerLocked = useFeatureLocked("accounting_ledger");
  const [range, setRange] = useState(6);
  const { data, isLoading } = useQuery({
    queryKey: ["ledger-monthly-summary"],
    queryFn: () => api.get<LedgerSummary>("/fees/accounting-entry/monthly_summary/"),
    refetchInterval: 60_000,
  });
  const trendQ = useQuery({
    queryKey: ["ledger-monthly-trend", range],
    queryFn: () => api.get<LedgerTrend>(`/fees/accounting-entry/monthly_trend/?months=${range}`),
    refetchInterval: 60_000,
  });
  const trendByStream: Record<string, LedgerTrendStream> = {};
  trendQ.data?.streams?.forEach((s) => {
    trendByStream[s.stream] = s;
  });

  const exportCsv = () => {
    if (!data?.streams) return;
    const months = trendQ.data?.months ?? [];
    const trendMap = new Map(trendQ.data?.streams?.map((s) => [s.stream, s]));
    const header = [
      "stream",
      "credits",
      "debits",
      "entry_count",
      "prev_credits",
      "prev_debits",
      ...months.flatMap((m) => [`cr_${m}`, `dr_${m}`]),
    ];
    const rows = data.streams.map((s) => {
      const t = trendMap.get(s.stream);
      return [
        s.stream,
        s.total_credits,
        s.total_debits,
        String(s.entry_count),
        s.prev_credits ?? "",
        s.prev_debits ?? "",
        ...months.flatMap((_, i) => [t?.credits[i] ?? "", t?.debits[i] ?? ""]),
      ];
    });
    const csv = [header, ...rows]
      .map((cells) => cells.map((c) => (c.includes(",") ? `"${c}"` : c)).join(","))
      .join("\n");
    const url = URL.createObjectURL(new Blob([csv], { type: "text/csv" }));
    const a = document.createElement("a");
    a.href = url;
    a.download = `ledger-summary-${data.month}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  if (ledgerLocked) {
    return <FeatureLockNotice featureKey="accounting_ledger" />;
  }

  if (isLoading) {
    return (
      <div className="h-40 animate-pulse rounded-2xl border border-slate-100 bg-white shadow-sm dark:border-slate-700 dark:bg-slate-800" />
    );
  }
  if (!data?.streams) return null;
  const streams = data.streams;

  const spiked = streams.filter((s) =>
    debitSpike(s.total_debits, trendByStream[s.stream]?.debits?.slice(0, -1)),
  );

  const maxVal = Math.max(
    1,
    ...streams.map((s) =>
      Math.max(parseFloat(s.total_debits) || 0, parseFloat(s.total_credits) || 0),
    ),
  );

  return (
    <div
      data-testid="ledger-summary"
      className="rounded-2xl border border-slate-100 bg-white p-5 shadow-sm dark:border-slate-700 dark:bg-slate-800"
    >
      <div className="flex flex-wrap items-baseline justify-between gap-2">
        <h2 className="text-sm font-semibold text-slate-900 dark:text-white">
          Ledger this month ({data.month})
          {data.prev_month && (
            <span className="ml-2 text-xs font-normal text-slate-400 dark:text-slate-500">
              vs {data.prev_month}
            </span>
          )}
        </h2>
        <div className="flex items-baseline gap-4 text-sm">
          <span className="text-slate-500 dark:text-slate-400">
            Credits{" "}
            <span className="font-semibold text-green-600 dark:text-green-400">
              {money(data.total_credits)}
            </span>
            <Delta current={data.total_credits} previous={data.prev_total_credits} />
          </span>
          <span className="text-slate-500 dark:text-slate-400">
            Debits{" "}
            <span className="font-semibold text-red-600 dark:text-red-400">
              {money(data.total_debits)}
            </span>
            <Delta current={data.total_debits} previous={data.prev_total_debits} invert />
          </span>
          <span
            className={`font-semibold ${
              parseFloat(data.net) >= 0
                ? "text-green-600 dark:text-green-400"
                : "text-red-600 dark:text-red-400"
            }`}
          >
            Net {money(data.net)}
            <Delta current={data.net} previous={data.prev_net} />
          </span>
        </div>
      </div>{" "}
      <div className="mt-3 flex items-center justify-between gap-2">
        <div
          className="flex items-center gap-1"
          role="group"
          aria-label="Trend range"
          data-testid="trend-range"
        >
          {[3, 6, 12].map((r) => (
            <button
              key={r}
              type="button"
              onClick={() => setRange(r)}
              aria-pressed={range === r}
              className={`rounded-md px-2 py-0.5 text-xs font-medium transition-colors ${
                range === r
                  ? "bg-slate-900 text-white dark:bg-slate-100 dark:text-slate-900"
                  : "bg-slate-100 text-slate-500 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300 dark:hover:bg-slate-600"
              }`}
            >
              {r}m
            </button>
          ))}
        </div>
        {spiked.length > 0 && (
          <span
            data-testid="ledger-spike-count"
            className="rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-700 dark:bg-amber-900/50 dark:text-amber-300"
            title="Streams spending unusually fast this month"
          >
            ⚠ {spiked.length} spike{spiked.length > 1 ? "s" : ""}
          </span>
        )}
        <button
          type="button"
          onClick={exportCsv}
          data-testid="export-csv"
          className="rounded-md bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600 transition-colors hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-200 dark:hover:bg-slate-600"
        >
          Export CSV
        </button>
      </div>
      <div className="mt-4 space-y-2.5">
        {streams.length === 0 && (
          <p className="text-sm text-slate-400 dark:text-slate-500">
            No accounting activity yet this month.
          </p>
        )}
        {streams.map((s) => {
          const debits = parseFloat(s.total_debits) || 0;
          const credits = parseFloat(s.total_credits) || 0;
          return (
            <div key={s.stream} className="flex items-center gap-3">
              {onDrillDown ? (
                <button
                  type="button"
                  onClick={() => onDrillDown(s.stream)}
                  title={`Show ${STREAM_LABELS[s.stream] ?? s.stream} entries below`}
                  data-testid={`drill-${s.stream}`}
                  className="w-40 shrink-0 truncate text-left text-xs font-medium text-indigo-600 hover:underline dark:text-indigo-400"
                >
                  {STREAM_LABELS[s.stream] ?? s.stream}
                </button>
              ) : (
                <span className="w-40 shrink-0 truncate text-xs font-medium text-slate-600 dark:text-slate-300">
                  {STREAM_LABELS[s.stream] ?? s.stream}
                </span>
              )}
              <div className="flex flex-1 flex-col gap-1">
                <div className="flex items-center gap-2">
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
                    <div
                      className="h-full rounded-full bg-green-500"
                      style={{
                        width: `${credits > 0 ? Math.max((credits / maxVal) * 100, 2) : 0}%`,
                      }}
                    />
                  </div>
                  <span className="w-24 shrink-0 text-right text-xs text-green-600 dark:text-green-400">
                    {money(credits)}
                    <Delta current={s.total_credits} previous={s.prev_credits} />
                  </span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
                    <div
                      className="h-full rounded-full bg-red-500"
                      style={{ width: `${debits > 0 ? Math.max((debits / maxVal) * 100, 2) : 0}%` }}
                    />
                    <span className="sr-only">Debits {money(debits)}</span>
                  </div>
                  <span className="w-24 shrink-0 text-right text-xs text-red-600 dark:text-red-400">
                    {money(debits)}
                    <Delta current={s.total_debits} previous={s.prev_debits} invert />
                  </span>
                </div>
              </div>
              <div className="hidden w-16 shrink-0 flex-col justify-center gap-1 sm:flex">
                <Sparkline values={trendByStream[s.stream]?.credits} tone="green" />
                <Sparkline values={trendByStream[s.stream]?.debits} tone="red" />
              </div>
              <DebitSpikeBadge
                stream={s.stream}
                debits={s.total_debits}
                priorDebits={trendByStream[s.stream]?.debits?.slice(0, -1)}
              />
              <span
                className="w-14 shrink-0 text-right text-xs text-slate-400 dark:text-slate-500"
                title={`${s.entry_count} entries`}
              >
                {s.entry_count} ent.
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
}
