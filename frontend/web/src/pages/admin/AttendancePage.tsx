/**
 * Admin Attendance Page — school-wide attendance overview with dashboard analytics,
 * weekly trends, at-risk students, and per-classroom drill-down
 */
import React, { useState, useEffect, useCallback, useMemo, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { api } from "../../api/client";
import {
  useClassrooms,
  useCurrentAcademicYear,
  useAttendanceDashboard,
  useAtRiskAttendanceStudents,
} from "../../api/hooks";
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
  ExclamationTriangleIcon,
  ChartBarIcon,
  ClockIcon,
  UserGroupIcon,
} from "@heroicons/react/24/outline";
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
  AreaChart,
  Area,
} from "recharts";
import ImportCsvModal from "../../components/common/ImportCsvModal";
import type { AttendanceDashboard, AtRiskAttendanceResponse } from "../../types";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useBulkSelect } from "../../hooks/useBulkSelect";
import { InfiniteScroll } from "../../components/common/InfiniteScroll";
import {
  KeyboardShortcutHelp,
  useShortcutHelp,
} from "../../components/common/KeyboardShortcutHelp";
import { Modal } from "../../components/common";
import {
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  MagnifyingGlassIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  CheckCircleIcon,
  XCircleIcon,
  DocumentArrowDownIcon,
  AdjustmentsHorizontalIcon,
  QrCodeIcon,
  TrophyIcon,
  WrenchScrewdriverIcon,
  UserMinusIcon,
  DocumentChartBarIcon,
  Cog6ToothIcon,
  FingerPrintIcon,
  CreditCardIcon,
  MapPinIcon,
  MapIcon,
  CalendarDaysIcon,
  CheckBadgeIcon,
  ScaleIcon,
  PaperAirplaneIcon,
  UserPlusIcon,
  DocumentTextIcon,
  ShieldExclamationIcon,
} from "@heroicons/react/24/outline";

