import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { Exam } from "../../types";
import { api } from "../../api/client";
import { Badge, SkeletonCard, Button, Modal, Input, Select } from "../../components/common";
import type { BadgeColor } from "../../components/common";
import {
  useCurrentAcademicYear,
  useGradeChangeProposals,
  useApproveGradeChangeProposal,
  useRejectGradeChangeProposal,
} from "../../api/hooks";
import { fmt, downloadFromUrl } from "../../utils";
import { useTitle } from "../../hooks";
import {
  PlusIcon,
  ArrowUpTrayIcon,
  ArrowDownTrayIcon,
  ChevronRightIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClipboardDocumentCheckIcon,
} from "@heroicons/react/24/outline";
import { useAuthStore } from "../../store/authStore";
import toast from "react-hot-toast";
import ImportCsvModal from "../../components/common/ImportCsvModal";
import type { GradeChangeProposal } from "../../types";

function CreateExamModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const { data: ay } = useCurrentAcademicYear();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [examType, setExamType] = useState("");

  const { mutate, isPending } = useMutation({
    mutationFn: () =>
      api.post("/gradebook/exams/", {
        name,
        description,
        academic_year: ay?.id,
        start_date: startDate,
        end_date: endDate,
        exam_type: Number(examType) || undefined,
        status: "scheduled",
      }),
    onSuccess: () => {
      toast.success("Exam created!");
      qc.invalidateQueries({ queryKey: ["exams"] });
      onClose();
    },
    onError: (err: any) => toast.error(err?.message ?? "Failed to create exam"),
  });

  return (
    <Modal
      open
      onClose={onClose}
      title="Create Exam"
      size="md"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button
            onClick={() => mutate()}
            loading={isPending}
            disabled={!name || !startDate || !endDate}
          >
            Create Exam
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        <Input
          label="Exam Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g. Midterm 2025"
          required
        />
        <Input
          label="Description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional description"
        />
        <Input
          label="Exam Type ID"
          type="number"
          value={examType}
          onChange={(e) => setExamType(e.target.value)}
          placeholder="Enter exam type ID (1=Midterm, 2=Final)"
        />
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="Start Date"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
            required
          />
          <Input
            label="End Date"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
            required
          />
        </div>
      </div>
    </Modal>
  );
}

/**
 * Admin review queue for grade changes proposed on published exams.
 */
