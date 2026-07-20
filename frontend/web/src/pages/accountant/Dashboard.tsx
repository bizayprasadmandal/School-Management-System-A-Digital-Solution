/** Accountant Dashboard — fee KPIs, collection trends, recent invoices */
import React from "react";
import { useNavigate } from "react-router-dom";
import {
  BanknotesIcon, ChartBarIcon, ClockIcon,
  ChevronRightIcon,
} from "@heroicons/react/24/outline";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from "recharts";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { useAuthStore } from "../../store/authStore";
import { SkeletonDashboard, ErrorState } from "../../components/common";
import dayjs from "dayjs";

interface DashboardStats {
  total_students: number;
  total_teachers: number;
  total_classrooms: number;
  attendance_today_pct: number;
  fees_collected_month: number;
  fees_outstanding: number;
}

const MONTHLY_FEES = [
  { month: "Sep", collected: 485000, outstanding: 82000 },
  { month: "Oct", collected: 512000, outstanding: 65000 },
  { month: "Nov", collected: 498000, outstanding: 71000 },
  { month: "Dec", collected: 532000, outstanding: 58000 },
  { month: "Jan", collected: 519000, outstanding: 74000 },
  { month: "Feb", collected: 548000, outstanding: 51000 },
];

export default function AccountantDashboard() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const today = dayjs().format("dddd, MMMM D YYYY");

  const { data, isLoading, isError, error, refetch } = useQuery<DashboardStats>({
    queryKey: ["accountant-dashboard"],
    queryFn: () => api.get("/reporting/dashboard-stats/"),
  });

  if (isLoading) return <SkeletonDashboard />;
  if (isError) return <ErrorState message={error?.message} onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Good morning, {user?.first_name} 💰
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{today}</p>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Fees Collected (Month)</p>
          <p className="mt-1.5 text-3xl font-bold text-slate-900 dark:text-white">
            ${data ? `${(data.fees_collected_month / 1000).toFixed(0)}K` : "—"}
          </p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Outstanding Fees</p>
          <p className="mt-1.5 text-3xl font-bold text-amber-600 dark:text-amber-400">
            ${data ? `${(data.fees_outstanding / 1000).toFixed(0)}K` : "—"}
          </p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Total Students</p>
          <p className="mt-1.5 text-3xl font-bold text-slate-900 dark:text-white">{data?.total_students?.toLocaleString() ?? "—"}</p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Teachers</p>
          <p className="mt-1.5 text-3xl font-bold text-slate-900 dark:text-white">{data?.total_teachers?.toLocaleString() ?? "—"}</p>
        </div>
      </div>

      {/* Fee collection chart */}
      <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
        <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200 mb-4">Fee Collection Trend</h2>
        <ResponsiveContainer width="100%" height={260}>
          <BarChart data={MONTHLY_FEES} margin={{ top: 4, right: 4, left: -10, bottom: 0 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
            <XAxis dataKey="month" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
            <YAxis tick={{ fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${v / 1000}K`} />
            <Tooltip formatter={(v: number) => [`$${v.toLocaleString()}`]} />
            <Bar dataKey="collected" name="Collected" fill="#f59e0b" radius={[4, 4, 0, 0]} />
            <Bar dataKey="outstanding" name="Outstanding" fill="#fca5a5" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* Quick action cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <button onClick={() => navigate("/accountant/fees")} className="rounded-xl bg-amber-50 dark:bg-amber-900/20 p-5 border border-amber-200 dark:border-amber-800 text-left hover:bg-amber-100 dark:hover:bg-amber-900/30 transition-colors group cursor-pointer">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-500">
              <BanknotesIcon className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-amber-800 dark:text-amber-300">Fee Management</p>
              <p className="text-sm text-amber-600 dark:text-amber-400">View & manage invoices</p>
            </div>
            <ChevronRightIcon className="h-5 w-5 text-amber-400 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </button>
        <button onClick={() => navigate("/accountant/reports")} className="rounded-xl bg-blue-50 dark:bg-blue-900/20 p-5 border border-blue-200 dark:border-blue-800 text-left hover:bg-blue-100 dark:hover:bg-blue-900/30 transition-colors group cursor-pointer">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-500">
              <ChartBarIcon className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-blue-800 dark:text-blue-300">Financial Reports</p>
              <p className="text-sm text-blue-600 dark:text-blue-400">View revenue & analytics</p>
            </div>
            <ChevronRightIcon className="h-5 w-5 text-blue-400 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </button>
        <button onClick={() => navigate("/accountant/conferences")} className="rounded-xl bg-violet-50 dark:bg-violet-900/20 p-5 border border-violet-200 dark:border-violet-800 text-left hover:bg-violet-100 dark:hover:bg-violet-900/30 transition-colors group cursor-pointer">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-500">
              <ClockIcon className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-violet-800 dark:text-violet-300">Conferences</p>
              <p className="text-sm text-violet-600 dark:text-violet-400">Manage parent-teacher meetings</p>
            </div>
            <ChevronRightIcon className="h-5 w-5 text-violet-400 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </button>
      </div>
    </div>
  );
}
