/**
 * Teacher Library Page — browse catalog and manage checkouts
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import { useBulkSelect } from "../../hooks/useBulkSelect";
import { useKeyboardShortcuts } from "../../hooks/useKeyboardShortcuts";
import dayjs from "dayjs";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { BulkActionBar } from "../../components/common/BulkActionBar";
import {
  BookOpenIcon,
  BanknotesIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  CheckIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";

interface Book {
  id: string;
  title: string;
  author: string;
  isbn: string;
  available_copies: number;
  total_copies: number;
  fine_per_day: string;
}

function LibrarySkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3].map((i) => (
        <div
          key={i}
          className="h-40 relative overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
        >
          <div
            className="absolute inset-0 animate-shimmer bg-gradient-to-r from-transparent via-slate-200/50 to-transparent dark:via-slate-600/30"
            style={{ backgroundSize: "200% 100%" }}
          />
        </div>
      ))}
    </div>
  );
}

export default function LibraryPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<Book | null>(null);

  const { data: allBooks = [], isLoading } = useQuery({
    queryKey: ["teacher-library-books"],
    queryFn: async () => {
      const r = await api.get<{ results: Book[] }>("/library/books/");
      return r.results ?? [];
    },
  });

  const books = React.useMemo(() => {
    if (!search.trim()) return allBooks;
    const q = search.toLowerCase();
    return allBooks.filter(
      (b) =>
        b.title?.toLowerCase().includes(q) ||
        b.author?.toLowerCase().includes(q) ||
        b.isbn?.toLowerCase().includes(q),
    );
  }, [allBooks, search]);

  const createBook = useMutation({
    mutationFn: (data: Partial<Book>) => api.post("/library/books/", data),
    onSuccess: () => {
      toast.success("Book added");
      qc.invalidateQueries({ queryKey: ["teacher-library-books"] });
      setShowForm(false);
    },
  });

  const updateBook = useMutation({
    mutationFn: (data: Partial<Book>) => api.patch(`/library/books/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Book updated");
      qc.invalidateQueries({ queryKey: ["teacher-library-books"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteBook = useMutation({
    mutationFn: (id: string) => api.delete(`/library/books/${id}/`),
    onSuccess: () => {
      toast.success("Book deleted");
      qc.invalidateQueries({ queryKey: ["teacher-library-books"] });
    },
  });

  const paginatedAllBooks = React.useMemo(() => {
    const start = (page - 1) * 12;
    return allBooks.slice(start, start + 12);
  }, [allBooks, page]);

  const totalPages = Math.ceil(allBooks.length / 12);

  const bulk = useBulkSelect(allBooks);

  const handleExport = () => {
    const cols = [
      { key: "title", label: "Title" },
      { key: "author", label: "Author" },
    ];
    const rows = allBooks.map((row) => ({
      title: row.title ?? "",
      author: row.author ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "library-books-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${bulk.selectedCount} items?`)) return;
    try {
      await Promise.all(bulk.selectedArray.map((id) => api.delete("/library/books//" + id + "/")));
      toast.success(`${bulk.selectedCount} items deleted`);
      bulk.clear();
      qc.invalidateQueries({ queryKey: ["teacher-library"] });
    } catch {
      toast.error("Failed to delete items");
    }
  };

  const handleBulkExport = () => {
    const cols = [{ key: "id", label: "ID" }];
    const rows = bulk.selectedItems.map((item) => ({ id: item.id }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "bulk-export-" + new Date().toISOString().slice(0, 10) + ".csv");
  };
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Library</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            Browse the library catalog
          </p>
        </div>

        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={bulk.allSelected}
            ref={(el) => {
              if (el) el.indeterminate = bulk.someSelected;
            }}
            onChange={bulk.toggleAll}
            className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600"
          />
          <span className="text-sm text-slate-500 dark:text-slate-400">Select all</span>
        </label>
        <Button
          variant="secondary"
          leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />}
          onClick={handleExport}
        >
          Export CSV
        </Button>
        <Button
          onClick={() => {
            setEditing(null);
            setShowForm(true);
          }}
        >
          <PlusIcon className="mr-1.5 h-4 w-4" />
          Add Book
        </Button>
      </div>

      {/* Search */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 dark:bg-slate-800 dark:border-slate-700">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            placeholder="Search by title, author, or ISBN..."
            value={search}
            onChange={(e) => {
              setSearch(e.target.value);
              setPage(1);
            }}
            className="w-full rounded-lg border border-slate-300 bg-white py-2 pl-10 pr-3 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-700 dark:text-white dark:placeholder-slate-400"
          />
        </div>
      </div>

      {isLoading ? (
        <LibrarySkeleton />
      ) : books.length === 0 ? (
        <EmptyState
          icon={BookOpenIcon}
          title="No books available"
          description="The library catalog will appear here once books are added."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {paginatedAllBooks.map((book) => (
            <div
              key={book.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="mb-1 flex items-start justify-between">
                <h3 className="font-semibold text-slate-900 dark:text-white">{book.title}</h3>
                <div className="flex gap-1">
                  <button
                    onClick={() => {
                      setEditing(book);
                      setShowForm(true);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm("Delete this book?")) deleteBook.mutate(book.id);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                {book.author || "Unknown author"}
              </p>
              <div className="mt-3 flex items-center gap-3">
                <span className="flex items-center gap-1 text-xs text-slate-400">
                  <BookOpenIcon className="h-3.5 w-3.5" />
                  {book.available_copies}/{book.total_copies} available
                </span>
                <span className="flex items-center gap-1 text-xs text-slate-400">
                  <BanknotesIcon className="h-3.5 w-3.5" />${book.fine_per_day}
                  /day
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination page={page} total={books.length} pageSize={12} onChange={setPage} />
      )}
      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit Book" : "Add Book"}
      >
        <BookForm
          book={editing}
          saving={createBook.isPending || updateBook.isPending}
          onSave={(data) => {
            if (editing) updateBook.mutate(data);
            else createBook.mutate(data);
          }}
          onCancel={() => {
            setShowForm(false);
            setEditing(null);
          }}
        />
      </Modal>
    </div>
  );
}

function BookForm({
  book,
  saving,
  onSave,
  onCancel,
}: {
  book: Book | null;
  saving: boolean;
  onSave: (data: Partial<Book>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    title: book?.title ?? "",
    author: book?.author ?? "",
    isbn: book?.isbn ?? "",
    total_copies: book?.total_copies ?? 1,
    fine_per_day: book?.fine_per_day ?? "0.50",
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.title.trim()) return toast.error("Title required");
        onSave({ ...f, available_copies: f.total_copies });
      }}
      className="space-y-4"
    >
      <div>
        <label className="mb-1 block text-sm font-medium">Title *</label>
        <input
          value={f.title}
          onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          required
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Author</label>
          <input
            value={f.author}
            onChange={(e) => setF((p) => ({ ...p, author: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">ISBN</label>
          <input
            value={f.isbn}
            onChange={(e) => setF((p) => ({ ...p, isbn: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Total Copies</label>
          <input
            type="number"
            min={1}
            value={f.total_copies}
            onChange={(e) => setF((p) => ({ ...p, total_copies: Number(e.target.value) }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Fine/Day ($)</label>
          <input
            step="0.01"
            value={f.fine_per_day}
            onChange={(e) => setF((p) => ({ ...p, fine_per_day: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {book ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
