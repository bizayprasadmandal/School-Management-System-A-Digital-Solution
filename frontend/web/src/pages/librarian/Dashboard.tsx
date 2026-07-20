/** Librarian Dashboard — library stats, recent additions, overdue counts */
import React from "react";
import { useNavigate } from "react-router-dom";
import {
  BookOpenIcon, MegaphoneIcon, ChevronRightIcon,
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
  fees_collected_month: number;
  fees_outstanding: number;
}

export default function LibrarianDashboard() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const today = dayjs().format("dddd, MMMM D YYYY");

  const { data: stats, isLoading, isError, error, refetch } = useQuery<DashboardStats>({
    queryKey: ["librarian-dashboard"],
    queryFn: () => api.get("/reporting/dashboard-stats/"),
  });

  if (isLoading) return <SkeletonDashboard />;
  if (isError) return <ErrorState message={error?.message} onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Good morning, {user?.first_name} 📚
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
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Today's Attendance</p>
          <p className="mt-1.5 text-3xl font-bold text-slate-900 dark:text-white">
            {stats ? `${stats.attendance_today_pct.toFixed(1)}%` : "—"}
          </p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Teachers</p>
          <p className="mt-1.5 text-3xl font-bold text-slate-900 dark:text-white">{stats?.total_teachers?.toLocaleString() ?? "—"}</p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Classrooms</p>
          <p className="mt-1.5 text-3xl font-bold text-slate-900 dark:text-white">{stats?.total_classrooms?.toLocaleString() ?? "—"}</p>
        </div>
      </div>

      {/* Quick action cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <button onClick={() => navigate("/librarian/library")} className="rounded-xl bg-teal-50 dark:bg-teal-900/20 p-5 border border-teal-200 dark:border-teal-800 text-left hover:bg-teal-100 dark:hover:bg-teal-900/30 transition-colors group cursor-pointer">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-teal-500">
              <BookOpenIcon className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-teal-800 dark:text-teal-300">Library Management</p>
              <p className="text-sm text-teal-600 dark:text-teal-400">Manage books & records</p>
            </div>
            <ChevronRightIcon className="h-5 w-5 text-teal-400 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </button>
        <button onClick={() => navigate("/librarian/announcements")} className="rounded-xl bg-sky-50 dark:bg-sky-900/20 p-5 border border-sky-200 dark:border-sky-800 text-left hover:bg-sky-100 dark:hover:bg-sky-900/30 transition-colors group cursor-pointer">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-sky-500">
              <MegaphoneIcon className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-sky-800 dark:text-sky-300">Announcements</p>
              <p className="text-sm text-sky-600 dark:text-sky-400">View school announcements</p>
            </div>
            <ChevronRightIcon className="h-5 w-5 text-sky-400 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </button>
      </div>
    </div>
  );
}
