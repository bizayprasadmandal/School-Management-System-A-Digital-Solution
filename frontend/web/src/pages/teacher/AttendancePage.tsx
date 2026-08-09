/**
 * Teacher Attendance Page — Daily class attendance recording
 */

import React, { useState, useMemo } from "react";
import { CheckCircleIcon, XCircleIcon, ClockIcon } from "@heroicons/react/24/solid";
import { CheckIcon } from "@heroicons/react/24/outline";
import toast from "react-hot-toast";
import dayjs from "dayjs";
import { useClassrooms, useBulkRecordAttendance } from "../../api/hooks";
import { Button, SkeletonTable } from "../../components/common";
import type { AttendanceStatus, StudentListItem } from "../../types";
import { api } from "../../api/client";
import { useQuery } from "@tanstack/react-query";

type StatusOption = {
  value: AttendanceStatus;
  label: string;
  color: string;
  icon: React.ReactNode;
};

const STATUS_OPTIONS: StatusOption[] = [
  {
    value: "P",
    label: "Present",
    color: "bg-green-100 text-green-700 ring-green-300",
    icon: <CheckCircleIcon className="h-4 w-4" />,
  },
  {
    value: "A",
    label: "Absent",
    color: "bg-red-100 text-red-700 ring-red-300",
    icon: <XCircleIcon className="h-4 w-4" />,
  },
  {
    value: "L",
    label: "Late",
    color: "bg-amber-100 text-amber-700 ring-amber-300",
    icon: <ClockIcon className="h-4 w-4" />,
  },
  {
    value: "E",
    label: "Excused",
    color: "bg-blue-100 text-blue-700 ring-blue-300",
    icon: <CheckIcon className="h-4 w-4" />,
  },
];

interface StudentAttendanceEntry {
  student_id: string;
  full_name: string;
  admission_number: string;
  avatar?: string;
  status: AttendanceStatus;
  remarks: string;
}

