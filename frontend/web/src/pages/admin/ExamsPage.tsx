import React from "react";
import { useQuery } from "@tanstack/react-query";
import type { Exam } from "../../types";
import { api } from "../../api/client";
import { Badge, SkeletonCard } from "../../components/common";
import type { BadgeColor } from "../../components/common";
import { useCurrentAcademicYear } from "../../api/hooks";
import { fmt } from "../../utils";
import { useTitle } from "../../hooks";

export default function ExamsPage() {
  useTitle("Examinations");
  const { data: ay } = useCurrentAcademicYear();
  const { data, isLoading } = useQuery({ queryKey:["exams",ay?.id], queryFn:()=>api.get<{results: Exam[]}>("/gradebook/exams/",{academic_year:ay?.id}), enabled:!!ay?.id });
  const exams = data?.results ?? [];
  const STATUS_COLOR: Record<string, BadgeColor> = { scheduled:"blue", ongoing:"amber", completed:"green", cancelled:"slate" };

  return (
    <div className="space-y-5">
      <div><h1 className="text-2xl font-bold text-slate-900">Examinations</h1><p className="text-sm text-slate-500 mt-0.5">Manage exams and assessment schedules</p></div>
      {isLoading ? <div className="grid grid-cols-1 gap-3"><SkeletonCard /><SkeletonCard /><SkeletonCard /></div>
        : <div className="space-y-3">
            {exams.length === 0 ? <div className="card p-12 text-center text-slate-400">No exams scheduled for this academic year.</div>
              : exams.map((e: { id: string; name: string; exam_type_name: string; start_date: string; end_date: string; schedule_count: number; status: string }) => (
                <div key={e.id} className="card p-4 flex items-center justify-between gap-4">
                  <div><p className="text-sm font-semibold text-slate-900">{e.name}</p><p className="text-xs text-slate-500 mt-0.5">{e.exam_type_name} · {fmt.date(e.start_date)} – {fmt.date(e.end_date)} · {e.schedule_count} subjects</p></div>
                  <Badge color={STATUS_COLOR[e.status] ?? "slate"}>{e.status}</Badge>
                </div>
              ))
            }
          </div>
      }
    </div>
  );
}
