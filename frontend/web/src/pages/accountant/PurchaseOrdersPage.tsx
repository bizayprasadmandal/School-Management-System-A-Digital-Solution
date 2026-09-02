/**
 * Accountant Purchase Orders Page — manage POs
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { EmptyState } from "../../components/common";
import { ClipboardDocumentListIcon } from "@heroicons/react/24/outline";

function POSkeleton() {
  return (
    <div className="space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 animate-pulse rounded-xl bg-slate-100 dark:bg-slate-800" />
      ))}
    </div>
  );
}

export default function PurchaseOrdersPage() {
  const { data: orders = [], isLoading } = useQuery({
    queryKey: ["accountant-pos"],
    queryFn: async () => {
      const r = await api.get<{ results: any[] }>("/fees/purchase-orders/");
      return r.results ?? [];
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Purchase Orders</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Manage purchase orders for school supplies
          </p>
        </div>
      </div>

      {isLoading ? (
        <POSkeleton />
      ) : orders.length === 0 ? (
        <EmptyState
          icon={ClipboardDocumentListIcon}
          title="No purchase orders"
          description="Create purchase orders for school supplies and services."
        />
      ) : (
        <div className="space-y-3">
          {orders.map((order: any) => (
            <div
              key={order.id}
              className="flex items-center justify-between rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div>
                <h3 className="font-semibold text-slate-900 dark:text-white">{order.po_number}</h3>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  {order.vendor ?? "—"} · {order.description ?? "—"}
                </p>
                <p className="text-xs text-slate-400">
                  {order.requested_by ?? "—"} ·{" "}
                  {order.created_at ? new Date(order.created_at).toLocaleDateString() : "—"}
                </p>
              </div>
              <div className="flex flex-col items-end gap-2">
                <p className="text-sm font-medium text-slate-900 dark:text-white">
                  ${(order.total_amount ?? 0).toLocaleString()}
                </p>
                <span
                  className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                    order.status === "approved" || order.status === "received"
                      ? "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
                      : order.status === "pending_approval"
                        ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
                        : order.status === "cancelled"
                          ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
                          : "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400"
                  }`}
                >
                  {(order.status ?? "draft").replace(/_/g, " ")}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
