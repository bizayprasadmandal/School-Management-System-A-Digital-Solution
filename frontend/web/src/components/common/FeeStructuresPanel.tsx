/** Fee Structures Panel — Admin CRUD for fee structures (grade + category + amount) */

import React, { useState } from "react";
import { toast } from "react-hot-toast";
import {
  PlusIcon, PencilIcon, TrashIcon, CurrencyDollarIcon,
} from "@heroicons/react/24/outline";
import {
  useFeeStructures, useCreateFeeStructure, useUpdateFeeStructure, useDeleteFeeStructure,
  useGradeLevels, useAcademicYears, useFeeCategories,
} from "../../api/hooks";
import { Button, Modal, EmptyState, Badge, Input, Select } from "./index";
import type { FeeCategory, FeeStructure } from "../../types";

function StructureFormModal({
  open, onClose, structure, onSaved,
}: {
  open: boolean; onClose: () => void; structure?: FeeStructure | null; onSaved: () => void;
}) {
  const [form, setForm] = useState({
    grade: structure?.grade ?? 0,
    fee_category: structure?.fee_category ?? 0,
    academic_year: structure?.academic_year ?? 0,
    amount: structure?.amount ?? 0,
    due_day: structure?.due_day ?? 10,
    late_fee_per_day: structure?.late_fee_per_day ?? 0,
    is_active: structure?.is_active ?? true,
  });

  const { data: gradesData } = useGradeLevels();
  const { data: yearsData } = useAcademicYears();
  const { data: categoriesData } = useFeeCategories();

  const grades = gradesData?.results ?? [];
  const years = yearsData?.results ?? [];
  const categories = Array.isArray(categoriesData) ? categoriesData : [];

  const isEdit = !!structure;
  const createMut = useCreateFeeStructure();
  const updateMut = useUpdateFeeStructure();
  const isSaving = createMut.isPending || updateMut.isPending;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.grade || !form.fee_category || !form.academic_year) {
      return toast.error("Grade, category, and academic year are required");
    }
    if (form.amount <= 0) return toast.error("Amount must be greater than 0");

    if (isEdit) {
      updateMut.mutate({ id: structure!.id, ...form }, {
        onSuccess: () => { toast.success("Structure updated"); onSaved(); },
      });
    } else {
      createMut.mutate(form, {
        onSuccess: () => { toast.success("Structure created"); onSaved(); },
      });
    }
  };

  return (
    <Modal open={open} onClose={onClose} title={isEdit ? "Edit Fee Structure" : "New Fee Structure"}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="grid grid-cols-2 gap-4">
          <Select label="Grade *" value={form.grade} onChange={e => setForm(p => ({ ...p, grade: parseInt(e.target.value) }))}
            options={[{ value: 0, label: "Select grade..." }, ...grades.map(g => ({ value: g.id, label: g.name }))]} />
          <Select label="Fee Category *" value={form.fee_category} onChange={e => setForm(p => ({ ...p, fee_category: parseInt(e.target.value) }))}
            options={[{ value: 0, label: "Select category..." }, ...categories.map((c: FeeCategory) => ({ value: c.id, label: c.name }))]} />
        </div>
        <Select label="Academic Year *" value={form.academic_year} onChange={e => setForm(p => ({ ...p, academic_year: parseInt(e.target.value) }))}
          options={[{ value: 0, label: "Select year..." }, ...years.map(y => ({ value: y.id, label: y.name }))]} />
        <div className="grid grid-cols-3 gap-4">
          <Input label="Amount ($) *" type="number" min={0} step={0.01} value={form.amount}
            onChange={e => setForm(p => ({ ...p, amount: parseFloat(e.target.value) || 0 }))} />
          <Input label="Due Day" type="number" min={1} max={31} value={form.due_day}
            onChange={e => setForm(p => ({ ...p, due_day: parseInt(e.target.value) || 10 }))} />
          <Input label="Late Fee/Day ($)" type="number" min={0} step={0.01} value={form.late_fee_per_day}
            onChange={e => setForm(p => ({ ...p, late_fee_per_day: parseFloat(e.target.value) || 0 }))} />
        </div>
        <label className="flex items-center gap-2 text-sm text-slate-700 dark:text-slate-300">
          <input type="checkbox" checked={form.is_active} onChange={e => setForm(p => ({ ...p, is_active: e.target.checked }))}
            className="rounded border-slate-300" />
          Active
        </label>
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose} disabled={isSaving}>Cancel</Button>
          <Button type="submit" loading={isSaving}>{isEdit ? "Update" : "Create"} Structure</Button>
        </div>
      </form>
    </Modal>
  );
}

export default function FeeStructuresPanel() {
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState<FeeStructure | null>(null);

  const { data: structuresData, isLoading } = useFeeStructures();
  const structures = structuresData?.results ?? [];
  const deleteMut = useDeleteFeeStructure();

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-900 dark:text-white">Fee Structures</h2>
          <p className="text-sm text-slate-500 dark:text-slate-400">Configure fee amounts per grade, category, and academic year</p>
        </div>
        <Button onClick={() => { setEditing(null); setShowForm(true); }} size="sm">
          <PlusIcon className="h-4 w-4 mr-1" /> Add Structure
        </Button>
      </div>

      {isLoading ? (
        <div className="space-y-2">{[1,2,3].map(i => <div key={i} className="h-16 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
      ) : structures.length === 0 ? (
        <EmptyState icon={CurrencyDollarIcon} title="No fee structures" description="Create fee structures linking categories to grades" />
      ) : (
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-800/80 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">
                <th className="px-4 py-3">Grade</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Year</th>
                <th className="px-4 py-3">Amount</th>
                <th className="px-4 py-3">Due Day</th>
                <th className="px-4 py-3">Late Fee</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {structures.map(s => (
                <tr key={s.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/50">
                  <td className="px-4 py-3 font-medium text-slate-900 dark:text-white">{s.grade_name}</td>
                  <td className="px-4 py-3 text-slate-600 dark:text-slate-400">{s.category_name}</td>
                  <td className="px-4 py-3 text-slate-500">{s.academic_year_name}</td>
                  <td className="px-4 py-3 font-semibold text-slate-900 dark:text-white">${Number(s.amount).toLocaleString()}</td>
                  <td className="px-4 py-3 text-slate-500">{s.due_day}th</td>
                  <td className="px-4 py-3 text-slate-500">${Number(s.late_fee_per_day).toFixed(2)}/day</td>
                  <td className="px-4 py-3">
                    <Badge color={s.is_active ? "green" : "slate"} dot>{s.is_active ? "Active" : "Inactive"}</Badge>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-1">
                      <button onClick={() => { setEditing(s); setShowForm(true); }}
                        className="p-1.5 rounded text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-700">
                        <PencilIcon className="h-4 w-4" />
                      </button>
                      <button onClick={() => { if (confirm("Delete this structure?")) deleteMut.mutate(s.id); }}
                        className="p-1.5 rounded text-red-400 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30">
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <StructureFormModal
          open={showForm} onClose={() => { setShowForm(false); setEditing(null); }}
          structure={editing} onSaved={() => { setShowForm(false); setEditing(null); }} />
      )}
    </div>
  );
}
