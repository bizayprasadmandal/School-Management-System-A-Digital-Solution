import React, { useState } from "react";
import { useClassrooms, useCurrentAcademicYear } from "../../api/hooks";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Select, SkeletonCard } from "../../components/common";
import { useTitle } from "../../hooks";

const DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
const COLORS = ["bg-indigo-100 text-indigo-800","bg-emerald-100 text-emerald-800","bg-amber-100 text-amber-800","bg-violet-100 text-violet-800","bg-rose-100 text-rose-800","bg-teal-100 text-teal-800","bg-orange-100 text-orange-800","bg-cyan-100 text-cyan-800"];

export default function TimetablePage() {
  useTitle("Timetable");
  const [classroomId, setClassroomId] = useState<number|null>(null);
  const { data: classroomsData } = useClassrooms();
  const { data: academicYear } = useCurrentAcademicYear();
  const classrooms = classroomsData?.results ?? [];

  interface WeeklySlot {
  subject_name: string;
  period_name: string;
  start_time: string;
  end_time: string;
  teacher_name: string;
  classroom_name: string;
  room: string;
}

const { data: weekly, isLoading } = useQuery({
    queryKey: ["admin-timetable", classroomId, academicYear?.id],
    queryFn: () => api.get<Record<string, WeeklySlot[]>>(`/timetable/slots/weekly/?classroom_id=${classroomId}&academic_year_id=${academicYear?.id}`),
    enabled: !!classroomId && !!academicYear?.id,
  });

  const colorMap: Record<string,string> = {};
  let ci = 0;
  if (weekly) Object.values(weekly).flat().forEach(s => { if (!colorMap[s.subject_name]) colorMap[s.subject_name] = COLORS[ci++ % COLORS.length]; });

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div><h1 className="text-2xl font-bold text-slate-900">Timetable</h1><p className="text-sm text-slate-500 mt-0.5">Weekly class schedules</p></div>
      </div>
      <div className="card p-4 flex flex-wrap gap-4">
        <div className="flex-1 min-w-48">
          <Select label="Select Classroom" placeholder="Choose a class…" value={classroomId ?? ""}
            onChange={e=>setClassroomId(Number(e.target.value)||null)}
            options={classrooms.map(c=>({value:c.id, label:`${c.grade_name} ${c.name}`}))} />
        </div>
      </div>
      {isLoading && <SkeletonCard className="max-w-md mx-auto" />}
      {weekly && !isLoading && (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-slate-50">
                  <th className="px-4 py-3 text-left text-xs font-semibold text-slate-500 uppercase border-b border-slate-100 w-24">Period</th>
                  {DAYS.map(d=><th key={d} className="px-3 py-3 text-left text-xs font-semibold text-slate-500 uppercase border-b border-l border-slate-100 min-w-36">{d}</th>)}
                </tr>
              </thead>
              <tbody>
                {Array.from(new Set(Object.values(weekly).flat().map(s=>s.period_name))).map((period, pi) => (
                  <tr key={String(period)} className={pi%2===0?"bg-white":"bg-slate-50/40"}>
                    <td className="px-4 py-3 border-b border-slate-100">
                      <p className="text-xs font-semibold text-slate-700">{String(period)}</p>
                      <p className="text-[10px] text-slate-400">{Object.values(weekly).flat().find(s=>s.period_name===period)?.start_time}</p>
                    </td>
                    {DAYS.map(day=>{
                      const slot = (weekly[day]??[]).find(s=>s.period_name===period);
                      return (
                        <td key={day} className="px-2 py-2 border-b border-l border-slate-100">
                          {slot ? (
                            <div className={`rounded-lg p-2 text-xs ${colorMap[slot.subject_name]??COLORS[0]}`}>
                              <p className="font-semibold truncate">{slot.subject_name}</p>
                              <p className="opacity-70 truncate mt-0.5">{slot.teacher_name}</p>
                            </div>
                          ) : <div className="h-10"/>}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
      {!classroomId && !isLoading && (
        <div className="card p-16 text-center text-slate-400"><p>Select a classroom to view its timetable</p></div>
      )}
    </div>
  );
}
