/**
 * Admin Dashboard — KPI cards, charts, quick actions
 */

import React, { useMemo } from "react";
import { useNavigate, Link } from "react-router-dom";
import {
  UsersIcon,
  AcademicCapIcon,
  ClipboardDocumentCheckIcon,
  BanknotesIcon,
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
  ArrowTrendingDownIcon,
  ChevronRightIcon,
  UserGroupIcon,
  InboxArrowDownIcon,
} from "@heroicons/react/24/outline";
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend,
} from "recharts";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { useAuthStore } from "../../store/authStore";
import {
  useAnnouncements,
  useAtRiskStudents,
  useEnrollmentFunnel,
  useFeeForecast,
} from "../../api/hooks";
import { SkeletonDashboard, ErrorState, ErrorBoundary } from "../../components/common";
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
  attendance_week?: { day: string; present: number; absent: number }[];
  grade_distribution?: { name: string; value: number }[];
}

const GRADE_COLORS: Record<string, string> = {
  "A+": "#22c55e",
  A: "#86efac",
  "B+": "#3b82f6",
  B: "#60a5fa",
  C: "#fbbf24",
  D: "#f97316",
  F: "#ef4444",
};

// ─── Sub-components ────────────────────────────────────────────────────────────

interface StatCardProps {
  label: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  delta?: number;
  deltaLabel?: string;
  to?: string;
}

function StatCard({ label, value, icon: Icon, color, delta, deltaLabel, to }: StatCardProps) {
  const isPositive = delta !== undefined && delta >= 0;
  const navigate = useNavigate();
  const content = (
    <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm dark:shadow-none border border-slate-100 dark:border-slate-700 h-full">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p>
          <p className="mt-1.5 text-3xl font-bold text-slate-900 dark:text-white">{value}</p>
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
          <span
            className={`text-sm font-medium ${
              isPositive ? "text-green-600 dark:text-green-400" : "text-red-600 dark:text-red-400"
            }`}
          >
            {Math.abs(delta)}%
          </span>
          <span className="text-sm text-slate-400 dark:text-slate-500">{deltaLabel}</span>
        </div>
      )}
    </div>
  );

  if (to) {
    return (
      <button onClick={() => navigate(to)} className="text-left w-full group cursor-pointer">
        {content}
      </button>
    );
  }
  return content;
}

// ─── Main component ────────────────────────────────────────────────────────────

