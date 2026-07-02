import React from "react";
import { useCurrentAcademicYear } from "../../api/hooks";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Badge, Spinner } from "../../components/common";
import { useTitle } from "../../hooks";
import { useAuthStore } from "../../store/authStore";
import dayjs from "dayjs";

const DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
const COLORS = ["bg-indigo-50 border-l-2 border-indigo-400","bg-emerald-50 border-l-2 border-emerald-400","bg-amber-50 border-l-2 border-amber-400","bg-violet-50 border-l-2 border-violet-400","bg-rose-50 border-l-2 border-rose-400"];

export default function TeacherTimetablePage() {
  useTitle("My Timetable");
  const { user } = useAuthStore();
  const { data: academicYear } = useCurrentAcademicYear();
  const todayIdx = (dayjs().day() + 6) % 7;

  const { data: slots, isLoading } = useQuery({
    queryKey: ["teacher-schedule", user?.id, academicYear?.id],
    queryFn: () => api.get<any[]>("/timetable/slots/teacher-schedule/", { academic_year_id: academicYear?.id }),
    enabled: !!academicYear?.id,
  });

  const byDay: Record<string, any[]> = {};
  DAYS.forEach(d => { byDay[d] = []; });
  (slots ?? []).forEach(s => {
    const dayName = DAYS[s.day_of_week];
    if (dayName) byDay[dayName].push(s);
  });
  Object.values(byDay).forEach(arr => arr.sort((a,b) => a.start_time.localeCompare(b.start_time)));

  const colorMap: Record<string,string> = {};
  let ci = 0;
  (slots ?? []).forEach(s => { if (!colorMap[s.subject_name]) colorMap[s.subject_name] = COLORS[ci++ % COLORS.length]; });

  if (isLoading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  return (
    <div className="space-y-5">
      <div><h1 className="text-2xl font-bold text-slate-900">My Timetable</h1><p className="text-sm text-slate-500 mt-1">Weekly teaching schedule · {academicYear?.name}</p></div>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {DAYS.map((day, idx) => (
          <div key={day} className={`card ${idx === todayIdx ? "ring-2 ring-indigo-500 ring-offset-2" : ""}`}>
            <div className="card-header">
              <h2 className="text-sm font-bold text-slate-800">{day}</h2>
              {idx === todayIdx && <Badge color="indigo" dot>Today</Badge>}
              {idx !== todayIdx && <Badge color="slate">{byDay[day].length} periods</Badge>}
            </div>
            <div className="card-body space-y-2">
              {byDay[day].length === 0
                ? <p className="text-xs text-slate-400 text-center py-3">No classes</p>
                : byDay[day].map((s, i) => (
                  <div key={i} className={`rounded-lg p-3 ${colorMap[s.subject_name] ?? COLORS[0]}`}>
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-semibold text-slate-800 truncate">{s.subject_name}</p>
                      <p className="text-xs text-slate-500 flex-shrink-0 ml-2">{s.start_time?.slice(0,5)}–{s.end_time?.slice(0,5)}</p>
                    </div>
                    <p className="text-xs text-slate-600 mt-0.5">{s.classroom_name} {s.room && `· ${s.room}`}</p>
                  </div>
                ))
              }
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
