/** Library Management — Book catalog, checkout/return, fine tracking */

import React, { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import dayjs from "dayjs";
import {
  PlusIcon, MagnifyingGlassIcon, BookOpenIcon,
  ArrowLeftOnRectangleIcon, ArrowRightOnRectangleIcon,
  PencilIcon, XCircleIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState } from "../../components/common";

interface Book {
  id: string;
  title: string;
  author: string;
  isbn: string;
  category: string;
  total_copies: number;
  available_copies: number;
  publisher: string;
  shelf_location: string;
  is_active: boolean;
}

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

function BookFormModal({ open, onClose, book, onSaved }: {
  open: boolean; onClose: () => void; book?: Book | null; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    title: book?.title ?? "",
    author: book?.author ?? "",
    isbn: book?.isbn ?? "",
    category: book?.category ?? "",
    publisher: book?.publisher ?? "",
    shelf_location: book?.shelf_location ?? "",
    total_copies: book?.total_copies ?? 1,
  });

  const isEdit = !!book;
  const createMut = useMutation({
    mutationFn: (d: typeof form) => api.post("/library/books/", { ...d, available_copies: d.total_copies }),
    onSuccess: () => { toast.success("Book added"); onSaved(); },
  });
  const updateMut = useMutation({
    mutationFn: (d: typeof form) => api.patch(`/library/books/${book!.id}/`, d),
    onSuccess: () => { toast.success("Book updated"); onSaved(); },
  });
  const isSaving = createMut.isPending || updateMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.title.trim() || !form.author.trim()) return toast.error("Title and author are required");
    if (isEdit) updateMut.mutate(form);
    else createMut.mutate(form);
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Book" : "Add New Book"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <div className="col-span-2">
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Title *</label>
            <input value={form.title} onChange={e => setForm(p => ({ ...p, title: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Author *</label>
            <input value={form.author} onChange={e => setForm(p => ({ ...p, author: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">ISBN</label>
            <input value={form.isbn} onChange={e => setForm(p => ({ ...p, isbn: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Category</label>
            <input value={form.category} onChange={e => setForm(p => ({ ...p, category: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" placeholder="Fiction, Reference..." />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Publisher</label>
            <input value={form.publisher} onChange={e => setForm(p => ({ ...p, publisher: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Shelf Location</label>
            <input value={form.shelf_location} onChange={e => setForm(p => ({ ...p, shelf_location: e.target.value }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Total Copies</label>
            <input type="number" min={1} value={form.total_copies} onChange={e => setForm(p => ({ ...p, total_copies: Math.max(1, parseInt(e.target.value) || 1) }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Add"} Book</Button>
        </div>
      </form>
    </Modal>
  );
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
    queryKey: ["library-book-search", bookSearch],
    queryFn: async () => {
      if (bookSearch.length < 2) return [];
      const res = await api.get<{ results: Book[] }>("/library/books/", { search: bookSearch, page_size: 10 });
      return res.results ?? [];
    },
    enabled: bookSearch.length >= 2,
  });

  const { data: students = [] } = useQuery({
    queryKey: ["student-search", studentSearch],
    queryFn: async () => {
      if (studentSearch.length < 2) return [];
      const res = await api.get<{ results: any[] }>("/students/students/", { search: studentSearch, page_size: 10 });
      return res.results ?? [];
    },
    enabled: studentSearch.length >= 2,
  });

  const checkoutMut = useMutation({
    mutationFn: () => api.post("/library/checkouts/", { book: bookId, student: studentId, due_date: dueDate }),
    onSuccess: () => { toast.success("Book checked out"); onSaved(); },
    onError: (err: any) => toast.error(err?.response?.data?.detail ?? "Checkout failed"),
  });

  return (
    <Modal open={open} onClose={onClose} title="Check Out Book">
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Book *</label>
          <input value={bookSearch} onChange={e => { setBookSearch(e.target.value); setBookId(""); }}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" placeholder="Search book..." required />
          {bookSearch.length >= 2 && !bookId && books.length > 0 && (
            <div className="mt-1 border border-slate-200 rounded-lg bg-white dark:bg-slate-800 shadow-lg max-h-32 overflow-y-auto">
              {books.map((b: any) => (
                <button key={b.id} type="button" onClick={() => { setBookId(b.id); setBookSearch(b.title); }}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-700 dark:text-slate-200">{b.title} — {b.author} ({b.available_copies} available)</button>
              ))}
            </div>
          )}
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Student *</label>
          <input value={studentSearch} onChange={e => { setStudentSearch(e.target.value); setStudentId(""); }}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" placeholder="Search student..." required />
          {studentSearch.length >= 2 && !studentId && students.length > 0 && (
            <div className="mt-1 border border-slate-200 rounded-lg bg-white dark:bg-slate-800 shadow-lg max-h-32 overflow-y-auto">
              {students.map((s: any) => (
                <button key={s.id} type="button" onClick={() => { setStudentId(s.id); setStudentSearch(s.full_name ?? s.user?.full_name); }}
                  className="w-full text-left px-3 py-2 text-sm hover:bg-slate-50 dark:hover:bg-slate-700 dark:text-slate-200">{s.full_name ?? s.user?.full_name}</button>
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
          <Button onClick={() => checkoutMut.mutate()} loading={checkoutMut.isPending} disabled={!bookId || !studentId}>Check Out</Button>
        </div>
      </div>
    </Modal>
  );
}

export default function LibraryPage() {
  const [activeTab, setActiveTab] = useState<"catalog" | "checkouts">("catalog");
  const [search, setSearch] = useState("");
  const [showBookForm, setShowBookForm] = useState(false);
  const [showCheckoutForm, setShowCheckoutForm] = useState(false);
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const qc = useQueryClient();

  const { data: books = [], isLoading } = useQuery({
    queryKey: ["library-books"],
    queryFn: async () => {
      const res = await api.get<{ results: Book[] }>("/library/books/");
      return res.results ?? [];
    },
  });

  const { data: checkouts = [] } = useQuery({
    queryKey: ["library-checkouts"],
    queryFn: async () => {
      const res = await api.get<{ results: Checkout[] }>("/library/checkouts/");
      return res.results ?? [];
    },
  });

  const returnMut = useMutation({
    mutationFn: (id: string) => api.post(`/library/checkouts/${id}/return/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["library-checkouts"] }); qc.invalidateQueries({ queryKey: ["library-books"] }); toast.success("Book returned"); },
  });

  const deleteBookMut = useMutation({
    mutationFn: (id: string) => api.delete(`/library/books/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["library-books"] }); toast.success("Book removed"); },
  });

  const filteredBooks = useMemo(() => {
    if (!search.trim()) return books;
    const q = search.toLowerCase();
    return books.filter(b =>
      b.title.toLowerCase().includes(q) || b.author.toLowerCase().includes(q) || b.isbn?.includes(q)
    );
  }, [books, search]);

  const availableCount = books.filter(b => b.available_copies > 0).length;
  const overdueCount = checkouts.filter(c => c.is_overdue && !c.returned_at).length;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Library Management</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage book catalog and checkouts</p>
        </div>
        <div className="flex gap-2">
          <Button variant="secondary" onClick={() => { setShowCheckoutForm(true); }}>
            <ArrowLeftOnRectangleIcon className="h-4 w-4 mr-1.5" /> Check Out
          </Button>
          <Button onClick={() => { setEditingBook(null); setShowBookForm(true); }}>
            <PlusIcon className="h-4 w-4 mr-1.5" /> Add Book
          </Button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-500 dark:text-slate-400">Total Books</p>
          <p className="text-2xl font-bold text-slate-900 dark:text-white">{books.length}</p>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-500 dark:text-slate-400">Available</p>
          <p className="text-2xl font-bold text-green-600">{availableCount}</p>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-500 dark:text-slate-400">Checked Out</p>
          <p className="text-2xl font-bold text-indigo-600">{checkouts.filter(c => !c.returned_at).length}</p>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-sm text-slate-500 dark:text-slate-400">Overdue</p>
          <p className="text-2xl font-bold text-red-600">{overdueCount}</p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 bg-slate-100 dark:bg-slate-800 rounded-lg p-1 w-fit">
        <button onClick={() => setActiveTab("catalog")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${activeTab === "catalog" ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm" : "text-slate-600 dark:text-slate-400"}`}>
          Book Catalog ({books.length})
        </button>
        <button onClick={() => setActiveTab("checkouts")}
          className={`px-4 py-2 rounded-md text-sm font-medium ${activeTab === "checkouts" ? "bg-white dark:bg-slate-700 text-slate-900 dark:text-white shadow-sm" : "text-slate-600 dark:text-slate-400"}`}>
          Checkouts ({checkouts.length})
        </button>
      </div>

      {activeTab === "catalog" ? (
        <>
          <div className="relative max-w-sm">
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
            <input value={search} onChange={e => setSearch(e.target.value)}
              className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm dark:text-slate-200"
              placeholder="Search by title, author, or ISBN..." />
          </div>
          {isLoading ? (
            <div className="grid grid-cols-3 gap-4">{[1,2,3,4,5,6].map(i => <div key={i} className="h-32 bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse" />)}</div>
          ) : filteredBooks.length === 0 ? (
            <EmptyState icon={BookOpenIcon} title="No books found" description={search ? "Try a different search" : "Add your first book to the library"} />
          ) : (
            <div className="grid grid-cols-3 gap-4">
              {filteredBooks.map(book => (
                <div key={book.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <BookOpenIcon className="h-5 w-5 text-indigo-500" />
                      <span className="text-xs text-slate-400">{book.category || "General"}</span>
                    </div>
                    <div className="flex gap-1">
                      <button onClick={() => { setEditingBook(book); setShowBookForm(true); }}
                        className="p-1 rounded text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700">
                        <PencilIcon className="h-3.5 w-3.5" />
                      </button>
                      <button onClick={() => { if (confirm("Remove this book?")) deleteBookMut.mutate(book.id); }}
                        className="p-1 rounded text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30">
                        <XCircleIcon className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </div>
                  <h3 className="font-semibold text-slate-900 dark:text-white truncate">{book.title}</h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400 truncate">{book.author}</p>
                  {book.isbn && <p className="text-xs text-slate-400 mt-1 font-mono">ISBN: {book.isbn}</p>}
                  <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100 dark:border-slate-700">
                    <span className="text-xs text-slate-500">Shelf: {book.shelf_location || "—"}</span>
                    <span className={`text-sm font-semibold ${book.available_copies > 0 ? "text-green-600" : "text-red-500"}`}>
                      {book.available_copies}/{book.total_copies} available
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </>
      ) : (
        <div className="space-y-3">
          {checkouts.length === 0 ? (
            <EmptyState icon={BookOpenIcon} title="No checkouts" description="No books have been checked out yet" />
          ) : (
            <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-slate-50 dark:bg-slate-800/80 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">
                    <th className="px-4 py-3">Book</th>
                    <th className="px-4 py-3">Student</th>
                    <th className="px-4 py-3">Checked Out</th>
                    <th className="px-4 py-3">Due</th>
                    <th className="px-4 py-3">Status</th>
                    <th className="px-4 py-3">Fine</th>
                    <th className="px-4 py-3"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                  {checkouts.map(co => (
                    <tr key={co.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50">
                      <td className="px-4 py-3 font-medium text-slate-900 dark:text-white">{co.book_title}</td>
                      <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{co.student_name}</td>
                      <td className="px-4 py-3 text-slate-500">{dayjs(co.checked_out_at).format("MMM D")}</td>
                      <td className="px-4 py-3 text-slate-500">{dayjs(co.due_date).format("MMM D")}</td>
                      <td className="px-4 py-3">
                        {co.returned_at ? (
                          <span className="px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300">Returned</span>
                        ) : co.is_overdue ? (
                          <span className="px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300">Overdue ({co.days_overdue}d)</span>
                        ) : (
                          <span className="px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300">Active</span>
                        )}
                      </td>
                      <td className="px-4 py-3 text-slate-500">
                        {parseFloat(co.fine_amount) > 0 ? (
                          <span className={co.fine_paid ? "text-green-600" : "text-red-500"}>
                            ${co.fine_amount} {co.fine_paid ? "(paid)" : "(unpaid)"}
                          </span>
                        ) : "—"}
                      </td>
                      <td className="px-4 py-3">
                        {!co.returned_at && (
                          <Button size="sm" variant="secondary" onClick={() => returnMut.mutate(co.id)} loading={returnMut.isPending}>
                            <ArrowRightOnRectangleIcon className="h-3.5 w-3.5 mr-1" /> Return
                          </Button>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {showCheckoutForm && (
        <CheckoutFormModal open={showCheckoutForm} onClose={() => setShowCheckoutForm(false)}
          onSaved={() => { setShowCheckoutForm(false); qc.invalidateQueries({ queryKey: ["library-checkouts"] }); qc.invalidateQueries({ queryKey: ["library-books"] }); }} />
      )}
      {showBookForm && (
        <BookFormModal open={showBookForm} onClose={() => { setShowBookForm(false); setEditingBook(null); }}
          book={editingBook} onSaved={() => { setShowBookForm(false); setEditingBook(null); qc.invalidateQueries({ queryKey: ["library-books"] }); }} />
      )}
    </div>
  );
}
