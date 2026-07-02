/**
 * Admin Dashboard — KPI cards, charts, quick actions
 */

import React from "react";
import {
  UsersIcon,
  AcademicCapIcon,
  ClipboardDocumentCheckIcon,
  BanknotesIcon,
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
} from "@heroicons/react/24/outline";
import {
  AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend,
} from "recharts";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { useAuthStore } from "../../store/authStore";
import { useAnnouncements } from "../../api/hooks";
import dayjs from "dayjs";

// ─── Types ─────────────────────────────────────────────────────────────────────

interface DashboardStats {
  total_students: number;
  total_teachers: number;
  total_classrooms: number;
  attendance_today_pct: number;
  fees_collected_month: number;
  fees_outstanding: number;
  student_delta_pct: number;
  attendance_delta_pct: number;
}

const ATTENDANCE_TREND = [
  { day: "Mon", present: 94, absent: 6 },
  { day: "Tue", present: 91, absent: 9 },
  { day: "Wed", present: 96, absent: 4 },
  { day: "Thu", present: 88, absent: 12 },
  { day: "Fri", present: 93, absent: 7 },
];

const GRADE_DISTRIBUTION = [
  { name: "A+", value: 18, color: "#22c55e" },
  { name: "A",  value: 24, color: "#86efac" },
  { name: "B",  value: 31, color: "#60a5fa" },
  { name: "C",  value: 17, color: "#fbbf24" },
  { name: "D",  value: 7,  color: "#f97316" },
  { name: "F",  value: 3,  color: "#ef4444" },
];

const FEE_TREND = [
  { month: "Sep", collected: 485000, outstanding: 82000 },
  { month: "Oct", collected: 512000, outstanding: 65000 },
  { month: "Nov", collected: 498000, outstanding: 71000 },
  { month: "Dec", collected: 532000, outstanding: 58000 },
  { month: "Jan", collected: 519000, outstanding: 74000 },
  { month: "Feb", collected: 548000, outstanding: 51000 },
];

// ─── Sub-components ────────────────────────────────────────────────────────────

interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  delta?: number;
  deltaLabel?: string;
}

