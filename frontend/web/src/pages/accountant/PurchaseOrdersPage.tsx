import { useEffect, useState } from "react";
import { useAuthStore } from "../../store/authStore";
import { ClipboardDocumentListIcon } from "@heroicons/react/24/outline";

interface PurchaseOrder {
  id: string;
  po_number: string;
  vendor: string;
  description: string;
  total_amount: number;
  status: "draft" | "pending_approval" | "approved" | "ordered" | "received" | "cancelled";
  requested_by: string;
  created_at: string;
}

function POSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 rounded-xl bg-white/5" />
      ))}
    </div>
  );
}

export default function PurchaseOrdersPage() {
  const token = useAuthStore((s) => s.tokens?.access);
  const [orders, setOrders] = useState<PurchaseOrder[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const res = await fetch("/api/fees/purchase-orders/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setOrders(data.results ?? data);
        }
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    fetchOrders();
  }, [token]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Purchase Orders</h1>
        <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500">
          Create PO
        </button>
      </div>

      {loading ? (
        <POSkeleton />
      ) : orders.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-white/10 bg-white/5 py-16 text-center">
          <ClipboardDocumentListIcon className="mb-4 h-12 w-12 text-gray-500" />
          <h3 className="text-lg font-semibold text-white">No purchase orders</h3>
          <p className="mt-1 text-sm text-gray-400">
            Create purchase orders for school supplies and services.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {orders.map((order) => (
            <div
              key={order.id}
              className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4"
            >
              <div>
                <h3 className="font-semibold text-white">{order.po_number}</h3>
                <p className="text-sm text-gray-400">
                  {order.vendor} &middot; {order.description}
                </p>
                <p className="text-xs text-gray-500">
                  {order.requested_by} &middot; {new Date(order.created_at).toLocaleDateString()}
                </p>
              </div>
              <div className="flex flex-col items-end gap-2">
                <p className="text-sm font-medium text-white">
                  ${order.total_amount.toLocaleString()}
                </p>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium ${
                    order.status === "approved" || order.status === "received"
                      ? "bg-green-500/20 text-green-400"
                      : order.status === "pending_approval"
                        ? "bg-yellow-500/20 text-yellow-400"
                        : order.status === "cancelled"
                          ? "bg-red-500/20 text-red-400"
                          : "bg-blue-500/20 text-blue-400"
                  }`}
                >
                  {order.status.replace(/_/g, " ")}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
