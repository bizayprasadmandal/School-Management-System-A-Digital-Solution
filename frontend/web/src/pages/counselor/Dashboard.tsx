/**
 * Counselor Dashboard — Real counseling KPIs from /counseling/dashboard/stats/
 * Shows today's appointments, upcoming, completed, pending referrals, etc.
 */

import React from "react";
import { useNavigate } from "react-router-dom";
import {
  CalendarDaysIcon, UserGroupIcon, ExclamationTriangleIcon,
  MegaphoneIcon, ChevronRightIcon, CheckCircleIcon, ClockIcon,
} from "@heroicons/react/24/outline";
import { useAuthStore } from "../../store/authStore";
import { SkeletonDashboard, ErrorState } from "../../components/common";
import { useCounselorDashboardStats } from "../../api/hooks";
import dayjs from "dayjs";

export default function CounselorDashboard() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const today = dayjs().format("dddd, MMMM D YYYY");

  const { data: stats, isLoading, isError, error, refetch } = useCounselorDashboardStats();

  if (isLoading) return <SkeletonDashboard />;
  if (isError) return <ErrorState message={error?.message} onRetry={() => refetch()} />;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
          Good morning, {user?.first_name} 🤝
        </h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">{today}</p>
      </div>

      {/* Counseling-specific KPI cards — 4x2 grid */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {/* Today's Appointments */}
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-pink-100 dark:bg-pink-900/40">
              <CalendarDaysIcon className="h-4 w-4 text-pink-600 dark:text-pink-400" />
            </div>
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Today</p>
          </div>
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {stats?.today_appointments ?? 0}
          </p>
          <p className="mt-1 text-xs text-slate-400">appointments scheduled</p>
        </div>

        {/* Upcoming Appointments */}
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-blue-100 dark:bg-blue-900/40">
              <ClockIcon className="h-4 w-4 text-blue-600 dark:text-blue-400" />
            </div>
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Upcoming</p>
          </div>
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {stats?.upcoming_appointments ?? 0}
          </p>
          <p className="mt-1 text-xs text-slate-400">future appointments</p>
        </div>

        {/* Completed Appointments */}
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-green-100 dark:bg-green-900/40">
              <CheckCircleIcon className="h-4 w-4 text-green-600 dark:text-green-400" />
            </div>
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Completed</p>
          </div>
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {stats?.appointments_completed ?? 0}
          </p>
          <p className="mt-1 text-xs text-slate-400">sessions finished</p>
        </div>

        {/* Pending Referrals */}
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-amber-100 dark:bg-amber-900/40">
              <UserGroupIcon className="h-4 w-4 text-amber-600 dark:text-amber-400" />
            </div>
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Pending Referrals</p>
          </div>
          <p className="text-3xl font-bold text-slate-900 dark:text-white">
            {stats?.pending_referrals ?? 0}
          </p>
          {stats && stats.urgent_referrals > 0 && (
            <p className="mt-1 text-xs font-semibold text-red-500 flex items-center gap-1">
              <ExclamationTriangleIcon className="h-3 w-3" />
              {stats.urgent_referrals} urgent
            </p>
          )}
        </div>
      </div>

      {/* Secondary metrics row — lighter stats */}
      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <div className="rounded-lg bg-slate-50 dark:bg-slate-800/50 px-4 py-3 border border-slate-100 dark:border-slate-700">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Total Appointments</p>
          <p className="text-xl font-bold text-slate-800 dark:text-slate-200">{stats?.total_appointments ?? 0}</p>
        </div>
        <div className="rounded-lg bg-slate-50 dark:bg-slate-800/50 px-4 py-3 border border-slate-100 dark:border-slate-700">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Total Referrals</p>
          <p className="text-xl font-bold text-slate-800 dark:text-slate-200">{stats?.total_referrals ?? 0}</p>
        </div>
        <div className="rounded-lg bg-slate-50 dark:bg-slate-800/50 px-4 py-3 border border-slate-100 dark:border-slate-700">
          <p className="text-xs font-medium text-slate-500 dark:text-slate-400 uppercase tracking-wide">Referrals Resolved</p>
          <p className="text-xl font-bold text-slate-800 dark:text-slate-200">{stats?.referrals_resolved ?? 0}</p>
        </div>
      </div>

      {/* Quick action cards */}
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
        <button
          onClick={() => navigate("/counselor/appointments")}
          className="rounded-xl bg-pink-50 dark:bg-pink-900/20 p-5 border border-pink-200 dark:border-pink-800 text-left hover:bg-pink-100 dark:hover:bg-pink-900/30 transition-colors group cursor-pointer"
        >
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-pink-500">
              <CalendarDaysIcon className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-pink-800 dark:text-pink-300">
                Appointments
                {stats && stats.today_appointments > 0 && (
                  <span className="ml-2 inline-flex items-center justify-center h-5 min-w-[1.25rem] rounded-full bg-pink-500 text-[10px] font-bold text-white px-1.5">
                    {stats.today_appointments} today
                  </span>
                )}
              </p>
              <p className="text-sm text-pink-600 dark:text-pink-400">Schedule & manage sessions</p>
            </div>
            <ChevronRightIcon className="h-5 w-5 text-pink-400 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </button>
        <button
          onClick={() => navigate("/counselor/referrals")}
          className="rounded-xl bg-rose-50 dark:bg-rose-900/20 p-5 border border-rose-200 dark:border-rose-800 text-left hover:bg-rose-100 dark:hover:bg-rose-900/30 transition-colors group cursor-pointer"
        >
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-rose-500">
              <UserGroupIcon className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1">
              <p className="font-semibold text-rose-800 dark:text-rose-300">
                Student Referrals
                {stats && stats.pending_referrals > 0 && (
                  <span className="ml-2 inline-flex items-center justify-center h-5 min-w-[1.25rem] rounded-full bg-rose-500 text-[10px] font-bold text-white px-1.5">
                    {stats.pending_referrals} pending
                  </span>
                )}
              </p>
              <p className="text-sm text-rose-600 dark:text-rose-400">Review & act on referrals</p>
            </div>
            <ChevronRightIcon className="h-5 w-5 text-rose-400 group-hover:translate-x-0.5 transition-transform" />
          </div>
        </button>
        <button
          onClick={() => navigate("/counselor/behavior")}
          className="rounded-xl bg-amber-50 dark:bg-amber-900/20 p-5 border border-amber-200 dark:border-amber-800 text-left hover:bg-amber-100 dark:hover:bg-amber-900/30 transition-colors group cursor-pointer"
        >
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

      {/* Announcements link */}
      <div className="flex items-center justify-center">
        <button
          onClick={() => navigate("/counselor/announcements")}
          className="inline-flex items-center gap-2 rounded-lg bg-white dark:bg-slate-800 px-4 py-2.5 text-sm font-medium text-slate-600 dark:text-slate-400 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white transition-colors"
        >
          <MegaphoneIcon className="h-4 w-4" />
          View School Announcements
          <ChevronRightIcon className="h-4 w-4" />
        </button>
      </div>
    </div>
  );
}
