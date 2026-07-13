/**
 * Parent Grades Page — view children's exam results and report cards
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Badge, DataTable, EmptyState, SkeletonCard } from "../../components/common";
import { percent, gradeBg } from "../../utils";
import { useTitle } from "../../hooks";
import type { StudentListItem, ReportCard, PaginatedResponse } from "../../types";
import { TrophyIcon } from "@heroicons/react/24/outline";

export default function ParentGradesPage() {
  useTitle("Children's Grades");
  const [childIdx, setChildIdx] = useState(0);

  const { data: children, isLoading: childrenLoading } = useQuery({ queryKey: ["parent-children-gr"], queryFn: () => api.get<PaginatedResponse<StudentListItem>>("/students/") });
  const childList = children?.results ?? [];
  const child = childList[childIdx];

  const { data: rcData, isLoading: rcLoading } = useQuery({
    queryKey: ["parent-child-rc", child?.id],
    queryFn: () => api.get<PaginatedResponse<ReportCard>>(`/gradebook/report-cards/?student=${child.id}`),
    enabled: !!child?.id,
  });
  const rcs = rcData?.results ?? [];

  return (
    <div className="space-y-5">
      <div><h1 className="text-2xl font-bold text-slate-900">Grades</h1><p className="text-sm text-slate-500 mt-1">Exam results and report cards</p></div>

      {childList.length > 1 && (
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-4 flex gap-2 overflow-x-auto">
          {childList.map((c: StudentListItem, i: number) => (
            <button key={c.id} onClick={() => setChildIdx(i)}
              className={`flex-shrink-0 rounded-xl px-4 py-2 text-sm font-semibold transition-colors ${i===childIdx?"bg-violet-600 text-white":"bg-slate-100 text-slate-600 hover:bg-slate-200"}`}>
              {c.full_name}
            </button>
          ))}
        </div>
      )}

      {childrenLoading || rcLoading ? <div className="p-4"><SkeletonCard /></div>
        : rcs.length === 0
        ? <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-8"><EmptyState icon={TrophyIcon} title="No published results" description="Report cards appear here once published by the school." /></div>
        : (
          <>
            {/* Latest result highlight */}
            {rcs[0] && (
              <div className="rounded-2xl bg-gradient-to-r from-violet-600 to-indigo-600 p-6 text-white">
                <p className="text-violet-200 text-sm">Latest — {rcs[0].exam_name}</p>
                <div className="flex gap-8 mt-3">
                  <div><p className="text-4xl font-black">{percent(Number(rcs[0].percentage))}</p><p className="text-violet-200 text-xs mt-1">Score</p></div>
                  <div><p className="text-4xl font-black">{rcs[0].grade_letter}</p><p className="text-violet-200 text-xs mt-1">Grade</p></div>
                  {rcs[0].rank_in_class && <div><p className="text-4xl font-black">#{rcs[0].rank_in_class}</p><p className="text-violet-200 text-xs mt-1">Rank</p></div>}
                </div>
              </div>
            )}
            <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
              <div className="px-5 py-4 border-b border-slate-100 flex items-center justify-between dark:border-slate-700"><h2 className="text-base font-semibold">All Report Cards</h2></div>
              <DataTable
                columns={[
                  { key:"exam_name", header:"Exam" },
                  { key:"academic_year_name", header:"Year" },
                  { key:"percentage", header:"Score", render:r=><span className={`text-xs font-bold px-2 py-1 rounded-full ${gradeBg(Number(r.percentage))}`}>{percent(Number(r.percentage))}</span> },
                  { key:"grade_letter", header:"Grade", render:r=><Badge color="indigo">{r.grade_letter}</Badge> },
                  { key:"obtained_marks", header:"Marks", render:r=>`${r.obtained_marks}/${r.total_marks}` },
                  { key:"rank_in_class", header:"Rank", render:r=>r.rank_in_class?`#${r.rank_in_class}`:"—" },
                  { key:"status", header:"Status", render:r=><Badge color={r.status==="published"?"green":"slate"}>{r.status}</Badge> },
                ]}
                data={rcs} rowKey={r=>r.id}
              />
            </div>
          </>
        )
      }
    </div>
  );
}
