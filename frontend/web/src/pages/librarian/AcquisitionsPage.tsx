import { useEffect, useState } from "react";
import { useAuthStore } from "../../store/authStore";
import { ShoppingCartIcon } from "@heroicons/react/24/outline";

interface Acquisition {
  id: string;
  title: string;
  author: string;
  quantity: number;
  unit_cost: number;
  status: "requested" | "ordered" | "received" | "cancelled";
  requested_by: string;
  requested_at: string;
}

function AcquisitionSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 rounded-xl bg-white/5" />
      ))}
    </div>
  );
}

export default function AcquisitionsPage() {
  const token = useAuthStore((s) => s.tokens?.access);
  const [items, setItems] = useState<Acquisition[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAcquisitions = async () => {
      try {
        const res = await fetch("/api/library/acquisitions/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setItems(data.results ?? data);
        }
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    fetchAcquisitions();
  }, [token]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Acquisitions</h1>
        <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500">
          New Request
        </button>
      </div>

      {loading ? (
        <AcquisitionSkeleton />
      ) : items.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-white/10 bg-white/5 py-16 text-center">
          <ShoppingCartIcon className="mb-4 h-12 w-12 text-gray-500" />
          <h3 className="text-lg font-semibold text-white">No acquisitions</h3>
          <p className="mt-1 text-sm text-gray-400">
            Request new books and materials for the library.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {items.map((item) => (
            <div
              key={item.id}
              className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4"
            >
              <div>
                <h3 className="font-semibold text-white">{item.title}</h3>
                <p className="text-sm text-gray-400">{item.author}</p>
                <p className="text-xs text-gray-500">
                  Qty: {item.quantity} &middot; ${item.unit_cost} ea &middot; {item.requested_by}
                </p>
              </div>
              <span
                className={`rounded-full px-3 py-1 text-xs font-medium ${
                  item.status === "requested"
                    ? "bg-yellow-500/20 text-yellow-400"
                    : item.status === "ordered"
                      ? "bg-blue-500/20 text-blue-400"
                      : item.status === "received"
                        ? "bg-green-500/20 text-green-400"
                        : "bg-red-500/20 text-red-400"
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
