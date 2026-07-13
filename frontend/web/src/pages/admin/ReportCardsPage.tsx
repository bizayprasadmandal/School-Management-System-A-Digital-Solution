/**
 * Admin Report Cards Page — generate and publish report cards per exam
 */
import React, { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import toast from "react-hot-toast";
import { api } from "../../api/client";
import { useCurrentAcademicYear } from "../../api/hooks";
import { Button, Badge, DataTable, SkeletonCard, SkeletonTable, EmptyState, Modal } from "../../components/common";
import { percent, gradeBg, fmt } from "../../utils";
import { useTitle } from "../../hooks";
import { DocumentTextIcon, RocketLaunchIcon, ArrowDownTrayIcon } from "@heroicons/react/24/outline";
export default function ReportCardsPage() {
  useTitle("Report Cards");
  const qc = useQueryClient();
  const [selectedExam, setSelectedExam] = useState<string | null>(null);
  const [publishConfirm, setPublishConfirm] = useState(false);
  const { data: academicYear } = useCurrentAcademicYear();

  const { data: exams, isLoading: examsLoading } = useQuery({
    queryKey: ["admin-rc-exams", academicYear?.id],
    queryFn: () => api.get<any>("/gradebook/exams/", { academic_year: academicYear?.id }),
    enabled: !!academicYear?.id,
  });

  const { data: reportCards, isLoading: rcLoading } = useQuery({
    queryKey: ["admin-rc-list", selectedExam],
    queryFn: () => api.get<any>(`/gradebook/report-cards/?page_size=50`),
    enabled: !!selectedExam,
  });

  const generateMutation = useMutation({
    mutationFn: (examId: string): Promise<{ task_id?: string }> =>
      api.post(`/gradebook/exams/${examId}/generate-report-cards/`, {}) as Promise<{ task_id?: string }>,
    onSuccess: (data: { task_id?: string }) => {
      toast.success(`Report card generation queued (task: ${data.task_id?.slice(0, 8)}…)`);
      setTimeout(() => qc.invalidateQueries({ queryKey: ["admin-rc-list"] }), 3000);
    },
    onError: () => toast.error("Failed to queue report card generation"),
  });

  const publishMutation = useMutation({
    mutationFn: (examId: string): Promise<{ published: number }> =>
      api.post(`/gradebook/exams/${examId}/publish-results/`, {}) as Promise<{ published: number }>,
    onSuccess: (data: { published: number }) => {
      toast.success(`${data.published} report cards published to students`);
      setPublishConfirm(false);
      qc.invalidateQueries({ queryKey: ["admin-rc-list"] });
    },
    onError: () => toast.error("Publish failed"),
  });

  const examList = exams?.results ?? [];
  const selected = examList.find((e: { id: string }) => e.id === selectedExam);
  const rcs = reportCards?.results ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Report Cards</h1>
        <p className="text-sm text-slate-500 mt-0.5">Generate, review, and publish student report cards</p>
      </div>

      {/* Exam selection */}
      {examsLoading ? <div className="grid grid-cols-3 gap-3 p-4"><SkeletonCard /><SkeletonCard /><SkeletonCard /></div> : (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {examList.length === 0 ? (
            <div className="col-span-3 card p-8 text-center text-slate-400">
              <DocumentTextIcon className="h-10 w-10 mx-auto mb-2 opacity-20" />
              <p>No exams found for {academicYear?.name}. Create exams first.</p>
            </div>
          ) : examList.map((exam: { id: string; name: string; status: string; exam_type_name: string; start_date: string; end_date: string; schedule_count: number }) => (
            <button key={exam.id} onClick={() => setSelectedExam(exam.id)}
              className={`card p-4 text-left hover:border-indigo-300 transition-colors ${selectedExam === exam.id ? "border-indigo-500 ring-2 ring-indigo-500 ring-offset-1" : ""}`}>
              <div className="flex items-start justify-between gap-2 mb-2">
                <p className="text-sm font-bold text-slate-900">{exam.name}</p>
                <Badge color={exam.status === "completed" ? "green" : exam.status === "ongoing" ? "amber" : "slate"}>
                  {exam.status}
                </Badge>
              </div>
              <p className="text-xs text-slate-500">{exam.exam_type_name}</p>
              <p className="text-xs text-slate-500 mt-0.5">{fmt.date(exam.start_date)} – {fmt.date(exam.end_date)}</p>
              <p className="text-xs text-slate-400 mt-2">{exam.schedule_count} subjects scheduled</p>
            </button>
          ))}
        </div>
      )}

      {/* Action bar for selected exam */}
      {selected && (
        <div className="card p-4 flex items-center justify-between flex-wrap gap-3">
          <div>
            <p className="text-sm font-semibold text-slate-900">{selected.name}</p>
            <p className="text-xs text-slate-500">Select an action for this exam</p>
          </div>
          <div className="flex gap-2">
            <Button variant="secondary"
              leftIcon={<RocketLaunchIcon className="h-4 w-4" />}
              loading={generateMutation.isPending}
              onClick={() => generateMutation.mutate(selected.id)}>
              Generate Report Cards
            </Button>
            <Button variant="primary"
              leftIcon={<DocumentTextIcon className="h-4 w-4" />}
              onClick={() => setPublishConfirm(true)}>
              Publish to Students
            </Button>
          </div>
        </div>
      )}

      {/* Report cards table */}
      {selectedExam && (
        <div className="card">
          <div className="card-header">
            <h2 className="text-base font-semibold">Report Cards — {selected?.name}</h2>
            <Badge color="slate">{reportCards?.count ?? 0} total</Badge>
          </div>            {rcLoading ? <SkeletonTable rows={6} cols={5} className="m-4" />
            : rcs.length === 0
            ? <div className="p-8"><EmptyState icon={DocumentTextIcon} title="No report cards yet" description="Click 'Generate Report Cards' to compute results for all students." /></div>
            : <DataTable
                columns={[
                  { key: "student_name", header: "Student" },
                  { key: "student_admission_number", header: "Adm #", render: r => <span className="font-mono text-xs">{r.student_admission_number}</span> },
                  { key: "percentage", header: "Score", render: r => <span className={`text-xs font-bold px-2 py-1 rounded-full ${gradeBg(Number(r.percentage))}`}>{percent(Number(r.percentage))}</span> },
                  { key: "grade_letter", header: "Grade", render: r => <Badge color="indigo">{r.grade_letter}</Badge> },
                  { key: "obtained_marks", header: "Marks", render: r => `${r.obtained_marks}/${r.total_marks}` },
                  { key: "rank_in_class", header: "Rank", render: r => r.rank_in_class ? `#${r.rank_in_class}` : "—" },
                  { key: "status", header: "Status", render: r => <Badge color={r.status === "published" ? "green" : r.status === "draft" ? "amber" : "slate"}>{r.status}</Badge> },
                  { key: "pdf_url", header: "PDF", render: r => r.pdf_url
                    ? <a href={r.pdf_url} target="_blank" rel="noreferrer" className="text-indigo-600 text-xs font-medium hover:underline flex items-center gap-1"><ArrowDownTrayIcon className="h-3.5 w-3.5" />Download</a>
                    : <span className="text-slate-400 text-xs">Not ready</span> },
                ]}
                data={rcs as any[]} rowKey={r => r.id}
              />
          }
        </div>
      )}

      {/* Publish confirmation */}
      <Modal open={publishConfirm} onClose={() => setPublishConfirm(false)} title="Publish Report Cards" size="sm"
        footer={
          <>
            <Button variant="secondary" onClick={() => setPublishConfirm(false)}>Cancel</Button>
            <Button variant="primary" loading={publishMutation.isPending} onClick={() => publishMutation.mutate(selectedExam!)}>
              Publish Now
            </Button>
          </>
        }>
        <p className="text-sm text-slate-600">
          This will publish all <strong>draft</strong> report cards for <strong>{selected?.name}</strong> and notify students and parents.
          This action cannot be easily reversed.
        </p>
      </Modal>
    </div>
  );
}
