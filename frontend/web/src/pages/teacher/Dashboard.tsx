/**
 * Teacher Dashboard — today's schedule, quick attendance, class statistics
 */
import React from "react";
import { useNavigate } from "react-router-dom";
import { ClipboardDocumentCheckIcon, BookOpenIcon, UsersIcon, CheckCircleIcon } from "@heroicons/react/24/outline";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import dayjs from "dayjs";
import { useAuthStore } from "../../store/authStore";
import { useClassrooms, useCurrentAcademicYear } from "../../api/hooks";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Button, Badge, Spinner } from "../../components/common";
import { percent, attendanceColor } from "../../utils";
import { useTitle } from "../../hooks";

const WEEK_ATTENDANCE = [
  { day: "Mon", pct: 94 }, { day: "Tue", pct: 91 }, { day: "Wed", pct: 96 },
  { day: "Thu", pct: 88 }, { day: "Fri", pct: 93 },
];

export default function TeacherDashboard() {
  useTitle("Dashboard");
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const today = dayjs();
  const todayStr = today.format("YYYY-MM-DD");
  const dayIndex = (today.day() + 6) % 7;

  const { data: academicYear } = useCurrentAcademicYear();
  const { data: classroomsData } = useClassrooms();
  const classrooms = classroomsData?.results ?? [];

  const { data: todaySlots, isLoading: slotsLoading } = useQuery({
    queryKey: ["teacher-today-slots", user?.id, academicYear?.id],
    queryFn: () => api.get<any[]>("/timetable/slots/teacher-schedule/", { academic_year_id: academicYear?.id }),
    enabled: !!user && !!academicYear,
  });

  const { data: attendanceSummaries } = useQuery({
    queryKey: ["teacher-today-attendance", classrooms.map(c => c.id), todayStr],
    queryFn: async () => {
      if (!classrooms.length) return [];
      const results = await Promise.allSettled(
        classrooms.map(c =>
          api.get<any>("/attendance/classroom-summary/", { classroom_id: c.id, date: todayStr })
            .then(d => ({ ...d, classroom: c }))
        )
      );
      return results.filter(r => r.status === "fulfilled").map(r => (r as any).value);
    },
    enabled: classrooms.length > 0,
  });

  const todaySchedule = (todaySlots ?? []).filter((s: any) => s.day_of_week === dayIndex);
  const avgAttendance = attendanceSummaries?.length
    ? attendanceSummaries.reduce((s: number, a: any) => s + (a.breakdown?.present / (a.total_students || 1) * 100), 0) / attendanceSummaries.length
    : null;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Good {today.hour() < 12 ? "morning" : "afternoon"}, {user?.first_name}! 👋</h1>
        <p className="text-sm text-slate-500 mt-1">{today.format("dddd, MMMM D YYYY")}</p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
        {[
          { label: "My Classes", value: classrooms.length, icon: UsersIcon, color: "bg-indigo-500" },
          { label: "Today's Periods", value: todaySchedule.length, icon: BookOpenIcon, color: "bg-violet-500" },
          { label: "Pending Grading", value: "—", icon: ClipboardDocumentCheckIcon, color: "bg-amber-500" },
          { label: "Avg Attendance", value: avgAttendance !== null ? percent(avgAttendance) : "—", icon: CheckCircleIcon, color: "bg-emerald-500" },
        ].map(({ label, value, icon: Icon, color }) => (
          <div key={label} className="card p-4 flex items-center gap-3">
            <div className={`flex h-10 w-10 items-center justify-center rounded-xl ${color} flex-shrink-0`}>
              <Icon className="h-5 w-5 text-white" />
            </div>
            <div><p className="text-xl font-bold text-slate-900">{value}</p><p className="text-xs text-slate-500">{label}</p></div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2 card">
          <div className="card-header">
            <h2 className="text-base font-semibold">Today&apos;s Schedule</h2>
            <Badge color="blue">{today.format("dddd")}</Badge>
          </div>
          <div className="card-body">
            {slotsLoading
              ? <div className="flex justify-center py-8"><Spinner /></div>
              : todaySchedule.length === 0
              ? <div className="text-center py-10 text-slate-400"><BookOpenIcon className="h-10 w-10 mx-auto mb-2 opacity-30" /><p>No classes scheduled today</p></div>
              : <div className="space-y-3">
                  {todaySchedule.map((slot: any, i: number) => (
                    <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-slate-50 hover:bg-indigo-50/60 transition-colors">
                      <div className="text-center w-16 flex-shrink-0">
                        <p className="text-xs font-bold text-indigo-600">{slot.start_time?.slice(0,5)}</p>
                        <p className="text-xs text-slate-400">{slot.end_time?.slice(0,5)}</p>
                      </div>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-semibold text-slate-900">{slot.subject_name}</p>
                        <p className="text-xs text-slate-500">{slot.classroom_name} · {slot.room ?? "Room TBD"}</p>
                      </div>
                      <Button variant="secondary" size="sm" onClick={() => navigate("/teacher/attendance")}>
                        Take Attendance
                      </Button>
                    </div>
                  ))}
                </div>
            }
          </div>
        </div>

        <div className="card">
          <div className="card-header"><h2 className="text-base font-semibold">This Week</h2></div>
          <div className="card-body">
            <ResponsiveContainer width="100%" height={180}>
              <BarChart data={WEEK_ATTENDANCE} margin={{ top: 4, right: 4, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="day" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 11 }} axisLine={false} tickLine={false} unit="%" domain={[75, 100]} />
                <Tooltip formatter={(v) => [`${v}%`, "Attendance"]} />
                <Bar dataKey="pct" fill="#6366f1" radius={[4, 4, 0, 0]} name="Attendance" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {(attendanceSummaries?.length ?? 0) > 0 && (
        <div className="card">
          <div className="card-header">
            <h2 className="text-base font-semibold">Today&apos;s Class Attendance</h2>
          </div>
          <div className="card-body">
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
              {attendanceSummaries?.map((summary: any, i: number) => {
                const pct = summary.total_students > 0 ? (summary.breakdown.present / summary.total_students * 100) : 0;
                return (
                  <div key={i} className="p-4 rounded-xl border border-slate-100 bg-slate-50 hover:border-indigo-200 transition-colors">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <p className="text-sm font-semibold text-slate-800">{summary.classroom?.grade_name} {summary.classroom?.name}</p>
                        <p className="text-xs text-slate-500">{summary.total_students} students</p>
                      </div>
                      <span className={`text-lg font-bold ${attendanceColor(pct)}`}>{percent(pct)}</span>
                    </div>
                    <div className="flex gap-2 text-xs">
                      <span className="text-green-600 font-medium">✓ {summary.breakdown?.present} Present</span>
                      <span className="text-red-600 font-medium">✗ {summary.breakdown?.absent} Absent</span>
                      {summary.not_recorded > 0 && <span className="text-amber-600">⚠ {summary.not_recorded} Unrecorded</span>}
                    </div>
                    <div className="mt-2 h-1.5 bg-slate-200 rounded-full overflow-hidden">
                      <div className="h-full bg-indigo-500 rounded-full" style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
