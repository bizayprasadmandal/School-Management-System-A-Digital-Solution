import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Badge, SkeletonCard, ErrorState } from "../../components/common";
import { useTitle } from "../../hooks";
import { fmt } from "../../utils";

const DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
const COLORS = ["bg-indigo-50 border-indigo-200 text-indigo-800","bg-emerald-50 border-emerald-200 text-emerald-800","bg-amber-50 border-amber-200 text-amber-800","bg-violet-50 border-violet-200 text-violet-800","bg-rose-50 border-rose-200 text-rose-800","bg-teal-50 border-teal-200 text-teal-800"];

export default function StudentTimetablePage() {
  useTitle("My Timetable");
  const { data: profile } = useQuery({ queryKey:["student-me-tt"], queryFn:()=>api.get<{ id: string; enrollments: { classroom: number }[] }>("/students/me/") });
  const classroomId = profile?.enrollments?.[0]?.classroom;

  const { data: weekly, isLoading, isError, refetch } = useQuery({
    queryKey: ["student-timetable", classroomId],
    queryFn: () => api.get<Record<string, { subject_name: string; start_time: string; end_time: string; teacher_name: string; room: string }[]>>(`/timetable/slots/weekly/?classroom_id=${classroomId}`),
    enabled: !!classroomId,
  });

  if (isLoading) return <div className="p-4"><SkeletonCard /></div>;
  if (isError) return <ErrorState onRetry={() => refetch()} />;

  const subjectColorMap: Record<string,string> = {};
  let colorIdx = 0;
  Object.values(weekly ?? {}).flat().forEach((s: { subject_name: string; teacher_name: string; start_time: string; end_time: string; room: string }) => {
    if (!subjectColorMap[s.subject_name]) subjectColorMap[s.subject_name] = COLORS[colorIdx++ % COLORS.length];
  });

  return (
    <div className="space-y-5">
      <div><h1 className="text-2xl font-bold text-slate-900">My Timetable</h1><p className="text-sm text-slate-500 mt-1">Weekly class schedule</p></div>
      {!weekly ? (
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-16 text-center text-slate-400"><p>No timetable available for your class yet.</p></div>
      ) : (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {DAYS.map(day => {
            const slots = weekly[day] ?? [];
            return (
              <div key={day} className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
                <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between dark:border-slate-700"><h2 className="text-sm font-bold text-slate-800">{day}</h2><Badge color="slate">{slots.length} periods</Badge></div>
                <div className="p-5 space-y-2">
                  {slots.length === 0
                    ? <p className="text-xs text-slate-400 text-center py-4">No classes</p>
                    : slots.map((s: { subject_name: string; teacher_name: string; start_time: string; end_time: string; room: string }, i: number) => (
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
