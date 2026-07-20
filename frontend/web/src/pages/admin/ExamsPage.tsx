import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import type { Exam } from "../../types";
import { api } from "../../api/client";
import { Badge, SkeletonCard, Button, Modal, Input, Select } from "../../components/common";
import type { BadgeColor } from "../../components/common";
import { useCurrentAcademicYear } from "../../api/hooks";
import { fmt, downloadFromUrl } from "../../utils";
import { useTitle } from "../../hooks";
import { PlusIcon, ArrowUpTrayIcon, ArrowDownTrayIcon, ChevronRightIcon } from "@heroicons/react/24/outline";
import { useAuthStore } from "../../store/authStore";
import toast from "react-hot-toast";
import ImportCsvModal from "../../components/common/ImportCsvModal";

function CreateExamModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const { data: ay } = useCurrentAcademicYear();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [examType, setExamType] = useState("");

  const { mutate, isPending } = useMutation({
    mutationFn: () => api.post("/gradebook/exams/", {
      name, description, academic_year: ay?.id,
      start_date: startDate, end_date: endDate,
      exam_type: Number(examType) || undefined, status: "scheduled",
    }),
    onSuccess: () => { toast.success("Exam created!"); qc.invalidateQueries({ queryKey: ["exams"] }); onClose(); },
    onError: (err: any) => toast.error(err?.message ?? "Failed to create exam"),
  });

  return (
    <Modal open onClose={onClose} title="Create Exam" size="md"
      footer={<><Button variant="secondary" onClick={onClose}>Cancel</Button><Button onClick={() => mutate()} loading={isPending} disabled={!name || !startDate || !endDate}>Create Exam</Button></>}>
      <div className="space-y-4">
        <Input label="Exam Name" value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Midterm 2025" required />
        <Input label="Description" value={description} onChange={e => setDescription(e.target.value)} placeholder="Optional description" />
        <Input label="Exam Type ID" type="number" value={examType} onChange={e => setExamType(e.target.value)} placeholder="Enter exam type ID (1=Midterm, 2=Final)" />
        <div className="grid grid-cols-2 gap-4">
          <Input label="Start Date" type="date" value={startDate} onChange={e => setStartDate(e.target.value)} required />
          <Input label="End Date" type="date" value={endDate} onChange={e => setEndDate(e.target.value)} required />
        </div>
      </div>
    </Modal>
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
  const { data, isLoading } = useQuery({ queryKey:["exams",ay?.id], queryFn:()=>api.get<{results: Exam[]}>("/gradebook/exams/",{academic_year:ay?.id}), enabled:!!ay?.id });
  const exams = data?.results ?? [];
  const STATUS_COLOR: Record<string, BadgeColor> = { scheduled:"blue", ongoing:"amber", completed:"green", cancelled:"slate" };

  const handleExportGrades = async (examId: string) => {
    setExportingExamId(examId);
    try {
      await downloadFromUrl(
        `${process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1"}/gradebook/grades/export-csv/?exam_id=${examId}`,
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
        <div><h1 className="text-2xl font-bold text-slate-900">Examinations</h1><p className="text-sm text-slate-500 mt-0.5">Manage exams and assessment schedules</p></div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" size="md" leftIcon={<ArrowUpTrayIcon className="h-4 w-4" />} onClick={() => setShowImport(true)}>
            Import Grades
          </Button>
          <Button variant="primary" leftIcon={<PlusIcon className="h-4 w-4" />} onClick={() => setShowCreate(true)}>Create Exam</Button>
        </div>
      </div>
      {isLoading ? <div className="grid grid-cols-1 gap-3"><SkeletonCard /><SkeletonCard /><SkeletonCard /></div>
        : <div className="space-y-3">
            {exams.length === 0 ? <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-12 text-center text-slate-400">No exams scheduled for this academic year.</div>
              : exams.map((e: { id: string; name: string; exam_type_name: string; start_date: string; end_date: string; schedule_count: number; status: string }) => (
                <div key={e.id}
                  onClick={() => navigate(`/admin/exams`, { state: { selectedExamId: e.id, selectedExamName: e.name } })}
                  className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-4 flex items-center justify-between gap-4 hover:border-indigo-300 dark:hover:border-indigo-600 hover:shadow-md transition-all cursor-pointer group">
                  <div className="flex-1">
                    <p className="text-sm font-semibold text-slate-900 dark:text-white group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">{e.name}</p>
                    <p className="text-xs text-slate-500 mt-0.5">{e.exam_type_name} · {fmt.date(e.start_date)} – {fmt.date(e.end_date)} · {e.schedule_count} subjects</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      leftIcon={<ArrowDownTrayIcon className="h-3.5 w-3.5" />}
                      onClick={(ev) => { ev.stopPropagation(); handleExportGrades(e.id); }}
                      loading={exportingExamId === e.id}
                    >
                      Export
                    </Button>
                    <Badge color={STATUS_COLOR[e.status] ?? "slate"}>{e.status}</Badge>
                    <ChevronRightIcon className="h-4 w-4 text-slate-300 dark:text-slate-600 opacity-0 group-hover:opacity-100 transition-opacity" />
                  </div>
                </div>
              ))
            }
          </div>
      }
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
