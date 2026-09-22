/**
 * Platform Revenue & Plans — per-school billing overview for the platform
 * console. Super-admin only: MRR/ARR per school (tier pricing × student
 * count), all-time revenue collected, tier distribution.
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { BanknotesIcon, BuildingOffice2Icon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { SkeletonCard, SkeletonStatCard } from "../../components/common";
import { useTitle } from "../../hooks";
import { npr } from "../../utils";

interface RevenueSchoolRow {
  id: string;
  name: string;
  code: string;
  subscription_tier: "basic" | "standard" | "premium";
  is_active: boolean;
  student_count: number;
  revenue: number;
  mrr: number;
  arr: number;
}

interface PlatformRevenue {
  total_mrr: number;
  total_arr: number;
  schools_by_tier: Record<string, number>;
  schools: RevenueSchoolRow[];
}

const TIER_BADGE: Record<string, string> = {
  basic: "bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-200",
  standard: "bg-sky-100 text-sky-700 dark:bg-sky-900/50 dark:text-sky-200",
  premium: "bg-amber-100 text-amber-800 dark:bg-amber-900/50 dark:text-amber-200",
};

export default function PlatformRevenuePage() {
  useTitle("Revenue & Plans");
  const navigate = useNavigate();
  const { data, isLoading } = useQuery({
    queryKey: ["platform-revenue"],
    queryFn: () => api.get<PlatformRevenue>("/auth/platform/revenue/"),
  });

  if (isLoading || !data) {
    return (
      <div className="space-y-5">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Revenue &amp; Plans</h1>
          <p className="text-sm text-slate-500 mt-0.5">Per-school billing across the platform</p>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <SkeletonStatCard />
          <SkeletonStatCard />
          <SkeletonStatCard />
        </div>
        <SkeletonCard />
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Revenue &amp; Plans</h1>
        <p className="text-sm text-slate-500 mt-0.5">Per-school billing across the platform</p>
      </div>

      {/* Totals */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
            <BanknotesIcon className="h-5 w-5" aria-hidden />
            <span className="text-sm font-medium">Platform MRR</span>
          </div>
          <p className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
            {npr(data.total_mrr)}
          </p>
        </div>
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
            <BanknotesIcon className="h-5 w-5" aria-hidden />
            <span className="text-sm font-medium">Platform ARR</span>
          </div>
          <p className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
            {npr(data.total_arr)}
          </p>
        </div>
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm p-5 dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
          <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
            <BuildingOffice2Icon className="h-5 w-5" aria-hidden />
            <span className="text-sm font-medium">Tier distribution</span>
          </div>
          <p className="mt-2 text-sm font-medium text-slate-700 dark:text-slate-200">
            {(["premium", "standard", "basic"] as const).map((t) =>
              data.schools_by_tier[t] ? (
                <span
                  key={t}
                  className={`inline-block rounded-full px-2 py-0.5 text-xs mr-1.5 ${TIER_BADGE[t]}`}
                >
                  {t}: {data.schools_by_tier[t]}
                </span>
              ) : null,
            )}
          </p>
        </div>
      </div>

      {/* Per-school table */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
        <div className="overflow-x-auto">
          <table className="w-full text-sm" aria-label="Per-school revenue and plan">
            <thead>
              <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-100 dark:border-slate-700">
                <th scope="col" className="px-5 py-3 font-medium">
                  School
                </th>
                <th scope="col" className="px-3 py-3 font-medium">
                  Plan
                </th>
                <th scope="col" className="px-3 py-3 font-medium text-center">
                  Students
                </th>
                <th scope="col" className="px-3 py-3 font-medium text-right">
                  MRR
                </th>
                <th scope="col" className="px-3 py-3 font-medium text-right">
                  ARR
                </th>
                <th scope="col" className="px-5 py-3 font-medium text-right">
                  Collected
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {data.schools.map((s) => (
                <tr
                  key={s.id}
                  className="hover:bg-slate-50 dark:hover:bg-slate-700/40 cursor-pointer"
                  onClick={() => navigate(`/admin/platform/schools/${s.id}`)}
                >
                  <td className="px-5 py-3 text-slate-800 dark:text-slate-100">
                    <span className="font-medium">{s.name}</span>
                    <span className="ml-2 text-xs text-slate-400">{s.code}</span>
                    {!s.is_active && <span className="ml-2 text-xs text-red-500">inactive</span>}
                  </td>
                  <td className="px-3 py-3">
                    <span
                      className={`inline-block rounded-full px-2 py-0.5 text-xs font-semibold ${
                        TIER_BADGE[s.subscription_tier]
                      }`}
                    >
                      {s.subscription_tier}
                    </span>
                  </td>
                  <td className="px-3 py-3 text-center text-slate-600 dark:text-slate-300">
                    {s.student_count}
                  </td>
                  <td className="px-3 py-3 text-right text-slate-600 dark:text-slate-300">
                    {npr(s.mrr)}
                  </td>
                  <td className="px-3 py-3 text-right text-slate-600 dark:text-slate-300">
                    {npr(s.arr)}
                  </td>
                  <td className="px-5 py-3 text-right font-medium text-slate-800 dark:text-slate-100">
                    {npr(s.revenue)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
