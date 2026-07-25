/** Fines Management — Track overdue fines, collect payments, view fine history */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  BanknotesIcon, BookOpenIcon, CheckCircleIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, EmptyState, Modal, SkeletonCard } from "../../components/common";

interface Checkout {
  id: string;
  book: string;
  book_title: string;
  student: string;
  student_name: string;
  checked_out_at: string;
  due_date: string;
  returned_at: string | null;
  fine_amount: string;
  fine_paid: boolean;
  is_overdue: boolean;
  days_overdue: number;
}

export default function FinesPage() {
  const [filter, setFilter] = useState<"unpaid" | "paid" | "all">("unpaid");
  const [selectedFine, setSelectedFine] = useState<Checkout | null>(null);
  const qc = useQueryClient();

  const { data: checkouts = [], isLoading } = useQuery({
    queryKey: ["librarian-fines"],
    queryFn: async () => {
      const res = await api.get<{ results: Checkout[] }>("/library/checkouts/");
      return res.results ?? [];
    },
  });

  const payFineMut = useMutation({
    mutationFn: (id: string) => api.post(`/library/checkouts/${id}/pay_fine/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["librarian-fines"] });
      toast.success("Fine marked as paid");
      setSelectedFine(null);
    },
    onError: () => toast.error("Failed to process payment"),
  });

  // Only show checkouts that have a fine
  const fines = checkouts.filter(co => parseFloat(co.fine_amount) > 0);

  const filteredFines = filter === "all" ? fines
    : filter === "unpaid" ? fines.filter(f => !f.fine_paid)
    : fines.filter(f => f.fine_paid);

  const totalUnpaid = fines.filter(f => !f.fine_paid).reduce((s, f) => s + parseFloat(f.fine_amount), 0);
  const totalCollected = fines.filter(f => f.fine_paid).reduce((s, f) => s + parseFloat(f.fine_amount), 0);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Library Fines</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Track overdue fines and collect payments</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-xs text-slate-500 dark:text-slate-400">Total Fines</p>
          <p className="text-xl font-bold text-slate-900 dark:text-white">{fines.length}</p>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-xs text-slate-500 dark:text-slate-400">Unpaid Amount</p>
          <p className="text-xl font-bold text-red-600">${totalUnpaid.toFixed(2)}</p>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-xs text-slate-500 dark:text-slate-400">Collected</p>
          <p className="text-xl font-bold text-green-600">${totalCollected.toFixed(2)}</p>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
        {(["unpaid", "paid", "all"] as const).map(tab => (
          <button key={tab} onClick={() => setFilter(tab)}
            className={`px-4 py-2 rounded-md text-sm font-medium capitalize ${
              filter === tab
                ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
            }`}>
            {tab} ({tab === "all" ? fines.length : tab === "unpaid" ? fines.filter(f => !f.fine_paid).length : fines.filter(f => f.fine_paid).length})
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="space-y-3">{[1,2,3].map(i => <SkeletonCard key={i} />)}</div>
      ) : filteredFines.length === 0 ? (
        <EmptyState icon={BanknotesIcon} title="No fines"
          description={filter === "unpaid" ? "No outstanding fines. All books returned on time!" : "No fines match this filter."} />
      ) : (
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-800/80 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">
                  <th className="px-4 py-3">Student</th>
                  <th className="px-4 py-3">Book</th>
                  <th className="px-4 py-3">Due / Returned</th>
                  <th className="px-4 py-3">Days Overdue</th>
                  <th className="px-4 py-3">Fine Amount</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                {filteredFines.map(co => (
                  <tr key={co.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                    <td className="px-4 py-3">
                      <span className="font-medium text-slate-900 dark:text-white">{co.student_name}</span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <BookOpenIcon className="h-4 w-4 text-teal-500 flex-shrink-0" />
                        <span className="text-slate-600 dark:text-slate-400">{co.book_title}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-500 whitespace-nowrap">
                      <div>Due: {dayjs(co.due_date).format("MMM D, YYYY")}</div>
                      {co.returned_at && <div>Returned: {dayjs(co.returned_at).format("MMM D, YYYY")}</div>}
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-semibold text-red-600">{co.days_overdue} days</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="font-semibold text-slate-900 dark:text-white">
                        ${parseFloat(co.fine_amount).toFixed(2)}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      {co.fine_paid ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300">
                          <CheckCircleIcon className="h-3.5 w-3.5" /> Paid
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300">
                          Unpaid
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3">
                      {!co.fine_paid && (
                        <Button size="sm" variant="primary"
                          onClick={() => setSelectedFine(co)}>
                          <CheckCircleIcon className="h-3.5 w-3.5 mr-1" /> Collect
                        </Button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Payment confirmation modal */}
      <Modal open={!!selectedFine} onClose={() => setSelectedFine(null)}
        title="Collect Fine Payment">
        {selectedFine && (
          <div className="space-y-4">
            <div className="bg-slate-50 dark:bg-slate-700/50 rounded-lg p-4 space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-slate-500 dark:text-slate-400">Student</span>
                <span className="font-medium text-slate-900 dark:text-white">{selectedFine.student_name}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500 dark:text-slate-400">Book</span>
                <span className="font-medium text-slate-900 dark:text-white">{selectedFine.book_title}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-slate-500 dark:text-slate-400">Days Overdue</span>
                <span className="font-medium text-red-600">{selectedFine.days_overdue} days</span>
              </div>
              <div className="border-t border-slate-200 dark:border-slate-600 pt-2 mt-2">
                <div className="flex justify-between text-base">
                  <span className="font-semibold text-slate-800 dark:text-slate-200">Fine Amount</span>
                  <span className="font-bold text-slate-900 dark:text-white">${parseFloat(selectedFine.fine_amount).toFixed(2)}</span>
                </div>
              </div>
            </div>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Mark this fine as paid? This will record the payment in the system.
            </p>
            <div className="flex justify-end gap-3 pt-2">
              <Button variant="secondary" onClick={() => setSelectedFine(null)}>Cancel</Button>
              <Button onClick={() => payFineMut.mutate(selectedFine.id)}
                loading={payFineMut.isPending}>
                <CheckCircleIcon className="h-4 w-4 mr-1.5" /> Confirm Payment
              </Button>
            </div>
          </div>
        )}
      </Modal>
    </div>
  );
}