function StatCard({ label, value, icon: Icon, color, delta, deltaLabel }: StatCardProps) {
  const isPositive = delta !== undefined && delta >= 0;
  return (
    <div className="rounded-xl bg-white p-5 shadow-sm border border-slate-100">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500">{label}</p>
          <p className="mt-1.5 text-3xl font-bold text-slate-900">{value}</p>
        </div>
        <div className={`flex h-12 w-12 items-center justify-center rounded-xl ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>
      {delta !== undefined && (
        <div className="mt-3 flex items-center gap-1.5">
          {isPositive ? (
            <ArrowTrendingUpIcon className="h-4 w-4 text-green-500" />
          ) : (
            <ArrowTrendingDownIcon className="h-4 w-4 text-red-500" />
          )}
          <span className={`text-sm font-medium ${isPositive ? "text-green-600" : "text-red-600"}`}>
            {Math.abs(delta)}%
          </span>
          <span className="text-sm text-slate-400">{deltaLabel}</span>
        </div>
      )}
    </div>
  );
}

// ─── Main component ────────────────────────────────────────────────────────────

export default function AdminDashboard() {
  const { user } = useAuthStore();
  const today = dayjs().format("dddd, MMMM D YYYY");

  const { data: stats } = useQuery<DashboardStats>({
    queryKey: ["dashboard-stats"],
    queryFn: () => api.get("/reporting/dashboard-stats/"),
  });

  const { data: announcements } = useAnnouncements();
  const recentAnnouncements = announcements?.results.slice(0, 4) ?? [];

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Good morning, {user?.first_name} 👋
        </h1>
        <p className="mt-1 text-sm text-slate-500">{today}</p>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <StatCard
          label="Total Students"
          value={stats?.total_students?.toLocaleString() ?? "—"}
          icon={UsersIcon}
          color="bg-indigo-500"
          delta={stats?.student_delta_pct}
          deltaLabel="vs last month"
        />
        <StatCard
          label="Teachers"
          value={stats?.total_teachers?.toLocaleString() ?? "—"}
          icon={AcademicCapIcon}
          color="bg-violet-500"
        />
        <StatCard
          label="Today's Attendance"
          value={stats ? `${stats.attendance_today_pct.toFixed(1)}%` : "—"}
          icon={ClipboardDocumentCheckIcon}
          color={
            stats && stats.attendance_today_pct >= 90
              ? "bg-emerald-500"
              : "bg-amber-500"
          }
          delta={stats?.attendance_delta_pct}
          deltaLabel="vs yesterday"
        />
        <StatCard
          label="Fees Collected (Month)"
          value={stats ? `$${(stats.fees_collected_month / 1000).toFixed(0)}K` : "—"}
          icon={BanknotesIcon}
          color="bg-blue-500"
        />
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Attendance trend */}
        <div className="lg:col-span-2 rounded-xl bg-white p-5 shadow-sm border border-slate-100">
          <h2 className="text-base font-semibold text-slate-800 mb-4">
            This Week&apos;s Attendance
          </h2>
          <ResponsiveContainer width="100%" height={220}>
            <AreaChart data={ATTENDANCE_TREND} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="presentGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#6366f1" stopOpacity={0.15} />
                  <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="day" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12 }} axisLine={false} tickLine={false} unit="%" />
              <Tooltip formatter={(v) => [`${v}%`]} />
              <Area
                type="monotone"
                dataKey="present"
                stroke="#6366f1"
                strokeWidth={2}
                fill="url(#presentGrad)"
                name="Present"
              />
              <Area
                type="monotone"
                dataKey="absent"
                stroke="#ef4444"
                strokeWidth={2}
                fill="transparent"
                name="Absent"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Grade distribution */}
        <div className="rounded-xl bg-white p-5 shadow-sm border border-slate-100">
          <h2 className="text-base font-semibold text-slate-800 mb-4">Grade Distribution</h2>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={GRADE_DISTRIBUTION}
                cx="50%"
                cy="45%"
                innerRadius={55}
                outerRadius={80}
                paddingAngle={2}
                dataKey="value"
              >
                {GRADE_DISTRIBUTION.map((entry) => (
                  <Cell key={entry.name} fill={entry.color} />
                ))}
              </Pie>
              <Legend iconSize={10} iconType="circle" wrapperStyle={{ fontSize: 12 }} />
              <Tooltip formatter={(v) => [`${v}%`]} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Fee collection chart + Announcements */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Fee trend */}
        <div className="lg:col-span-2 rounded-xl bg-white p-5 shadow-sm border border-slate-100">
          <h2 className="text-base font-semibold text-slate-800 mb-4">Fee Collection Trend</h2>
          <ResponsiveContainer width="100%" height={200}>
            <BarChart data={FEE_TREND} margin={{ top: 4, right: 4, left: -10, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
              <XAxis dataKey="month" tick={{ fontSize: 12 }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fontSize: 12 }} axisLine={false} tickLine={false} tickFormatter={(v) => `$${v / 1000}K`} />
              <Tooltip formatter={(v: number) => [`$${v.toLocaleString()}`]} />
              <Bar dataKey="collected" name="Collected" fill="#6366f1" radius={[4, 4, 0, 0]} />
              <Bar dataKey="outstanding" name="Outstanding" fill="#fca5a5" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Recent announcements */}
        <div className="rounded-xl bg-white p-5 shadow-sm border border-slate-100">
          <h2 className="text-base font-semibold text-slate-800 mb-4">Recent Announcements</h2>
          {recentAnnouncements.length === 0 ? (
            <p className="text-sm text-slate-400 text-center py-8">No announcements yet</p>
          ) : (
            <ul className="space-y-3">
              {recentAnnouncements.map((a) => (
                <li key={a.id} className="flex items-start gap-3">
                  <span
                    className={`mt-1 h-2 w-2 flex-shrink-0 rounded-full ${
                      a.priority === "urgent"
                        ? "bg-red-500"
                        : a.priority === "high"
                        ? "bg-amber-500"
                        : "bg-indigo-400"
                    }`}
                  />
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-slate-800 truncate">{a.title}</p>
                    <p className="text-xs text-slate-400">
                      {dayjs(a.created_at).fromNow()}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Outstanding fees alert */}
      {stats && stats.fees_outstanding > 0 && (
        <div className="flex items-start gap-3 rounded-xl border border-amber-200 bg-amber-50 p-4">
          <ExclamationTriangleIcon className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
          <div>
            <p className="text-sm font-semibold text-amber-800">
              Outstanding Fees Alert
            </p>
            <p className="text-sm text-amber-700">
              ${stats.fees_outstanding.toLocaleString()} in unpaid fees. Consider sending payment reminders.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}
