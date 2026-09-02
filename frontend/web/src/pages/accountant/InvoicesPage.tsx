/**
 * Accountant Invoices Page — generate and manage student invoices
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { DocumentTextIcon } from "@heroicons/react/24/outline";

function InvoiceSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function InvoicesPage() {
  const { data: invoices = [], isLoading } = useQuery({
    queryKey: ["accountant-invoices"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/fees/invoices/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Invoices</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Generate and manage student invoices
          </p>
        </div>
      </div>

      {isLoading ? (
        <InvoiceSkeleton />
      ) : invoices.length === 0 ? (
        <EmptyState
          icon={DocumentTextIcon}
          title="No invoices"
          description="Generate and manage student invoices."
        />
      ) : (
        <div className="space-y-3">
          {invoices.map((inv: any) => (
            <div
              key={inv.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">
                  {inv.invoice_number}
                </h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {inv.student_name ?? "—"} · {inv.description ?? "—"}
                </p>
                <p className="text-xs text-slate-400">
                  Due: {inv.due_date ? new Date(inv.due_date).toLocaleDateString() : "—"}
                </p>
              </div>
              <div className="flex flex-col items-end gap-2">
                <p className="text-sm font-medium text-slate-900 dark:text-white">
                  ${(inv.amount ?? 0).toLocaleString()}
                </p>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    inv.status === "paid"
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : inv.status === "overdue"
                        ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                        : inv.status === "sent"
                          ? "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                          : "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-400"
                  }`}
                >
                  {inv.status}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
