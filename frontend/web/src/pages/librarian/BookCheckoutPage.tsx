/** Book Checkout/Return — Checkout books to students, return, and manage active loans */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  MagnifyingGlassIcon, BookOpenIcon,
  ArrowLeftOnRectangleIcon, ArrowRightOnRectangleIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, SkeletonCard } from "../../components/common";

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

function CheckoutFormModal({ open, onClose, onSaved }: {
  open: boolean; onClose: () => void; onSaved: () => void;
}) {
  const [bookId, setBookId] = useState("");
  const [studentId, setStudentId] = useState("");
  const [bookSearch, setBookSearch] = useState("");
  const [studentSearch, setStudentSearch] = useState("");
  const [dueDate, setDueDate] = useState(dayjs().add(14, "day").format("YYYY-MM-DD"));

  const { data: books = [] } = useQuery({
    queryKey: ["co-book-search", bookSearch],
    queryFn: async () => {
      if (bookSearch.length < 2) return [];
      const res = await api.get<{ results: any[] }>("/library/books/", { search: bookSearch, page_size: 10 });
      return res.results ?? [];
    },
    enabled: bookSearch.length >= 2,
  });

  const { data: students = [] } = useQuery({
    queryKey: ["co-student-search", studentSearch],
    queryFn: async () => {
      if (studentSearch.length < 2) return [];
      const res = await api.get<{ results: any[] }>("/students/students/", { search: studentSearch, page_size: 10 });
      return res.results ?? [];
    },
    enabled: studentSearch.length >= 2,
  });

  const checkoutMut = useMutation({
    mutationFn: () => api.post("/library/checkouts/", { book: bookId, student: studentId, due_date: dueDate }),
    onSuccess: () => { toast.success("Book checked out successfully!"); onSaved(); },
    onError: (err: any) => toast.error(err?.response?.data?.detail ?? "Checkout failed"),
  });

  return (
    <Modal open={open} onClose={onClose} title="Check Out Book">
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Book *</label>
          <input value={bookSearch} onChange={e => { setBookSearch(e.target.value); setBookId(""); }}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
            placeholder="Search by title, author, ISBN..." />
          {bookSearch.length >= 2 && !bookId && (
            <div className="mt-1 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 shadow-lg max-h-40 overflow-y-auto">
              {books.length === 0 ? (
                <p className="px-3 py-2 text-sm text-slate-400">No books found</p>
              ) : books.map((b: any) => (
                <button key={b.id} type="button" onClick={() => { setBookId(b.id); setBookSearch(`${b.title} — ${b.author}`); }}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-700 dark:text-slate-200 border-b border-slate-100 dark:border-slate-700 last:border-0">
                  <div className="flex justify-between items-center">
                    <span className="font-medium">{b.title}</span>
                    <span className={`text-xs font-semibold ${b.available_copies > 0 ? "text-green-600" : "text-red-500"}`}>
                      {b.available_copies}/{b.total_copies} avail.
                    </span>
                  </div>
                  <span className="text-xs text-slate-400">{b.author}</span>
                </button>
              ))}
            </div>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Student *</label>
          <input value={studentSearch} onChange={e => { setStudentSearch(e.target.value); setStudentId(""); }}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200"
            placeholder="Search student name..." />
          {studentSearch.length >= 2 && !studentId && (
            <div className="mt-1 border border-slate-200 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 shadow-lg max-h-40 overflow-y-auto">
              {students.length === 0 ? (
                <p className="px-3 py-2 text-sm text-slate-400">No students found</p>
              ) : students.map((s: any) => (
                <button key={s.id} type="button" onClick={() => { setStudentId(s.id); setStudentSearch(s.full_name ?? s.user?.full_name); }}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-700 dark:text-slate-200 border-b border-slate-100 dark:border-slate-700 last:border-0">
                  {s.full_name ?? s.user?.full_name}
                  <span className="text-xs text-slate-400 ml-2">{s.admission_number || s.classroom?.name || ""}</span>
                </button>
              ))}
            </div>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Due Date</label>
          <input type="date" value={dueDate} onChange={e => setDueDate(e.target.value)}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button onClick={() => checkoutMut.mutate()} loading={checkoutMut.isPending}
            disabled={!bookId || !studentId}>
            <ArrowLeftOnRectangleIcon className="h-4 w-4 mr-1.5" /> Check Out
          </Button>
        </div>
      </div>
    </Modal>
  );
}

export default function BookCheckoutPage() {
  const [showCheckoutForm, setShowCheckoutForm] = useState(false);
  const [filter, setFilter] = useState<"all" | "active" | "overdue" | "returned">("active");
  const qc = useQueryClient();

  const { data: checkouts = [], isLoading } = useQuery({
    queryKey: ["librarian-checkouts"],
    queryFn: async () => {
      const res = await api.get<{ results: Checkout[] }>("/library/checkouts/");
      return res.results ?? [];
    },
  });

  const returnMut = useMutation({
    mutationFn: (id: string) => api.post(`/library/checkouts/${id}/return/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["librarian-checkouts"] });
      qc.invalidateQueries({ queryKey: ["librarian-books"] });
      toast.success("Book returned successfully");
    },
    onError: () => toast.error("Failed to return book"),
  });

  const filtered = filter === "all" ? checkouts
    : filter === "active" ? checkouts.filter(c => !c.returned_at && !c.is_overdue)
    : filter === "overdue" ? checkouts.filter(c => !c.returned_at && c.is_overdue)
    : checkouts.filter(c => c.returned_at);

  const activeCount = checkouts.filter(c => !c.returned_at).length;
  const overdueCount = checkouts.filter(c => !c.returned_at && c.is_overdue).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Checkouts</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage book loans and returns</p>
        </div>
        <Button onClick={() => setShowCheckoutForm(true)}>
          <ArrowLeftOnRectangleIcon className="h-4 w-4 mr-1.5" /> Check Out
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-xs text-slate-500 dark:text-slate-400">Active Loans</p>
          <p className="text-xl font-bold text-indigo-600">{activeCount}</p>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-xs text-slate-500 dark:text-slate-400">Overdue</p>
          <p className="text-xl font-bold text-red-600">{overdueCount}</p>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-xs text-slate-500 dark:text-slate-400">Returned</p>
          <p className="text-xl font-bold text-green-600">{checkouts.filter(c => c.returned_at).length}</p>
        </div>
      </div>

      {/* Filter tabs */}
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
        {(["active", "overdue", "all", "returned"] as const).map(tab => (
          <button key={tab} onClick={() => setFilter(tab)}
            className={`px-4 py-2 rounded-md text-sm font-medium capitalize ${
              filter === tab
                ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm"
                : "text-slate-600 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-200"
            }`}>
            {tab} ({tab === "all" ? checkouts.length : tab === "active" ? activeCount : tab === "overdue" ? overdueCount : checkouts.filter(c => c.returned_at).length})
          </button>
        ))}
      </div>

      {/* Checkout list */}
      {isLoading ? (
        <div className="space-y-3">{[1,2,3].map(i => <SkeletonCard key={i} />)}</div>
      ) : filtered.length === 0 ? (
        <EmptyState icon={BookOpenIcon} title="No checkouts" description={filter === "active" ? "No active loans. Check out a book to get started." : "No checkouts match this filter."} />
      ) : (
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 dark:bg-slate-800/80 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">
                  <th className="px-4 py-3">Book</th>
                  <th className="px-4 py-3">Student</th>
                  <th className="px-4 py-3">Checked Out</th>
                  <th className="px-4 py-3">Due Date</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Fine</th>
                  <th className="px-4 py-3"></th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                {filtered.map(co => (
                  <tr key={co.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-2">
                        <BookOpenIcon className="h-4 w-4 text-teal-500 flex-shrink-0" />
                        <span className="font-medium text-slate-900 dark:text-white">{co.book_title}</span>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{co.student_name}</td>
                    <td className="px-4 py-3 text-slate-500 whitespace-nowrap">
                      {dayjs(co.checked_out_at).format("MMM D, YYYY")}
                    </td>
                    <td className="px-4 py-3 text-slate-500 whitespace-nowrap">
                      {dayjs(co.due_date).format("MMM D, YYYY")}
                    </td>
                    <td className="px-4 py-3">
                      {co.returned_at ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300">
                          Returned {dayjs(co.returned_at).format("MMM D")}
                        </span>
                      ) : co.is_overdue ? (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300">
                          Overdue {co.days_overdue}d
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300">
                          Active
                        </span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-slate-500 whitespace-nowrap">
                      {parseFloat(co.fine_amount) > 0 ? (
                        <span className={co.fine_paid ? "text-green-600 font-medium" : "text-red-500 font-medium"}>
                          ${co.fine_amount} {co.fine_paid ? "(paid)" : "(unpaid)"}
                        </span>
                      ) : "—"}
                    </td>
                    <td className="px-4 py-3">
                      {!co.returned_at && (
                        <Button size="sm" variant="secondary"
                          onClick={() => returnMut.mutate(co.id)}
                          loading={returnMut.isPending}>
                          <ArrowRightOnRectangleIcon className="h-3.5 w-3.5 mr-1" /> Return
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

      {showCheckoutForm && (
        <CheckoutFormModal open={showCheckoutForm} onClose={() => setShowCheckoutForm(false)}
          onSaved={() => {
            setShowCheckoutForm(false);
            qc.invalidateQueries({ queryKey: ["librarian-checkouts"] });
            qc.invalidateQueries({ queryKey: ["librarian-books"] });
          }} />
      )}
    </div>
  );
}
