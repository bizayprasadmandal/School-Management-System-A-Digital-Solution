import React from "react";
import { DocumentArrowDownIcon, TrophyIcon } from "@heroicons/react/24/outline";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { useReportCards } from "../../api/hooks";
import { Badge, EmptyState, DataTable, SkeletonCard } from "../../components/common";
import { percent, gradeBg } from "../../utils";
import { useTitle } from "../../hooks";
import { useAuthStore } from "../../store/authStore";

export default function StudentGradesPage() {
  useTitle("My Grades");
  const { tokens } = useAuthStore();
  const { data: profile, isLoading: profileLoading } = useQuery({ queryKey: ["student-me"], queryFn: () => api.get<{ id: string }>("/students/me/") });
  const { data: rcData, isLoading: rcLoading } = useReportCards(profile?.id ?? "");
  const reportCards = rcData?.results ?? [];
  const latest = reportCards.find((r: { status: string }) => r.status === "published") ?? reportCards[0];

  const downloadPDF = async (url: string, name: string) => {
    const res = await fetch(url, { headers: { Authorization: `Bearer ${tokens?.access}` } });
    const blob = await res.blob();
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = `${name}.pdf`; a.click();
  };

  if (profileLoading || rcLoading) return <div className="p-4"><SkeletonCard /></div>;

  return (
    <div className="space-y-6">
      <div><h1 className="text-2xl font-bold text-slate-900">My Grades</h1><p className="text-sm text-slate-500 mt-1">Exam results and report cards</p></div>
      {latest && (
        <div className="rounded-2xl bg-gradient-to-r from-indigo-600 to-violet-600 p-6 text-white">
          <p className="text-indigo-200 text-sm">Latest Result — {latest.exam_name}</p>
          <div className="flex items-center gap-8 mt-3">
            <div><p className="text-4xl font-black">{percent(Number(latest.percentage))}</p><p className="text-indigo-200 text-xs mt-1">Overall Score</p></div>
            <div><p className="text-4xl font-black">{latest.grade_letter}</p><p className="text-indigo-200 text-xs mt-1">Grade</p></div>
            {latest.rank_in_class && <div><p className="text-4xl font-black">#{latest.rank_in_class}</p><p className="text-indigo-200 text-xs mt-1">Class Rank</p></div>}
          </div>
          {latest.pdf_url && <button onClick={() => downloadPDF(latest.pdf_url!, latest.exam_name)} className="mt-4 flex items-center gap-2 rounded-xl bg-white/20 hover:bg-white/30 px-4 py-2 text-sm font-semibold transition-colors"><DocumentArrowDownIcon className="h-4 w-4" />Download PDF</button>}
        </div>
      )}
      <div className="card">
        <div className="card-header"><h2 className="text-base font-semibold">All Report Cards</h2></div>
        {reportCards.length === 0
          ? <div className="p-8"><EmptyState icon={TrophyIcon} title="No results published yet" description="Your exam results will appear here once published." /></div>
          : <DataTable
              columns={[
                { key:"exam_name", header:"Exam" },
                { key:"academic_year_name", header:"Year" },
                { key:"percentage", header:"Score", render:r=><span className={`font-semibold text-xs px-2 py-1 rounded-full ${gradeBg(Number(r.percentage))}`}>{percent(Number(r.percentage))}</span> },
                { key:"grade_letter", header:"Grade", render:r=><Badge color="indigo">{r.grade_letter}</Badge> },
                { key:"obtained_marks", header:"Marks", render:r=>`${r.obtained_marks}/${r.total_marks}` },
                { key:"rank_in_class", header:"Rank", render:r=>r.rank_in_class?`#${r.rank_in_class}`:"—" },
                { key:"status", header:"Status", render:r=><Badge color={r.status==="published"?"green":"slate"}>{r.status}</Badge> },
                { key:"pdf_url", header:"PDF", render:r=>r.pdf_url?<button onClick={()=>downloadPDF(r.pdf_url,r.exam_name)} className="text-indigo-600 text-xs font-medium hover:underline">Download</button>:null },
              ]}
              data={reportCards as any[]} rowKey={r=>r.id}
            />
        }
      </div>
    </div>
  );
}