function OverviewTab() {
  const navigate = useNavigate();
  const [selectedDate, setSelectedDate] = useState(dayjs().format("YYYY-MM-DD"));
  const [selectedClassroom, setSelectedClassroom] = useState<number | undefined>();
  const [page, setPage] = useState(1);
  const [showImportModal, setShowImportModal] = useState(false);
  const [showDashboard, setShowDashboard] = useState(true);
  useCurrentAcademicYear();
  const { data: classroomsData } = useClassrooms();
  const classrooms = classroomsData?.results ?? [];

  // Dashboard analytics. The endpoint returns a rich object; degrade to "no
  // dashboard" instead of crashing if the payload is unexpectedly shaped.
  const { data: dashboardRaw, isLoading: dashboardLoading } = useAttendanceDashboard();
  const dashboard = dashboardRaw?.today ? dashboardRaw : undefined;
  const { data: atRiskData } = useAtRiskAttendanceStudents(75, 30);

  // Fetch attendance for each classroom on the selected date
  const { data: summaries, isLoading } = useQuery({
    queryKey: ["admin-attendance-overview", selectedDate, classrooms.length],
    queryFn: async () => {
      if (!classrooms.length) return [];
      const results = await Promise.allSettled(
        classrooms.map((c) =>
          api
            .get<any>("/attendance/classroom-summary/", {
              classroom_id: c.id,
              date: selectedDate,
            })
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

  const handleExportAttendance = useCallback(async () => {
    try {
      const response = await api.get<any>("/attendance/export/", {
        date_from: selectedDate,
        date_to: selectedDate,
        classroom_id: selectedClassroom,
        format: "csv",
      });
      if (response.csv_data) {
        downloadCsv(response.csv_data, `attendance-${selectedDate}.csv`);
        toast.success(`Exported ${response.count} records`);
      } else {
        toast.error("No data to export");
      }
    } catch (error) {
      toast.error("Export failed");
    }
  }, [selectedDate, selectedClassroom]);

  const handleExportRange = useCallback(async (days: number) => {
    const dateFrom = dayjs().subtract(days, "day").format("YYYY-MM-DD");
    const dateTo = dayjs().format("YYYY-MM-DD");
    try {
      const response = await api.get<any>("/attendance/export/", {
        date_from: dateFrom,
        date_to: dateTo,
        format: "csv",
      });
      if (response.csv_data) {
        downloadCsv(response.csv_data, `attendance-${dateFrom}-to-${dateTo}.csv`);
        toast.success(`Exported ${response.count} records for last ${days} days`);
      } else {
        toast.error("No data to export");
      }
    } catch (error) {
      toast.error("Export failed");
    }
  }, []);

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
        <div className="flex items-center gap-3">
          <Button
            variant="secondary"
            size="md"
            onClick={() => setShowImportModal(true)}
            leftIcon={<ArrowUpTrayIcon className="h-4 w-4" />}
          >
            Import CSV
          </Button>
          <div className="relative group">
            <Button
              variant="secondary"
              size="md"
              onClick={handleExportAttendance}
              leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />}
            >
              Export CSV
            </Button>
            <div className="absolute right-0 mt-1 w-48 bg-white rounded-lg shadow-lg border border-slate-200 py-1 z-10 hidden group-hover:block">
              <button
                onClick={() => handleExportRange(7)}
                className="w-full px-4 py-2 text-left text-sm hover:bg-slate-50"
              >
                Last 7 days
              </button>
              <button
                onClick={() => handleExportRange(30)}
                className="w-full px-4 py-2 text-left text-sm hover:bg-slate-50"
              >
                Last 30 days
              </button>
              <button
                onClick={() => handleExportRange(90)}
                className="w-full px-4 py-2 text-left text-sm hover:bg-slate-50"
              >
                Last 90 days
              </button>
            </div>
          </div>
          <input
            type="date"
            value={selectedDate}
            onChange={(e) => setSelectedDate(e.target.value)}
            className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm placeholder:text-slate-400 text-slate-900 transition focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-400 disabled:bg-slate-50 disabled:text-slate-400 disabled:cursor-not-allowed dark:bg-slate-800 dark:border-slate-600 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:ring-indigo-400 w-44"
            max={dayjs().format("YYYY-MM-DD")}
          />
        </div>
      </div>
      {/* Dashboard Toggle */}
      <div className="flex items-center gap-2">
        <button
          onClick={() => setShowDashboard(!showDashboard)}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
            showDashboard
              ? "bg-indigo-100 text-indigo-700"
              : "bg-slate-100 text-slate-600 hover:bg-slate-200"
          }`}
        >
          <ChartBarIcon className="h-4 w-4 inline mr-1" />
          Dashboard View
        </button>
      </div>
      {/* Dashboard Analytics Section */}{" "}
      {showDashboard && dashboard && !dashboardLoading && (
        <div className="space-y-6">
          {/* Today's Stats */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 p-4 text-center">
              <p className="text-2xl font-bold text-indigo-600">{dashboard.today?.recorded ?? 0}</p>
              <p className="text-xs text-slate-500 mt-1">Recorded Today</p>
            </div>
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 p-4 text-center">
              {" "}
              <p className="text-2xl font-bold text-green-600">{dashboard.today?.present ?? 0}</p>
              <p className="text-xs text-slate-500 mt-1">Present</p>
            </div>
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 p-4 text-center">
              {" "}
              <p className="text-2xl font-bold text-red-600">{dashboard.today?.absent ?? 0}</p>
              <p className="text-xs text-slate-500 mt-1">Absent</p>
            </div>
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 p-4 text-center">
              {" "}
              <p className="text-2xl font-bold text-amber-600">{dashboard.today?.late ?? 0}</p>
              <p className="text-xs text-slate-500 mt-1">Late</p>
            </div>
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 p-4 text-center">
              {" "}
              <p className="text-2xl font-bold text-blue-600">
                {dashboard.today?.percentage ?? 0}%
              </p>
              <p className="text-xs text-slate-500 mt-1">Attendance Rate</p>
            </div>
          </div>

          {/* Weekly Trend Chart */}
          {(dashboard?.weekly_trend ?? []).length > 0 && (
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700">
              <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700">
                <h2 className="text-base font-semibold flex items-center gap-2">
                  <ClockIcon className="h-5 w-5 text-slate-400" />
                  Weekly Attendance Trend
                </h2>
              </div>
              <div className="p-5">
                <ResponsiveContainer width="100%" height={200}>
                  <AreaChart
                    data={dashboard?.weekly_trend ?? []}
                    margin={{ top: 4, right: 8, left: -20, bottom: 4 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="day_name" tick={{ fontSize: 11 }} />
                    <YAxis tick={{ fontSize: 11 }} domain={[0, 100]} unit="%" />
                    <Tooltip formatter={(v: number) => [`${v}%`, "Attendance"]} />
                    <Area
                      type="monotone"
                      dataKey="percentage"
                      stroke="#6366f1"
                      fill="#818cf8"
                      fillOpacity={0.3}
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>
          )}

          {/* At-Risk Students */}
          {(dashboard?.at_risk_students ?? []).length > 0 && (
            <div className="bg-white rounded-2xl border border-red-100 shadow-sm dark:bg-slate-800 dark:border-red-900">
              <div className="px-5 py-4 border-b border-red-100 dark:border-red-900 flex items-center justify-between">
                <h2 className="text-base font-semibold flex items-center gap-2 text-red-700 dark:text-red-400">
                  <ExclamationTriangleIcon className="h-5 w-5" />
                  At-Risk Students ({(dashboard?.at_risk_students ?? []).length})
                </h2>
                <span className="text-xs text-slate-500">Attendance below 75%</span>
              </div>
              <div className="p-5">
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="text-left text-slate-500 border-b border-slate-100">
                        <th className="pb-2 font-medium">Student</th>
                        <th className="pb-2 font-medium">Admission #</th>
                        <th className="pb-2 font-medium text-center">Attendance</th>
                        <th className="pb-2 font-medium text-center">Present/Total</th>
                      </tr>
                    </thead>
                    <tbody>
                      {(dashboard?.at_risk_students ?? []).map((student) => (
                        <tr
                          key={student.student_id}
                          className="border-b border-slate-50 hover:bg-slate-50 cursor-pointer"
                          onClick={() => navigate(`/admin/students/${student.student_id}`)}
                        >
                          <td className="py-2 font-medium text-slate-900">{student.name}</td>
                          <td className="py-2 text-slate-500">{student.admission_number}</td>
                          <td className="py-2 text-center">
                            <Badge color={student.attendance_percentage < 60 ? "red" : "amber"} dot>
                              {student.attendance_percentage}%
                            </Badge>
                          </td>
                          <td className="py-2 text-center text-slate-500">
                            {student.present_days}/{student.total_days}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Pending Leaves */}
          {(dashboard?.pending_leaves ?? 0) > 0 && (
            <div className="bg-amber-50 rounded-2xl border border-amber-200 p-4 flex items-center gap-3">
              <ExclamationTriangleIcon className="h-5 w-5 text-amber-600" />
              <p className="text-sm text-amber-800">
                <span className="font-semibold">{dashboard?.pending_leaves ?? 0}</span> pending
                leave request(s) need your review
              </p>
            </div>
          )}
        </div>
      )}
      {/* School summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          {
            label: "School Avg",
            value: percent(schoolAvg),
            color: attendanceColor(schoolAvg),
          },
          {
            label: "Total Classes",
            value: classrooms.length,
            color: "text-indigo-600",
          },
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
            options={classrooms.map((c) => ({
              value: c.id,
              label: `${c.grade_name} ${c.name}`,
            }))}
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
                        {
                          P: "Present",
                          A: "Absent",
                          L: "Late",
                          E: "Excused",
                        } as Record<string, string>
                      )[r.status] ?? r.status;
                    const c =
                      (
                        {
                          P: "green",
                          A: "red",
                          L: "amber",
                          E: "blue",
                        } as Record<string, BadgeColor>
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

// =============================================================================
// Attendance entity management (config-driven)
// =============================================================================

type FieldType = "text" | "number" | "date" | "datetime" | "select" | "textarea" | "bool";

interface FieldSpec {
  key: string;
  label: string;
  type?: FieldType;
  options?: [string, string][];
  card?: boolean; // show as meta row on card
  badge?: boolean; // render as colored badge
  main?: boolean; // card title
  subtitle?: boolean; // card subtitle
  skipForm?: boolean; // display-only, exclude from form
  full?: boolean; // full-width in form
}

interface EntityAction {
  label: string;
  url: (id: string | number) => string;
  confirm?: string;
  kind: "approve" | "reject" | "info";
}

interface EntityConfig {
  key: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
  endpoint: string;
  titleField: string;
  subtitleField?: string;
  fields: FieldSpec[];
  toggleField?: string;
  actions?: EntityAction[];
  readOnly?: boolean;
  searchKeys?: string[];
}

const STATUS_ATT = [
  ["P", "Present"],
  ["A", "Absent"],
  ["L", "Late"],
  ["E", "Excused"],
  ["H", "Half Day"],
] as [string, string][];
const STATUS_FLOW = [
  ["pending", "Pending"],
  ["approved", "Approved"],
  ["rejected", "Rejected"],
] as [string, string][];
const STATUS_GENERIC = [
  ["active", "Active"],
  ["inactive", "Inactive"],
  ["completed", "Completed"],
  ["cancelled", "Cancelled"],
  ["planned", "Planned"],
  ["in_progress", "In Progress"],
] as [string, string][];
const BOOL_OPTS = [
  ["true", "Yes"],
  ["false", "No"],
] as [string, string][];

const BADGE_COLORS: Record<string, string> = {
  P: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  present: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  approved: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  active: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  completed: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  paid: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  verified: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  low: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  A: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  absent: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  rejected: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  cancelled: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  critical: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  overdue: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
  L: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  late: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  pending: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  in_progress: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  medium: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  warning_only: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  E: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  excused: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  planned: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  fingerprint: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  high: "bg-orange-100 text-orange-700 dark:bg-orange-900/40 dark:text-orange-300",
  H: "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300",
};

const inputCls =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200";
const labelCls = "mb-1 block text-sm font-medium text-slate-700 dark:text-slate-300";

function StatusBadge({ value, colors }: { value: string; colors?: Record<string, string> }) {
  const map = colors ?? BADGE_COLORS;
  const key = String(value ?? "").toLowerCase();
  return (
    <span
      className={`inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium ${
        map[key] ?? "bg-slate-100 text-slate-600 dark:bg-slate-700 dark:text-slate-300"
      }`}
    >
      {String(value ?? "—").replace(/_/g, " ")}
    </span>
  );
}

function Toggle({ checked, onChange }: { checked: boolean; onChange: () => void }) {
  return (
    <button
      type="button"
      onClick={onChange}
      className={`relative inline-flex h-5 w-9 shrink-0 items-center rounded-full transition-colors ${
        checked ? "bg-indigo-600" : "bg-slate-300 dark:bg-slate-600"
      }`}
      aria-label={checked ? "Active" : "Inactive"}
    >
      <span
        className={`inline-block h-3.5 w-3.5 transform rounded-full bg-white transition-transform ${
          checked ? "translate-x-[18px]" : "translate-x-[3px]"
        }`}
      />
    </button>
  );
}

function CardSkeleton() {
  return (
    <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {[1, 2, 3, 4, 5, 6].map((i) => (
        <div
          key={i}
          className="relative h-32 overflow-hidden rounded-xl bg-slate-100 dark:bg-slate-800"
        >
          <div
            className="absolute inset-0 animate-shimmer bg-gradient-to-r from-transparent via-slate-200/50 to-transparent dark:via-slate-600/30"
            style={{ backgroundSize: "200% 100%" }}
          />
        </div>
      ))}
    </div>
  );
}

function formatValue(value: unknown, spec: FieldSpec): string {
  if (value === null || value === undefined || value === "") return "—";
  if (spec.type === "bool") {
    return String(value) === "true" ? "Yes" : "No";
  }
  if (spec.type === "select" && spec.options) {
    const found = spec.options.find(([v]) => v === value);
    return found ? found[1] : String(value);
  }
  if (spec.type === "date" && typeof value === "string") {
    return dayjs(value).format("MMM D, YYYY");
  }
  if (spec.type === "datetime" && typeof value === "string") {
    return dayjs(value).format("MMM D, YYYY h:mm A");
  }
  return String(value);
}

function FormField({
  spec,
  value,
  onChange,
}: {
  spec: FieldSpec;
  value: unknown;
  onChange: (v: unknown) => void;
}) {
  const type = spec.type ?? "text";
  if (type === "select") {
    return (
      <div className={spec.full ? "sm:col-span-2" : undefined}>
        <label className={labelCls}>{spec.label}</label>
        <select
          className={inputCls}
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
        >
          <option value="">— Select —</option>
          {(spec.options ?? []).map(([v, l]) => (
            <option key={v} value={v}>
              {l}
            </option>
          ))}
        </select>
      </div>
    );
  }
  if (type === "bool") {
    return (
      <div className={spec.full ? "sm:col-span-2" : undefined}>
        <label className={labelCls}>{spec.label}</label>
        <select
          className={inputCls}
          value={value ? "true" : "false"}
          onChange={(e) => onChange(e.target.value === "true")}
        >
          <option value="true">Yes</option>
          <option value="false">No</option>
        </select>
      </div>
    );
  }
  if (type === "textarea") {
    return (
      <div className={spec.full ? "sm:col-span-2" : undefined}>
        <label className={labelCls}>{spec.label}</label>
        <textarea
          className={inputCls}
          rows={3}
          value={String(value ?? "")}
          onChange={(e) => onChange(e.target.value)}
        />
      </div>
    );
  }
  return (
    <div className={spec.full ? "sm:col-span-2" : undefined}>
      <label className={labelCls}>{spec.label}</label>
      <input
        type={type === "datetime" ? "datetime-local" : type === "number" ? "number" : "text"}
        className={inputCls}
        value={value === null || value === undefined ? "" : String(value)}
        onChange={(e) => onChange(type === "number" ? Number(e.target.value) : e.target.value)}
      />
    </div>
  );
}

function EntitySection({
  cfg,
  search,
  page,
  setPage,
  viewMode,
  registerActions,
}: {
  cfg: EntityConfig;
  search: string;
  page: number;
  setPage: (p: number) => void;
  viewMode: "pagination" | "infinite";
  registerActions?: (h: { add?: () => void; export?: () => void }) => void;
}) {
  const qc = useQueryClient();
  const queryKey = ["attendance", cfg.endpoint];
  const { data: rows = [], isLoading } = useQuery({
    queryKey,
    queryFn: async () => {
      const res = await api.get<{ results: any[] }>(`/attendance/${cfg.endpoint}/`, {
        page_size: 200,
      });
      return res.results ?? [];
    },
  });

  const searchKeys = useMemo(
    () =>
      cfg.searchKeys ??
      cfg.fields.filter((f) => f.main || f.subtitle || f.badge || f.card).map((f) => f.key),
    [cfg],
  );

  const filtered = useMemo(() => {
    if (!search.trim()) return rows;
    const q = search.toLowerCase();
    return rows.filter((r: any) =>
      searchKeys.some((k: string) =>
        String(r[k] ?? "")
          .toLowerCase()
          .includes(q),
      ),
    );
  }, [rows, search, searchKeys]);

  const PAGE_SIZE = 12;
  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const safePage = Math.min(page, totalPages);
  const paginated = filtered.slice((safePage - 1) * PAGE_SIZE, safePage * PAGE_SIZE);
  const [infiniteCount, setInfiniteCount] = useState(PAGE_SIZE);
  useEffect(() => {
    setInfiniteCount(PAGE_SIZE);
  }, [cfg.key, search]);
  const infiniteItems = filtered.slice(0, infiniteCount);
  const visible = viewMode === "pagination" ? paginated : infiniteItems;
  const hasMore = infiniteItems.length < filtered.length;

  const bulk = useBulkSelect<{ id: string }>(filtered as unknown as { id: string }[]);

  const save = useMutation({
    mutationFn: ({ id, payload }: { id?: string | number; payload: Record<string, unknown> }) =>
      id !== undefined && id !== null
        ? api.patch(`/attendance/${cfg.endpoint}/${id}/`, payload)
        : api.post(`/attendance/${cfg.endpoint}/`, payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey });
      setModalOpen(false);
      toast.success("Saved");
    },
    onError: (e: any) => toast.error(e?.message ?? "Save failed"),
  });

  const del = useMutation({
    mutationFn: (id: string | number) => api.delete(`/attendance/${cfg.endpoint}/${id}/`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey });
      toast.success("Deleted");
    },
  });

  const toggle = useMutation({
    mutationFn: ({ id, value }: { id: string | number; value: boolean }) =>
      api.patch(`/attendance/${cfg.endpoint}/${id}/`, {
        [cfg.toggleField!]: value,
      }),
    onSuccess: () => qc.invalidateQueries({ queryKey }),
  });

  const runAction = useMutation({
    mutationFn: (url: string) => api.post(url),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey });
      toast.success("Done");
    },
  });

  const [modalOpen, setModalOpen] = useState(false);
  const [editing, setEditing] = useState<any>(null);
  const [form, setForm] = useState<Record<string, unknown>>({});

  const formFields = cfg.fields.filter((f) => !f.skipForm);

  const openCreate = () => {
    setEditing(null);
    const f: Record<string, unknown> = {};
    formFields.forEach((x) => (f[x.key] = x.type === "bool" ? false : ""));
    setForm(f);
    setModalOpen(true);
  };

  const openEdit = (row: any) => {
    setEditing(row);
    const f: Record<string, unknown> = {};
    formFields.forEach((x) => {
      const v = row[x.key];
      f[x.key] = v === null || v === undefined ? (x.type === "bool" ? false : "") : v;
    });
    setForm(f);
    setModalOpen(true);
  };

  const submit = (ev: React.FormEvent) => {
    ev.preventDefault();
    save.mutateAsync({ id: editing?.id, payload: form }).catch(() => undefined);
  };

  const handleBulkDelete = async () => {
    if (bulk.selectedCount === 0) return;
    if (!confirm(`Delete ${bulk.selectedCount} ${cfg.label.toLowerCase()}?`)) return;
    try {
      await Promise.all(bulk.selectedArray.map((id) => del.mutateAsync(id)));
      bulk.clear();
      toast.success("Selected items deleted");
    } catch {
      toast.error("Some deletions failed");
    }
  };

  const handleExport = () => {
    const cols = cfg.fields
      .filter((f) => f.main || f.subtitle || f.badge || f.card)
      .map((f) => ({ key: f.key, label: f.label }));
    downloadCsv(
      toCsv(filtered as unknown as Record<string, unknown>[], cols),
      `${cfg.endpoint}-${dayjs().format("YYYY-MM-DD")}.csv`,
    );
  };

  useEffect(() => {
    registerActions?.({
      add: cfg.readOnly ? undefined : openCreate,
      export: handleExport,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [cfg, filtered]);

  if (isLoading) return <CardSkeleton />;

  const metaFields = cfg.fields.filter((f) => f.card && !f.main && !f.subtitle && !f.badge);
  const badgeFields = cfg.fields.filter((f) => f.badge);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <p className="text-sm text-slate-500 dark:text-slate-400">
          {filtered.length} {cfg.label.toLowerCase()}
        </p>
        <div className="flex items-center gap-2">
          <Button
            variant="secondary"
            size="sm"
            onClick={handleExport}
            leftIcon={<DocumentArrowDownIcon className="h-4 w-4" />}
          >
            Export CSV
          </Button>
          {!cfg.readOnly && (
            <Button size="sm" onClick={openCreate} leftIcon={<PlusIcon className="h-4 w-4" />}>
              Add {cfg.label}
            </Button>
          )}
        </div>
      </div>

      {filtered.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 p-10 text-center text-slate-400 dark:border-slate-600">
          <p className="text-sm">No {cfg.label.toLowerCase()} found</p>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {visible.map((row: any) => {
            const title = row[cfg.titleField];
            const sub = cfg.subtitleField ? row[cfg.subtitleField] : undefined;
            return (
              <div
                key={row.id}
                className="relative rounded-xl border border-slate-200 bg-white p-4 shadow-sm transition hover:shadow-md dark:border-slate-700 dark:bg-slate-800"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex min-w-0 items-start gap-3">
                    <input
                      type="checkbox"
                      checked={bulk.isSelected(String(row.id))}
                      onChange={() => bulk.toggle(String(row.id))}
                      aria-label={`Select ${title ?? row.id}`}
                      className="mt-1 h-4 w-4 shrink-0 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 dark:border-slate-600"
                    />
                    <div className="min-w-0">
                      <p className="truncate font-semibold text-slate-900 dark:text-slate-100">
                        {title ?? "—"}
                      </p>
                      {sub !== undefined && sub !== null && sub !== "" && (
                        <p className="truncate text-sm text-slate-500 dark:text-slate-400">{sub}</p>
                      )}
                    </div>
                  </div>
                  <div className="flex shrink-0 items-center gap-1.5">
                    {cfg.toggleField && (
                      <Toggle
                        checked={!!row[cfg.toggleField as string]}
                        onChange={() =>
                          toggle.mutate({
                            id: row.id,
                            value: !row[cfg.toggleField as string],
                          })
                        }
                      />
                    )}
                    {cfg.actions?.map((a) => {
                      const Icon =
                        a.kind === "approve"
                          ? CheckCircleIcon
                          : a.kind === "reject"
                            ? XCircleIcon
                            : AdjustmentsHorizontalIcon;
                      return (
                        <button
                          key={a.label}
                          type="button"
                          title={a.label}
                          onClick={() => {
                            if (a.confirm && !confirm(a.confirm)) return;
                            runAction.mutate(a.url(row.id));
                          }}
                          className={`rounded-md p-1.5 ${
                            a.kind === "approve"
                              ? "text-green-600 hover:bg-green-50 dark:hover:bg-green-900/30"
                              : a.kind === "reject"
                                ? "text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30"
                                : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700"
                          }`}
                        >
                          <Icon className="h-4 w-4" />
                        </button>
                      );
                    })}
                    {!cfg.readOnly && (
                      <>
                        <button
                          type="button"
                          title="Edit"
                          onClick={() => openEdit(row)}
                          className="rounded-md p-1.5 text-slate-500 hover:bg-slate-100 dark:text-slate-400 dark:hover:bg-slate-700"
                        >
                          <PencilSquareIcon className="h-4 w-4" />
                        </button>
                        <button
                          type="button"
                          title="Delete"
                          onClick={() => del.mutate(row.id)}
                          className="rounded-md p-1.5 text-red-500 hover:bg-red-50 dark:hover:bg-red-900/30"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </>
                    )}
                  </div>
                </div>
                {badgeFields.length > 0 && (
                  <div className="mt-2.5 flex flex-wrap gap-1.5">
                    {badgeFields.map((f) => (
                      <StatusBadge key={f.key} value={String(row[f.key] ?? "—")} />
                    ))}
                  </div>
                )}
                {metaFields.length > 0 && (
                  <dl className="mt-3 grid grid-cols-2 gap-x-3 gap-y-1.5 text-sm">
                    {metaFields.map((f) => (
                      <div key={f.key}>
                        <dt className="text-xs text-slate-400 dark:text-slate-500">{f.label}</dt>
                        <dd className="truncate text-slate-700 dark:text-slate-200">
                          {formatValue(row[f.key], f)}
                        </dd>
                      </div>
                    ))}
                  </dl>
                )}
              </div>
            );
          })}
        </div>
      )}

      {bulk.selectedCount > 0 && (
        <div className="fixed bottom-6 left-1/2 z-40 flex -translate-x-1/2 items-center gap-3 rounded-xl border border-slate-200 bg-white px-4 py-2.5 shadow-xl dark:border-slate-700 dark:bg-slate-800">
          <span className="text-sm font-medium text-slate-700 dark:text-slate-200">
            {bulk.selectedCount} selected
          </span>
          {!cfg.readOnly && (
            <button
              onClick={handleBulkDelete}
              className="inline-flex items-center gap-1 rounded-lg bg-red-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-red-700"
            >
              <TrashIcon className="h-4 w-4" /> Delete
            </button>
          )}
          <button
            onClick={bulk.clear}
            className="rounded-lg bg-slate-100 px-3 py-1.5 text-sm font-medium text-slate-600 hover:bg-slate-200 dark:bg-slate-700 dark:text-slate-300"
          >
            Clear
          </button>
        </div>
      )}

      {viewMode === "pagination" && filtered.length > PAGE_SIZE && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-slate-500 dark:text-slate-400">
            Page {safePage} of {totalPages}
          </p>
          <div className="flex items-center gap-1">
            <button
              onClick={() => setPage(safePage - 1)}
              disabled={safePage <= 1}
              className="rounded-lg border border-slate-200 p-1.5 text-slate-600 disabled:opacity-40 dark:border-slate-600 dark:text-slate-300"
              aria-label="Previous page"
            >
              <ChevronLeftIcon className="h-4 w-4" />
            </button>
            <button
              onClick={() => setPage(safePage + 1)}
              disabled={safePage >= totalPages}
              className="rounded-lg border border-slate-200 p-1.5 text-slate-600 disabled:opacity-40 dark:border-slate-600 dark:text-slate-300"
              aria-label="Next page"
            >
              <ChevronRightIcon className="h-4 w-4" />
            </button>
          </div>
        </div>
      )}

      {viewMode === "infinite" && hasMore && (
        <InfiniteScroll
          items={[]}
          totalCount={filtered.length}
          hasMore={hasMore}
          isLoading={isLoading}
          isFetchingNext={false}
          onLoadMore={() => setInfiniteCount((c) => c + PAGE_SIZE)}
          renderItem={() => null}
          endMessage="End of list"
        />
      )}

      <Modal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        title={editing ? `Edit ${cfg.label}` : `Add ${cfg.label}`}
      >
        <form onSubmit={submit} className="space-y-4">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {formFields.map((f) => (
              <FormField
                key={f.key}
                spec={f}
                value={form[f.key]}
                onChange={(v) => setForm((prev) => ({ ...prev, [f.key]: v }))}
              />
            ))}
          </div>
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="secondary" type="button" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button type="submit" loading={save.isPending}>
              {editing ? "Save Changes" : "Create"}
            </Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}

// ─── Entity configs ────────────────────────────────────────────────────────────

const ENTITY_CONFIGS: Record<string, EntityConfig> = {
  records: {
    key: "records",
    label: "Attendance Record",
    icon: ClipboardDocumentCheckIcon,
    endpoint: "attendance-record",
    titleField: "student_name",
    subtitleField: "classroom_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", type: "number", card: true },
      {
        key: "classroom_name",
        label: "Classroom",
        subtitle: true,
        skipForm: true,
      },
      { key: "classroom", label: "Classroom ID", type: "number", card: true },
      {
        key: "academic_year",
        label: "Academic Year ID",
        type: "number",
        card: true,
      },
      { key: "date", label: "Date", type: "date", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: STATUS_ATT,
        badge: true,
      },
      {
        key: "recorded_by_name",
        label: "Recorded By",
        card: true,
        skipForm: true,
      },
      {
        key: "remarks",
        label: "Remarks",
        type: "textarea",
        full: true,
        card: true,
      },
    ],
    searchKeys: ["student_name", "classroom_name", "status", "date"],
  },
  periods: {
    key: "periods",
    label: "Period Attendance",
    icon: ClockIcon,
    endpoint: "periods",
    titleField: "student_name",
    subtitleField: "assignment_label",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", type: "number", card: true },
      {
        key: "assignment_label",
        label: "Assignment",
        subtitle: true,
        skipForm: true,
      },
      { key: "assignment", label: "Assignment ID", type: "number", card: true },
      { key: "date", label: "Date", type: "date", card: true },
      { key: "period_number", label: "Period", type: "number", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: STATUS_ATT,
        badge: true,
      },
      {
        key: "recorded_by_name",
        label: "Recorded By",
        card: true,
        skipForm: true,
      },
    ],
    searchKeys: ["student_name", "assignment_label", "status"],
  },
  leaves: {
    key: "leaves",
    label: "Leave Request",
    icon: PaperAirplaneIcon,
    endpoint: "leaves",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", type: "number", card: true },
      {
        key: "leave_type",
        label: "Type",
        type: "select",
        options: [
          ["sick", "Sick"],
          ["casual", "Casual"],
          ["other", "Other"],
        ],
        badge: true,
      },
      { key: "from_date", label: "From", type: "date", card: true },
      { key: "to_date", label: "To", type: "date", card: true },
      {
        key: "reason",
        label: "Reason",
        type: "textarea",
        full: true,
        card: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: STATUS_FLOW,
        badge: true,
      },
      {
        key: "requested_at",
        label: "Requested",
        type: "datetime",
        skipForm: true,
      },
      {
        key: "review_remarks",
        label: "Review Remarks",
        type: "textarea",
        full: true,
      },
    ],
    actions: [
      {
        label: "Approve",
        kind: "approve",
        url: (id) => `/attendance/leaves/${id}/approve/`,
        confirm: "Approve this leave request?",
      },
      {
        label: "Reject",
        kind: "reject",
        url: (id) => `/attendance/leaves/${id}/reject/`,
        confirm: "Reject this leave request?",
      },
    ],
    searchKeys: ["student_name", "leave_type", "status"],
  },
  balances: {
    key: "balances",
    label: "Leave Balance",
    icon: ScaleIcon,
    endpoint: "leave-balances",
    titleField: "student_name",
    subtitleField: "academic_year_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", type: "number" },
      {
        key: "academic_year_name",
        label: "Year",
        subtitle: true,
        skipForm: true,
      },
      { key: "academic_year", label: "Academic Year ID", type: "number" },
      {
        key: "sick_leave_total",
        label: "Sick Total",
        type: "number",
        card: true,
      },
      {
        key: "sick_leave_used",
        label: "Sick Used",
        type: "number",
        card: true,
      },
      {
        key: "casual_leave_total",
        label: "Casual Total",
        type: "number",
        card: true,
      },
      {
        key: "casual_leave_used",
        label: "Casual Used",
        type: "number",
        card: true,
      },
      {
        key: "other_leave_total",
        label: "Other Total",
        type: "number",
        card: true,
      },
      {
        key: "other_leave_used",
        label: "Other Used",
        type: "number",
        card: true,
      },
    ],
    searchKeys: ["student_name"],
  },
  approval: {
    key: "approval",
    label: "Approval Level",
    icon: CheckBadgeIcon,
    endpoint: "leave-approval-level",
    titleField: "leave_student_name",
    fields: [
      {
        key: "leave_student_name",
        label: "Student",
        main: true,
        skipForm: true,
      },
      { key: "leave", label: "Leave ID", type: "number", card: true },
      { key: "level", label: "Level", type: "number", card: true },
      { key: "approver", label: "Approver ID", type: "number", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: STATUS_FLOW,
        badge: true,
      },
      {
        key: "remarks",
        label: "Remarks",
        type: "textarea",
        full: true,
        card: true,
      },
      { key: "decided_at", label: "Decided", type: "datetime", skipForm: true },
    ],
    searchKeys: ["leave_student_name", "status"],
  },
  holidays: {
    key: "holidays",
    label: "Holiday",
    icon: CalendarDaysIcon,
    endpoint: "holidays",
    titleField: "name",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "date", label: "Date", type: "date", card: true },
      {
        key: "holiday_type",
        label: "Type",
        type: "select",
        options: [
          ["public", "Public"],
          ["religious", "Religious"],
          ["school", "School"],
          ["other", "Other"],
        ],
        badge: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
        card: true,
      },
      {
        key: "academic_year",
        label: "Academic Year ID",
        type: "number",
        card: true,
      },
    ],
    searchKeys: ["name", "holiday_type"],
  },
  policies: {
    key: "policies",
    label: "Attendance Policy",
    icon: DocumentTextIcon,
    endpoint: "policies",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      { key: "min_attendance_pct", label: "Min %", type: "number", card: true },
      {
        key: "auto_fail_below",
        label: "Auto-fail Below",
        type: "number",
        card: true,
      },
      {
        key: "notify_parent_below_pct",
        label: "Notify Parent < %",
        type: "number",
        card: true,
      },
      {
        key: "notify_admin_below_pct",
        label: "Notify Admin < %",
        type: "number",
        card: true,
      },
      {
        key: "edit_window_days",
        label: "Edit Window (days)",
        type: "number",
        card: true,
      },
      {
        key: "escalation_enabled",
        label: "Escalation",
        type: "bool",
        card: true,
      },
      {
        key: "escalation_after_minutes",
        label: "Escalate After (min)",
        type: "number",
        card: true,
      },
      { key: "is_active", label: "Active", type: "bool", card: true },
    ],
    searchKeys: ["name"],
  },
  substitutes: {
    key: "substitutes",
    label: "Substitute Teacher",
    icon: UserPlusIcon,
    endpoint: "substitutes",
    titleField: "classroom_name",
    fields: [
      { key: "classroom_name", label: "Classroom", main: true, skipForm: true },
      {
        key: "original_teacher",
        label: "Original Teacher ID",
        type: "number",
        card: true,
      },
      {
        key: "substitute_teacher",
        label: "Substitute ID",
        type: "number",
        card: true,
      },
      { key: "classroom", label: "Classroom ID", type: "number" },
      { key: "subject", label: "Subject ID", type: "number", card: true },
      { key: "date", label: "Date", type: "date", card: true },
      { key: "period_number", label: "Period", type: "number", card: true },
      {
        key: "reason",
        label: "Reason",
        type: "textarea",
        full: true,
        card: true,
      },
      {
        key: "is_auto_assigned",
        label: "Auto Assigned",
        type: "bool",
        card: true,
      },
    ],
    searchKeys: ["classroom_name", "reason"],
  },
  qrsessions: {
    key: "qrsessions",
    label: "QR Session",
    icon: QrCodeIcon,
    endpoint: "qr-sessions",
    titleField: "classroom_name",
    subtitleField: "teacher_name",
    toggleField: "is_active",
    fields: [
      { key: "classroom_name", label: "Classroom", main: true, skipForm: true },
      { key: "classroom", label: "Classroom ID", type: "number" },
      { key: "teacher_name", label: "Teacher", subtitle: true, skipForm: true },
      { key: "teacher", label: "Teacher ID", type: "number" },
      { key: "date", label: "Date", type: "date", card: true },
      { key: "period_number", label: "Period", type: "number", card: true },
      { key: "is_active", label: "Active", type: "bool", card: true },
      {
        key: "expires_at",
        label: "Expires",
        type: "datetime",
        card: true,
        skipForm: true,
      },
      { key: "created_at", label: "Created", type: "datetime", skipForm: true },
    ],
    searchKeys: ["classroom_name", "teacher_name"],
  },
  biometric: {
    key: "biometric",
    label: "Biometric Check-in",
    icon: FingerPrintIcon,
    endpoint: "biometric",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", type: "number" },
      {
        key: "biometric_type",
        label: "Type",
        type: "select",
        options: [
          ["fingerprint", "Fingerprint"],
          ["face", "Face"],
          ["iris", "Iris"],
          ["palm", "Palm"],
        ],
        badge: true,
      },
      { key: "device_id", label: "Device ID", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["success", "Success"],
          ["failed", "Failed"],
          ["retry", "Retry"],
        ],
        badge: true,
      },
      {
        key: "confidence_score",
        label: "Confidence",
        type: "number",
        card: true,
      },
      { key: "checkin_time", label: "Check-in", type: "datetime", card: true },
      { key: "latitude", label: "Latitude", type: "number" },
      { key: "longitude", label: "Longitude", type: "number" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "device_id", "status"],
  },
  rfid: {
    key: "rfid",
    label: "RFID Check-in",
    icon: CreditCardIcon,
    endpoint: "rfid",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", type: "number" },
      { key: "card_number", label: "Card #", card: true },
      { key: "reader_id", label: "Reader", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["success", "Success"],
          ["failed", "Failed"],
          ["unknown_card", "Unknown Card"],
        ],
        badge: true,
      },
      { key: "location", label: "Location", card: true },
      { key: "checkin_time", label: "Check-in", type: "datetime", card: true },
      { key: "latitude", label: "Latitude", type: "number" },
      { key: "longitude", label: "Longitude", type: "number" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "card_number", "location"],
  },
  gps: {
    key: "gps",
    label: "GPS Attendance",
    icon: MapPinIcon,
    endpoint: "gps",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", type: "number" },
      { key: "geofence_name", label: "Geofence", card: true },
      {
        key: "geofence_radius",
        label: "Radius (m)",
        type: "number",
        card: true,
      },
      {
        key: "distance_from_school",
        label: "Distance (m)",
        type: "number",
        card: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["within_geofence", "Within"],
          ["outside_geofence", "Outside"],
          ["failed", "Failed"],
        ],
        badge: true,
      },
      { key: "checkin_time", label: "Check-in", type: "datetime", card: true },
      { key: "device_id", label: "Device ID" },
      { key: "device_type", label: "Device Type" },
      { key: "latitude", label: "Latitude", type: "number" },
      { key: "longitude", label: "Longitude", type: "number" },
      { key: "accuracy_meters", label: "Accuracy (m)", type: "number" },
      { key: "notes", label: "Notes", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "geofence_name", "status"],
  },
  fieldtrips: {
    key: "fieldtrips",
    label: "Field Trip",
    icon: MapIcon,
    endpoint: "field-trip",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      { key: "destination", label: "Destination", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["planned", "Planned"],
          ["approved", "Approved"],
          ["completed", "Completed"],
          ["cancelled", "Cancelled"],
        ],
        badge: true,
      },
      { key: "departure_date", label: "Departure", type: "date", card: true },
      { key: "departure_time", label: "Departure Time", card: true },
      { key: "return_date", label: "Return", type: "date", card: true },
      { key: "return_time", label: "Return Time", card: true },
      { key: "organizer", label: "Organizer ID", type: "number", card: true },
      { key: "organizer_name", label: "Organizer", card: true, skipForm: true },
      { key: "chaperones", label: "Chaperones", card: true },
      { key: "eligible_grades", label: "Eligible Grades", card: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
        card: true,
      },
    ],
    searchKeys: ["title", "destination", "status"],
  },
  incentives: {
    key: "incentives",
    label: "Attendance Incentive",
    icon: TrophyIcon,
    endpoint: "attendance-incentive",
    titleField: "name",
    toggleField: "is_active",
    fields: [
      { key: "name", label: "Name", main: true },
      {
        key: "incentive_type",
        label: "Type",
        type: "select",
        options: [
          ["badge", "Badge"],
          ["certificate", "Certificate"],
          ["reward", "Reward"],
          ["points", "Points"],
        ],
        badge: true,
      },
      {
        key: "required_streak_days",
        label: "Streak Days",
        type: "number",
        card: true,
      },
      {
        key: "required_percentage",
        label: "Required %",
        type: "number",
        card: true,
      },
      { key: "points_value", label: "Points", type: "number", card: true },
      {
        key: "total_available",
        label: "Available",
        type: "number",
        card: true,
      },
      { key: "total_awarded", label: "Awarded", type: "number", card: true },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "is_active", label: "Active", type: "bool", card: true },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
      },
    ],
    searchKeys: ["name", "incentive_type"],
  },
  tardies: {
    key: "tardies",
    label: "Tardy Record",
    icon: ExclamationTriangleIcon,
    endpoint: "tardy-record",
    titleField: "student_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", type: "number" },
      { key: "tardy_date", label: "Date", type: "date", card: true },
      { key: "arrival_time", label: "Arrival", card: true },
      {
        key: "minutes_late",
        label: "Minutes Late",
        type: "number",
        card: true,
      },
      { key: "policy_applied", label: "Policy ID", type: "number", card: true },
      { key: "policy_name", label: "Policy", card: true, skipForm: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["recorded", "Recorded"],
          ["excused", "Excused"],
          ["unexcused", "Unexcused"],
          ["resolved", "Resolved"],
        ],
        badge: true,
      },
      { key: "excuse", label: "Excused", type: "bool", card: true },
      {
        key: "parent_notified",
        label: "Parent Notified",
        type: "bool",
        card: true,
      },
      { key: "consequence", label: "Consequence", card: true },
      { key: "reason", label: "Reason", type: "textarea", full: true },
    ],
    searchKeys: ["student_name", "status"],
  },
  corrections: {
    key: "corrections",
    label: "Correction Request",
    icon: WrenchScrewdriverIcon,
    endpoint: "corrections",
    titleField: "correction_type",
    fields: [
      {
        key: "correction_type",
        label: "Type",
        type: "select",
        options: [
          ["status", "Status"],
          ["time", "Time"],
          ["manual_entry", "Manual Entry"],
          ["duplicate", "Duplicate"],
          ["other", "Other"],
        ],
        main: true,
      },
      {
        key: "attendance_record",
        label: "Record ID",
        type: "number",
        card: true,
      },
      {
        key: "period_attendance",
        label: "Period ID",
        type: "number",
        card: true,
      },
      {
        key: "old_status",
        label: "Old Status",
        type: "select",
        options: STATUS_ATT,
        card: true,
      },
      {
        key: "new_status",
        label: "New Status",
        type: "select",
        options: STATUS_ATT,
        card: true,
      },
      { key: "old_time", label: "Old Time" },
      { key: "new_time", label: "New Time" },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["pending", "Pending"],
          ["approved", "Approved"],
          ["rejected", "Rejected"],
          ["resolved", "Resolved"],
        ],
        badge: true,
      },
      {
        key: "reason",
        label: "Reason",
        type: "textarea",
        full: true,
        card: true,
      },
    ],
    searchKeys: ["correction_type", "status", "reason"],
  },
  chronic: {
    key: "chronic",
    label: "Chronic Absence",
    icon: UserMinusIcon,
    endpoint: "chronic-absence",
    titleField: "student_name",
    subtitleField: "academic_year_name",
    fields: [
      { key: "student_name", label: "Student", main: true, skipForm: true },
      { key: "student", label: "Student ID", type: "number" },
      {
        key: "academic_year_name",
        label: "Year",
        subtitle: true,
        skipForm: true,
      },
      { key: "academic_year", label: "Academic Year ID", type: "number" },
      { key: "term", label: "Term", card: true },
      {
        key: "absence_percentage",
        label: "Absence %",
        type: "number",
        card: true,
      },
      {
        key: "attendance_percentage",
        label: "Attendance %",
        type: "number",
        card: true,
      },
      {
        key: "severity_level",
        label: "Severity",
        type: "select",
        options: [
          ["low", "Low"],
          ["medium", "Medium"],
          ["high", "High"],
          ["critical", "Critical"],
        ],
        badge: true,
      },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["monitoring", "Monitoring"],
          ["intervention", "Intervention"],
          ["resolved", "Resolved"],
        ],
        badge: true,
      },
      { key: "total_days", label: "Total Days", type: "number" },
      { key: "days_present", label: "Present", type: "number" },
      { key: "days_absent", label: "Absent", type: "number" },
      { key: "days_late", label: "Late", type: "number" },
      {
        key: "intervention_plan",
        label: "Intervention Plan",
        type: "textarea",
        full: true,
        card: true,
      },
    ],
    searchKeys: ["student_name", "severity_level", "status"],
  },
  reports: {
    key: "reports",
    label: "Attendance Report",
    icon: DocumentChartBarIcon,
    endpoint: "reports",
    titleField: "title",
    fields: [
      { key: "title", label: "Title", main: true },
      {
        key: "report_type",
        label: "Type",
        type: "select",
        options: [
          ["daily", "Daily"],
          ["weekly", "Weekly"],
          ["monthly", "Monthly"],
          ["term", "Term"],
          ["yearly", "Yearly"],
        ],
        badge: true,
      },
      { key: "start_date", label: "Start", type: "date", card: true },
      { key: "end_date", label: "End", type: "date", card: true },
      { key: "classroom", label: "Classroom ID", type: "number", card: true },
      { key: "classroom_name", label: "Classroom", card: true, skipForm: true },
      { key: "student", label: "Student ID", type: "number" },
      { key: "student_name", label: "Student", card: true, skipForm: true },
      { key: "grade", label: "Grade ID", type: "number" },
      { key: "total_students", label: "Students", type: "number", card: true },
      {
        key: "status",
        label: "Status",
        type: "select",
        options: [
          ["draft", "Draft"],
          ["generated", "Generated"],
          ["sent", "Sent"],
        ],
        card: true,
      },
      {
        key: "description",
        label: "Description",
        type: "textarea",
        full: true,
        card: true,
      },
    ],
    searchKeys: ["title", "report_type"],
  },
  config: {
    key: "config",
    label: "Attendance Config",
    icon: Cog6ToothIcon,
    endpoint: "attendance-configuration",
    titleField: "attendance_mode",
    fields: [
      {
        key: "attendance_mode",
        label: "Mode",
        type: "select",
        options: [
          ["class_period", "Class Period"],
          ["daily", "Daily"],
          ["both", "Both"],
        ],
        main: true,
      },
      {
        key: "check_in_method",
        label: "Check-in Method",
        type: "select",
        options: [
          ["manual", "Manual"],
          ["qr", "QR Code"],
          ["biometric", "Biometric"],
          ["rfid", "RFID"],
          ["gps", "GPS"],
          ["app", "Mobile App"],
        ],
        card: true,
      },
      {
        key: "grace_period_minutes",
        label: "Grace (min)",
        type: "number",
        card: true,
      },
      {
        key: "tardy_threshold_minutes",
        label: "Tardy Threshold (min)",
        type: "number",
        card: true,
      },
      {
        key: "absent_threshold_minutes",
        label: "Absent Threshold (min)",
        type: "number",
        card: true,
      },
      {
        key: "early_departure_threshold_minutes",
        label: "Early Dep. Threshold",
        type: "number",
        card: true,
      },
      {
        key: "auto_notify_absent",
        label: "Auto-notify Absent",
        type: "bool",
        card: true,
      },
      {
        key: "auto_notify_tardy",
        label: "Auto-notify Tardy",
        type: "bool",
        card: true,
      },
      {
        key: "notify_after_minutes",
        label: "Notify After (min)",
        type: "number",
        card: true,
      },
      {
        key: "parent_portal_enabled",
        label: "Parent Portal",
        type: "bool",
        card: true,
      },
      {
        key: "parent_real_time_view",
        label: "Parent Real-time",
        type: "bool",
        card: true,
      },
      {
        key: "auto_apply_holidays",
        label: "Auto Holidays",
        type: "bool",
        card: true,
      },
    ],
    searchKeys: ["attendance_mode", "check_in_method"],
  },
};

const TABS: {
  key: string;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}[] = [
  { key: "overview", label: "Overview", icon: ChartBarIcon },
  ...Object.values(ENTITY_CONFIGS).map((c) => ({
    key: c.key,
    label: c.label,
    icon: c.icon,
  })),
];

// ─── Page shell ────────────────────────────────────────────────────────────────

export default function AdminAttendancePage() {
  useTitle("Attendance");
  const [activeTab, setActiveTab] = useState("overview");
  const [search, setSearch] = useState("");
  const [page, setPage] = useState(1);
  const [viewMode, setViewMode] = useState<"pagination" | "infinite">("pagination");
  const searchRef = useRef<HTMLInputElement>(null);
  const actionRef = useRef<{ add?: () => void; export?: () => void }>({});
  const { open: helpOpen, setOpen: setHelpOpen } = useShortcutHelp();

  useEffect(() => {
    setPage(1);
    setSearch("");
  }, [activeTab]);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement;
      if (
        target.tagName === "INPUT" ||
        target.tagName === "TEXTAREA" ||
        target.tagName === "SELECT" ||
        target.isContentEditable
      ) {
        return;
      }
      if (e.key === "/") {
        e.preventDefault();
        searchRef.current?.focus();
      }
      if (e.key.toLowerCase() === "n") {
        e.preventDefault();
        actionRef.current?.add?.();
      }
      if (e.key.toLowerCase() === "e") {
        e.preventDefault();
        actionRef.current?.export?.();
      }
      if (e.key.toLowerCase() === "p") {
        e.preventDefault();
        setViewMode((v) => (v === "pagination" ? "infinite" : "pagination"));
      }
    };
    document.addEventListener("keydown", handler);
    return () => document.removeEventListener("keydown", handler);
  }, []);

  const activeCfg = ENTITY_CONFIGS[activeTab];

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Attendance</h1>
          <p className="mt-0.5 text-sm text-slate-500 dark:text-slate-400">
            School-wide attendance, leaves, check-ins and analytics
          </p>
        </div>
        <div className="flex items-center gap-3">
          <div className="relative">
            <MagnifyingGlassIcon className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
            <input
              ref={searchRef}
              type="search"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setPage(1);
              }}
              placeholder="Search…  ( / )"
              className="w-56 rounded-xl border border-slate-200 bg-white px-4 py-2 pl-9 text-sm text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-100"
            />
          </div>
          <div className="flex items-center gap-1 rounded-xl border border-slate-200 p-1 dark:border-slate-600">
            <button
              onClick={() => setViewMode("pagination")}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                viewMode === "pagination"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300"
                  : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700"
              }`}
            >
              Paginated
            </button>
            <button
              onClick={() => setViewMode("infinite")}
              className={`rounded-lg px-3 py-1.5 text-xs font-medium transition ${
                viewMode === "infinite"
                  ? "bg-indigo-100 text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300"
                  : "text-slate-500 hover:bg-slate-100 dark:hover:bg-slate-700"
              }`}
            >
              Infinite
            </button>
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setHelpOpen(true)}
            leftIcon={<ShieldExclamationIcon className="h-4 w-4" />}
          >
            Shortcuts
          </Button>
        </div>
      </div>

      {/* Tab bar */}
      <div className="flex gap-1.5 overflow-x-auto pb-1">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setActiveTab(t.key)}
            className={`flex shrink-0 items-center gap-1.5 rounded-xl px-3.5 py-2 text-sm font-medium transition ${
              activeTab === t.key
                ? "bg-indigo-600 text-white shadow-sm"
                : "bg-white text-slate-600 hover:bg-slate-50 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
            }`}
          >
            <t.icon className="h-4 w-4" />
            {t.label}
          </button>
        ))}
      </div>

      {activeTab === "overview" ? (
        <OverviewTab />
      ) : (
        <EntitySection
          cfg={activeCfg}
          search={search}
          page={page}
          setPage={setPage}
          viewMode={viewMode}
          registerActions={(h) => {
            actionRef.current = h;
          }}
        />
      )}

      <KeyboardShortcutHelp
        open={helpOpen}
        onClose={() => setHelpOpen(false)}
        shortcuts={[
          { keys: ["N"], label: "New", description: "Open create form" },
          { keys: ["/"], label: "Search", description: "Focus search input" },
          { keys: ["E"], label: "Export", description: "Export data to CSV" },
          {
            keys: ["P"],
            label: "View Mode",
            description: "Toggle pagination / infinite scroll",
          },
          {
            keys: ["?"],
            label: "Help",
            description: "Show this shortcut help",
          },
        ]}
      />
    </div>
  );
}
