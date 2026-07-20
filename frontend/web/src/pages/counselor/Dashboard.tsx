/** Counselor Dashboard — student stats, appointments, quick actions */
import React from "react";
import { useNavigate } from "react-router-dom";
import {
  CalendarDaysIcon, UserGroupIcon, ExclamationTriangleIcon,
  MegaphoneIcon, ChevronRightIcon,
} from "@heroicons/react/24/outline";
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
}

export default function CounselorDashboard() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const today = dayjs().format("dddd, MMMM D YYYY");

  const { data: stats, isLoading, isError, error, refetch } = useQuery<DashboardStats>({
    queryKey: ["counselor-dashboard"],
    queryFn: () => api.get("/reporting/dashboard-stats/"),
  });

  if (isLoading) return <SkeletonDashboard />;
  if (isError) return <ErrorState message={error?.message} onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Good morning, {user?.first_name} 🤝
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{today}</p>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Total Students</p>
          <p className="mt-1.5 text-3xl font-bold text-slate-900 dark:text-white">{stats?.total_students?.toLocaleString() ?? "—"}</p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Teachers</p>
          <p className="mt-1.5 text-3xl font-bold text-slate-900 dark:text-white">{stats?.total_teachers?.toLocaleString() ?? "—"}</p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Classrooms</p>
          <p className="mt-1.5 text-3xl font-bold text-slate-900 dark:text-white">{stats?.total_classrooms?.toLocaleString() ?? "—"}</p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Today's Attendance</p>
          <p className="mt-1.5 text-3xl font-bold text-slate-900 dark:text-white">
            {stats ? `${stats.attendance_today_pct.toFixed(1)}%` : "—"}
          </p>
        </div>
      </div>

      {/* Quick action cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <button onClick={() => navigate("/counselor/appointments")} className="rounded-xl bg-pink-50 dark:bg-pink-900/20 p-5 border border-pink-200 dark:border-pink-800 text-left hover:bg-pink-100 dark:hover:bg-pink-900/30 transition-colors group cursor-pointer">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-pink-500">
              <CalendarDaysIcon className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-pink-800 dark:text-pink-300">Appointments</p>
              <p className="text-sm text-pink-600 dark:text-pink-400">Schedule & manage sessions</p>
            </div>
            <ChevronRightIcon className="h-5 w-5 text-pink-400 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </button>
        <button onClick={() => navigate("/counselor/referrals")} className="rounded-xl bg-rose-50 dark:bg-rose-900/20 p-5 border border-rose-200 dark:border-rose-800 text-left hover:bg-rose-100 dark:hover:bg-rose-900/30 transition-colors group cursor-pointer">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-rose-500">
              <UserGroupIcon className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-rose-800 dark:text-rose-300">Student Referrals</p>
              <p className="text-sm text-rose-600 dark:text-rose-400">View teacher referrals</p>
            </div>
            <ChevronRightIcon className="h-5 w-5 text-rose-400 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </button>
        <button onClick={() => navigate("/counselor/behavior")} className="rounded-xl bg-amber-50 dark:bg-amber-900/20 p-5 border border-amber-200 dark:border-amber-800 text-left hover:bg-amber-100 dark:hover:bg-amber-900/30 transition-colors group cursor-pointer">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-amber-500">
              <ExclamationTriangleIcon className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-amber-800 dark:text-amber-300">Behavior Records</p>
              <p className="text-sm text-amber-600 dark:text-amber-400">Monitor student behavior</p>
            </div>
            <ChevronRightIcon className="h-5 w-5 text-amber-400 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </button>
      </div>
    </div>
  );
}
