/**
 * Admin Attendance Page — school-wide attendance overview with per-classroom drill-down
 */
import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { api } from "../../api/client";
import { useClassrooms, useCurrentAcademicYear } from "../../api/hooks";
import {
  Button,
  Badge,
  Select,
  DataTable,
  SkeletonChart,
  SkeletonTable,
} from "../../components/common";
import type { BadgeColor } from "../../components/common";
import { percent, attendanceColor, fmt } from "../../utils";
import { toCsv, downloadCsv } from "../../utils";
import toast from "react-hot-toast";
import { useTitle } from "../../hooks";
import {
  ArrowDownTrayIcon,
  ArrowUpTrayIcon,
  ClipboardDocumentCheckIcon,
} from "@heroicons/react/24/outline";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import ImportCsvModal from "../../components/common/ImportCsvModal";

export default function AdminAttendancePage() {
  useTitle("Attendance");
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState(dayjs().format("YYYY-MM-DD"));
  const [selectedClassroom, setSelectedClassroom] = useState<number | undefined>();
  const [page, setPage] = useState(1);
  const [showImportModal, setShowImportModal] = useState(false);
  useCurrentAcademicYear();
  const { data: classroomsData } = useClassrooms();
  const classrooms = classroomsData?.results ?? [];

  // Fetch attendance for each classroom on the selected date
  const { data: summaries, isLoading } = useQuery({
    queryKey: ["admin-attendance-overview", selectedDate, classrooms.length],
    queryFn: async () => {
      if (!classrooms.length) return [];
      const results = await Promise.allSettled(
        classrooms.map((c) =>
          api
            .get<any>("/attendance/classroom-summary/", { classroom_id: c.id, date: selectedDate })
            .then((d) => ({ ...d, classroom: c })),
        ),
      );
      return results
        .filter((r) => r.status === "fulfilled")
        .map((r) => (r as PromiseFulfilledResult<any>).value);
    },
    enabled: classrooms.length > 0,
  });

  // Student-level records for selected classroom
  const { data: records, isLoading: recLoading } = useQuery({
    queryKey: ["admin-attendance-detail", selectedClassroom, selectedDate, page],
    queryFn: () =>
      api.get<any>("/attendance/", {
        classroom: selectedClassroom,
        date: selectedDate,
        page_size: 100,
        page,
      }),
    enabled: !!selectedClassroom,
  });

  const handleExportAttendance = () => {
    if (!records?.results?.length) {
      toast.error("No attendance data to export");
      return;
    }
    const cols = [
      { key: "student_name", label: "Student" },
      { key: "status", label: "Status" },
      { key: "remarks", label: "Remarks" },
    ];
    const statusLabels: Record<string, string> = {
      P: "Present",
      A: "Absent",
      L: "Late",
      E: "Excused",
      H: "Half Day",
    };
    const rows = (records?.results ?? []).map((r: any) => ({
      student_name: r.student_name,
      status: statusLabels[r.status] ?? r.status,
      remarks: r.remarks ?? "",
    }));
    const csv = toCsv(rows, cols);
    downloadCsv(csv, `attendance-${selectedDate}.csv`);
    toast.success("Attendance CSV exported");
  };

  // Reset to page 1 when switching classroom or date
  useEffect(() => {
    setPage(1);
  }, [selectedClassroom, selectedDate]);

  const chartData = (summaries ?? []).map((s) => ({
    name: `${s.classroom.grade_name} ${s.classroom.name}`,
    pct: s.total_students > 0 ? Math.round((s.breakdown.present / s.total_students) * 100) : 0,
    present: s.breakdown?.present ?? 0,
    absent: s.breakdown?.absent ?? 0,
  }));

  const schoolAvg =
    chartData.length > 0
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
          <Button
            variant="secondary"
            size="md"
            onClick={() => setShowImportModal(true)}
            leftIcon={<ArrowUpTrayIcon className="h-4 w-4" />}
          >
            Import CSV
          </Button>
          <Button
            variant="secondary"
            size="md"
            onClick={handleExportAttendance}
            leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />}
            disabled={!selectedClassroom}
          >
            Export CSV
          </Button>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm placeholder:text-slate-400 text-slate-900 transition focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-400 disabled:bg-slate-50 disabled:text-slate-400 disabled:cursor-not-allowed dark:bg-slate-800 dark:border-slate-600 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:ring-indigo-400 w-44"
            max={dayjs().format("YYYY-MM-DD")}
          />
        </div>
      </div>

      {/* School summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "School Avg", value: percent(schoolAvg), color: attendanceColor(schoolAvg) },
          { label: "Total Classes", value: classrooms.length, color: "text-indigo-600" },
          {
            label: "Total Present",
            value: chartData.reduce((s, d) => s + d.present, 0),
            color: "text-green-600",
          },
          {
            label: "Total Absent",
            value: chartData.reduce((s, d) => s + d.absent, 0),
            color: "text-red-600",
          },
        ].map(({ label, value, color }) => (
          <div
            key={label}
            className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-4 text-center"
          >
            <p className={`text-2xl font-bold ${color}`}>{value}</p>
            <p className="text-xs text-slate-500 mt-1">{label}</p>
          </div>
        ))}
      </div>

      {/* Bar chart */}
      {isLoading ? (
        <SkeletonChart className="m-4" />
      ) : (
        chartData.length > 0 && (
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
            <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between dark:border-slate-700">
              <h2 className="text-base font-semibold">
                Attendance by Classroom — {fmt.date(selectedDate)}
              </h2>
            </div>
            <div className="p-5">
              <ResponsiveContainer width="100%" height={220}>
                <BarChart data={chartData} margin={{ top: 4, right: 8, left: -20, bottom: 40 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis
                    dataKey="name"
                    tick={{ fontSize: 10 }}
                    angle={-35}
                    textAnchor="end"
                    interval={0}
                  />
                  <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} unit="%" />
                  <Tooltip formatter={(v: number) => [`${v}%`, "Attendance"]} />
                  <Bar dataKey="pct" radius={[4, 4, 0, 0]} name="Attendance">
                    {chartData.map((entry, i) => (
                      <Cell
                        key={i}
                        fill={entry.pct >= 90 ? "#22c55e" : entry.pct >= 75 ? "#f59e0b" : "#ef4444"}
                      />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        )
      )}

      {/* Classroom drill-down */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
        <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between dark:border-slate-700">
          <h2 className="text-base font-semibold">Classroom Detail</h2>
          <Select
            placeholder="Select a classroom…"
            value={selectedClassroom ?? ""}
            onChange={(e) => setSelectedClassroom(Number(e.target.value) || undefined)}
            options={classrooms.map((c) => ({ value: c.id, label: `${c.grade_name} ${c.name}` }))}
            className="w-48"
          />
        </div>
        {selectedClassroom &&
          (recLoading ? (
            <SkeletonTable rows={8} cols={4} />
          ) : (
            <DataTable
              columns={[
                { key: "student_name", header: "Student" },
                {
                  key: "status",
                  header: "Status",
                  render: (r) => {
                    const s =
                      (
                        { P: "Present", A: "Absent", L: "Late", E: "Excused" } as Record<
                          string,
                          string
                        >
                      )[r.status] ?? r.status;
                    const c =
                      (
                        { P: "green", A: "red", L: "amber", E: "blue" } as Record<
                          string,
                          BadgeColor
                        >
                      )[r.status] ?? "slate";
                    return (
                      <Badge color={c} dot>
                        {s}
                      </Badge>
                    );
                  },
                },
                {
                  key: "remarks",
                  header: "Remarks",
                  render: (r) => r.remarks || <span className="text-slate-400">—</span>,
                },
              ]}
              data={(records?.results ?? []) as any[]}
              rowKey={(r) => r.id}
              emptyMessage="No attendance records for this classroom today"
              page={page}
              total={records?.count ?? 0}
              pageSize={100}
              onPageChange={setPage}
              onRowClick={(r) => navigate(`/admin/students/${r.student_id}`)}
            />
          ))}
        {!selectedClassroom && (
          <div className="p-10 text-center text-slate-400">
            <ClipboardDocumentCheckIcon className="h-10 w-10 mx-auto mb-2 opacity-20" />
            <p className="text-sm">Select a classroom to view individual student attendance</p>
          </div>
        )}
      </div>

      {/* CSV import wizard */}
      <ImportCsvModal
        open={showImportModal}
        onClose={() => setShowImportModal(false)}
        endpoint="/attendance/import-csv/"
        invalidateQueries={[
          ["attendance"],
          ["admin-attendance-overview"],
          ["admin-attendance-detail"],
        ]}
        helpText={`admission_number,date,status,remarks,classroom_name
ADM-001,2024-06-10,P,,
ADM-002,2024-06-10,A,Family emergency,

Status codes: P (Present), A (Absent), L (Late), E (Excused), H (Half Day)
Rows are upserted per (student, date); unknown students become row errors.`}
      />
    </div>
  );
}
