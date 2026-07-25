/** Accountant Fee Reports — revenue summaries, collection trends, CSV export */
import React, { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend,
} from "recharts";
import {
  BanknotesIcon, ArrowDownTrayIcon, CalendarDaysIcon,
  CheckCircleIcon, ClockIcon, ExclamationCircleIcon, ChartBarIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Select, EmptyState, SkeletonCard, ErrorBoundary } from "../../components/common";
import { useCurrentAcademicYear } from "../../api/hooks";
import { toCsv, downloadCsv, currency } from "../../utils";
import toast from "react-hot-toast";
import dayjs from "dayjs";

const PIE_COLORS = ["#22c55e", "#f59e0b", "#ef4444", "#3b82f6", "#8b5cf6", "#6b7280"];

interface FeeReportData {
  total_invoiced: number;
  total_collected: number;
  total_outstanding: number;
  total_overdue: number;
  collection_rate: number;
  by_status: Array<{ status: string; total: number; count: number }>;
  by_category: Array<{ category: string; total: number; collected: number }>;
  monthly: Array<{ month: string; invoiced: number; collected: number; outstanding: number }>;
  recent_payments: Array<{
    id: string;
    receipt_number: string;
    invoice_number: string;
    student_name: string;
    amount: number;
    payment_method: string;
    status: string;
    paid_at: string;
  }>;
}

