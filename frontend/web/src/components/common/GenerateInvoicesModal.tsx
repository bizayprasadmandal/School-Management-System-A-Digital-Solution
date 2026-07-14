/**
 * GenerateInvoicesModal — Admin form to bulk-generate invoices
 * for all students in a grade associated with a fee structure.
 */

import React, { useState } from "react";
import { DocumentPlusIcon } from "@heroicons/react/24/outline";
import { Modal, Button, Select } from "./";
import { useFeeStructures, useAcademicYears, useBulkGenerateInvoices } from "../../api/hooks";
import toast from "react-hot-toast";

interface Props {
  open: boolean;
  onClose: () => void;
}

export default function GenerateInvoicesModal({ open, onClose }: Props) {
  const [feeStructureId, setFeeStructureId] = useState<number | "">("");
  const [academicYearId, setAcademicYearId] = useState<number | "">("");

  const { data: structuresData, isLoading: loadingStructures } = useFeeStructures();
  const { data: yearsData, isLoading: loadingYears } = useAcademicYears();
  const { mutate, isPending } = useBulkGenerateInvoices();

  const structures = structuresData?.results ?? [];
  const activeStructures = structures.filter((s) => s.is_active);
  const years = yearsData?.results ?? [];

  const selectedStructure = structures.find((s) => s.id === feeStructureId);

  const handleGenerate = () => {
    if (!feeStructureId || !academicYearId) return;

    mutate(
      { fee_structure_id: feeStructureId as number, academic_year_id: academicYearId as number },
      {
        onSuccess: (data) => {
          toast.success(data.detail || "Bulk invoice generation queued!");
          onClose();
        },
        onError: () => {
          toast.error("Failed to queue invoice generation.");
        },
      },
    );
  };

  return (
    <Modal
      open={open}
      onClose={onClose}
      title="Generate Invoices"
      description="Create invoices for all students in a grade based on a fee structure"
      size="md"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={handleGenerate}
            loading={isPending}
            disabled={!feeStructureId || !academicYearId}
          >
            Generate Invoices
          </Button>
        </>
      }
    >
      <div className="space-y-5">
        {/* Fee Structure */}
        {loadingStructures || loadingYears ? (
          <div className="flex items-center justify-center py-8 text-sm text-slate-500">
            <span className="animate-spin h-5 w-5 border-2 border-indigo-500 border-t-transparent rounded-full mr-2" />
            Loading fee structures…
          </div>
        ) : (
          <>
            <Select
              label="Fee Structure"
              value={feeStructureId}
              onChange={(e) => setFeeStructureId(e.target.value ? Number(e.target.value) : "")}
              placeholder="Select a fee structure…"
              options={activeStructures.map((s) => ({
                value: s.id,
                label: `${s.category_name} — ${s.grade_name} ($${Number(s.amount).toLocaleString()})`,
              }))}
            />

            <Select
              label="Academic Year"
              value={academicYearId}
              onChange={(e) => setAcademicYearId(e.target.value ? Number(e.target.value) : "")}
              placeholder="Select academic year…"
              options={years.map((y) => ({
                value: y.id,
                label: `${y.name}${y.is_current ? " (Current)" : ""}`,
              }))}
            />
          </>
        )}

        {/* Summary of what will be generated */}
        {selectedStructure && academicYearId && (
          <div className="rounded-lg bg-indigo-50 border border-indigo-100 p-4 space-y-1.5">
            <div className="flex items-center gap-2 text-indigo-700 font-medium text-sm">
              <DocumentPlusIcon className="h-4 w-4" />
              Summary
            </div>
            <div className="text-sm text-indigo-600 space-y-0.5">
              <p>Grade: <span className="font-medium">{selectedStructure.grade_name}</span></p>
              <p>Category: <span className="font-medium">{selectedStructure.category_name}</span></p>
              <p>Amount: <span className="font-medium">${Number(selectedStructure.amount).toLocaleString()}</span></p>
              <p>Due day: <span className="font-medium">{selectedStructure.due_day}th</span></p>
            </div>
          </div>
        )}
      </div>
    </Modal>
  );
}
