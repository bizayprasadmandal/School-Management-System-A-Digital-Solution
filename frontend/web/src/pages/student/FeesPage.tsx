/**
 * Student Fees Page — View fee invoices and pay online with Nepali gateways
 */

import React, { useState } from "react";
import {
  BanknotesIcon,
  CheckCircleIcon,
  ClockIcon,
  CreditCardIcon,
} from "@heroicons/react/24/outline";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { useStudentInvoices } from "../../api/hooks";
import { Badge, EmptyState, SkeletonCard, ErrorState } from "../../components/common";
import PayFeePickerModal from "../../components/common/PayFeePickerModal";
import { npr, FEE_STATUS, fmt } from "../../utils";
import { useTitle } from "../../hooks";
import dayjs from "dayjs";
import type { FeeInvoice } from "../../types";

export default function StudentFeesPage() {
  useTitle("My Fees");

  const [payingInvoice, setPayingInvoice] = useState<FeeInvoice | null>(null);

  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ["student-me-fees"],
    queryFn: () => api.get<{ id: string }>("/students/me/"),
  });

  const {
    data: invData,
    isLoading: invLoading,
    isError,
    refetch,
  } = useStudentInvoices(profile?.id ?? "");

  const invoices = invData?.results ?? [];
  const isLoading = profileLoading || invLoading;

  const totalDue = invoices
    .filter((i) => ["unpaid", "overdue", "partial"].includes(i.status))
    .reduce((s, i) => s + Number(i.outstanding_amount), 0);

  const totalPaid = invoices.reduce(
    (s, i) => s + Number(i.paid_amount),
    0,
  );

  if (isLoading) {
    return (
      <div className="space-y-4">
        <div className="h-8 w-48 rounded-lg bg-slate-200 animate-pulse" />
        <div className="grid grid-cols-3 gap-4">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
        <SkeletonCard />
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-4">
        <ErrorState
          title="Failed to load fee data"
          onRetry={() => refetch()}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">My Fees</h1>
        <p className="text-sm text-slate-500 mt-1">
          Payment history and outstanding balances
        </p>
      </div>

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
            className="bg-white rounded-2xl border border-slate-100 shadow-sm p-4 flex items-center gap-3"
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

      {/* Outstanding alert */}
      {totalDue > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-amber-800">
              Outstanding Balance
            </p>
            <p className="text-xs text-amber-600 mt-0.5">
              Please pay {npr(totalDue)} to avoid late penalties.
            </p>
          </div>
          <span className="text-lg font-bold text-amber-800">
            {npr(totalDue)}
          </span>
        </div>
      )}

      {/* Invoice history */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm overflow-hidden">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between">
          <h2 className="text-base font-semibold">Invoice History</h2>
        </div>

        {invoices.length === 0 ? (
          <div className="p-8">
            <EmptyState
              icon={BanknotesIcon}
              title="No invoices yet"
              description="Your fee invoices will appear here once generated."
            />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-100">
              <thead className="bg-slate-50">
                <tr>
                  {[
                    "Invoice #",
                    "Due Date",
                    "Total",
                    "Paid",
                    "Outstanding",
                    "Status",
                    "",
                  ].map((h) => (
                    <th
                      key={h}
                      className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide"
                    >
                      {h}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-50 bg-white">
                {invoices.map((inv: FeeInvoice) => {
                  const isOverdue =
                    dayjs(inv.due_date).isBefore(dayjs()) &&
                    inv.status !== "paid";
                  const canPay = ["unpaid", "overdue", "partial"].includes(
                    inv.status,
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
                          <button
                            onClick={() => setPayingInvoice(inv)}
                            className="inline-flex items-center gap-1.5 rounded-xl bg-indigo-600 px-3 py-2 text-xs font-semibold text-white shadow-sm transition-all hover:bg-indigo-700 active:bg-indigo-800"
                          >
                            <CreditCardIcon className="h-3.5 w-3.5" />
                            Pay Now
                          </button>
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

      {/* Unified Payment Modal — Stripe, Khalti, or eSewa */}
      {payingInvoice && (
        <PayFeePickerModal
          invoice={payingInvoice}
          open={!!payingInvoice}
          onClose={() => setPayingInvoice(null)}
          onSuccess={() => {
            setPayingInvoice(null);
            refetch();
          }}
        />
      )}
    </div>
  );
}
