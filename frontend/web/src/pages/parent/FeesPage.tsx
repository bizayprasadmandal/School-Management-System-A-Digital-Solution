/**
 * Parent Fees Page — view fee invoices and pay online with Nepali gateways
 */
import React, { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Badge, Button, EmptyState, SkeletonCard } from "../../components/common";
import NepaliPayModal from "../../components/common/NepaliPayModal";
import { npr, FEE_STATUS, fmt } from "../../utils";
import { useTitle } from "../../hooks";
import type { StudentListItem, FeeInvoice, PaginatedResponse } from "../../types";
import {
  BanknotesIcon,
  CheckCircleIcon,
  ClockIcon,
  CreditCardIcon,
} from "@heroicons/react/24/outline";
import dayjs from "dayjs";

export default function ParentFeesPage() {
  useTitle("Fee Management");
  const qc = useQueryClient();
  const [childIdx, setChildIdx] = useState(0);
  const [payingInvoice, setPayingInvoice] = useState<FeeInvoice | null>(null);

  const { data: children, isLoading: childrenLoading } = useQuery({
    queryKey: ["parent-children-fees"],
    queryFn: () => api.get<PaginatedResponse<StudentListItem>>("/students/"),
  });
  const childList = children?.results ?? [];
  const child = childList[childIdx];

  const { data: invData, isLoading: invLoading } = useQuery({
    queryKey: ["parent-child-inv", child?.id],
    queryFn: () => api.get<PaginatedResponse<FeeInvoice>>(`/fees/invoices/?student=${child.id}`),
    enabled: !!child?.id,
  });
  const invoices = invData?.results ?? [];
  const totalDue = invoices
    .filter((i: FeeInvoice) => ["unpaid", "overdue", "partial"].includes(i.status))
    .reduce((s: number, i: FeeInvoice) => s + Number(i.outstanding_amount), 0);
  const totalPaid = invoices.reduce(
    (s: number, i: FeeInvoice) => s + Number(i.paid_amount),
    0
  );

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Fee Management</h1>
        <p className="text-sm text-slate-500 mt-1">
          Track fee invoices and pay online securely
        </p>
      </div>

      {childList.length > 1 && (
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-4 flex gap-2 overflow-x-auto">
          {childList.map((c: StudentListItem, i: number) => (
            <button
              key={c.id}
              onClick={() => setChildIdx(i)}
              className={`flex-shrink-0 rounded-xl px-4 py-2 text-sm font-semibold transition-colors ${
                i === childIdx
                  ? "bg-violet-600 text-white"
                  : "bg-slate-100 text-slate-600 hover:bg-slate-200"
              }`}
            >
              {c.full_name}
            </button>
          ))}
        </div>
      )}

      {childrenLoading || invLoading ? (
        <div className="p-4">
          <SkeletonCard />
        </div>
      ) : (
        <>
          {/* Summary cards */}
          <div className="grid grid-cols-3 gap-4">
            {[
              {
                label: "Total Paid",
                value: npr(totalPaid),
                icon: CheckCircleIcon,
                color: "text-green-600 bg-green-50",
              },
              {
                label: "Outstanding",
                value: npr(totalDue),
                icon: ClockIcon,
                color:
                  totalDue > 0
                    ? "text-red-600 bg-red-50"
                    : "text-slate-500 bg-slate-50",
              },
              {
                label: "Invoices",
                value: invoices.length,
                icon: BanknotesIcon,
                color: "text-indigo-600 bg-indigo-50",
              },
            ].map(({ label, value, icon: Icon, color }) => (
              <div
                key={label}
                className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-4 flex items-center gap-3"
              >
                <div
                  className={`h-10 w-10 rounded-xl flex items-center justify-center flex-shrink-0 ${
                    color.split(" ")[1]
                  }`}
                >
                  <Icon className={`h-5 w-5 ${color.split(" ")[0]}`} />
                </div>
                <div>
                  <p className={`text-xl font-bold ${color.split(" ")[0]}`}>
                    {value}
                  </p>
                  <p className="text-xs text-slate-500">{label}</p>
                </div>
              </div>
            ))}
          </div>

          {totalDue > 0 && (
            <div className="rounded-xl border border-amber-200 bg-amber-50 p-4">
              <p className="text-sm font-semibold text-amber-800">
                Payment Required
              </p>
              <p className="text-xs text-amber-700 mt-0.5">
                {npr(totalDue)} outstanding. Pay online with Khalti or eSewa.
              </p>
            </div>
          )}

          {/* Invoice history with Pay Now button */}
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden">
            <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between dark:border-slate-700">
              <h2 className="text-base font-semibold">Invoice History</h2>
            </div>
            {invoices.length === 0 ? (
              <div className="p-8">
                <EmptyState
                  icon={BanknotesIcon}
                  title="No invoices yet"
                  description="Fee invoices for your child appear here."
                />
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-100">
                  <thead className="bg-slate-50">
                    <tr>
                      {["Invoice #", "Due Date", "Total", "Paid", "Outstanding", "Status", ""].map(
                        (h) => (
                          <th
                            key={h}
                            className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide"
                          >
                            {h}
                          </th>
                        )
                      )}
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50 bg-white">
                    {invoices.map((inv: FeeInvoice) => {
                      const isOverdue =
                        dayjs(inv.due_date).isBefore(dayjs()) &&
                        inv.status !== "paid";
                      const canPay = ["unpaid", "overdue", "partial"].includes(
                        inv.status
                      );
                      const s = FEE_STATUS[inv.status];
                      return (
                        <tr
                          key={inv.id}
                          className="hover:bg-slate-50/60 transition-colors"
                        >
                          <td className="px-4 py-3 text-sm font-mono text-slate-700">
                            {inv.invoice_number}
                          </td>
                          <td
                            className={`px-4 py-3 text-sm ${
                              isOverdue
                                ? "text-red-600 font-medium"
                                : "text-slate-600"
                            }`}
                          >
                            {fmt.date(inv.due_date)}
                          </td>
                          <td className="px-4 py-3 text-sm text-slate-700">
                        {npr(inv.total_amount)}
                      </td>
                      <td className="px-4 py-3 text-sm text-green-600">
                        {npr(inv.paid_amount)}
                      </td>
                      <td className="px-4 py-3 text-sm">
                        {Number(inv.outstanding_amount) > 0 ? (
                          <span className="text-red-600 font-semibold">
                            {npr(inv.outstanding_amount)}
                              </span>
                            ) : (
                              <span className="text-slate-400">—</span>
                            )}
                          </td>
                          <td className="px-4 py-3 text-sm">
                            <Badge color={s?.color ?? "slate"}>
                              {s?.label ?? inv.status}
                            </Badge>
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {canPay ? (
                              <Button
                                variant="primary"
                                size="sm"
                                onClick={() => setPayingInvoice(inv)}
                                leftIcon={<CreditCardIcon className="h-4 w-4" />}
                                className="bg-violet-600 hover:bg-violet-700 whitespace-nowrap"
                              >
                                Pay Now
                              </Button>
                            ) : null}
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}              {/* Nepali Payment Modal */}
              {payingInvoice && (
                <NepaliPayModal
                  invoice={payingInvoice}
                  open={!!payingInvoice}
                  onClose={() => setPayingInvoice(null)}
                  onSuccess={() => {
                    qc.invalidateQueries({ queryKey: ["parent-child-inv", child?.id] });
                    setPayingInvoice(null);
                  }}
                />
              )}
    </div>
  );
}
