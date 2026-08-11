/**
 * Teacher Gradebook — Enter and manage student marks per exam
 */

import React, { useState, useCallback } from "react";
import { CheckCircleIcon, XCircleIcon } from "@heroicons/react/24/solid";
import { MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import { useExams, useClassrooms, useSubmitGrades, useCurrentAcademicYear } from "../../api/hooks";
import { Button, SkeletonTable } from "../../components/common";
import { api } from "../../api/client";
import { useQuery } from "@tanstack/react-query";
import type { StudentListItem } from "../../types";

interface GradeEntry {
  student_id: string;
  full_name: string;
  admission_number: string;
  marks_obtained: string;
  is_absent: boolean;
  remarks: string;
}

export default function TeacherGradebookPage() {
  const { data: academicYear } = useCurrentAcademicYear();
  const { data: examsData } = useExams(academicYear?.id ?? 0);
  const { data: classroomsData } = useClassrooms();
  const classrooms = classroomsData?.results ?? [];
  const exams = examsData?.results ?? [];

  const [selectedExam, setSelectedExam] = useState("");
  const [selectedClassroom, setSelectedClassroom] = useState<number | null>(null);
  const [selectedSubject, setSelectedSubject] = useState<number | null>(null);
  const [maxMarks, setMaxMarks] = useState(100);
  const [passingMarks, setPassingMarks] = useState(35);
  const [entries, setEntries] = useState<Record<string, GradeEntry>>({});
  const [search, setSearch] = useState("");
  const [saved, setSaved] = useState(false);
  const [pendingApproval, setPendingApproval] = useState(0);

  const submitGrades = useSubmitGrades();

  const { data: students, isLoading: studentsLoading } = useQuery<StudentListItem[]>({
    queryKey: ["classroom-students", selectedClassroom],
    queryFn: () => api.get(`/students/classrooms/${selectedClassroom}/students/`),
    enabled: !!selectedClassroom,
  });

  // Exam schedules for the subject selector (exam + classroom both required).
  const { data: schedulesData } = useQuery<unknown[]>({
    queryKey: ["exam-schedules", selectedExam, selectedClassroom],
    queryFn: () =>
      api.get(`/gradebook/exams/${selectedExam}/schedules/`, { classroom_id: selectedClassroom }),
    enabled: !!selectedExam && !!selectedClassroom,
  });
  const schedules = Array.isArray(schedulesData) ? (schedulesData as any[]) : [];

  // Reset subject when the exam or classroom changes.
  React.useEffect(() => {
    setSelectedSubject(null);
  }, [selectedExam, selectedClassroom]);

  React.useEffect(() => {
    if (students) {
      const init: Record<string, GradeEntry> = {};
      students.forEach((s) => {
        init[s.id] = {
          student_id: s.id,
          full_name: s.full_name,
          admission_number: s.admission_number,
          marks_obtained: "",
          is_absent: false,
          remarks: "",
        };
      });
      setEntries(init);
      setSaved(false);
      setPendingApproval(0);
    }
  }, [students]);

  const setField = useCallback((id: string, field: keyof GradeEntry, value: string | boolean) => {
    setEntries((prev) => ({ ...prev, [id]: { ...prev[id], [field]: value } }));
    setSaved(false);
  }, []);

  const handleSubmit = async () => {
    if (!selectedSubject) {
      toast.error("Please select a subject");
      return;
    }
    const grades = Object.values(entries).map((e) => ({
      student_id: e.student_id,
      marks_obtained: e.is_absent ? null : parseFloat(e.marks_obtained) || null,
      is_absent: e.is_absent,
      remarks: e.remarks,
    }));
    try {
      const result = await submitGrades.mutateAsync({ exam_schedule_id: selectedSubject, grades });
      const pending = (result as { pending_approval?: number })?.pending_approval ?? 0;
      setSaved(true);
      setPendingApproval(pending);
      if (pending > 0) {
        const applied = grades.length - pending;
        toast.success(
          applied > 0
            ? `${applied} saved, ${pending} submitted for admin approval`
            : `${pending} grades submitted for admin approval`,
        );
      } else {
        toast.success(`Grades saved for ${grades.length} students`);
      }
    } catch {
      toast.error("Failed to save grades. Please try again.");
    }
  };

  const filtered = Object.values(entries).filter(
    (e) =>
      !search ||
      e.full_name.toLowerCase().includes(search.toLowerCase()) ||
      e.admission_number.toLowerCase().includes(search.toLowerCase()),
  );

  const stats = {
    entered: Object.values(entries).filter((e) => e.marks_obtained !== "" || e.is_absent).length,
    total: Object.keys(entries).length,
    passing: Object.values(entries).filter(
      (e) => !e.is_absent && parseFloat(e.marks_obtained) >= passingMarks,
    ).length,
    failing: Object.values(entries).filter(
      (e) => !e.is_absent && e.marks_obtained !== "" && parseFloat(e.marks_obtained) < passingMarks,
    ).length,
    absent: Object.values(entries).filter((e) => e.is_absent).length,
    avgScore: (() => {
      const scored = Object.values(entries).filter((e) => !e.is_absent && e.marks_obtained !== "");
      if (!scored.length) return 0;
      return scored.reduce((s, e) => s + parseFloat(e.marks_obtained), 0) / scored.length;
    })(),
  };

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Gradebook</h1>
        <p className="text-sm text-slate-500 mt-1">Enter student marks for exams and assessments</p>
      </div>

      {/* Config panel */}
      <div className="rounded-xl bg-white p-5 shadow-sm border border-slate-100">
        <h2 className="text-sm font-semibold text-slate-700 mb-4">Exam Configuration</h2>
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-600">Exam</label>
            <select
              value={selectedExam}
              onChange={(e) => setSelectedExam(e.target.value)}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Select exam…</option>
              {exams.map((e) => (
                <option key={e.id} value={e.id}>
                  {e.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-600">Classroom</label>
            <select
              value={selectedClassroom ?? ""}
              onChange={(e) => setSelectedClassroom(Number(e.target.value) || null)}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Select class…</option>
              {classrooms.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.grade_name} {c.name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-600">Subject</label>
            <select
              value={selectedSubject ?? ""}
              onChange={(e) => {
                const id = Number(e.target.value) || null;
                setSelectedSubject(id);
                const sched = schedules.find((s) => Number(s.id) === id);
                if (sched?.max_marks) setMaxMarks(Number(sched.max_marks));
                if (sched?.passing_marks) setPassingMarks(Number(sched.passing_marks));
              }}
              disabled={!selectedExam || !selectedClassroom}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:bg-slate-50 disabled:text-slate-400 disabled:cursor-not-allowed"
            >
              <option value="">
                {!selectedExam || !selectedClassroom
                  ? "Select exam & class first…"
                  : "Select subject…"}
              </option>
              {schedules.map((s) => (
                <option key={s.id} value={s.id}>
                  {s.subject_name}
                </option>
              ))}
            </select>
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-600">Max Marks</label>
            <input
              type="number"
              min={1}
              max={1000}
              value={maxMarks}
              onChange={(e) => setMaxMarks(Number(e.target.value))}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-600">Passing Marks</label>
            <input
              type="number"
              min={0}
              max={maxMarks}
              value={passingMarks}
              onChange={(e) => setPassingMarks(Number(e.target.value))}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
        </div>
      </div>

      {/* Pending approval notice */}
      {pendingApproval > 0 && (
        <div className="flex items-start gap-3 rounded-xl border border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/30 p-4">
          <svg
            className="h-5 w-5 text-amber-500 flex-shrink-0 mt-0.5"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126ZM12 15.75h.007v.008H12v-.008Z"
            />
          </svg>
          <div className="flex-1">
            <p className="text-sm font-semibold text-amber-800 dark:text-amber-300">
              {pendingApproval} grade change{pendingApproval === 1 ? "" : "s"} awaiting admin
              approval
            </p>
            <p className="text-sm text-amber-700 dark:text-amber-400">
              These results were already published to students, so your edits are queued for review
              instead of being applied immediately.
            </p>
          </div>
        </div>
      )}

      {/* Stats row */}
      {Object.keys(entries).length > 0 && (
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-5">
          {[
            {
              label: "Entered",
              value: `${stats.entered}/${stats.total}`,
              color: "text-indigo-600 bg-indigo-50",
            },
            { label: "Passing", value: stats.passing, color: "text-green-600 bg-green-50" },
            { label: "Failing", value: stats.failing, color: "text-red-600 bg-red-50" },
            { label: "Absent", value: stats.absent, color: "text-amber-600 bg-amber-50" },
            {
              label: "Avg Score",
              value: `${stats.avgScore.toFixed(1)}/${maxMarks}`,
              color: "text-slate-600 bg-slate-50",
            },
          ].map(({ label, value, color }) => (
            <div key={label} className={`rounded-xl px-4 py-3 text-center ${color.split(" ")[1]}`}>
              <p className={`text-xl font-bold ${color.split(" ")[0]}`}>{value}</p>
              <p className="text-xs text-slate-500 mt-0.5">{label}</p>
            </div>
          ))}
        </div>
      )}

      {/* Student marks table */}
      {selectedClassroom && (
        <>
          <div className="flex items-center gap-3">
            <div className="relative flex-1 max-w-xs">
              <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
              <input
                type="search"
                placeholder="Search student…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full rounded-lg border border-slate-200 py-2 pl-9 pr-4 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </div>

          <div className="rounded-xl bg-white shadow-sm border border-slate-100 overflow-hidden">
            {studentsLoading ? (
              <SkeletonTable rows={8} cols={7} />
            ) : (
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-slate-100">
                  <thead className="bg-slate-50">
                    <tr>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">
                        #
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">
                        Student
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">
                        Absent
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">
                        Marks <span className="font-normal text-slate-400">/ {maxMarks}</span>
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">
                        %
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">
                        Result
                      </th>
                      <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase">
                        Remarks
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-50">
                    {filtered.map((entry, idx) => {
                      const marks = parseFloat(entry.marks_obtained);
                      const pct = !isNaN(marks) && maxMarks > 0 ? (marks / maxMarks) * 100 : null;
                      const pass = pct !== null && marks >= passingMarks;
                      return (
                        <tr
                          key={entry.student_id}
                          className={`hover:bg-slate-50/60 transition-colors ${
                            entry.is_absent ? "opacity-50" : ""
                          }`}
                        >
                          <td className="px-4 py-3 text-sm text-slate-400">{idx + 1}</td>
                          <td className="px-4 py-3">
                            <p className="text-sm font-medium text-slate-800">{entry.full_name}</p>
                            <p className="text-xs text-slate-400">{entry.admission_number}</p>
                          </td>
                          <td className="px-4 py-3">
                            <input
                              type="checkbox"
                              checked={entry.is_absent}
                              onChange={(e) =>
                                setField(entry.student_id, "is_absent", e.target.checked)
                              }
                              className="h-4 w-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                            />
                          </td>
                          <td className="px-4 py-3">
                            <input
                              type="number"
                              min={0}
                              max={maxMarks}
                              disabled={entry.is_absent}
                              value={entry.marks_obtained}
                              placeholder="—"
                              onChange={(e) =>
                                setField(entry.student_id, "marks_obtained", e.target.value)
                              }
                              className="w-24 rounded-lg border border-slate-200 px-2 py-1.5 text-sm text-center focus:outline-none focus:ring-2 focus:ring-indigo-400 disabled:bg-slate-100 disabled:cursor-not-allowed"
                            />
                          </td>
                          <td className="px-4 py-3 text-sm">
                            {pct !== null && !entry.is_absent ? (
                              <span
                                className={`font-medium ${
                                  pct >= 75
                                    ? "text-green-600"
                                    : pct >= (passingMarks / maxMarks) * 100
                                      ? "text-amber-600"
                                      : "text-red-600"
                                }`}
                              >
                                {pct.toFixed(1)}%
                              </span>
                            ) : (
                              <span className="text-slate-300">—</span>
                            )}
                          </td>
                          <td className="px-4 py-3">
                            {!entry.is_absent && entry.marks_obtained !== "" ? (
                              pass ? (
                                <CheckCircleIcon className="h-5 w-5 text-green-500" />
                              ) : (
                                <XCircleIcon className="h-5 w-5 text-red-500" />
                              )
                            ) : (
                              <span className="text-slate-300 text-sm">—</span>
                            )}
                          </td>
                          <td className="px-4 py-3">
                            <input
                              type="text"
                              placeholder="Note…"
                              value={entry.remarks}
                              onChange={(e) =>
                                setField(entry.student_id, "remarks", e.target.value)
                              }
                              className="w-32 rounded-lg border border-slate-200 px-2 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-400"
                            />
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="flex justify-end">
            <Button
              onClick={handleSubmit}
              disabled={submitGrades.isPending || saved}
              loading={submitGrades.isPending}
            >
              {saved ? "✓ Grades Saved" : "Save Grades"}
            </Button>
          </div>
        </>
      )}
    </div>
  );
}
