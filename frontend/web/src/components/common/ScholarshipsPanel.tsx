/**
 * ScholarshipsPanel — Admin UI for awarding and managing student scholarships.
 * Renders as a section within the FeesPage with full CRUD via modals.
 */

import React, { useState } from "react";
import {
  AcademicCapIcon, PlusIcon, PencilIcon,
  CheckCircleIcon, XCircleIcon,
} from "@heroicons/react/24/outline";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { api } from "../../api/client";
import { useScholarships, useCreateScholarship, useUpdateScholarship, useToggleScholarship, useAcademicYears } from "../../api/hooks";
import type { Scholarship, StudentListItem } from "../../types";
import {
  Button, Badge, Modal, Input, Select, DataTable, EmptyState, ConfirmDialog,
} from "./";
import type { Column, BadgeColor } from "./";

// ─── Student Search (inline fetch) ──────────────────────────────────────────

function useStudentSearch(query: string) {
  return useQuery({
    queryKey: ["students", "search", query],
    queryFn: () =>
      api.get<{ count: number; results: StudentListItem[] }>("/students/", {
        search: query || undefined,
      }),
    enabled: query.length >= 2,
    staleTime: 30_000,
  });
}

// ─── Scholarship Form Modal ──────────────────────────────────────────────────

interface ScholarshipFormModalProps {
  scholarship?: Scholarship | null;
  onClose: () => void;
}

function ScholarshipFormModal({ scholarship, onClose }: ScholarshipFormModalProps) {
  const qc = useQueryClient();
  const isEdit = !!scholarship;

  const [studentQuery, setStudentQuery] = useState(scholarship?.student_name ?? "");
  const [studentId, setStudentId] = useState(scholarship?.student ?? "");
  const [name, setName] = useState(scholarship?.name ?? "");
  const [discountType, setDiscountType] = useState<"percent" | "fixed">(scholarship?.discount_type ?? "percent");
  const [discountValue, setDiscountValue] = useState(String(scholarship?.discount_value ?? ""));
  const [academicYearId, setAcademicYearId] = useState<number | "">(scholarship?.academic_year ?? "");
  const [reason, setReason] = useState(scholarship?.reason ?? "");

  const { data: yearsData } = useAcademicYears();
  const { data: searchData } = useStudentSearch(studentQuery);

  const students = searchData?.results ?? [];
  const years = yearsData?.results ?? [];

  const { mutate: createMutate, isPending: isCreating } = useCreateScholarship();
  const { mutate: updateMutate, isPending: isUpdating } = useUpdateScholarship();

  const handleSubmit = () => {
    if (!studentId || !name || !discountValue || !academicYearId) {
      toast.error("Please fill in all required fields");
      return;
    }

    const payload = {
      student: studentId,
      name,
      discount_type: discountType,
      discount_value: parseFloat(discountValue),
      academic_year: academicYearId as number,
      reason,
    };

    if (isEdit && scholarship) {
      updateMutate(
        { id: scholarship.id, ...payload },
        { onSuccess: () => { toast.success("Scholarship updated!"); onClose(); }, onError: () => toast.error("Failed to update scholarship") },
      );
    } else {
      createMutate(
        payload,
        { onSuccess: () => { toast.success("Scholarship awarded!"); onClose(); }, onError: () => toast.error("Failed to create scholarship") },
      );
    }
  };

  const selectStudent = (s: StudentListItem) => {
    setStudentId(s.id);
    setStudentQuery(s.full_name);
  };

  return (
    <Modal
      open
      onClose={onClose}
      title={isEdit ? "Edit Scholarship" : "Award Scholarship"}
      description={isEdit ? `Updating ${scholarship!.name}` : "Grant a discount or scholarship to a student"}
      size="lg"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button onClick={handleSubmit} loading={isCreating || isUpdating} disabled={!studentId || !name || !discountValue || !academicYearId}>
            {isEdit ? "Update Scholarship" : "Award Scholarship"}
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        {/* Student selector */}
        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-slate-700">Student *</label>
          <Input
            placeholder="Search student by name or admission no…"
            value={studentQuery}
            onChange={(e) => { setStudentQuery(e.target.value); if (!isEdit) setStudentId(""); }}
            disabled={isEdit}
          />
          {studentQuery.length >= 2 && !studentId && students.length > 0 && (
            <div className="border border-slate-200 rounded-lg max-h-36 overflow-y-auto divide-y divide-slate-100">
              {students.map((s) => (
                <button
                  key={s.id}
                  type="button"
                  onClick={() => selectStudent(s)}
                  className="w-full text-left px-3 py-2 text-sm text-slate-700 hover:bg-indigo-50 transition-colors"
                >
                  {s.full_name} <span className="text-slate-400">({s.admission_number})</span>
                </button>
              ))}
            </div>
          )}
          {studentId && !isEdit && (
            <div className="flex items-center gap-2 text-xs text-green-600">
              <CheckCircleIcon className="h-3.5 w-3.5" />
              Student selected
            </div>
          )}
        </div>

        <Input label="Scholarship Name *" value={name} onChange={(e) => setName(e.target.value)} placeholder="e.g. Merit Scholarship 2025" />

        <div className="grid grid-cols-2 gap-4">
          <Select
            label="Discount Type *"
            value={discountType}
            onChange={(e) => setDiscountType(e.target.value as "percent" | "fixed")}
            options={[
              { value: "percent", label: "Percentage (%)" },
              { value: "fixed", label: "Fixed Amount ($)" },
            ]}
          />
          <Input
            label={discountType === "percent" ? "Discount Percentage *" : "Discount Amount *"}
            type="number"
            min={0}
            max={discountType === "percent" ? 100 : undefined}
            step="0.01"
            value={discountValue}
            onChange={(e) => setDiscountValue(e.target.value)}
            placeholder={discountType === "percent" ? "e.g. 25" : "e.g. 500"}
          />
        </div>

        <Select
          label="Academic Year *"
          value={academicYearId}
          onChange={(e) => setAcademicYearId(e.target.value ? Number(e.target.value) : "")}
          placeholder="Select academic year…"
          options={years.map((y) => ({ value: y.id, label: `${y.name}${y.is_current ? " (Current)" : ""}` }))}
        />

        <div className="flex flex-col gap-1.5">
          <label className="text-xs font-semibold text-slate-700">Reason</label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            rows={3}
            placeholder="Why is this scholarship being awarded?"
            className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-700 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-400 resize-y"
          />
        </div>
      </div>
    </Modal>
  );
}

