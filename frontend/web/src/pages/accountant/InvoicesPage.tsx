import { useEffect, useState } from "react";
import { useAuthStore } from "../../store/authStore";
import { DocumentTextIcon } from "@heroicons/react/24/outline";

interface Invoice {
  id: string;
  invoice_number: string;
  student_name: string;
  description: string;
  amount: number;
  due_date: string;
  status: "draft" | "sent" | "paid" | "overdue" | "cancelled";
  issued_at: string;
}

function InvoiceSkeleton() {
  return (
    <div className="animate-pulse space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="h-24 rounded-xl bg-white/5" />
      ))}
    </div>
  );
}

export default function InvoicesPage() {
  const token = useAuthStore((s) => s.tokens?.access);
  const [invoices, setInvoices] = useState<Invoice[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchInvoices = async () => {
      try {
        const res = await fetch("/api/fees/invoices/", {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setInvoices(data.results ?? data);
        }
      } catch {
        // ignore
      } finally {
        setLoading(false);
      }
    };
    fetchInvoices();
  }, [token]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white">Invoices</h1>
        <button className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-500">
          Create Invoice
        </button>
      </div>

      {loading ? (
        <InvoiceSkeleton />
      ) : invoices.length === 0 ? (
        <div className="flex flex-col items-center justify-center rounded-xl border border-white/10 bg-white/5 py-16 text-center">
          <DocumentTextIcon className="mb-4 h-12 w-12 text-gray-500" />
          <h3 className="text-lg font-semibold text-white">No invoices</h3>
          <p className="mt-1 text-sm text-gray-400">Generate and manage student invoices.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {invoices.map((inv) => (
            <div
              key={inv.id}
              className="flex items-center justify-between rounded-xl border border-white/10 bg-white/5 p-4"
            >
              <div>
                <h3 className="font-semibold text-white">{inv.invoice_number}</h3>
                <p className="text-sm text-gray-400">
                  {inv.student_name} &middot; {inv.description}
                </p>
                <p className="text-xs text-gray-500">
                  Due: {new Date(inv.due_date).toLocaleDateString()}
                </p>
              </div>
              <div className="flex flex-col items-end gap-2">
                <p className="text-sm font-medium text-white">${inv.amount.toLocaleString()}</p>
                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium ${
                    inv.status === "paid"
                      ? "bg-green-500/20 text-green-400"
                      : inv.status === "overdue"
                        ? "bg-red-500/20 text-red-400"
                        : inv.status === "sent"
                          ? "bg-blue-500/20 text-blue-400"
                          : "bg-gray-500/20 text-gray-400"
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