export default function AccountantFeeReportsPage() {
  const { data: currentYear } = useCurrentAcademicYear();
  const [selectedYear, setSelectedYear] = useState<number | undefined>();
  const [dateRange, setDateRange] = useState<"this_month" | "this_quarter" | "this_year" | "all">("this_year");

  const yearId = selectedYear ?? currentYear?.id;

  const { data, isLoading, error, refetch } = useQuery<FeeReportData>({
    queryKey: ["fee-report", "accountant", yearId, dateRange],
    queryFn: () => api.get("/reporting/fee-report/", { academic_year_id: yearId, period: dateRange }),
    enabled: !!yearId,
  });

  const handleExportReport = () => {
    if (!data) return;
    const cols = [
      { key: "month", label: "Month" },
      { key: "invoiced", label: "Invoiced" },
      { key: "collected", label: "Collected" },
      { key: "outstanding", label: "Outstanding" },
    ];
    const rows = (data.monthly ?? []).map((m) => ({
      month: m.month,
      invoiced: currency(m.invoiced),
      collected: currency(m.collected),
      outstanding: currency(m.outstanding),
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, `fee-report-${dayjs().format("YYYY-MM-DD")}.csv`);
    toast.success("Report exported");
  };

  const collectionRate = data?.collection_rate ?? 0;
  const statusData = data?.by_status ?? [];
  const categoryData = data?.by_category ?? [];
  const monthlyData = data?.monthly ?? [];
  const recentPayments = data?.recent_payments ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Fee Reports</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-0.5">Revenue summaries, collection trends, and exports</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-44">
            <Select
              value={dateRange}
              onChange={(e) => setDateRange(e.target.value as typeof dateRange)}
              options={[
                { value: "this_month", label: "This Month" },
                { value: "this_quarter", label: "This Quarter" },
                { value: "this_year", label: "This Year" },
                { value: "all", label: "All Time" },
              ]}
            />
          </div>
          <Button
            variant="secondary"
            onClick={handleExportReport}
            leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />}
            disabled={!data}
          >
            Export CSV
          </Button>
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: "Total Invoiced", value: data ? currency(data.total_invoiced) : "—", icon: BanknotesIcon, color: "bg-indigo-500" },
          { label: "Collected", value: data ? currency(data.total_collected) : "—", icon: CheckCircleIcon, color: "bg-green-500" },
          { label: "Outstanding", value: data ? currency(data.total_outstanding) : "—", icon: ClockIcon, color: "bg-amber-500" },
          { label: "Overdue", value: data ? currency(data.total_overdue) : "—", icon: ExclamationCircleIcon, color: "bg-red-500" },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="rounded-xl bg-white dark:bg-slate-800 p-4 shadow-sm border border-slate-100 dark:border-slate-700 flex items-center gap-4">
            <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${color}`}>
              <Icon className="h-5 w-5 text-white" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-500 dark:text-slate-400">{label}</p>
              <p className="text-xl font-bold text-slate-900 dark:text-white">{value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Collection Rate */}
      <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">Collection Rate</h2>
          <span className={`text-2xl font-bold ${collectionRate >= 80 ? "text-green-600" : collectionRate >= 50 ? "text-amber-600" : "text-red-600"}`}>
            {collectionRate.toFixed(1)}%
          </span>
        </div>
        <div className="h-2.5 rounded-full bg-slate-100 dark:bg-slate-700 overflow-hidden">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              collectionRate >= 80 ? "bg-green-500" : collectionRate >= 50 ? "bg-amber-500" : "bg-red-500"
            }`}
            style={{ width: `${Math.min(collectionRate, 100)}%` }}
          />
        </div>
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Monthly trend */}
        <ErrorBoundary>
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200 mb-4">Monthly Collection Trend</h2>
          {monthlyData.length === 0 ? (
            <EmptyState icon={ChartBarIcon} title="No data for this period" />
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={monthlyData} margin={{ top: 4, right: 4, left: -10, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="month" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${v / 1000}K`} />
                <Tooltip formatter={(v: number) => [currency(v)]} />
                <Bar dataKey="collected" name="Collected" fill="#22c55e" radius={[4, 4, 0, 0]} />
                <Bar dataKey="outstanding" name="Outstanding" fill="#f59e0b" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
        </ErrorBoundary>

        {/* Status breakdown */}
        <ErrorBoundary>
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200 mb-4">By Status</h2>
          {statusData.length === 0 ? (
            <EmptyState icon={ChartBarIcon} title="No data" />
          ) : (
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={statusData.map((s) => ({ name: s.status, value: Number(s.total) }))}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {statusData.map((_, idx) => (
                    <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip formatter={(v: number) => currency(v)} />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          )}
        </div>
        </ErrorBoundary>
      </div>

      {/* Category breakdown */}
      {categoryData.length > 0 && (
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200 mb-4">By Fee Category</h2>
          <div className="space-y-3">
            {categoryData.map((cat) => {
              const pct = cat.total > 0 ? (cat.collected / cat.total) * 100 : 0;
              return (
                <div key={cat.category}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="font-medium text-slate-700 dark:text-slate-300">{cat.category}</span>
                    <span className="text-slate-500">{currency(cat.collected)} / {currency(cat.total)} ({pct.toFixed(0)}%)</span>
                  </div>
                  <div className="h-2 rounded-full bg-slate-100 dark:bg-slate-700 overflow-hidden">
                    <div className="h-full rounded-full bg-indigo-500" style={{ width: `${pct}%` }} />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Recent Payments */}
      {recentPayments.length > 0 && (
        <div className="rounded-xl bg-white dark:bg-slate-800 shadow-sm border border-slate-100 dark:border-slate-700 overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700">
            <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">Recent Payments</h2>
          </div>
          <div className="divide-y divide-slate-100 dark:divide-slate-700">
            {recentPayments.slice(0, 10).map((p) => (
              <div key={p.id} className="px-5 py-3 flex items-center justify-between hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-slate-900 dark:text-white truncate">{p.student_name}</p>
                  <p className="text-xs text-slate-500">
                    {p.invoice_number} · {p.receipt_number} · {dayjs(p.paid_at).format("MMM D, YYYY")}
                  </p>
                </div>
                <div className="text-right ml-4">
                  <p className="text-sm font-semibold text-green-600">{currency(p.amount)}</p>
                  <p className="text-xs text-slate-400 capitalize">{p.payment_method}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
