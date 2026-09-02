/**
 * Accountant Budget Page — manage department budgets with progress tracking
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { ChartBarIcon } from "@heroicons/react/24/outline";

function BudgetSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function BudgetPage() {
  const { data: budgets = [], isLoading } = useQuery({
    queryKey: ["accountant-budgets"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/fees/budgets/");
      return r.results ?? [];
    },
  });

  const totalAllocated = budgets.reduce((sum: number, b: any) => sum + (b.allocated ?? 0), 0);
  const totalSpent = budgets.reduce((sum: number, b: any) => sum + (b.spent ?? 0), 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Budget Management</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Track department budgets and spending
          </p>
        </div>
      </div>

      {!isLoading && budgets.length > 0 && (
        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
            <p className="text-sm text-slate-500 dark:text-slate-400">Total Allocated</p>
            <p className="text-2xl font-bold text-slate-900 dark:text-white">
              ${totalAllocated.toLocaleString()}
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
            <p className="text-sm text-slate-500 dark:text-slate-400">Total Spent</p>
            <p className="text-2xl font-bold text-red-600 dark:text-red-400">
              ${totalSpent.toLocaleString()}
            </p>
          </div>
          <div className="rounded-xl border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-800">
            <p className="text-sm text-slate-500 dark:text-slate-400">Remaining</p>
            <p className="text-2xl font-bold text-green-600 dark:text-green-400">
              ${(totalAllocated - totalSpent).toLocaleString()}
            </p>
          </div>
        </div>
      )}

      {isLoading ? (
        <BudgetSkeleton />
      ) : budgets.length === 0 ? (
        <EmptyState
          icon={ChartBarIcon}
          title="No budget data"
          description="Set up budgets for different departments and categories."
        />
      ) : (
        <div className="space-y-3">
          {budgets.map((b: any) => {
            const pct = b.allocated > 0 ? (b.spent / b.allocated) * 100 : 0;
            return (
              <div
                key={b.id}
                className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-slate-900 dark:text-white">{b.category}</h3>
                    <p className="text-sm text-slate-500 dark:text-slate-400">
                      {b.department ?? "—"}
                    </p>
                    <p className="text-xs text-slate-400">{b.fiscal_year ?? "—"}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-slate-900 dark:text-white">
                      ${(b.spent ?? 0).toLocaleString()} / ${(b.allocated ?? 0).toLocaleString()}
                    </p>
                    <p className="text-xs text-slate-400">
                      ${(b.remaining ?? 0).toLocaleString()} remaining
                    </p>
                  </div>
                </div>
                <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100 dark:bg-slate-700">
                  <div
                    className={`h-full rounded-full ${
                      pct > 90 ? "bg-red-500" : pct > 70 ? "bg-amber-500" : "bg-green-500"
                    }`}
                    style={{ width: `${Math.min(pct, 100)}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
