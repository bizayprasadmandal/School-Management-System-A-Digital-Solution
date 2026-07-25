/** Book Management — Full catalog CRUD for librarians */
import React, { useState, useMemo } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import {
  PlusIcon, MagnifyingGlassIcon, BookOpenIcon,
  PencilIcon, XCircleIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, Modal, EmptyState, SkeletonCard } from "../../components/common";

interface Book {
  id: string;
  title: string;
  author: string;
  isbn: string;
  category: string;
  publisher: string;
  shelf_location: string;
  total_copies: number;
  available_copies: number;
  is_active: boolean;
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
    onError: () => toast.error("Failed to add book"),
  });
  const updateMut = useMutation({
    mutationFn: (d: typeof form) => api.patch(`/library/books/${book!.id}/`, d),
    onSuccess: () => { toast.success("Book updated"); onSaved(); },
    onError: () => toast.error("Failed to update book"),
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
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Title *</label>
          <input value={form.title} onChange={e => setForm(p => ({ ...p, title: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" required />
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
            <input type="number" min={1} value={form.total_copies}
              onChange={e => setForm(p => ({ ...p, total_copies: Math.max(1, parseInt(e.target.value) || 1) }))}
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

export default function BookManagementPage() {
  const [search, setSearch] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [editingBook, setEditingBook] = useState<Book | null>(null);
  const qc = useQueryClient();

  const { data: books = [], isLoading } = useQuery({
    queryKey: ["librarian-books"],
    queryFn: async () => {
      const res = await api.get<{ results: Book[] }>("/library/books/");
      return res.results ?? [];
    },
  });

  const deleteMut = useMutation({
    mutationFn: (id: string) => api.delete(`/library/books/${id}/`),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["librarian-books"] }); toast.success("Book removed"); },
    onError: () => toast.error("Failed to remove book"),
  });

  const filteredBooks = useMemo(() => {
    if (!search.trim()) return books;
    const q = search.toLowerCase();
    return books.filter(b =>
      b.title.toLowerCase().includes(q) || b.author.toLowerCase().includes(q) || b.isbn?.toLowerCase().includes(q)
    );
  }, [books, search]);

  const totalCheckedOut = books.reduce((sum, b) => sum + (b.total_copies - b.available_copies), 0);
  const totalAvailable = books.reduce((sum, b) => sum + b.available_copies, 0);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Book Catalog</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Manage library book inventory</p>
        </div>
        <Button onClick={() => { setEditingBook(null); setShowForm(true); }}>
          <PlusIcon className="h-4 w-4 mr-1.5" /> Add Book
        </Button>
      </div>

      {/* Stats bar */}
      <div className="grid grid-cols-4 gap-4">
        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-xs text-slate-500 dark:text-slate-400">Total Titles</p>
          <p className="text-xl font-bold text-slate-900 dark:text-white">{books.length}</p>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-xs text-slate-500 dark:text-slate-400">Total Copies</p>
          <p className="text-xl font-bold text-slate-900 dark:text-white">{totalAvailable + totalCheckedOut}</p>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-xs text-slate-500 dark:text-slate-400">Available</p>
          <p className="text-xl font-bold text-green-600">{totalAvailable}</p>
        </div>
        <div className="bg-white dark:bg-slate-800 rounded-xl p-4 border border-slate-200 dark:border-slate-700">
          <p className="text-xs text-slate-500 dark:text-slate-400">Checked Out</p>
          <p className="text-xl font-bold text-indigo-600">{totalCheckedOut}</p>
        </div>
      </div>

      {/* Search */}
      <div className="relative max-w-sm">
        <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
        <input value={search} onChange={e => setSearch(e.target.value)}
          className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm dark:text-slate-200"
          placeholder="Search by title, author, or ISBN..." />
      </div>

      {/* Book grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {[1,2,3,4,5,6].map(i => <SkeletonCard key={i} />)}
        </div>
      ) : filteredBooks.length === 0 ? (
        <EmptyState icon={BookOpenIcon} title="No books found"
          description={search ? "Try a different search term" : "Add your first book to the library"} />
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {filteredBooks.map(book => (
            <div key={book.id}
              className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:border-teal-300 dark:hover:border-teal-600 hover:shadow-md transition-all group">
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <BookOpenIcon className="h-5 w-5 text-teal-500" />
                  <span className="text-xs font-medium text-slate-400 uppercase">{book.category || "General"}</span>
                </div>
                <div className="flex gap-1" onClick={e => e.stopPropagation()}>
                  <button onClick={() => { setEditingBook(book); setShowForm(true); }}
                    className="p-1.5 rounded text-slate-400 hover:text-teal-600 hover:bg-teal-50 dark:hover:bg-teal-900/30 transition-colors"
                    title="Edit book">
                    <PencilIcon className="h-3.5 w-3.5" />
                  </button>
                  <button onClick={() => { if (confirm("Remove this book from the catalog?")) deleteMut.mutate(book.id); }}
                    className="p-1.5 rounded text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors"
                    title="Delete book">
                    <XCircleIcon className="h-3.5 w-3.5" />
                  </button>
                </div>
              </div>
              <h3 className="font-semibold text-slate-900 dark:text-white truncate group-hover:text-teal-600 dark:group-hover:text-teal-400 transition-colors">
                {book.title}
              </h3>
              <p className="text-sm text-slate-500 dark:text-slate-400 truncate">{book.author}</p>
              {book.isbn && <p className="text-xs text-slate-400 mt-1 font-mono">ISBN: {book.isbn}</p>}
              <div className="flex items-center justify-between mt-3 pt-3 border-t border-slate-100 dark:border-slate-700">
                <span className="text-xs text-slate-500">Shelf: {book.shelf_location || "—"}</span>
                <span className={`text-sm font-semibold ${book.available_copies > 0 ? "text-green-600" : "text-red-500"}`}>
                  {book.available_copies}/{book.total_copies} avail.
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {showForm && (
        <BookFormModal open={showForm} onClose={() => { setShowForm(false); setEditingBook(null); }}
          book={editingBook}
          onSaved={() => { setShowForm(false); setEditingBook(null); qc.invalidateQueries({ queryKey: ["librarian-books"] }); }} />
      )}
    </div>
  );
}
