/**
 * Student Grades Page — Exam results, cumulative GPA, grade trend chart,
 * subject breakdown, and report card history
 */
import React, { useMemo } from "react";
import { DocumentArrowDownIcon, TrophyIcon, AcademicCapIcon, ChartBarIcon } from "@heroicons/react/24/outline";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { useReportCards } from "../../api/hooks";
import { Badge, EmptyState, DataTable, SkeletonCard, ErrorState } from "../../components/common";
import { percent, gradeBg, gradeColor } from "../../utils";
import { useTitle } from "../../hooks";
import { useAuthStore } from "../../store/authStore";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";


// ─── Interfaces ───────────────────────────────────────────────────────────────

interface CumulativeGPA {
  cumulative_gpa: number;
  total_exams: number;
  average_percentage: number;
  academic_year_name: string;
}

interface GradeSummaryItem {
  subject: string;
  exam: string;
  marks_obtained: number | null;
  max_marks: number;
  percentage: number | null;
  is_pass: boolean;
}

interface SubjectAggregate {
  subject: string;
  avg_percentage: number;
  total_exams: number;
  best_score: number;
}

// ─── Main component ───────────────────────────────────────────────────────────

export default function StudentGradesPage() {
  useTitle("My Grades");
  const { tokens } = useAuthStore();

  // ── Data fetching ───────────────────────────────────────────────────────

  const { data: profile, isLoading: profileLoading, isError: profileError, refetch: refetchProfile } = useQuery({
    queryKey: ["student-me"],
    queryFn: () => api.get<{ id: string }>("/students/me/"),
  });

  const { data: rcData, isLoading: rcLoading, isError: rcError, refetch: refetchRc } = useReportCards(profile?.id ?? "");
  const reportCards = rcData?.results ?? [];
  const latest = reportCards.find((r) => r.status === "published") ?? reportCards[0];

  // Cumulative GPA
  const { data: gpaData, isLoading: gpaLoading } = useQuery({
    queryKey: ["student-gpa", profile?.id],
    queryFn: () => api.get<CumulativeGPA>(`/students/${profile!.id}/cumulative-gpa/`),
    enabled: !!profile?.id,
    staleTime: 5 * 60 * 1000,
  });

  // Subject breakdown
  const { data: gradeSummary, isLoading: gsLoading } = useQuery({
    queryKey: ["student-grade-summary", profile?.id],
    queryFn: () => api.get<{ grades: GradeSummaryItem[] }>(`/students/${profile!.id}/grade-summary/`),
    enabled: !!profile?.id,
    staleTime: 5 * 60 * 1000,
  });

  // ── Derived data ────────────────────────────────────────────────────────

  // Trend data: percentage over exam results (chronological by last exam date)
  const trendData = useMemo(() => {
    // Sort report cards by published_at or fallback to exam name
    const sorted = [...reportCards].sort((a, b) => {
      const dateA = a.published_at ? new Date(a.published_at).getTime() : 0;
      const dateB = b.published_at ? new Date(b.published_at).getTime() : 0;
      return dateA - dateB;
    });
    return sorted.map((rc, idx) => ({
      name: rc.exam_name?.length > 12 ? rc.exam_name.slice(0, 12) + "…" : rc.exam_name || `Exam ${idx + 1}`,
      percentage: Number(rc.percentage),
      gpa: Number(rc.gpa ?? 0),
      fullName: rc.exam_name,
    }));
  }, [reportCards]);

  // Subject aggregates: average per subject
  const subjectData = useMemo(() => {
    if (!gradeSummary?.grades) return [];
    const bySubject: Record<string, { percentages: number[]; best: number; count: number }> = {};
    gradeSummary.grades.forEach((g) => {
      if (g.percentage == null) return;
      if (!bySubject[g.subject]) bySubject[g.subject] = { percentages: [], best: 0, count: 0 };
      bySubject[g.subject].percentages.push(g.percentage);
      bySubject[g.subject].best = Math.max(bySubject[g.subject].best, g.percentage);
      bySubject[g.subject].count += 1;
    });
    return Object.entries(bySubject).map(([subject, data]) => ({
      subject,
      avg_percentage: Math.round(data.percentages.reduce((a, b) => a + b, 0) / data.percentages.length),
      total_exams: data.count,
      best_score: Math.round(data.best),
    }));
  }, [gradeSummary]);

  const downloadPDF = async (url: string, name: string) => {
    const res = await fetch(url, { headers: { Authorization: `Bearer ${tokens?.access}` } });
    const blob = await res.blob();
    const a = document.createElement("a"); a.href = URL.createObjectURL(blob); a.download = `${name}.pdf`; a.click();
  };

  if (profileLoading || rcLoading) return <div className="p-4"><SkeletonCard /></div>;
  if (profileError) return <ErrorState onRetry={() => refetchProfile()} />;
  if (rcError) return <ErrorState onRetry={() => refetchRc()} />;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">My Grades</h1>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Exam results, GPA, and performance trends</p>
      </div>

      {/* Hero card — Latest result + GPA */}
      <div className="rounded-2xl bg-gradient-to-r from-indigo-600 via-indigo-600 to-violet-600 p-6 text-white">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-indigo-200 text-sm">
              {latest ? `Latest Result — ${latest.exam_name}` : "No results yet"}
            </p>
            {latest && (
              <div className="flex items-center gap-6 sm:gap-10 mt-3 flex-wrap">
                <div className="text-center">
                  <p className="text-4xl font-black">{percent(Number(latest.percentage))}</p>
                  <p className="text-indigo-200 text-xs mt-1">Score</p>
                </div>
                <div className="text-center">
                  <p className="text-4xl font-black">{latest.grade_letter}</p>
                  <p className="text-indigo-200 text-xs mt-1">Grade</p>
                </div>
                {latest.rank_in_class && (
                  <div className="text-center">
                    <p className="text-4xl font-black">#{latest.rank_in_class}</p>
                    <p className="text-indigo-200 text-xs mt-1">Class Rank</p>
                  </div>
                )}
              </div>
            )}
          </div>
          {/* Cumulative GPA badge */}
          {!gpaLoading && gpaData && (
            <div className="hidden sm:flex flex-col items-center rounded-xl bg-white/15 px-5 py-3">
              <p className="text-xs text-indigo-200 font-medium">Cumulative GPA</p>
              <p className="text-3xl font-black mt-1">{gpaData.cumulative_gpa.toFixed(2)}</p>
              <p className="text-[10px] text-indigo-200 mt-0.5">{gpaData.total_exams} exams</p>
            </div>
          )}
        </div>

        <div className="flex items-center gap-3 mt-4 flex-wrap">
          {latest?.pdf_url && (
            <button
              onClick={() => downloadPDF(latest.pdf_url!, latest.exam_name)}
              className="flex items-center gap-2 rounded-xl bg-white/20 hover:bg-white/30 px-4 py-2 text-sm font-semibold transition-colors"
            >
              <DocumentArrowDownIcon className="h-4 w-4" />
              Download PDF
            </button>
          )}
          {gpaData && (
            <div className="sm:hidden flex items-center gap-2 rounded-xl bg-white/15 px-4 py-2 text-sm">
              <AcademicCapIcon className="h-4 w-4" />
              GPA: <strong>{gpaData.cumulative_gpa.toFixed(2)}</strong>
            </div>
          )}
        </div>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div className="rounded-xl bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 p-4">
          <p className="text-xs text-slate-500 dark:text-slate-400">Total Exams</p>
          <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">{reportCards.length}</p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 p-4">
          <p className="text-xs text-slate-500 dark:text-slate-400">Average Score</p>
          <p className="text-2xl font-bold text-slate-900 dark:text-white mt-1">
            {reportCards.length > 0
              ? percent(Math.round(reportCards.reduce((s, r) => s + Number(r.percentage), 0) / reportCards.length))
              : "—"}
          </p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 p-4">
          <p className="text-xs text-slate-500 dark:text-slate-400">Best Score</p>
          <p className="text-2xl font-bold text-emerald-600 dark:text-emerald-400 mt-1">
            {reportCards.length > 0
              ? percent(Math.round(Math.max(...reportCards.map((r) => Number(r.percentage)))))
              : "—"}
          </p>
        </div>
        <div className="rounded-xl bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700 p-4">
          <p className="text-xs text-slate-500 dark:text-slate-400">Published</p>
          <p className="text-2xl font-bold text-indigo-600 dark:text-indigo-400 mt-1">
            {reportCards.filter((r) => r.status === "published").length}
          </p>
        </div>
      </div>

      {/* Grade trend chart + Subject breakdown */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        {/* ─── Trend chart ────────────────────────────────────────────────── */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm">
          <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
            <ChartBarIcon className="h-4 w-4 text-indigo-500" />
            <h2 className="text-base font-semibold text-slate-800 dark:text-white">Grade Trend</h2>
          </div>
          <div className="p-5">
            {trendData.length < 2 ? (
              <div className="flex flex-col items-center justify-center py-10 text-slate-400 dark:text-slate-500">
                <ChartBarIcon className="h-10 w-10 mb-2 opacity-30" />
                <p className="text-sm">Need at least 2 exams to show a trend</p>
              </div>
            ) : (
              <ResponsiveContainer width="100%" height={220}>
                <LineChart data={trendData} margin={{ top: 5, right: 10, left: -20, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 11 }} axisLine={false} tickLine={false} />
                  <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} axisLine={false} tickLine={false} unit="%" />
                  <Tooltip
                    formatter={(value: number) => [`${value.toFixed(1)}%`, "Score"]}
                    labelFormatter={(label, payload) => payload?.[0]?.payload?.fullName ?? label}
                  />
                  <Line
                    type="monotone"
                    dataKey="percentage"
                    stroke="#6366f1"
                    strokeWidth={2}
                    dot={{ fill: "#6366f1", r: 4, strokeWidth: 0 }}
                    activeDot={{ r: 6, fill: "#6366f1", stroke: "#fff", strokeWidth: 2 }}
                  />
                </LineChart>
              </ResponsiveContainer>
            )}
          </div>
        </div>

        {/* ─── Subject breakdown ──────────────────────────────────────────── */}
        <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm">
          <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center gap-2">
            <AcademicCapIcon className="h-4 w-4 text-indigo-500" />
            <h2 className="text-base font-semibold text-slate-800 dark:text-white">Subject Performance</h2>
          </div>
          <div className="p-5">
            {gsLoading ? (
              <div className="space-y-3">{[1,2,3,4].map(i => <div key={i} className="h-12 bg-slate-100 dark:bg-slate-700 rounded-lg animate-pulse" />)}</div>
            ) : subjectData.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-10 text-slate-400 dark:text-slate-500">
                <AcademicCapIcon className="h-10 w-10 mb-2 opacity-30" />
                <p className="text-sm">No grade data available yet</p>
              </div>
            ) : (
              <div className="space-y-3">
                {subjectData.map((s) => (
                  <div key={s.subject}>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span className="font-medium text-slate-700 dark:text-slate-300 truncate">{s.subject}</span>
                      <span className={`font-semibold ${gradeColor(String(s.avg_percentage))}`}>{percent(s.avg_percentage)}</span>
                    </div>
                    <div className="h-2 bg-slate-100 dark:bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full rounded-full transition-all duration-500"
                        style={{
                          width: `${s.avg_percentage}%`,
                          backgroundColor: s.avg_percentage >= 75 ? "#22c55e" : s.avg_percentage >= 50 ? "#f59e0b" : "#ef4444",
                        }}
                      />
                    </div>
                    <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5">
                      {s.total_exams} exam{s.total_exams !== 1 ? "s" : ""} · Best: {percent(s.best_score)}
                    </p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* All Report Cards table */}
      <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm">
        <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
          <h2 className="text-base font-semibold text-slate-800 dark:text-white">All Report Cards</h2>
          <Badge color="indigo">{reportCards.length} total</Badge>
        </div>
        {reportCards.length === 0 ? (
          <div className="p-8">
            <EmptyState
              icon={TrophyIcon}
              title="No results published yet"
              description="Your exam results will appear here once published."
            />
          </div>
        ) : (
          <DataTable
            columns={[
              { key: "exam_name", header: "Exam" },
              { key: "academic_year_name", header: "Year" },
              {
                key: "percentage",
                header: "Score",
                render: (r) => (
                  <span className={`font-semibold text-xs px-2 py-1 rounded-full ${gradeBg(Number(r.percentage))}`}>
                    {percent(Number(r.percentage))}
                  </span>
                ),
              },
              {
                key: "grade_letter",
                header: "Grade",
                render: (r) => <Badge color="indigo">{r.grade_letter}</Badge>,
              },
              {
                key: "obtained_marks",
                header: "Marks",
                render: (r) => `${r.obtained_marks}/${r.total_marks}`,
              },
              {
                key: "gpa",
                header: "GPA",
                render: (r) => (r.gpa ? Number(r.gpa).toFixed(2) : "—"),
              },
              {
                key: "rank_in_class",
                header: "Rank",
                render: (r) => (r.rank_in_class ? `#${r.rank_in_class}` : "—"),
              },
              {
                key: "status",
                header: "Status",
                render: (r) => (
                  <Badge color={r.status === "published" ? "green" : "slate"}>{r.status}</Badge>
                ),
              },
              {
                key: "pdf_url",
                header: "PDF",
                render: (r) =>
                  r.pdf_url ? (
                    <button
                      onClick={() => r.pdf_url && downloadPDF(r.pdf_url, r.exam_name)}
                      className="text-indigo-600 dark:text-indigo-400 text-xs font-medium hover:underline"
                    >
                      Download
                    </button>
                  ) : null,
              },
            ]}
            data={reportCards}
            rowKey={(r) => r.id}
            emptyMessage="No report cards"
          />
        )}
      </div>
    </div>
  );
}