export default function AdminDashboard() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const today = dayjs().format("dddd, MMMM D YYYY");

  const {
    data: stats,
    isLoading,
    isError,
    error,
    refetch,
  } = useQuery<DashboardStats>({
    queryKey: ["dashboard-stats"],
    queryFn: () => api.get("/reporting/dashboard-stats/"),
  });

  const { data: announcements } = useAnnouncements();
  const recentAnnouncements = announcements?.results.slice(0, 4) ?? [];

  const { data: atRisk, isError: atRiskError } = useAtRiskStudents();
  const { data: funnel, isError: funnelError } = useEnrollmentFunnel();
  const { data: forecast, isError: forecastError } = useFeeForecast();
  const atRiskStudents = atRisk?.students?.slice(0, 5) ?? [];

  /**
   * Fee collection trend = trailing 3 months of real collections
   * + next 90 days of forecast windows (expected vs already paid).
   */
  const feeTrendData = useMemo(() => {
    const history =
      forecast?.history_3m?.map((h) => ({
        label: dayjs(`${h.month}-01`).format("MMM"),
        collected: h.collected,
        expected: null,
      })) ?? [];
    const future =
      forecast?.forecast_90d?.map((f) => ({
        label: dayjs(f.window_start).format("MMM"),
        collected: f.already_paid,
        expected: f.expected,
      })) ?? [];
    return [...history, ...future];
  }, [forecast]);

  if (isLoading) return <SkeletonDashboard />;
  if (isError) return <ErrorState message={error?.message} onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Good morning, {user?.first_name} 👋
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{today}</p>
      </div>

      {/* KPI cards */}
      <ErrorBoundary>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Total Students"
            value={stats?.total_students?.toLocaleString() ?? "—"}
            icon={UsersIcon}
            color="bg-indigo-500"
            delta={stats?.student_delta_pct}
            deltaLabel="vs last month"
            to="/admin/students"
          />
          <StatCard
            label="Teachers"
            value={stats?.total_teachers?.toLocaleString() ?? "—"}
            icon={AcademicCapIcon}
            color="bg-violet-500"
            to="/admin/teachers"
          />
          <StatCard
            label="Today's Attendance"
            value={stats ? `${stats.attendance_today_pct.toFixed(1)}%` : "—"}
            icon={ClipboardDocumentCheckIcon}
            color={stats && stats.attendance_today_pct >= 90 ? "bg-emerald-500" : "bg-amber-500"}
            delta={stats?.attendance_delta_pct}
            deltaLabel="vs yesterday"
            to="/admin/attendance"
          />
          <StatCard
            label="Fees Collected (Month)"
            value={stats ? `$${(stats.fees_collected_month / 1000).toFixed(0)}K` : "—"}
            icon={BanknotesIcon}
            color="bg-blue-500"
            to="/admin/fees"
          />
        </div>
      </ErrorBoundary>

      {/* Charts row */}
      <ErrorBoundary>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Attendance trend */}
          <div className="lg:col-span-2 rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm dark:shadow-none border border-slate-100 dark:border-slate-700">
            <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200 mb-4">
              This Week&apos;s Attendance
            </h2>
            {(stats?.attendance_week?.length ?? 0) === 0 ? (
              <p className="text-sm text-slate-400 dark:text-slate-500 text-center py-16">
                No attendance recorded yet
              </p>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <AreaChart
                  data={stats!.attendance_week!}
                  margin={{ top: 4, right: 4, left: -20, bottom: 0 }}
                >
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
            )}
          </div>

          {/* Grade distribution */}
          <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm dark:shadow-none border border-slate-100 dark:border-slate-700">
            <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200 mb-4">
              Grade Distribution
            </h2>
            {(stats?.grade_distribution?.length ?? 0) === 0 ? (
              <p className="text-sm text-slate-400 dark:text-slate-500 text-center py-16">
                No published report cards yet
              </p>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <PieChart>
                  <Pie
                    data={stats!.grade_distribution!}
                    cx="50%"
                    cy="45%"
                    innerRadius={55}
                    outerRadius={80}
                    paddingAngle={2}
                    dataKey="value"
                  >
                    {stats!.grade_distribution!.map((entry) => (
                      <Cell key={entry.name} fill={GRADE_COLORS[entry.name] ?? "#94a3b8"} />
                    ))}
                  </Pie>
                  <Legend iconSize={10} iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                  <Tooltip formatter={(v) => [`${v} students`]} />
                </PieChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>
      </ErrorBoundary>

      {/* Fee collection chart + Announcements */}
      <ErrorBoundary>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* Fee trend + forecast */}
          <div className="lg:col-span-2 rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm dark:shadow-none border border-slate-100 dark:border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
                Fee Collection Trend
              </h2>
              <div className="flex items-center gap-2">
                {!forecastError && forecast && (
                  <span className="inline-flex items-center gap-1 rounded-full bg-amber-50 dark:bg-amber-900/30 px-2.5 py-1 text-xs font-medium text-amber-700 dark:text-amber-300">
                    <ExclamationTriangleIcon className="h-3.5 w-3.5" />$
                    {(forecast.overdue_total / 1000).toFixed(0)}K overdue
                  </span>
                )}
                {!forecastError && (forecast?.forecast_90d?.length ?? 0) > 0 && (
                  <span className="rounded-full bg-indigo-50 dark:bg-indigo-900/30 px-2.5 py-1 text-xs font-medium text-indigo-700 dark:text-indigo-300">
                    90-day forecast
                  </span>
                )}
              </div>
            </div>
            {forecastError ? (
              <p className="text-sm text-slate-400 dark:text-slate-500 text-center py-10">
                Fee forecast unavailable
              </p>
            ) : feeTrendData.length === 0 ? (
              <p className="text-sm text-slate-400 dark:text-slate-500 text-center py-10">
                No fee collections yet
              </p>
            ) : (
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={feeTrendData} margin={{ top: 4, right: 4, left: -10, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis
                    dataKey="label"
                    tick={{ fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                  />
                  <YAxis
                    tick={{ fontSize: 12 }}
                    axisLine={false}
                    tickLine={false}
                    tickFormatter={(v) => `$${v / 1000}K`}
                  />
                  <Tooltip formatter={(v: number) => [`$${v.toLocaleString()}`]} />
                  <Legend iconSize={10} iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                  <Bar dataKey="collected" name="Collected" fill="#6366f1" radius={[4, 4, 0, 0]} />
                  <Bar
                    dataKey="expected"
                    name="Expected (due)"
                    fill="#fbbf24"
                    radius={[4, 4, 0, 0]}
                  />
                </BarChart>
              </ResponsiveContainer>
            )}
          </div>

          {/* Recent announcements */}
          <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm dark:shadow-none border border-slate-100 dark:border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200">
                Recent Announcements
              </h2>
              <Link
                to="/admin/announcements"
                className="text-xs font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors flex items-center gap-0.5"
              >
                View all <ChevronRightIcon className="h-3 w-3" />
              </Link>
            </div>
            {recentAnnouncements.length === 0 ? (
              <p className="text-sm text-slate-400 dark:text-slate-500 text-center py-8">
                No announcements yet
              </p>
            ) : (
              <ul className="space-y-1">
                {recentAnnouncements.map((a) => (
                  <li key={a.id}>
                    <Link
                      to="/admin/announcements"
                      className="flex items-start gap-3 rounded-lg px-2 py-2 -mx-2 hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors group"
                    >
                      <span
                        className={`mt-1 h-2 w-2 flex-shrink-0 rounded-full ${
                          a.priority === "urgent"
                            ? "bg-red-500"
                            : a.priority === "high"
                              ? "bg-amber-500"
                              : "bg-indigo-400"
                        }`}
                      />
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-slate-800 dark:text-slate-200 truncate group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                          {a.title}
                        </p>
                        <p className="text-xs text-slate-400 dark:text-slate-500">
                          {dayjs(a.created_at).fromNow()}
                        </p>
                      </div>
                      <ChevronRightIcon className="h-4 w-4 text-slate-300 dark:text-slate-600 flex-shrink-0 self-center opacity-0 group-hover:opacity-100 transition-opacity" />
                    </Link>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </ErrorBoundary>

      {/* At-risk students + enrollment funnel */}
      <ErrorBoundary>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* At-risk students */}
          <div className="lg:col-span-2 rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm dark:shadow-none border border-slate-100 dark:border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                <UserGroupIcon className="h-5 w-5 text-amber-500" />
                At-Risk Students
              </h2>
              {!atRiskError && atRisk && atRisk.count > 0 && (
                <span className="rounded-full bg-red-50 dark:bg-red-900/30 px-2.5 py-1 text-xs font-semibold text-red-600 dark:text-red-300">
                  {atRisk.count} flagged
                </span>
              )}
            </div>
            {atRiskError ? (
              <p className="text-sm text-slate-400 dark:text-slate-500 text-center py-8">
                Risk analytics unavailable
              </p>
            ) : atRiskStudents.length === 0 ? (
              <p className="text-sm text-slate-400 dark:text-slate-500 text-center py-8">
                🎉 No students currently flagged
              </p>
            ) : (
              <ul className="divide-y divide-slate-100 dark:divide-slate-700">
                {atRiskStudents.map((s) => (
                  <li key={s.student_id} className="flex items-center gap-3 py-2.5">
                    <span className="flex h-9 w-9 items-center justify-center rounded-full bg-red-50 dark:bg-red-900/30 text-red-500 text-sm font-semibold flex-shrink-0">
                      {s.student_name.charAt(0)}
                    </span>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-slate-800 dark:text-slate-200 truncate">
                        {s.student_name}
                      </p>
                      <p className="text-xs text-slate-400 dark:text-slate-500 truncate">
                        {s.classroom ?? "No classroom"} · Adm. {s.admission_number}
                      </p>
                    </div>
                    <div className="flex items-center gap-1.5 flex-shrink-0">
                      {s.reasons.map((r) => (
                        <span
                          key={r}
                          className={`rounded-full px-2 py-0.5 text-[11px] font-medium ${
                            r === "low_academics"
                              ? "bg-amber-50 dark:bg-amber-900/30 text-amber-700 dark:text-amber-300"
                              : "bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-300"
                          }`}
                        >
                          {r === "low_academics" ? "Academics" : "Attendance"}
                        </span>
                      ))}
                      {s.attendance_pct !== null && (
                        <span className="text-xs font-semibold text-slate-500 dark:text-slate-400 w-12 text-right">
                          {s.attendance_pct}%
                        </span>
                      )}
                    </div>
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Enrollment funnel */}
          <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm dark:shadow-none border border-slate-100 dark:border-slate-700">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-slate-800 dark:text-slate-200 flex items-center gap-2">
                <InboxArrowDownIcon className="h-5 w-5 text-indigo-500" />
                Enrollment Funnel
              </h2>
              {!funnelError && funnel && funnel.total_applications > 0 && (
                <span className="rounded-full bg-indigo-50 dark:bg-indigo-900/30 px-2.5 py-1 text-xs font-semibold text-indigo-600 dark:text-indigo-300">
                  {funnel.total_applications} apps
                </span>
              )}
            </div>
            {funnelError ? (
              <p className="text-sm text-slate-400 dark:text-slate-500 text-center py-8">
                Funnel data unavailable
              </p>
            ) : !funnel?.funnel || funnel.funnel.every((f) => f.count === 0) ? (
              <p className="text-sm text-slate-400 dark:text-slate-500 text-center py-8">
                No applications yet
              </p>
            ) : (
              <>
                <ResponsiveContainer width="100%" height={210}>
                  <BarChart
                    data={funnel.funnel}
                    layout="vertical"
                    margin={{ top: 0, right: 32, left: 0, bottom: 0 }}
                  >
                    <XAxis type="number" hide />
                    <YAxis
                      type="category"
                      dataKey="stage"
                      width={88}
                      tick={{ fontSize: 11 }}
                      axisLine={false}
                      tickLine={false}
                      tickFormatter={(v: string) => v.replace(/_/g, " ")}
                    />
                    <Tooltip formatter={(v: number) => [`${v} applications`]} />
                    <Bar
                      dataKey="count"
                      name="Applications"
                      radius={[0, 4, 4, 0]}
                      label={{ position: "right", fontSize: 11, fill: "#94a3b8" }}
                    >
                      {funnel.funnel.map((entry) => (
                        <Cell
                          key={entry.stage}
                          fill={
                            entry.stage === "rejected"
                              ? "#ef4444"
                              : entry.stage === "enrolled" || entry.stage === "accepted"
                                ? "#22c55e"
                                : entry.stage === "waitlisted"
                                  ? "#fbbf24"
                                  : "#6366f1"
                          }
                        />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
                {funnel?.conversion && (
                  <div className="mt-4 grid grid-cols-2 gap-3">
                    <div className="rounded-lg bg-slate-50 dark:bg-slate-700/40 p-3 text-center">
                      <p className="text-[11px] text-slate-400 dark:text-slate-500">
                        Submitted → Accepted
                      </p>
                      <p className="mt-0.5 text-lg font-bold text-slate-800 dark:text-white">
                        {funnel.conversion.submitted_to_accepted}%
                      </p>
                    </div>
                    <div className="rounded-lg bg-slate-50 dark:bg-slate-700/40 p-3 text-center">
                      <p className="text-[11px] text-slate-400 dark:text-slate-500">
                        Accepted → Enrolled
                      </p>
                      <p className="mt-0.5 text-lg font-bold text-slate-800 dark:text-white">
                        {funnel.conversion.accepted_to_enrolled}%
                      </p>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </ErrorBoundary>

      {/* Outstanding fees alert */}
      <ErrorBoundary>
        {stats && stats.fees_outstanding > 0 && (
          <button onClick={() => navigate("/admin/fees")} className="w-full text-left">
            <div className="flex items-start gap-3 rounded-xl border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/30 p-4 hover:bg-amber-100 dark:hover:bg-amber-900/50 transition-colors cursor-pointer group">
              <ExclamationTriangleIcon className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
              <div className="flex-1">
                <p className="text-sm font-semibold text-amber-800 dark:text-amber-300">
                  Outstanding Fees Alert
                </p>
                <p className="text-sm text-amber-700 dark:text-amber-400">
                  ${stats.fees_outstanding.toLocaleString()} in unpaid fees. Consider sending
                  payment reminders.
                </p>
              </div>
              <ChevronRightIcon className="h-5 w-5 text-amber-400 flex-shrink-0 self-center opacity-0 group-hover:opacity-100 transition-opacity" />
            </div>
          </button>
        )}
      </ErrorBoundary>
    </div>
  );
}
