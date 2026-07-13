import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { SkeletonCard, ErrorState } from "../../components/common";
import { percent, attendanceColor, ATTENDANCE_STATUS, fmt } from "../../utils";
import { useTitle } from "../../hooks";
import dayjs from "dayjs";

export default function StudentAttendancePage() {
  useTitle("My Attendance");
  const [month, setMonth] = useState(dayjs().month() + 1);
  const [year, setYear] = useState(dayjs().year());
  const { data: profile } = useQuery({ queryKey:["student-me-att"], queryFn:()=>api.get<{ id: string }>("/students/me/") });
  const { data: report, isLoading, isError, refetch } = useQuery({
    queryKey: ["student-monthly-att", profile?.id, month, year],
    queryFn: () => api.get<{ records: { date: string; status: string }[]; present: number; absent: number; late: number; percentage: number; total_school_days: number }>(`/attendance/student-report/?student_id=${profile?.id}&month=${month}&year=${year}`),
    enabled: !!profile?.id,
  });

  const colorMap: Record<string,string> = { P:"bg-green-500", A:"bg-red-500", L:"bg-amber-500", E:"bg-blue-400", H:"bg-slate-400" };

  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-bold text-slate-900">My Attendance</h1><p className="text-sm text-slate-500 mt-1">Track your daily attendance record</p></div>

      {/* Controls */}
      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-4 flex flex-wrap gap-3">
        <select value={month} onChange={e=>setMonth(Number(e.target.value))} className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm placeholder:text-slate-400 text-slate-900 transition focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-400 disabled:bg-slate-50 disabled:text-slate-400 disabled:cursor-not-allowed dark:bg-slate-800 dark:border-slate-600 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:ring-indigo-400 w-40">
          {Array.from({length:12},(_,i)=><option key={i+1} value={i+1}>{dayjs().month(i).format("MMMM")}</option>)}
        </select>
        <select value={year} onChange={e=>setYear(Number(e.target.value))} className="w-full rounded-xl border border-slate-200 bg-white px-4 py-2.5 text-sm placeholder:text-slate-400 text-slate-900 transition focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-400 disabled:bg-slate-50 disabled:text-slate-400 disabled:cursor-not-allowed dark:bg-slate-800 dark:border-slate-600 dark:text-slate-100 dark:placeholder:text-slate-500 dark:focus:ring-indigo-400 w-28">
          {[dayjs().year()-1, dayjs().year()].map(y=><option key={y} value={y}>{y}</option>)}
        </select>
      </div>

      {isLoading ? <div className="p-4"><SkeletonCard /></div> : isError ? <ErrorState onRetry={() => refetch()} /> : report && (
        <>
          {/* Summary */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
            {[
              ["Total Days", report.total_school_days, "text-slate-800"],
              ["Present",    report.present,           "text-green-600"],
              ["Absent",     report.absent,            "text-red-600"],
              ["Late",       report.late,              "text-amber-600"],
              ["Attendance", percent(report.percentage), attendanceColor(report.percentage)],
            ].map(([l,v,c])=>(
              <div key={String(l)} className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-4 text-center">
                <p className={`text-2xl font-bold ${c}`}>{v}</p>
                <p className="text-xs text-slate-500 mt-1">{l}</p>
              </div>
            ))}
          </div>

          {/* Calendar */}
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
            <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between dark:border-slate-700"><h2 className="text-base font-semibold">{dayjs(`${year}-${month}`).format("MMMM YYYY")} — Daily Record</h2></div>
            <div className="p-5">
              <div className="grid grid-cols-7 gap-1 text-center text-xs font-medium text-slate-500 mb-2">
                {["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].map(d=><div key={d}>{d}</div>)}
              </div>
              <div className="grid grid-cols-7 gap-1">
                {/* Offset for first day */}
                {Array.from({length:(dayjs(`${year}-${String(month).padStart(2,"0")}-01`).day()+6)%7},(_,i)=><div key={`pad-${i}`}/>)}
                {(report.records ?? []).map((rec: { date: string; status: string }) => {
                  const s = rec.status;
                  const bg = colorMap[s] ?? "bg-slate-100";
                  const day = dayjs(rec.date).date();
                  return (
                    <div key={rec.date} title={`${fmt.date(rec.date)}: ${ATTENDANCE_STATUS[s]?.label ?? s}`}
                      className={`rounded-lg p-2 text-center text-xs font-semibold cursor-default ${bg} ${s==="P"||s==="E"?"text-white":"text-white"}`}>
                      {day}
                    </div>
                  );
                })}
              </div>
              <div className="flex flex-wrap gap-4 mt-5 text-xs">
                {Object.entries(ATTENDANCE_STATUS).map(([k,v])=>(
                  <div key={k} className="flex items-center gap-1.5">
                    <span className={`h-3 w-3 rounded-sm ${colorMap[k]??""}`}/>
                    <span className="text-slate-600">{v.label}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