function PendingGradeApprovals() {
  const { data, isLoading } = useGradeChangeProposals({ status: "proposed" });
  const approve = useApproveGradeChangeProposal();
  const reject = useRejectGradeChangeProposal();
  const proposals = data?.results ?? [];

  const handleApprove = (p: GradeChangeProposal) => {
    approve.mutate(p.id, {
      onSuccess: () => toast.success(`Approved change for ${p.student_name}`),
      onError: () => toast.error("Failed to approve change"),
    });
  };

  const handleReject = (p: GradeChangeProposal) => {
    const notes = window.prompt(`Reason for rejecting the change for ${p.student_name}?`) ?? "";
    reject.mutate(
      { id: p.id, notes },
      {
        onSuccess: () => toast.success(`Rejected change for ${p.student_name}`),
        onError: () => toast.error("Failed to reject change"),
      },
    );
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
      <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between dark:border-slate-700">
        <h2 className="text-base font-semibold flex items-center gap-2">
          <ClipboardDocumentCheckIcon className="h-5 w-5 text-amber-500" />
          Pending Grade Changes
        </h2>
        {proposals.length > 0 && <Badge color="amber">{proposals.length} awaiting review</Badge>}
      </div>
      {isLoading ? (
        <div className="p-6 text-center text-sm text-slate-400">Loading…</div>
      ) : proposals.length === 0 ? (
        <div className="p-6 text-center text-sm text-slate-400">
          No grade changes awaiting approval
        </div>
      ) : (
        <ul className="divide-y divide-slate-100 dark:divide-slate-700">
          {proposals.map((p) => (
            <li key={p.id} className="px-5 py-3 flex items-center gap-3">
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-slate-800 dark:text-slate-200">
                  {p.student_name}{" "}
                  <span className="font-mono text-xs text-slate-400">· {p.admission_number}</span>
                </p>
                <p className="text-xs text-slate-500 dark:text-slate-400">
                  {p.subject} — {p.exam}
                  <span
                    className={
                      p.action === "delete"
                        ? "ml-2 inline-flex rounded-full bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-300 px-2 py-0.5 text-[11px] font-medium"
                        : p.action === "create"
                          ? "ml-2 inline-flex rounded-full bg-indigo-50 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-300 px-2 py-0.5 text-[11px] font-medium"
                          : "ml-2 inline-flex rounded-full bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-300 px-2 py-0.5 text-[11px] font-medium"
                    }
                  >
                    {p.action === "delete" ? "Delete" : p.action === "create" ? "Add" : "Update"}
                  </span>
                </p>
                {p.action !== "delete" && (
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
                    {p.action === "create" ? "New marks" : "Current"}:{" "}
                    <span className="font-semibold text-slate-700 dark:text-slate-300">
                      {p.marks_obtained_current ?? "—"}
                    </span>
                    {" → "}
                    <span className="font-semibold text-slate-700 dark:text-slate-300">
                      {p.marks_obtained_new ?? "—"}
                    </span>
                    {" / "}
                    {p.max_marks}
                  </p>
                )}
                {p.reason && <p className="text-xs text-slate-400 italic mt-0.5">“{p.reason}”</p>}
              </div>
              <div className="flex items-center gap-1.5 flex-shrink-0">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleReject(p)}
                  leftIcon={<XCircleIcon className="h-4 w-4 text-red-500" />}
                >
                  Reject
                </Button>
                <Button
                  variant="primary"
                  size="sm"
                  onClick={() => handleApprove(p)}
                  leftIcon={<CheckCircleIcon className="h-4 w-4" />}
                  loading={approve.isPending}
                >
                  Approve
                </Button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default function ExamsPage() {
  useTitle("Examinations");
  const navigate = useNavigate();
  const [showCreate, setShowCreate] = useState(false);
  const [showImport, setShowImport] = useState(false);
  const [exportingExamId, setExportingExamId] = useState<string | null>(null);
  const { tokens } = useAuthStore();
  const qc = useQueryClient();
  const { data: ay } = useCurrentAcademicYear();
  const { data, isLoading } = useQuery({
    queryKey: ["exams", ay?.id],
    queryFn: () => api.get<{ results: Exam[] }>("/gradebook/exams/", { academic_year: ay?.id }),
    enabled: !!ay?.id,
  });
  const exams = data?.results ?? [];
  const STATUS_COLOR: Record<string, BadgeColor> = {
    scheduled: "blue",
    ongoing: "amber",
    completed: "green",
    cancelled: "slate",
  };

  const handleExportGrades = async (examId: string) => {
    setExportingExamId(examId);
    try {
      await downloadFromUrl(
        `${
          process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1"
        }/gradebook/grades/export-csv/?exam_id=${examId}`,
        `grades_exam_${examId}.csv`,
        tokens?.access ?? "",
      );
    } catch {
      toast.error("Export failed. Please try again.");
    } finally {
      setExportingExamId(null);
    }
  };

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Examinations</h1>
          <p className="text-sm text-slate-500 mt-0.5">Manage exams and assessment schedules</p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="md"
            leftIcon={<ArrowUpTrayIcon className="h-4 w-4" />}
            onClick={() => setShowImport(true)}
          >
            Import Grades
          </Button>
          <Button
            variant="primary"
            leftIcon={<PlusIcon className="h-4 w-4" />}
            onClick={() => setShowCreate(true)}
          >
            Create Exam
          </Button>
        </div>
      </div>
      {isLoading ? (
        <div className="grid grid-cols-1 gap-3">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      ) : (
        <div className="space-y-3">
          {exams.length === 0 ? (
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-12 text-center text-slate-400">
              No exams scheduled for this academic year.
            </div>
          ) : (
            exams.map(
              (e: {
                id: string;
                name: string;
                exam_type_name: string;
                start_date: string;
                end_date: string;
                schedule_count: number;
                status: string;
              }) => (
                <div
                  key={e.id}
                  onClick={() =>
                    navigate(`/admin/exams`, {
                      state: { selectedExamId: e.id, selectedExamName: e.name },
                    })
                  }
                  className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-4 flex items-center justify-between gap-4 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all cursor-pointer group"
                >
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                      {e.name}
                    </p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {e.exam_type_name} · {fmt.date(e.start_date)} – {fmt.date(e.end_date)} ·{" "}
                      {e.schedule_count} subjects
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      leftIcon={<ArrowDownTrayIcon className="h-3.5 w-3.5" />}
                      onClick={(ev) => {
                        ev.stopPropagation();
                        handleExportGrades(e.id);
                      }}
                      loading={exportingExamId === e.id}
                    >
                      Export
                    </Button>
                    <Badge color={STATUS_COLOR[e.status] ?? "slate"}>{e.status}</Badge>
                    <ChevronRightIcon className="h-4 w-4 text-slate-300 dark:text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </div>
              ),
            )
          )}
        </div>
      )}
      {/* Pending grade-change approvals */}
      <PendingGradeApprovals />

      {showCreate && <CreateExamModal onClose={() => setShowCreate(false)} />}

      <ImportCsvModal
        open={showImport}
        onClose={() => setShowImport(false)}
        endpoint="/gradebook/grades/import-csv/"
        invalidateQueries={[["gradebook"], ["grades"]]}
        helpText={`admission_number,exam_schedule_id,marks_obtained,is_absent,remarks
STU001,1,85,No,Good performance
STU002,1,72,No,Satisfactory`}
      />
    </div>
  );
}
