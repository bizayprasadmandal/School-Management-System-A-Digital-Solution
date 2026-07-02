/**
 * Admin Attendance Page — school-wide attendance overview with per-classroom drill-down
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { api } from "../../api/client";
import { useClassrooms, useCurrentAcademicYear } from "../../api/hooks";
import { Button, Badge, Select, DataTable, Spinner } from "../../components/common";
import type { BadgeColor } from "../../components/common";
import { percent, attendanceColor, fmt } from "../../utils";
import { useTitle } from "../../hooks";
import { ClipboardDocumentCheckIcon } from "@heroicons/react/24/outline";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from "recharts";

export default function AdminAttendancePage() {
  useTitle("Attendance");
  const [selectedDate, setSelectedDate] = useState(dayjs().format("YYYY-MM-DD"));
  const [selectedClassroom, setSelectedClassroom] = useState<number | undefined>();
  const { data: academicYear } = useCurrentAcademicYear();
  const { data: classroomsData } = useClassrooms();
  const classrooms = classroomsData?.results ?? [];

  // Fetch attendance for each classroom on the selected date
  const { data: summaries, isLoading } = useQuery({
    queryKey: ["admin-attendance-overview", selectedDate, classrooms.length],
    queryFn: async () => {
      if (!classrooms.length) return [];
      const results = await Promise.allSettled(
        classrooms.map(c =>
          api.get<any>("/attendance/classroom-summary/", { classroom_id: c.id, date: selectedDate })
            .then(d => ({ ...d, classroom: c }))
        )
      );
      return results
        .filter(r => r.status === "fulfilled")
        .map(r => (r as PromiseFulfilledResult<any>).value);
    },
    enabled: classrooms.length > 0,
  });

  // Student-level records for selected classroom
  const { data: records, isLoading: recLoading } = useQuery({
    queryKey: ["admin-attendance-detail", selectedClassroom, selectedDate],
    queryFn: () => api.get<any>("/attendance/", { classroom: selectedClassroom, date: selectedDate, page_size: 100 }),
    enabled: !!selectedClassroom,
  });

  const chartData = (summaries ?? []).map(s => ({
    name: `${s.classroom.grade_name} ${s.classroom.name}`,
    pct: s.total_students > 0 ? Math.round(s.breakdown.present / s.total_students * 100) : 0,
    present: s.breakdown?.present ?? 0,
    absent: s.breakdown?.absent ?? 0,
  }));

  const schoolAvg = chartData.length > 0
    ? Math.round(chartData.reduce((sum, d) => sum + d.pct, 0) / chartData.length)
    : 0;

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Attendance</h1>
          <p className="text-sm text-slate-500 mt-0.5">School-wide attendance monitoring</p>
        </div>
        <div className="flex items-center gap-3">
          <input type="date" value={selectedDate} onChange={e => setSelectedDate(e.target.value)}
            className="input w-44" max={dayjs().format("YYYY-MM-DD")} />
        </div>
      </div>

      {/* School summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "School Avg", value: percent(schoolAvg), color: attendanceColor(schoolAvg) },
          { label: "Total Classes", value: classrooms.length, color: "text-indigo-600" },
          { label: "Total Present", value: chartData.reduce((s,d) => s + d.present, 0), color: "text-green-600" },
          { label: "Total Absent", value: chartData.reduce((s,d) => s + d.absent, 0), color: "text-red-600" },
        ].map(({ label, value, color }) => (
          <div key={label} className="card p-4 text-center">
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
            <p className="text-xs text-slate-500 mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Bar chart */}
      {isLoading ? <div className="flex justify-center py-10"><Spinner /></div> : chartData.length > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="text-base font-semibold">Attendance by Classroom — {fmt.date(selectedDate)}</h2>
          </div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={220}>
              <BarChart data={chartData} margin={{ top: 4, right: 8, left: -20, bottom: 40 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="name" tick={{ fontSize: 10 }} angle={-35} textAnchor="end" interval={0} />
                <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} unit="%" />
                <Tooltip formatter={(v: number) => [`${v}%`, "Attendance"]} />
                <Bar dataKey="pct" radius={[4, 4, 0, 0]} name="Attendance">
                  {chartData.map((entry, i) => (
                    <Cell key={i} fill={entry.pct >= 90 ? "#22c55e" : entry.pct >= 75 ? "#f59e0b" : "#ef4444"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Classroom drill-down */}
      <div className="card">
        <div className="card-header">
          <h2 className="text-base font-semibold">Classroom Detail</h2>
          <Select placeholder="Select a classroom…" value={selectedClassroom ?? ""}
            onChange={e => setSelectedClassroom(Number(e.target.value) || undefined)}
            options={classrooms.map(c => ({ value: c.id, label: `${c.grade_name} ${c.name}` }))}
            className="w-48" />
        </div>
        {selectedClassroom && (
          recLoading ? <div className="p-8 flex justify-center"><Spinner /></div>
          : <DataTable
              columns={[
                { key: "student_name", header: "Student" },
                { key: "status", header: "Status", render: r => {
                  const s = ({ P:"Present", A:"Absent", L:"Late", E:"Excused" } as Record<string, string>)[r.status] ?? r.status;
                  const c = ({ P:"green", A:"red", L:"amber", E:"blue" } as Record<string, BadgeColor>)[r.status] ?? "slate";
                  return <Badge color={c} dot>{s}</Badge>;
                }},
                { key: "remarks", header: "Remarks", render: r => r.remarks || <span className="text-slate-400">—</span> },
              ]}
              data={(records?.results ?? []) as any[]}
              rowKey={r => r.id}
              emptyMessage="No attendance records for this classroom today"
            />
        )}
        {!selectedClassroom && (
          <div className="p-10 text-center text-slate-400">
            <ClipboardDocumentCheckIcon className="h-10 w-10 mx-auto mb-2 opacity-20" />
            <p className="text-sm">Select a classroom to view individual student attendance</p>
          </div>
        )}
      </div>
    </div>
  );
}
