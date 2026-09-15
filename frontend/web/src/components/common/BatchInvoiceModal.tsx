/**
 * BatchInvoiceModal — Generate invoices for all students in a grade for a fee structure.
 */
import React, { useState } from "react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Modal, Button } from "./index";
import toast from "react-hot-toast";
import {
  DocumentDuplicateIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";

interface FeeStructure {
  id: string;
  grade_name: string;
  category_name: string;
  amount: number;
  due_day: number;
  academic_year_name: string;
}

interface AcademicYear {
  id: string;
  name: string;
  is_current: boolean;
}

interface BatchInvoiceModalProps {
  open: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export default function BatchInvoiceModal({ open, onClose, onSuccess }: BatchInvoiceModalProps) {
  const [selectedStructure, setSelectedStructure] = useState<string>("");
  const [selectedYear, setSelectedYear] = useState<string>("");

  const { data: structures = [], isLoading: structuresLoading } = useQuery({
    queryKey: ["fee-structures-for-batch"],
    queryFn: async () => {
      const res = await api.get<{ results: FeeStructure[] }>("/fees/structures/", {
        is_active: true,
      });
      return res.results ?? [];
    },
    enabled: open,
  });

  const { data: years = [], isLoading: yearsLoading } = useQuery({
    queryKey: ["academic-years-for-batch"],
    queryFn: async () => {
      const res = await api.get<{ results: AcademicYear[] }>("/students/academic-years/");
      return res.results ?? [];
    },
    enabled: open,
  });

  const selectedStructureData = structures.find((s) => s.id === selectedStructure);

  const generateMutation = useMutation({
    mutationFn: () =>
      api.post("/fees/invoices/bulk-generate/", {
        fee_structure_id: selectedStructure,
        academic_year_id: selectedYear,
      }),
    onSuccess: (data: any) => {
      toast.success(`Bulk invoice generation queued! Task ID: ${data.task_id}`);
      onSuccess();
    },
    onError: (err: any) => {
      toast.error(err?.response?.data?.detail || "Failed to queue batch generation");
    },
  });

  const handleSubmit = () => {
    if (!selectedStructure || !selectedYear) {
      toast.error("Please select both a fee structure and academic year");
      return;
    }
    generateMutation.mutate();
  };

  return (
    <Modal open={open} onClose={onClose} title="Batch Invoice Generation" size="md">
      <div className="space-y-4">
        <p className="text-sm text-slate-500">
          Generate invoices for all active students in a grade for a specific fee structure. This
          will run as a background task.
        </p>

        {/* Academic Year */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Academic Year</label>
          {yearsLoading ? (
            <div className="h-10 rounded-lg bg-slate-100 animate-pulse" />
          ) : (
            <select
              value={selectedYear}
              onChange={(e) => setSelectedYear(e.target.value)}
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            >
              <option value="">Select academic year...</option>
              {years.map((y) => (
                <option key={y.id} value={y.id}>
                  {y.name} {y.is_current ? "(Current)" : ""}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Fee Structure */}
        <div>
          <label className="block text-sm font-medium text-slate-700 mb-1">Fee Structure</label>
          {structuresLoading ? (
            <div className="h-10 rounded-lg bg-slate-100 animate-pulse" />
          ) : (
            <select
              value={selectedStructure}
              onChange={(e) => setSelectedStructure(e.target.value)}
              className="w-full rounded-lg border border-slate-200 px-3 py-2 text-sm focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500"
            >
              <option value="">Select fee structure...</option>
              {structures.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.grade_name} — {s.category_name} — Rs. {s.amount.toLocaleString()} (Due:{" "}
                  {s.due_day})
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Preview */}
        {selectedStructureData && (
          <div className="rounded-lg bg-indigo-50 border border-indigo-100 p-4">
            <h4 className="text-sm font-semibold text-indigo-800 mb-2">Invoice Preview</h4>
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-indigo-600">Grade:</span>{" "}
                <span className="font-medium">{selectedStructureData.grade_name}</span>
              </div>
              <div>
                <span className="text-indigo-600">Category:</span>{" "}
                <span className="font-medium">{selectedStructureData.category_name}</span>
              </div>
              <div>
                <span className="text-indigo-600">Amount:</span>{" "}
                <span className="font-medium">
                  Rs. {selectedStructureData.amount.toLocaleString()}
                </span>
              </div>
              <div>
                <span className="text-indigo-600">Due Day:</span>{" "}
                <span className="font-medium">{selectedStructureData.due_day} of each month</span>
              </div>
            </div>
          </div>
        )}

        {/* Warning */}
        <div className="flex items-start gap-2 rounded-lg bg-amber-50 border border-amber-100 p-3">
          <ExclamationTriangleIcon className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-amber-700">
            <p className="font-medium">Important</p>
            <p className="mt-1">
              This will generate invoices for all active students in the selected grade. Duplicate
              invoices will not be created for students who already have an invoice for this fee
              structure and academic year.
            </p>
          </div>
        </div>

        {/* Actions */}
        <div className="flex justify-end gap-2 pt-2 border-t border-slate-100">
          <Button variant="ghost" onClick={onClose}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSubmit}
            disabled={!selectedStructure || !selectedYear || generateMutation.isPending}
            leftIcon={<DocumentDuplicateIcon className="h-4 w-4" />}
          >
            {generateMutation.isPending ? "Queuing..." : "Generate Invoices"}
          </Button>
        </div>
      </div>
    </Modal>
  );
}
