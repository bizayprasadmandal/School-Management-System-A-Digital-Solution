/**
 * Student Dashboard — Personal overview with fee summary, upcoming events,
 * enriched attendance gauge, and recent notifications
 */

import React, { useMemo } from "react";
import { Link } from "react-router-dom";
import {
  ClipboardDocumentCheckIcon,
  BookOpenIcon,
  CalendarDaysIcon,
  BanknotesIcon,
  BellIcon,
  TrophyIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  ClockIcon,
  ChevronRightIcon,
  AcademicCapIcon,
} from "@heroicons/react/24/outline";
import {
  RadialBarChart,
  RadialBar,
  PolarAngleAxis,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from "recharts";
import dayjs from "dayjs";
import { useAuthStore } from "../../store/authStore";
import {
  useStudentAttendanceSummary,
  useCurrentAcademicYear,
  useNotifications,
  useStudentInvoices,
  useSchoolEvents,
  useStudentAssessments,
} from "../../api/hooks";
import { SkeletonStudentDashboard, ErrorState } from "../../components/common";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import type { StudentDetail, SchoolEvent, Assessment, FeeInvoice } from "../../types";

// ─── Colour palette ───────────────────────────────────────────────────────────

const COLORS = {
  present: "#22c55e",
  absent: "#ef4444",
  late: "#f59e0b",
  excused: "#8b5cf6",
  paid: "#22c55e",
  unpaid: "#ef4444",
  overdue: "#f59e0b",
  partial: "#3b82f6",
  indigo: "#6366f1",
};

const PIE_COLORS = ["#22c55e", "#ef4444", "#f59e0b", "#3b82f6"];

// ─── InfoCard component ────────────────────────────────────────────────────────

function InfoCard({ label, value, icon: Icon, accent }: {
  label: string; value: string; icon: React.ComponentType<{ className?: string }>; accent: string;
}) {
  return (
    <div className={`rounded-xl p-4 ${accent} flex items-center gap-4 transition-transform hover:scale-[1.02] duration-200`}>
      <div className="rounded-lg bg-white/30 p-2.5">
        <Icon className="h-5 w-5 text-white" />
      </div>
      <div>
        <p className="text-xs font-medium text-white/80">{label}</p>
        <p className="text-xl font-bold text-white">{value}</p>
      </div>
    </div>
  );
}

// ─── StatBadge component ───────────────────────────────────────────────────────

function StatBadge({ label, value, color }: { label: string; value: number | string; color: string }) {
  return (
    <div className="rounded-lg px-3 py-2 text-center" style={{ backgroundColor: `${color}15` }}>
      <p className="text-lg font-bold" style={{ color }}>{value}</p>
      <p className="text-xs" style={{ color: `${color}cc` }}>{label}</p>
    </div>
  );
}

// ─── EventItem component ───────────────────────────────────────────────────────

function getEventIcon(type: string) {
  switch (type) {
    case "holiday": return "🎉";
    case "exam": return "📝";
    case "sports": return "⚽";
    case "cultural": return "🎭";
    case "meeting": return "🤝";
    case "deadline": return "⏰";
    default: return "📌";
  }
}

function EventItem({ event }: { event: SchoolEvent | Assessment }) {
  const isAssessment = "assessment_type" in event;
  const title = isAssessment ? (event as Assessment).title : (event as SchoolEvent).title;
  const date = isAssessment
    ? dayjs((event as Assessment).due_date)
    : dayjs((event as SchoolEvent).start_date);
  const type = !isAssessment ? (event as SchoolEvent).event_type : "deadline";
  const isPast = date.isBefore(dayjs(), "day");
  const isToday = date.isSame(dayjs(), "day");

  return (
    <div className={`flex items-start gap-3 rounded-lg p-3 transition-colors ${
      isPast ? "opacity-50" : isToday ? "bg-indigo-50 border border-indigo-100" : "bg-slate-50 hover:bg-slate-100"
    }`}>
      <span className="text-lg flex-shrink-0">{getEventIcon(type)}</span>
      <div className="min-w-0 flex-1">
        <p className={`text-sm font-medium truncate ${isPast ? "text-slate-500" : isToday ? "text-indigo-800" : "text-slate-800"}`}>
          {title}
        </p>
        <p className="text-xs text-slate-500 mt-0.5">
          {isToday ? "Today" : date.format("MMM D, ddd")}
          {" — "}
          {isAssessment ? "Due" : type.charAt(0).toUpperCase() + type.slice(1)}
        </p>
      </div>
      {isToday && <span className="h-2 w-2 rounded-full bg-indigo-500 animate-pulse flex-shrink-0 mt-1.5" />}
    </div>
  );
}

// ─── Main Dashboard ────────────────────────────────────────────────────────────

export default function StudentDashboard() {
  const { user } = useAuthStore();

  // ── Data fetches ──────────────────────────────────────────────────────────

  const { data: profile, isLoading: profileLoading, isError: profileError, refetch: refetchProfile } =
    useQuery<StudentDetail>({
      queryKey: ["student-profile"],
      queryFn: () => api.get("/students/me/"),
    });

  const { data: academicYear } = useCurrentAcademicYear();

  const { data: attendanceSummary, isLoading: attLoading, isError: attError } = useStudentAttendanceSummary(
    profile?.id ?? "",
    academicYear?.id
  );

  const { data: notifications, isLoading: notifLoading } = useNotifications();
  const unread = notifications?.results.filter((n) => !n.read_at) ?? [];

  const { data: invoices, isLoading: invLoading } = useStudentInvoices(profile?.id ?? "");
  const { data: events, isLoading: eventsLoading } = useSchoolEvents();
  const { data: assessments, isLoading: assessmentsLoading } = useStudentAssessments(profile?.id);

  // ── Derived state ─────────────────────────────────────────────────────────

  const attendancePct = attendanceSummary?.attendance_percentage ?? 0;
  const attendanceColor =
    attendancePct >= 90 ? COLORS.present : attendancePct >= 75 ? COLORS.late : COLORS.absent;

  const gaugeData = [{ value: attendancePct, fill: attendanceColor }];

  // Fee breakdown
  const feeSummary = useMemo(() => {
    const list = invoices?.results ?? [];
    return {
      total: list.length,
      paid: list.filter((i) => i.status === "paid").length,
      unpaid: list.filter((i) => i.status === "unpaid").length,
      overdue: list.filter((i) => i.status === "overdue").length,
      partial: list.filter((i) => i.status === "partial").length,
      totalPaid: list.reduce((s, i) => s + Number(i.paid_amount), 0),
      totalOutstanding: list.reduce((s, i) => s + Number(i.outstanding_amount), 0),
      nextDue: list
        .filter((i) => i.status === "unpaid" || i.status === "partial")
        .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())[0],
    };
  }, [invoices]);

  const pieData = useMemo(() => [
    { name: "Paid", value: Math.max(feeSummary.totalPaid, 0) },
    { name: "Outstanding", value: Math.max(feeSummary.totalOutstanding, 0) },
  ].filter(d => d.value > 0), [feeSummary]);

  // Upcoming events (next 7 school events + upcoming assignment deadlines)
  const upcomingEvents = useMemo(() => {
    const now = dayjs();
    const schoolEvents: (SchoolEvent | Assessment)[] = [];
    if (events?.results) {
      schoolEvents.push(...events.results.filter((e) => dayjs(e.start_date).isAfter(now.subtract(1, "day"))));
    }
    if (assessments?.results) {
      schoolEvents.push(...assessments.results.filter((a) => dayjs(a.due_date).isAfter(now.subtract(1, "day"))));
    }
    return schoolEvents
      .sort((a, b) => {
        const dateA = "due_date" in a ? dayjs((a as Assessment).due_date) : dayjs((a as SchoolEvent).start_date);
        const dateB = "due_date" in b ? dayjs((b as Assessment).due_date) : dayjs((b as SchoolEvent).start_date);
        return dateA.valueOf() - dateB.valueOf();
      })
      .slice(0, 8);
  }, [events, assessments]);

  const isLoading = profileLoading || attLoading || invLoading || eventsLoading || assessmentsLoading || notifLoading;

  // ── Loading / Error states ────────────────────────────────────────────────

  if (isLoading) return <SkeletonStudentDashboard />;
  if (profileError) return <ErrorState onRetry={() => refetchProfile()} />;

  // ── Render ────────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* ── Greeting ─────────────────────────────────────────────────────── */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Hello, {user?.first_name}! 👋
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {dayjs().format("dddd, MMMM D YYYY")}
          </p>
        </div>
        {attendanceSummary && (
          <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400 bg-white dark:bg-slate-800 rounded-lg px-3 py-1.5 border border-slate-200 dark:border-slate-700">
            <AcademicCapIcon className="h-4 w-4" />
            Overall attendance: <span className="font-semibold" style={{ color: attendanceColor }}>{attendancePct.toFixed(1)}%</span>
          </div>
        )}
      </div>

      {/* ── Quick info grid ──────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <InfoCard
          label="Current Class"
          value={profile?.enrollments?.[0]?.classroom_name ?? "—"}
          icon={BookOpenIcon}
          accent="bg-gradient-to-br from-indigo-500 to-indigo-600"
        />
        <InfoCard
          label="Admission No."
          value={profile?.admission_number ?? "—"}
          icon={ClipboardDocumentCheckIcon}
          accent="bg-gradient-to-br from-violet-500 to-violet-600"
        />
        <InfoCard
          label="Notifications"
          value={String(unread.length)}
          icon={BellIcon}
          accent={unread.length > 0
            ? "bg-gradient-to-br from-red-500 to-red-600"
            : "bg-gradient-to-br from-slate-400 to-slate-500"
          }
        />
        <InfoCard
          label="Fees Due"
          value={feeSummary.totalOutstanding > 0 ? `$${feeSummary.totalOutstanding.toLocaleString()}` : "All Paid ✓"}
          icon={BanknotesIcon}
          accent={feeSummary.totalOutstanding > 0
            ? "bg-gradient-to-br from-amber-500 to-amber-600"
            : "bg-gradient-to-br from-emerald-500 to-emerald-600"
          }
        />
      </div>

      {/* ── Main content grid ────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">

        {/* ─── Col 1-2: Attendance gauge + stats ─────────────────────────── */}
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700 flex flex-col items-center lg:col-span-1">
          <h2 className="text-base font-semibold text-slate-800 dark:text-white self-start mb-2 flex items-center gap-2">
            <ClipboardDocumentCheckIcon className="h-4 w-4 text-indigo-500" />
            My Attendance
          </h2>

          <ResponsiveContainer width="100%" height={190}>
            <RadialBarChart
              cx="50%"
              cy="72%"
              innerRadius="60%"
              outerRadius="90%"
              startAngle={180}
              endAngle={0}
              data={gaugeData}
            >
              <PolarAngleAxis type="number" domain={[0, 100]} angleAxisId={0} tick={false} />
              <RadialBar
                background={{ fill: "#f1f5f9" }}
                dataKey="value"
                cornerRadius={8}
                angleAxisId={0}
              />
            </RadialBarChart>
          </ResponsiveContainer>

          <div className="-mt-8 text-center">
            <p className="text-3xl font-bold" style={{ color: attendanceColor }}>
              {attendancePct.toFixed(1)}%
            </p>
            <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5">
              {attendanceSummary?.present ?? 0} / {attendanceSummary?.total_days ?? 0} days
            </p>
          </div>

          <div className="mt-4 w-full grid grid-cols-3 gap-2 text-center text-xs">
            <StatBadge label="Present" value={attendanceSummary?.present ?? 0} color={COLORS.present} />
            <StatBadge label="Absent" value={attendanceSummary?.absent ?? 0} color={COLORS.absent} />
            <StatBadge label="Late" value={attendanceSummary?.late ?? 0} color={COLORS.late} />
          </div>

          {attError && (
            <div className="mt-3 w-full flex items-center gap-2 text-xs text-amber-600 bg-amber-50 dark:bg-amber-900/20 rounded-lg px-3 py-2">
              <ExclamationTriangleIcon className="h-3.5 w-3.5 flex-shrink-0" />
              Could not load attendance data
            </div>
          )}

          <Link
            to="/student/attendance"
            className="mt-4 w-full inline-flex items-center justify-center gap-1 text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 py-2 rounded-lg hover:bg-indigo-50 dark:hover:bg-indigo-900/20 transition-colors"
          >
            View Full Report <ChevronRightIcon className="h-3 w-3" />
          </Link>
        </div>

        {/* ─── Col 2: Upcoming Events ──────────────────────────────────────── */}
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <h2 className="text-base font-semibold text-slate-800 dark:text-white mb-4 flex items-center gap-2">
            <CalendarDaysIcon className="h-4 w-4 text-indigo-500" />
            Upcoming Events
          </h2>

          {upcomingEvents.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 text-slate-400 dark:text-slate-500">
              <CalendarDaysIcon className="h-10 w-10 mb-2 opacity-30" />
              <p className="text-sm">No upcoming events</p>
              <p className="text-xs mt-1 text-slate-400">Check back later for new events</p>
            </div>
          ) : (
            <div className="space-y-2">
      {upcomingEvents.slice(0, 6).map((evt, idx) => (
        <EventItem key={`evt-${(evt as SchoolEvent).id ?? idx}`} event={evt} />
              ))}
              {upcomingEvents.length > 6 && (
                <button className="w-full text-xs text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 font-medium py-2 transition-colors">
                  +{upcomingEvents.length - 6} more events
                </button>
              )}
            </div>
          )}

          <Link
            to="/student/assignments"
            className="mt-4 inline-flex items-center gap-1 text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors"
          >
            View Assignments <ChevronRightIcon className="h-3 w-3" />
          </Link>
        </div>

        {/* ─── Col 3: Fee Summary ──────────────────────────────────────────── */}
        <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
          <h2 className="text-base font-semibold text-slate-800 dark:text-white mb-4 flex items-center gap-2">
            <BanknotesIcon className="h-4 w-4 text-indigo-500" />
            Fee Summary
          </h2>

          {feeSummary.total === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 text-slate-400 dark:text-slate-500">
              <BanknotesIcon className="h-10 w-10 mb-2 opacity-30" />
              <p className="text-sm">No invoices yet</p>
            </div>
          ) : (
            <>
              {/* Mini pie chart */}
              {pieData.length > 0 && (
                <div className="flex items-center justify-center mb-3">
                  <ResponsiveContainer width={120} height={120}>
                    <PieChart>
                      <Pie
                        data={pieData}
                        cx="50%"
                        cy="50%"
                        innerRadius={32}
                        outerRadius={52}
                        paddingAngle={3}
                        dataKey="value"
                      >
                        {pieData.map((_, idx) => (
                          <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                        ))}
                      </Pie>
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="ml-2 text-xs space-y-1">
                    {pieData.map((d, idx) => (
                      <div key={d.name} className="flex items-center gap-2">
                        <span className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: PIE_COLORS[idx] }} />
                        <span className="text-slate-600 dark:text-slate-400">{d.name}</span>
                        <span className="font-medium text-slate-800 dark:text-white">${d.value.toLocaleString()}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Status badges */}
              <div className="grid grid-cols-2 gap-2 text-center text-xs mb-4">
                <StatBadge label="Paid" value={feeSummary.paid} color={COLORS.paid} />
                <StatBadge label="Unpaid" value={feeSummary.unpaid} color={COLORS.unpaid} />
                <StatBadge label="Overdue" value={feeSummary.overdue} color={COLORS.overdue} />
                <StatBadge label="Partial" value={feeSummary.partial} color={COLORS.partial} />
              </div>

              {/* Next due date */}
              {feeSummary.nextDue && (
                <div className="flex items-center gap-2 rounded-lg bg-amber-50 dark:bg-amber-900/20 px-3 py-2 text-xs">
                  <ClockIcon className="h-3.5 w-3.5 text-amber-500 flex-shrink-0" />
                  <div>
                    <span className="text-amber-700 dark:text-amber-300">
                      Next due: <strong>{dayjs(feeSummary.nextDue.due_date).format("MMM D, YYYY")}</strong>
                    </span>
                    <span className="text-amber-500 ml-1">
                      (${Number(feeSummary.nextDue.outstanding_amount).toLocaleString()})
                    </span>
                  </div>
                </div>
              )}
            </>
          )}

          <Link
            to="/student/fees"
            className="mt-4 w-full inline-flex items-center justify-center gap-1.5 rounded-lg bg-indigo-600 px-4 py-2 text-xs font-semibold text-white hover:bg-indigo-700 transition-colors"
          >
            <BanknotesIcon className="h-3.5 w-3.5" />
            {feeSummary.totalOutstanding > 0 ? `Pay $${feeSummary.totalOutstanding.toLocaleString()}` : "View Fees"}
          </Link>
        </div>
      </div>

      {/* ── Outstanding fee banner (if any overdue) ──────────────────────── */}
      {feeSummary.overdue > 0 && (
        <div className="rounded-xl border border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <ExclamationTriangleIcon className="h-6 w-6 text-red-500 flex-shrink-0" />
            <div>
              <p className="text-sm font-semibold text-red-800 dark:text-red-300">
                {feeSummary.overdue} Overdue Invoice{feeSummary.overdue > 1 ? "s" : ""}
              </p>
              <p className="text-xs text-red-600 dark:text-red-400">
                ${feeSummary.totalOutstanding.toLocaleString()} total outstanding. Late fees may apply.
              </p>
            </div>
          </div>
          <Link
            to="/student/fees"
            className="rounded-lg bg-red-500 px-4 py-2 text-xs font-semibold text-white hover:bg-red-600 transition-colors flex-shrink-0"
          >
            Pay Now
          </Link>
        </div>
      )}

      {/* ── Recent notifications ───────────────────────────────────────────── */}
      <div className="rounded-xl bg-white dark:bg-slate-800 p-5 shadow-sm border border-slate-100 dark:border-slate-700">
        <h2 className="text-base font-semibold text-slate-800 dark:text-white mb-4 flex items-center gap-2">
          <BellIcon className="h-4 w-4 text-indigo-500" />
          Recent Notifications
          {unread.length > 0 && (
            <span className="ml-auto text-xs font-medium text-white bg-indigo-500 rounded-full px-2 py-0.5">
              {unread.length} new
            </span>
          )}
        </h2>
        {unread.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-10 text-slate-400 dark:text-slate-500">
            <CheckCircleIcon className="h-10 w-10 mb-2 opacity-30" />
            <p className="text-sm">You&apos;re all caught up!</p>
            <p className="text-xs mt-1 text-slate-400">No unread notifications</p>
          </div>
        ) : (
          <ul className="space-y-2">
            {unread.slice(0, 5).map((notif) => (
              <li key={notif.id} className="flex items-start gap-3 rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3 transition-colors hover:bg-slate-100 dark:hover:bg-slate-700">
                <div className="mt-1.5 h-2 w-2 flex-shrink-0 rounded-full bg-indigo-500" />
                <div className="min-w-0 flex-1">
                  <p className="text-sm font-medium text-slate-800 dark:text-white">{notif.title}</p>
                  <p className="text-xs text-slate-500 dark:text-slate-400 mt-0.5 line-clamp-1">{notif.body}</p>
                  <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">{dayjs(notif.created_at).fromNow()}</p>
                </div>
              </li>
            ))}
          </ul>
        )}
        {unread.length > 0 && (
          <Link
            to="/student/messages"
            className="mt-4 inline-flex items-center gap-1 text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors"
          >
            View All Notifications <ChevronRightIcon className="h-3 w-3" />
          </Link>
        )}
      </div>

      {/* ── Quick links ──────────────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {[
          { to: "/student/timetable", label: "Timetable", icon: CalendarDaysIcon, color: "bg-blue-500" },
          { to: "/student/grades", label: "My Grades", icon: TrophyIcon, color: "bg-emerald-500" },
          { to: "/student/messages", label: "Messages", icon: BellIcon, color: "bg-purple-500" },
          { to: "/student/fees", label: "Fee Details", icon: BanknotesIcon, color: "bg-amber-500" },
        ].map(({ to, label, icon: Icon, color }) => (
          <Link
            key={to}
            to={to}
            className="flex items-center gap-3 rounded-xl bg-white dark:bg-slate-800 p-4 shadow-sm border border-slate-100 dark:border-slate-700 hover:shadow-md hover:border-indigo-200 dark:hover:border-indigo-700 transition-all duration-200"
          >
            <div className={`rounded-lg ${color} p-2`}>
              <Icon className="h-4 w-4 text-white" />
            </div>
            <span className="text-sm font-medium text-slate-700 dark:text-slate-300">{label}</span>
          </Link>
        ))}
      </div>
    </div>
  );
}
