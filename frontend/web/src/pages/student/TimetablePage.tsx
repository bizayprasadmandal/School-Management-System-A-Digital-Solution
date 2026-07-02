import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Badge, Spinner } from "../../components/common";
import { useTitle } from "../../hooks";
import { fmt } from "../../utils";

const DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
const COLORS = ["bg-indigo-50 border-indigo-200 text-indigo-800","bg-emerald-50 border-emerald-200 text-emerald-800","bg-amber-50 border-amber-200 text-amber-800","bg-violet-50 border-violet-200 text-violet-800","bg-rose-50 border-rose-200 text-rose-800","bg-teal-50 border-teal-200 text-teal-800"];

export default function StudentTimetablePage() {
  useTitle("My Timetable");
  const { data: profile } = useQuery({ queryKey:["student-me-tt"], queryFn:()=>api.get<any>("/students/me/") });
  const classroomId = profile?.enrollments?.[0]?.classroom;

  const { data: weekly, isLoading } = useQuery({
    queryKey: ["student-timetable", classroomId],
    queryFn: () => api.get<any>(`/timetable/slots/weekly/?classroom_id=${classroomId}`),
    enabled: !!classroomId,
  });

  if (isLoading) return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;

  const subjectColorMap: Record<string,string> = {};
  let colorIdx = 0;
  Object.values(weekly ?? {}).flat().forEach((s: any) => {
    if (!subjectColorMap[s.subject_name]) subjectColorMap[s.subject_name] = COLORS[colorIdx++ % COLORS.length];
  });

  return (
    <div className="space-y-5">
      <div><h1 className="text-2xl font-bold text-slate-900">My Timetable</h1><p className="text-sm text-slate-500 mt-1">Weekly class schedule</p></div>
      {!weekly ? (
        <div className="card p-16 text-center text-slate-400"><p>No timetable available for your class yet.</p></div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {DAYS.map(day => {
            const slots: any[] = weekly[day] ?? [];
            return (
              <div key={day} className="card">
                <div className="card-header"><h2 className="text-sm font-bold text-slate-800">{day}</h2><Badge color="slate">{slots.length} periods</Badge></div>
                <div className="card-body space-y-2">
                  {slots.length === 0
                    ? <p className="text-xs text-slate-400 text-center py-4">No classes</p>
                    : slots.map((s: any, i: number) => (
                      <div key={i} className={`rounded-xl border px-3 py-2.5 ${subjectColorMap[s.subject_name] ?? COLORS[0]}`}>
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-semibold truncate">{s.subject_name}</p>
                          <p className="text-xs opacity-70 ml-2 flex-shrink-0">{fmt.time(s.start_time)}</p>
                        </div>
                        <p className="text-xs opacity-70 mt-0.5">{s.teacher_name} {s.room && `· ${s.room}`}</p>
                      </div>
                    ))
                  }
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
