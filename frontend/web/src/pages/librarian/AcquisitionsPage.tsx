/**
 * Librarian Acquisitions Page — track book purchases
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { ShoppingCartIcon } from "@heroicons/react/24/outline";

function AcquisitionSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-20 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function AcquisitionsPage() {
  const { data: items = [], isLoading } = useQuery({
    queryKey: ["librarian-acquisitions"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/library/acquisitions/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Acquisitions</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Track book and material purchase requests
          </p>
        </div>
      </div>

      {isLoading ? (
        <AcquisitionSkeleton />
      ) : items.length === 0 ? (
        <EmptyState
          icon={ShoppingCartIcon}
          title="No acquisitions"
          description="Request new books and materials for the library."
        />
      ) : (
        <div className="space-y-3">
          {items.map((item: any) => (
            <div
              key={item.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">{item.title}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">{item.author ?? "—"}</p>
                <p className="text-xs text-slate-400">
                  Qty: {item.quantity ?? 1} · ${item.unit_cost ?? "0.00"} ea ·{" "}
                  {item.requested_by ?? "—"}
                </p>
              </div>
              <span
                className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                  item.status === "received"
                    ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                    : item.status === "ordered"
                      ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                      : item.status === "cancelled"
                        ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                        : "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                }`}
              >
                {item.status}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
