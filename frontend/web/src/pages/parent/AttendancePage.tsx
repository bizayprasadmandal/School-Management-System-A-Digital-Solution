/**
 * Parent Attendance Page — view attendance for all children
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { api } from "../../api/client";
import { Badge, Select, SkeletonCard, SkeletonChart } from "../../components/common";
import { percent, attendanceColor, ATTENDANCE_STATUS } from "../../utils";
import { useTitle } from "../../hooks";
import type { StudentListItem, PaginatedResponse } from "../../types";

interface AttendanceReport {
  total_school_days: number;
  present: number;
  absent: number;
  late: number;
  excused: number;
  percentage: number;
  records: AttendanceDayRecord[];
}

interface AttendanceDayRecord {
  date: string;
  status: string;
}

const colorMap: Record<string,string> = { P:"bg-green-500", A:"bg-red-500", L:"bg-amber-500", E:"bg-blue-400" };

export default function ParentAttendancePage() {
  useTitle("Children's Attendance");
  const [month, setMonth] = useState(dayjs().month() + 1);
  const [year] = useState(dayjs().year());
  const [childIdx, setChildIdx] = useState(0);

  const { data: children } = useQuery({
    queryKey: ["parent-children-att"],
    queryFn: () => api.get<PaginatedResponse<StudentListItem>>("/students/"),
  });
  const childList = children?.results ?? [];
  const child = childList[childIdx];

  const { data: report, isLoading } = useQuery({
    queryKey: ["parent-child-att", child?.id, month, year],
    queryFn: () => api.get<AttendanceReport>(`/attendance/student-report/?student_id=${child.id}&month=${month}&year=${year}`),
    enabled: !!child?.id,
  });

  const daysInMonth = dayjs(`${year}-${String(month).padStart(2,"0")}-01`).daysInMonth();
  const firstDay = (dayjs(`${year}-${String(month).padStart(2,"0")}-01`).day() + 6) % 7;

  return (
    <div className="space-y-5">
      <div><h1 className="text-2xl font-bold text-slate-900">Attendance</h1><p className="text-sm text-slate-500 mt-1">Monitor your children&apos;s daily attendance</p></div>

      {/* Child + month selectors */}
      <div className="card p-4 flex flex-wrap gap-4">
        {childList.length > 1 && (
          <Select label="Child" value={childIdx} onChange={e => setChildIdx(Number(e.target.value))}
            options={childList.map((c: StudentListItem, i: number) => ({ value: i, label: c.full_name }))} className="w-52" />
        )}
        <Select label="Month" value={month} onChange={e => setMonth(Number(e.target.value))}
          options={Array.from({length:12},(_,i)=>({value:i+1,label:dayjs().month(i).format("MMMM")}))} className="w-40" />
      </div>

      {child && (
        <div className="card p-4 flex items-center gap-4">
          <div className="h-12 w-12 rounded-xl bg-violet-100 flex items-center justify-center text-lg font-bold text-violet-700 flex-shrink-0">
            {child.full_name.split(" ").map((n: string)=>n[0]).join("").slice(0,2)}
          </div>
          <div><p className="text-sm font-bold text-slate-900">{child.full_name}</p><p className="text-xs text-slate-500">{child.current_class ?? "—"} · Adm: {child.admission_number}</p></div>
        </div>
      )}

      {isLoading ? <div className="space-y-4"><SkeletonChart /><SkeletonCard /></div> : report && (
        <>
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-4">
            {[
              ["Total Days", report.total_school_days, "text-slate-800"],
              ["Present", report.present, "text-green-600"],
              ["Absent", report.absent, "text-red-600"],
              ["Late", report.late, "text-amber-600"],
              ["Rate", percent(report.percentage), attendanceColor(report.percentage)],
            ].map(([l,v,c])=>(
              <div key={String(l)} className="card p-4 text-center">
                <p className={`text-2xl font-bold ${c}`}>{v}</p>
                <p className="text-xs text-slate-500 mt-1">{l}</p>
              </div>
            ))}
          </div>

          {report.percentage < 75 && (
            <div className="rounded-xl border border-red-200 bg-red-50 p-4">
              <p className="text-sm font-semibold text-red-800">⚠️ Attendance below 75% minimum</p>
              <p className="text-xs text-red-600 mt-1">Please contact the school to discuss your child&apos;s attendance.</p>
            </div>
          )}

          <div className="card">
            <div className="card-header"><h2 className="text-base font-semibold">{dayjs(`${year}-${String(month).padStart(2,"0")}-01`).format("MMMM YYYY")}</h2></div>
            <div className="card-body">
              <div className="grid grid-cols-7 gap-1 text-center text-xs font-medium text-slate-500 mb-2">
                {["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].map(d=><div key={d}>{d}</div>)}
              </div>
              <div className="grid grid-cols-7 gap-1">
                {Array.from({length:firstDay},(_,i)=><div key={`p${i}`}/>)}
                {Array.from({length:daysInMonth},(_,i)=>{
                  const day = i + 1;
                  const rec = (report.records??[]).find((r: AttendanceDayRecord)=>dayjs(r.date).date()===day);
                  const s = rec?.status;
                  return (
                    <div key={day} title={s ? ATTENDANCE_STATUS[s]?.label : undefined}
                      className={`aspect-square flex items-center justify-center rounded-lg text-xs font-semibold ${s ? `${colorMap[s]??""} text-white` : "text-slate-700"}`}>
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