export default function TeacherAttendancePage() {
  const today = dayjs().format("YYYY-MM-DD");
  const [selectedDate, setSelectedDate] = useState(today);
  const [selectedClassroom, setSelectedClassroom] = useState<number | null>(null);
  const [entries, setEntries] = useState<Record<string, StudentAttendanceEntry>>({});
  const [submitted, setSubmitted] = useState(false);

  const { data: classroomsData } = useClassrooms();
  const classrooms = classroomsData?.results ?? [];

  // Fetch students for selected classroom
  const { data: studentsData, isLoading: studentsLoading } = useQuery({
    queryKey: ["classroom-students", selectedClassroom],
    queryFn: () =>
      api.get<StudentListItem[]>(`/students/classrooms/${selectedClassroom}/students/`),
    enabled: !!selectedClassroom,
  });

  // Fetch existing attendance for the day
  // (keeping useClassroomAttendance imported for future drill-down feature)

  // Initialize entries when students load
  React.useEffect(() => {
    if (studentsData) {
      const initial: Record<string, StudentAttendanceEntry> = {};
      studentsData.forEach((s) => {
        initial[s.id] = {
          student_id: s.id,
          full_name: s.full_name,
          admission_number: s.admission_number,
          avatar: s.avatar,
          status: "P",
          remarks: "",
        };
      });
      setEntries(initial);
      setSubmitted(false);
    }
  }, [studentsData]);

  const mutate = useBulkRecordAttendance();

  const setStatus = (studentId: string, status: AttendanceStatus) => {
    setEntries((prev) => ({
      ...prev,
      [studentId]: { ...prev[studentId], status },
    }));
  };

  const setRemarks = (studentId: string, remarks: string) => {
    setEntries((prev) => ({
      ...prev,
      [studentId]: { ...prev[studentId], remarks },
    }));
  };

  const markAll = (status: AttendanceStatus) => {
    setEntries((prev) => {
      const updated = { ...prev };
      Object.keys(updated).forEach((id) => {
        updated[id] = { ...updated[id], status };
      });
      return updated;
    });
  };

  const stats = useMemo(() => {
    const list = Object.values(entries);
    return {
      present: list.filter((e) => e.status === "P").length,
      absent: list.filter((e) => e.status === "A").length,
      late: list.filter((e) => e.status === "L").length,
      excused: list.filter((e) => e.status === "E").length,
      total: list.length,
    };
  }, [entries]);

  const handleSubmit = async () => {
    if (!selectedClassroom) return;
    const records = Object.values(entries).map(({ student_id, status, remarks }) => ({
      student_id,
      status,
      remarks,
    }));
    try {
      await mutate.mutateAsync({ classroom_id: selectedClassroom, date: selectedDate, records });
      setSubmitted(true);
      toast.success(`Attendance recorded for ${records.length} students`);
    } catch {
      toast.error("Failed to record attendance. Please try again.");
    }
  };

  const studentList = Object.values(entries);

  return (
    <div className="space-y-5">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Record Attendance</h1>
        <p className="text-sm text-slate-500 mt-1">Mark student attendance for your class</p>
      </div>

      {/* Controls */}
      <div className="flex flex-wrap gap-4 rounded-xl bg-white p-4 shadow-sm border border-slate-100">
        <div className="flex flex-col gap-1">
          <label htmlFor="attendance-date" className="text-xs font-medium text-slate-600">
            Date
          </label>
          <input
            id="attendance-date"
            type="date"
            value={selectedDate}
            max={today}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          />
        </div>
        <div className="flex flex-col gap-1 flex-1 min-w-48">
          <label className="text-xs font-medium text-slate-600">Classroom</label>
          <select
            value={selectedClassroom ?? ""}
            onChange={(e) => setSelectedClassroom(Number(e.target.value) || null)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Select a classroom…</option>
            {classrooms.map((c) => (
              <option key={c.id} value={c.id}>
                {c.grade_name} {c.name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {selectedClassroom && studentList.length > 0 && (
        <>
          {/* Summary + bulk actions */}
          <div className="flex flex-wrap items-center justify-between gap-4 rounded-xl bg-white p-4 shadow-sm border border-slate-100">
            <div className="flex gap-6 text-sm">
              <span>
                <span className="font-semibold text-green-600">{stats.present}</span> Present
              </span>
              <span>
                <span className="font-semibold text-red-600">{stats.absent}</span> Absent
              </span>
              <span>
                <span className="font-semibold text-amber-600">{stats.late}</span> Late
              </span>
              <span>
                <span className="font-semibold text-blue-600">{stats.excused}</span> Excused
              </span>
              <span className="text-slate-400">/ {stats.total} total</span>
            </div>
            <div className="flex gap-2">
              <Button variant="ghost" size="sm" onClick={() => markAll("P")}>
                Mark All Present
              </Button>
              <Button variant="ghost" size="sm" onClick={() => markAll("A")}>
                Mark All Absent
              </Button>
            </div>
          </div>

          {/* Student list */}
          <div className="rounded-xl bg-white shadow-sm border border-slate-100 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-slate-100">
                <thead className="bg-slate-50">
                  <tr>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">
                      #
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">
                      Student
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">
                      Status
                    </th>
                    <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase tracking-wide">
                      Remarks
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-50">
                  {studentList.map((entry, idx) => (
                    <tr key={entry.student_id} className="hover:bg-slate-50/50 transition-colors">
                      <td className="px-4 py-3 text-sm text-slate-400">{idx + 1}</td>
                      <td className="px-4 py-3">
                        <div className="flex items-center gap-3">
                          {entry.avatar ? (
                            <img
                              src={entry.avatar}
                              alt=""
                              className="h-8 w-8 rounded-full object-cover"
                            />
                          ) : (
                            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 text-indigo-700 text-xs font-semibold">
                              {entry.full_name
                                .split(" ")
                                .map((n) => n[0])
                                .join("")
                                .slice(0, 2)}
                            </div>
                          )}
                          <div>
                            <p className="text-sm font-medium text-slate-800">{entry.full_name}</p>
                            <p className="text-xs text-slate-400">{entry.admission_number}</p>
                          </div>
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <div className="flex gap-1.5 flex-wrap">
                          {STATUS_OPTIONS.map((opt) => (
                            <button
                              key={opt.value}
                              onClick={() => setStatus(entry.student_id, opt.value)}
                              aria-pressed={entry.status === opt.value}
                              className={`flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ring-1 transition-all ${
                                entry.status === opt.value
                                  ? `${opt.color} ring-2 scale-105`
                                  : "bg-slate-100 text-slate-500 ring-slate-200 hover:bg-slate-200"
                              }`}
                            >
                              {opt.icon}
                              {opt.label}
                            </button>
                          ))}
                        </div>
                      </td>
                      <td className="px-4 py-3">
                        <input
                          type="text"
                          placeholder="Optional note…"
                          value={entry.remarks}
                          onChange={(e) => setRemarks(entry.student_id, e.target.value)}
                          className="w-full rounded-lg border border-slate-200 px-3 py-1.5 text-xs focus:outline-none focus:ring-2 focus:ring-indigo-400"
                        />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Submit */}
          <div className="flex justify-end">
            <Button
              onClick={handleSubmit}
              disabled={mutate.isPending || submitted}
              loading={mutate.isPending}
            >
              {submitted ? "✓ Attendance Saved" : "Save Attendance"}
            </Button>
          </div>
        </>
      )}

      {selectedClassroom && studentsLoading && <SkeletonTable rows={8} cols={4} />}

      {!selectedClassroom && (
        <div className="flex flex-col items-center justify-center py-20 text-center text-slate-400">
          <ClockIcon className="h-12 w-12 mb-3 opacity-30" />
          <p className="text-base">Select a classroom to start recording attendance</p>
        </div>
      )}
    </div>
  );
}
