/**
 * PlatformDashboard — Cross-school analytics for Super Admin
 * Shows aggregate stats across all schools managed by the platform.
 */

import React from "react";
import { useNavigate } from "react-router-dom";
import {
  BuildingOffice2Icon,
  UsersIcon,
  AcademicCapIcon,
  BanknotesIcon,
  CheckBadgeIcon,
  ArrowTrendingUpIcon,
  ChevronRightIcon,
} from "@heroicons/react/24/outline";
import { usePlatformDashboardStats } from "../../api/hooks";

function formatCurrency(amount: number): string {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount);
}

function StatCard({
  label,
  value,
  icon: Icon,
  color,
  subtitle,
}: {
  label: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  color: string;
  subtitle?: string;
}) {
  return (
    <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5 hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{label}</p>
          <p className="mt-1 text-3xl font-bold text-slate-900 dark:text-white">{value}</p>
          {subtitle && (
            <p className="mt-1 text-xs text-slate-400 dark:text-slate-500">{subtitle}</p>
          )}
        </div>
        <div className={`rounded-lg p-3 ${color}`}>
          <Icon className="h-6 w-6 text-white" />
        </div>
      </div>
    </div>
  );
}

function TierPill({ tier, count }: { tier: string; count: number }) {
  const colors: Record<string, string> = {
    basic: "bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300",
    standard: "bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300",
    premium: "bg-amber-100 text-amber-700 dark:bg-amber-900/50 dark:text-amber-300",
  };
  return (
    <div className="flex items-center justify-between rounded-lg border border-slate-200 dark:border-slate-700 px-4 py-2.5">
      <span className="text-sm font-medium text-slate-700 dark:text-slate-300 capitalize">{tier}</span>
      <span className={`ml-2 rounded-full px-2.5 py-0.5 text-xs font-semibold ${colors[tier] || colors.basic}`}>
        {count}
      </span>
    </div>
  );
}

export default function PlatformDashboard() {
  const navigate = useNavigate();
  const { data: stats, isLoading, error } = usePlatformDashboardStats();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
      </div>
    );
  }

  if (error || !stats) {
    return (
      <div className="rounded-xl border border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20 p-6 text-center">
        <p className="text-red-600 dark:text-red-400">Failed to load platform data.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Platform Dashboard</h1>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Cross-school analytics — overview of all schools on the platform
        </p>
      </div>

      {/* Stats grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-4">
        <StatCard
          label="Total Schools"
          value={stats.total_schools}
          icon={BuildingOffice2Icon}
          color="bg-indigo-600"
          subtitle={`${stats.active_schools} active`}
        />
        <StatCard
          label="Total Users"
          value={stats.total_users}
          icon={UsersIcon}
          color="bg-blue-600"
        />
        <StatCard
          label="Students"
          value={stats.total_students}
          icon={AcademicCapIcon}
          color="bg-emerald-600"
        />
        <StatCard
          label="Teachers"
          value={stats.total_teachers}
          icon={UsersIcon}
          color="bg-violet-600"
        />
        <StatCard
          label="Total Revenue"
          value={formatCurrency(stats.total_revenue)}
          icon={BanknotesIcon}
          color="bg-amber-600"
        />
        <StatCard
          label="Active Schools"
          value={stats.active_schools}
          icon={CheckBadgeIcon}
          color="bg-green-600"
          subtitle={`${Math.round((stats.active_schools / Math.max(stats.total_schools, 1)) * 100)}% of total`}
        />
      </div>

      {/* Two-column layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left: Schools by tier */}
        <div className="lg:col-span-1 space-y-4">
          <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5">
            <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-4">Schools by Tier</h2>
            <div className="space-y-2">
              {Object.entries(stats.schools_by_tier).map(([tier, count]) => (
                <TierPill key={tier} tier={tier} count={count} />
              ))}
            </div>
          </div>

          {/* Quick actions */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5">
            <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-3">Quick Actions</h2>
            <div className="space-y-2">
              <button
                onClick={() => navigate("/admin/platform/schools")}
                className="flex w-full items-center justify-between rounded-lg bg-indigo-50 dark:bg-indigo-900/30 px-4 py-2.5 text-sm font-medium text-indigo-700 dark:text-indigo-300 hover:bg-indigo-100 dark:hover:bg-indigo-900/50 transition-colors"
              >
                <span>Manage Schools</span>
                <ChevronRightIcon className="h-4 w-4" />
              </button>
              <button
                onClick={() => navigate("/admin/platform/schools?action=new")}
                className="flex w-full items-center justify-between rounded-lg bg-emerald-50 dark:bg-emerald-900/30 px-4 py-2.5 text-sm font-medium text-emerald-700 dark:text-emerald-300 hover:bg-emerald-100 dark:hover:bg-emerald-900/50 transition-colors"
              >
                <span>Add New School</span>
                <ChevronRightIcon className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        {/* Right: Recent schools + Top schools by revenue */}
        <div className="lg:col-span-2 space-y-6">
          {/* Recent schools */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-base font-semibold text-slate-900 dark:text-white">Recently Created Schools</h2>
              <button
                onClick={() => navigate("/admin/platform/schools")}
                className="text-sm font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300"
              >
                View all
              </button>
            </div>
            {stats.recent_schools.length === 0 ? (
              <p className="text-sm text-slate-400 dark:text-slate-500">No schools created yet.</p>
            ) : (
              <div className="divide-y divide-slate-100 dark:divide-slate-700">
                {stats.recent_schools.map((school) => (
                  <button
                    key={school.id}
                    onClick={() => navigate(`/admin/platform/schools/${school.id}`)}
                    className="flex w-full items-center justify-between py-3 hover:bg-slate-50 dark:hover:bg-slate-700/50 px-2 -mx-2 rounded-lg transition-colors text-left"
                  >
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                        {school.name}
                      </p>
                      <p className="text-xs text-slate-500 dark:text-slate-400">
                        {school.code} · {school.subdomain} · {school.student_count || 0} students
                      </p>
                    </div>
                    <span
                      className={`ml-3 inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        school.is_active
                          ? "bg-green-100 text-green-700 dark:bg-green-900/50 dark:text-green-300"
                          : "bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-300"
                      }`}
                    >
                      {school.is_active ? "Active" : "Inactive"}
                    </span>
                  </button>
                ))}
              </div>
            )}
          </div>

          {/* Top schools by revenue */}
          <div className="rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-slate-800 p-5">
            <h2 className="text-base font-semibold text-slate-900 dark:text-white mb-4">
              <ArrowTrendingUpIcon className="inline h-5 w-5 mr-1.5 text-emerald-500" />
              Top Schools by Revenue
            </h2>
            {stats.top_schools.length === 0 ? (
              <p className="text-sm text-slate-400 dark:text-slate-500">No revenue data available.</p>
            ) : (
              <div className="space-y-3">
                {stats.top_schools.map((school, idx) => (
                  <div
                    key={school.id}
                    className="flex items-center justify-between rounded-lg bg-slate-50 dark:bg-slate-700/50 px-4 py-3"
                  >
                    <div className="flex items-center gap-3 min-w-0">
                      <span className="flex h-7 w-7 items-center justify-center rounded-full bg-indigo-100 dark:bg-indigo-900/50 text-xs font-bold text-indigo-700 dark:text-indigo-300">
                        {idx + 1}
                      </span>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-slate-900 dark:text-white truncate">{school.name}</p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">{school.code}</p>
                      </div>
                    </div>
                    <span className="text-sm font-semibold text-emerald-600 dark:text-emerald-400">
                      {formatCurrency(school.revenue)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
