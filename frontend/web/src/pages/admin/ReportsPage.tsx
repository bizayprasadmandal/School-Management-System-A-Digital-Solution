/**
 * Admin Reports & Analytics Page
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { BarChart, Bar, LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { ArrowDownTrayIcon } from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { Button, SkeletonStatCard, SkeletonCard, SkeletonChart } from "../../components/common";
import { useCurrentAcademicYear } from "../../api/hooks";
import { useTitle } from "../../hooks";
import { currency, percent } from "../../utils";
import toast from "react-hot-toast";
import { useAuthStore } from "../../store/authStore";

export default function ReportsPage() {
  useTitle("Reports & Analytics");
  const { tokens } = useAuthStore();
  const { data: currentYear } = useCurrentAcademicYear();
  const { data: dashStats, isLoading } = useQuery({
    queryKey: ["dashboard-stats"],
    queryFn: () => api.get<any>("/reporting/dashboard-stats/"),
  });

  const { data: attendanceReport } = useQuery({
    queryKey: ["attendance-report"],
    queryFn: () => api.get<any>("/reporting/attendance-report/", {
      from_date: new Date(new Date().getFullYear(), new Date().getMonth(), 1).toISOString().split("T")[0],
      to_date: new Date().toISOString().split("T")[0],
    }),
  });

  const { data: feeReport } = useQuery({
    queryKey: ["fee-report", currentYear?.id],
    queryFn: () => api.get<any>("/reporting/fee-report/", { academic_year_id: currentYear?.id }),
    enabled: !!currentYear?.id,
  });

  const handleExport = async (type: "attendance" | "students") => {
    try {
      const url = type === "students" ? "/api/v1/reporting/export/students-csv/" : "/api/v1/reporting/export/attendance-pdf/";
      const res = await fetch(url, { headers: { Authorization: `Bearer ${tokens?.access}` } });
      const blob = await res.blob();
      const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = `${type}_export.${type === "students" ? "csv" : "pdf"}`; a.click();
    } catch { toast.error("Export failed"); }
  };

  if (isLoading) return <div className="grid grid-cols-3 gap-4 p-4"><SkeletonStatCard /><SkeletonStatCard /><SkeletonStatCard /><SkeletonCard className="col-span-2" /><SkeletonChart /></div>;

  const attendanceDailyData = attendanceReport?.daily ?? [];
  const feeByStatus = feeReport?.by_status ?? [];
  const gradeDistribution = [
    { name: "A+/A", value: 42, fill: "#22c55e" }, { name: "B", value: 31, fill: "#60a5fa" },
    { name: "C", value: 17, fill: "#fbbf24" }, { name: "D/F", value: 10, fill: "#ef4444" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div><h1 className="text-2xl font-bold text-slate-900">Reports & Analytics</h1><p className="text-sm text-slate-500 mt-0.5">School-wide performance insights</p></div>
        <div className="flex gap-2">
          <Button variant="secondary" leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />} onClick={() => handleExport("students")}>Export Students CSV</Button>
          <Button variant="secondary" leftIcon={<ArrowDownTrayIcon className="h-4 w-4" />} onClick={() => handleExport("attendance")}>Export Attendance PDF</Button>
        </div>
      </div>

      {/* KPI summary */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {[
          { label: "Total Students", value: dashStats?.total_students?.toLocaleString() ?? "—", color: "text-indigo-600" },
          { label: "Teachers", value: dashStats?.total_teachers ?? "—", color: "text-violet-600" },
          { label: "Today Attendance", value: dashStats ? percent(dashStats.attendance_today_pct) : "—", color: "text-emerald-600" },
          { label: "Monthly Fees", value: dashStats ? currency(dashStats.fees_collected_month) : "—", color: "text-blue-600" },
        ].map(({ label, value, color }) => (
          <div key={label} className="card p-5 text-center">
            <p className={`text-3xl font-bold ${color}`}>{value}</p>
            <p className="text-xs text-slate-500 mt-1">{label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* Attendance trend */}
        <div className="card">
          <div className="card-header"><h2 className="text-base font-semibold">Attendance Trend (This Month)</h2></div>
          <div className="card-body">
            {attendanceDailyData.length === 0
              ? <p className="text-center text-slate-400 py-10 text-sm">No attendance data for this period</p>
              : <ResponsiveContainer width="100%" height={220}>
                  <LineChart data={attendanceDailyData} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="date" tick={{ fontSize: 10 }} tickFormatter={d => d.slice(5)} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                    <Tooltip />
                    <Line type="monotone" dataKey="present" name="Present" stroke="#22c55e" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="absent" name="Absent" stroke="#ef4444" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
            }
          </div>
        </div>

        {/* Grade distribution */}
        <div className="card">
          <div className="card-header"><h2 className="text-base font-semibold">Grade Distribution</h2></div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={220}>
              <PieChart>
                <Pie data={gradeDistribution} cx="50%" cy="50%" outerRadius={80} paddingAngle={2} dataKey="value">
                  {gradeDistribution.map((entry, i) => <Cell key={i} fill={entry.fill} />)}
                </Pie>
                <Legend iconSize={10} iconType="circle" wrapperStyle={{ fontSize: 12 }} />
                <Tooltip formatter={(v: number) => [`${v}%`]} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Fee collection */}
        <div className="card">
          <div className="card-header"><h2 className="text-base font-semibold">Fee Collection Status</h2></div>
          <div className="card-body">
            {feeByStatus.length === 0
              ? <p className="text-center text-slate-400 py-10 text-sm">No fee data available</p>
              : <ResponsiveContainer width="100%" height={220}>
                  <BarChart data={feeByStatus} margin={{ top: 4, right: 4, left: -10, bottom: 0 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis dataKey="status" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                    <YAxis tick={{ fontSize: 11 }} axisLine={false} tickLine={false} tickFormatter={v => `$${(v/1000).toFixed(0)}K`} />
                    <Tooltip formatter={(v: number) => [currency(v)]} />
                    <Bar dataKey="amount" fill="#6366f1" radius={[4,4,0,0]} name="Amount" />
                  </BarChart>
                </ResponsiveContainer>
            }
            {feeReport && (
              <div className="mt-4 flex gap-4 justify-center text-sm">
                <span><span className="font-semibold text-slate-800">{currency(feeReport.total_invoiced)}</span> <span className="text-slate-500">Invoiced</span></span>
                <span><span className="font-semibold text-green-600">{currency(feeReport.total_collected)}</span> <span className="text-slate-500">Collected</span></span>
                <span><span className="font-semibold text-indigo-600">{percent(feeReport.collection_rate)}</span> <span className="text-slate-500">Rate</span></span>
              </div>
            )}
          </div>
        </div>

        {/* Quick stats table */}
        <div className="card">
          <div className="card-header"><h2 className="text-base font-semibold">School Summary</h2></div>
          <div className="card-body space-y-3">
            {[
              ["Total Students",     dashStats?.total_students?.toLocaleString() ?? "—"],
              ["Total Teachers",     dashStats?.total_teachers ?? "—"],
              ["Total Classrooms",   dashStats?.total_classrooms ?? "—"],
              ["Today's Attendance", dashStats ? percent(dashStats.attendance_today_pct) : "—"],
              ["Monthly Collection", dashStats ? currency(dashStats.fees_collected_month) : "—"],
              ["Outstanding Fees",   dashStats ? currency(dashStats.fees_outstanding) : "—"],
            ].map(([label, value]) => (
              <div key={String(label)} className="flex justify-between items-center py-2 border-b border-slate-50 last:border-0">
                <span className="text-sm text-slate-600">{label}</span>
                <span className="text-sm font-semibold text-slate-900">{value}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