// ─── Scholarships Panel ─────────────────────────────────────────────────────

export default function ScholarshipsPanel() {
  const [showForm, setShowForm] = useState(false);
  const [editingScholarship, setEditingScholarship] = useState<Scholarship | null>(null);
  const [togglingScholarship, setTogglingScholarship] = useState<Scholarship | null>(null);
  const [filterActive, setFilterActive] = useState<string>("all");

  const { data, isLoading } = useScholarships();
  const { mutate: toggleMutate, isPending: isToggling } = useToggleScholarship();

  let scholarships = data?.results ?? [];
  if (filterActive === "active") scholarships = scholarships.filter((s) => s.is_active);
  else if (filterActive === "inactive") scholarships = scholarships.filter((s) => !s.is_active);

  const handleToggle = (s: Scholarship) => {
    setTogglingScholarship(s);
  };

  const confirmToggle = () => {
    if (!togglingScholarship) return;
    const s = togglingScholarship;
    toggleMutate(
      { id: s.id, is_active: !s.is_active },
      {
        onSuccess: () => {
          toast.success(s.is_active ? "Scholarship deactivated" : "Scholarship activated");
          setTogglingScholarship(null);
        },
      },
    );
  };

  const columns: Column<Scholarship>[] = [
    {
      key: "student_name",
      header: "Student",
      render: (s) => <span className="font-medium text-slate-800">{s.student_name}</span>,
    },
    {
      key: "name",
      header: "Scholarship",
      render: (s) => <span className="text-slate-700">{s.name}</span>,
    },
    {
      key: "discount_type",
      header: "Type",
      render: (s) => (
        <Badge color={s.discount_type === "percent" ? "blue" : "purple"}>
          {s.discount_type === "percent" ? "% Off" : "$ Fixed"}
        </Badge>
      ),
    },
    {
      key: "discount_value",
      header: "Value",
      render: (s) => (
        <span className="font-semibold text-indigo-600">
          {s.discount_type === "percent" ? `${s.discount_value}%` : `$${Number(s.discount_value).toLocaleString()}`}
        </span>
      ),
    },
    {
      key: "approved_by_name",
      header: "Approved By",
      render: (s) => <span className="text-slate-600">{s.approved_by_name || "—"}</span>,
    },
    {
      key: "is_active",
      header: "Status",
      render: (s) => (
        <Badge color={s.is_active ? "green" : "slate"} dot>
          {s.is_active ? "Active" : "Inactive"}
        </Badge>
      ),
    },
    {
      key: "actions",
      header: "Actions",
      render: (s) => (
        <div className="flex gap-1">
          <button
            onClick={() => { setEditingScholarship(s); setShowForm(true); }}
            className="rounded-lg p-1.5 text-slate-400 hover:bg-indigo-50 hover:text-indigo-600 transition-colors"
            title="Edit"
          >
            <PencilIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => handleToggle(s)}
            className={`rounded-lg p-1.5 transition-colors ${
              s.is_active
                ? "text-slate-400 hover:bg-red-50 hover:text-red-600"
                : "text-slate-400 hover:bg-green-50 hover:text-green-600"
            }`}
            title={s.is_active ? "Deactivate" : "Activate"}
          >
            {s.is_active ? <XCircleIcon className="h-4 w-4" /> : <CheckCircleIcon className="h-4 w-4" />}
          </button>
        </div>
      ),
    },
  ];

  return (
    <div className="space-y-5">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-lg font-bold text-slate-900">Scholarships & Discounts</h2>
          <p className="text-sm text-slate-500 mt-0.5">{data?.count ?? 0} total scholarships</p>
        </div>
        <Button onClick={() => { setEditingScholarship(null); setShowForm(true); }} leftIcon={<PlusIcon className="h-4 w-4" />}>
          Award Scholarship
        </Button>
      </div>

      {/* Filter */}
      <div className="flex gap-2">
        {[
          { value: "all", label: "All" },
          { value: "active", label: "Active" },
          { value: "inactive", label: "Inactive" },
        ].map((opt) => (
          <button
            key={opt.value}
            onClick={() => setFilterActive(opt.value)}
            className={`rounded-lg px-3 py-1.5 text-xs font-semibold transition-colors ${
              filterActive === opt.value
                ? "bg-indigo-100 text-indigo-700"
                : "bg-slate-100 text-slate-500 hover:bg-slate-200"
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* Table */}
      {!isLoading && scholarships.length === 0 ? (
        <div className="rounded-xl bg-white shadow-sm border border-slate-100">
          <EmptyState
            icon={AcademicCapIcon}
            title="No scholarships awarded yet"
            description="Award scholarships to students to apply discounts on fee invoices"
          />
        </div>
      ) : (
        <div className="rounded-xl bg-white shadow-sm border border-slate-100 overflow-hidden">
          <DataTable<Scholarship>
            columns={columns}
            data={scholarships}
            loading={isLoading}
            emptyMessage="No scholarships match the current filter"
            rowKey={(s) => s.id}
          />
        </div>
      )}

      {showForm && (
        <ScholarshipFormModal
          scholarship={editingScholarship}
          onClose={() => { setShowForm(false); setEditingScholarship(null); }}
        />
      )}

      <ConfirmDialog
        open={!!togglingScholarship}
        title={togglingScholarship?.is_active ? "Deactivate Scholarship" : "Activate Scholarship"}
        message={`Are you sure you want to ${togglingScholarship?.is_active ? "deactivate" : "activate"} the scholarship "${togglingScholarship?.name ?? ""}" for ${togglingScholarship?.student_name ?? ""}?`}
        confirmLabel={togglingScholarship?.is_active ? "Deactivate" : "Activate"}
        confirmVariant={togglingScholarship?.is_active ? "danger" : "primary"}
        onConfirm={confirmToggle}
        onCancel={() => setTogglingScholarship(null)}
        loading={isToggling}
      />
    </div>
  );
}
