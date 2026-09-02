import { useEffect, useState } from "react";
import { useAuthStore } from "../../store/authStore";
import { ChartBarIcon } from "@heroicons/react/24/outline";

interface BudgetItem {
  id: string;
  category: string;
  allocated: number;
  spent: number;
  remaining: number;
  fiscal_year: string;
  department: string;
}

function BudgetSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 rounded-xl bg-white/5" />
      ))}
    </div>
  );
}

export default function BudgetPage() {
  const token = useAuthStore((s) => s.tokens?.access);
  const [budgets, setBudgets] = useState<BudgetItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchBudgets = async () => {
      try {
        const res = await fetch("/api/fees/budgets/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setBudgets(data.results ?? data);
        }
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    fetchBudgets();
  }, [token]);

  const totalAllocated = budgets.reduce((sum, b) => sum + b.allocated, 0);
  const totalSpent = budgets.reduce((sum, b) => sum + b.spent, 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Budget Management</h1>
        <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500">
          Add Budget
        </button>
      </div>

      {!loading && budgets.length > 0 && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-white/10 bg-white/5 p-4">
            <p className="text-sm text-gray-400">Total Allocated</p>
            <p className="text-2xl font-bold text-white">${totalAllocated.toLocaleString()}</p>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 p-4">
            <p className="text-sm text-gray-400">Total Spent</p>
            <p className="text-2xl font-bold text-red-400">${totalSpent.toLocaleString()}</p>
          </div>
          <div className="rounded-xl border border-white/10 bg-white/5 p-4">
            <p className="text-sm text-gray-400">Remaining</p>
            <p className="text-2xl font-bold text-green-400">
              ${(totalAllocated - totalSpent).toLocaleString()}
            </p>
          </div>
        </div>
      )}

      {loading ? (
        <BudgetSkeleton />
      ) : budgets.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-white/10 bg-white/5 py-16 text-center">
          <ChartBarIcon className="mb-4 h-12 w-12 text-gray-500" />
          <h3 className="text-lg font-semibold text-white">No budget data</h3>
          <p className="mt-1 text-sm text-gray-400">
            Set up budgets for different departments and categories.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {budgets.map((b) => {
            const pct = b.allocated > 0 ? (b.spent / b.allocated) * 100 : 0;
            return (
              <div key={b.id} className="rounded-xl border border-white/10 bg-white/5 p-4">
                <div className="flex items-start justify-between">
                  <div>
                    <h3 className="font-semibold text-white">{b.category}</h3>
                    <p className="text-sm text-gray-400">{b.department}</p>
                    <p className="text-xs text-gray-500">{b.fiscal_year}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-white">
                      ${b.spent.toLocaleString()} / ${b.allocated.toLocaleString()}
                    </p>
                    <p className="text-xs text-gray-500">
                      ${b.remaining.toLocaleString()} remaining
                    </p>
                  </div>
                </div>
                <div className="mt-3 h-2 overflow-hidden rounded-full bg-white/10">
                  <div
                    className={`h-full rounded-full ${
                      pct > 90 ? "bg-red-500" : pct > 70 ? "bg-yellow-500" : "bg-green-500"
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
