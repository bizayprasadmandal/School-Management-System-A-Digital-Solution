/**
 * Student Cafeteria Page — view menus, book meals
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { toast } from "react-hot-toast";
import { api } from "../../api/client";
import dayjs from "dayjs";
import { toCsv, downloadCsv } from "../../utils";
import { Button, EmptyState, Modal, Pagination } from "../../components/common";
import {
  CakeIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  CalendarDaysIcon,
  MagnifyingGlassIcon,
  ArrowDownTrayIcon,
} from "@heroicons/react/24/outline";

interface MenuItem {
  id: string;
  title: string;
  description: string;
  date: string;
  price: string;
  items: string;
}

function CafeteriaSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2">
      {[1, 2, 3, 4].map((i) => (
        <div
          key={i}
          className="h-28 relative overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
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

export default function CafeteriaPage() {
  const qc = useQueryClient();
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<MenuItem | null>(null);

  const { data: menus = [], isLoading } = useQuery({
    queryKey: ["student-cafeteria-menus"],
    queryFn: async () => {
      const r = await api.get<{ results: MenuItem[] }>("/cafeteria/daily-menus/");
      return r.results ?? [];
    },
  });

  const createMenu = useMutation({
    mutationFn: (data: Partial<MenuItem>) => api.post("/cafeteria/daily-menus/", data),
    onSuccess: () => {
      toast.success("Menu created");
      qc.invalidateQueries({ queryKey: ["student-cafeteria-menus"] });
      setShowForm(false);
    },
  });

  const updateMenu = useMutation({
    mutationFn: (data: Partial<MenuItem>) =>
      api.patch(`/cafeteria/daily-menus/${editing!.id}/`, data),
    onSuccess: () => {
      toast.success("Menu updated");
      qc.invalidateQueries({ queryKey: ["student-cafeteria-menus"] });
      setShowForm(false);
      setEditing(null);
    },
  });

  const deleteMenu = useMutation({
    mutationFn: (id: string) => api.delete(`/cafeteria/daily-menus/${id}/`),
    onSuccess: () => {
      toast.success("Menu deleted");
      qc.invalidateQueries({ queryKey: ["student-cafeteria-menus"] });
    },
  });

  const paginatedMenus = React.useMemo(() => {
    const start = (page - 1) * 12;
    return menus.slice(start, start + 12);
  }, [menus, page]);

  const totalPages = Math.ceil(menus.length / 12);

  const handleExport = () => {
    const cols = [
      { key: "name", label: "Name" },
      { key: "description", label: "Description" },
    ];
    const rows = menus.map((row) => ({
      name: row.title ?? "",
      description: row.description ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, "cafeteria-menus-" + dayjs().format("YYYY-MM-DD") + ".csv");
  };
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Cafeteria</h1>
          <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
            View daily menus and book your meals
          </p>
        </div>
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
          Add Menu
        </Button>
      </div>

      {/* Search */}
      <div className="rounded-xl bg-white p-4 shadow-sm border border-slate-100 dark:bg-slate-800 dark:border-slate-700">
        <div className="relative">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
          <input
            type="search"
            placeholder="Search meals..."
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
        <CafeteriaSkeleton />
      ) : menus.length === 0 ? (
        <EmptyState
          icon={CakeIcon}
          title="No menus available"
          description="Daily menus will appear here once published."
        />
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {menus.map((menu) => (
            <div
              key={menu.id}
              className="rounded-xl border border-slate-200 bg-white p-4 transition-all hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
            >
              <div className="mb-2 flex items-start justify-between">
                <div>
                  <h3 className="font-semibold text-slate-900 dark:text-white">{menu.title}</h3>
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    {menu.description || "—"}
                  </p>
                </div>
                <div className="flex gap-1">
                  <button
                    onClick={() => {
                      setEditing(menu);
                      setShowForm(true);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-slate-100 hover:text-indigo-600 dark:hover:bg-slate-700"
                  >
                    <PencilIcon className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => {
                      if (confirm("Delete this menu?")) deleteMenu.mutate(menu.id);
                    }}
                    className="rounded p-1 text-slate-400 hover:bg-red-50 hover:text-red-600 dark:hover:bg-red-900/20"
                  >
                    <TrashIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <span className="flex items-center gap-1 text-xs text-slate-400">
                  <CalendarDaysIcon className="h-3.5 w-3.5" />
                  {menu.date || "—"}
                </span>
                <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700 dark:bg-green-900/30 dark:text-green-400">
                  ${menu.price || "0.00"}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <Pagination page={page} total={menus.length} pageSize={12} onChange={setPage} />
      )}
      <Modal
        open={showForm}
        onClose={() => {
          setShowForm(false);
          setEditing(null);
        }}
        title={editing ? "Edit Menu" : "Add Menu"}
      >
        <MenuForm
          menu={editing}
          saving={createMenu.isPending || updateMenu.isPending}
          onSave={(data) => {
            if (editing) updateMenu.mutate(data);
            else createMenu.mutate(data);
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

function MenuForm({
  menu,
  saving,
  onSave,
  onCancel,
}: {
  menu: MenuItem | null;
  saving: boolean;
  onSave: (data: Partial<MenuItem>) => void;
  onCancel: () => void;
}) {
  const [f, setF] = useState({
    title: menu?.title ?? "",
    description: menu?.description ?? "",
    date: menu?.date ?? "",
    price: menu?.price ?? "0.00",
    items: menu?.items ?? "",
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        if (!f.title.trim()) return toast.error("Title required");
        onSave(f);
      }}
      className="space-y-4"
    >
      <div>
        <label className="mb-1 block text-sm font-medium">Menu Title *</label>
        <input
          value={f.title}
          onChange={(e) => setF((p) => ({ ...p, title: e.target.value }))}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          required
        />
      </div>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="mb-1 block text-sm font-medium">Date *</label>
          <input
            type="date"
            value={f.date}
            onChange={(e) => setF((p) => ({ ...p, date: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
            required
          />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium">Price ($)</label>
          <input
            step="0.01"
            value={f.price}
            onChange={(e) => setF((p) => ({ ...p, price: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
          />
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Description</label>
        <textarea
          value={f.description}
          onChange={(e) => setF((p) => ({ ...p, description: e.target.value }))}
          rows={2}
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium">Menu Items</label>
        <textarea
          value={f.items}
          onChange={(e) => setF((p) => ({ ...p, items: e.target.value }))}
          rows={3}
          placeholder="One item per line"
          className="w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200"
        />
      </div>
      <div className="flex justify-end gap-3 pt-2">
        <Button variant="secondary" onClick={onCancel} disabled={saving}>
          Cancel
        </Button>
        <Button type="submit" loading={saving}>
          {menu ? "Update" : "Create"}
        </Button>
      </div>
    </form>
  );
}
