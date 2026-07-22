/** Fee Categories Panel — Admin CRUD for fee categories */

import React, { useState } from "react";
import { toast } from "react-hot-toast";
import {
  PlusIcon, PencilIcon, TrashIcon, TagIcon,
} from "@heroicons/react/24/outline";
import {
  useFeeCategories, useCreateFeeCategory, useUpdateFeeCategory, useDeleteFeeCategory,
} from "../../api/hooks";
import { Button, Modal, EmptyState, Badge } from "./index";
import type { FeeCategory } from "../../types";

const RECURRENCE_BADGES: Record<string, { label: string; color: "blue" | "purple" | "amber" | "slate" }> = {
  monthly: { label: "Monthly", color: "blue" },
  quarterly: { label: "Quarterly", color: "purple" },
  annual: { label: "Annual", color: "amber" },
  one_time: { label: "One Time", color: "slate" },
};

function CategoryFormModal({
  open, onClose, category, onSaved,
}: {
  open: boolean; onClose: () => void; category?: FeeCategory | null; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    name: category?.name ?? "",
    description: category?.description ?? "",
    is_mandatory: category?.is_mandatory ?? true,
    is_recurring: category?.is_recurring ?? true,
    recurrence: category?.recurrence ?? "monthly",
  });

  const isEdit = !!category;
  const createMut = useCreateFeeCategory();
  const updateMut = useUpdateFeeCategory();
  const isSaving = createMut.isPending || updateMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.name.trim()) return toast.error("Category name is required");
    if (isEdit) {
      updateMut.mutate({ id: category!.id, ...form }, {
        onSuccess: () => { toast.success("Category updated"); onSaved(); },
      });
    } else {
      createMut.mutate(form, {
        onSuccess: () => { toast.success("Category created"); onSaved(); },
      });
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Fee Category" : "New Fee Category"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Name *</label>
          <input value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" placeholder="e.g. Tuition, Transport, Hostel" />
        </div>
        <div>
          <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
          <textarea value={form.description} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} rows={2}
            className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200" />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Recurrence</label>
            <select value={form.recurrence} onChange={e => setForm(p => ({ ...p, recurrence: e.target.value as FeeCategory["recurrence"] }))}
              className="w-full rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
              <option value="monthly">Monthly</option>
              <option value="quarterly">Quarterly</option>
              <option value="annual">Annual</option>
              <option value="one_time">One Time</option>
            </select>
          </div>
          <div className="flex items-end gap-4 pb-2">
            <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
              <input type="checkbox" checked={form.is_mandatory} onChange={e => setForm(p => ({ ...p, is_mandatory: e.target.checked }))}
                className="rounded border-slate-300" />
              Mandatory
            </label>
            <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
              <input type="checkbox" checked={form.is_recurring} onChange={e => setForm(p => ({ ...p, is_recurring: e.target.checked }))}
                className="rounded border-slate-300" />
              Recurring
            </label>
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Create"} Category</Button>
        </div>
      </form>
    </Modal>
  );
}

export default function FeeCategoriesPanel() {
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<FeeCategory | null>(null);

  const { data: categories = [], isLoading } = useFeeCategories();
  const deleteMut = useDeleteFeeCategory();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Fee Categories</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">Define types of fees charged (Tuition, Transport, etc.)</p>
        </div>
        <Button onClick={() => { setEditing(null); setShowForm(true); }} size="sm">
          <PlusIcon className="h-4 w-4 mr-1" /> Add Category
        </Button>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-2 gap-4">{[1,2].map(i => <div key={i} className="h-24 bg-slate-100 dark:bg-slate-800 rounded-xl animate-pulse" />)}</div>
      ) : categories.length === 0 ? (
        <EmptyState icon={TagIcon} title="No fee categories" description="Create your first fee category to get started" />
      ) : (
        <div className="grid grid-cols-2 gap-4">
          {categories.map(cat => {
            const rec = RECURRENCE_BADGES[cat.recurrence] ?? { label: cat.recurrence, color: "slate" as const };
            return (
              <div key={cat.id} className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 p-4 hover:shadow-sm transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-slate-900 dark:text-white">{cat.name}</h3>
                      <Badge color={rec.color}>{rec.label}</Badge>
                      {cat.is_mandatory && <Badge color="red" dot>Required</Badge>}
                    </div>
                    {cat.description && <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">{cat.description}</p>}
                  </div>
                  <div className="flex gap-1 ml-3">
                    <button onClick={() => { setEditing(cat); setShowForm(true); }}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700">
                      <PencilIcon className="h-4 w-4" />
                    </button>
                    <button onClick={() => { if (confirm("Delete this category?")) deleteMut.mutate(cat.id); }}
                      className="p-1.5 rounded-lg text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30">
                      <TrashIcon className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {showForm && (
        <CategoryFormModal
          open={showForm} onClose={() => { setShowForm(false); setEditing(null); }}
          category={editing} onSaved={() => { setShowForm(false); setEditing(null); }} />
      )}
    </div>
  );
}
