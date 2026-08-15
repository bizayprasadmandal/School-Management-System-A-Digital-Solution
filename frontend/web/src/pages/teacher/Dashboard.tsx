/**
 * Teacher Dashboard — today's schedule, quick attendance, class statistics,
 * pending grading, upcoming conferences, and recent messages
 */
import React, { useMemo } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  ClipboardDocumentCheckIcon,
  BookOpenIcon,
  UsersIcon,
  CheckCircleIcon,
  CalendarDaysIcon,
  ChatBubbleLeftEllipsisIcon,
  StarIcon,
  ChevronRightIcon,
} from "@heroicons/react/24/outline";
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import { useAuthStore } from "../../store/authStore";
import { useClassrooms, useCurrentAcademicYear } from "../../api/hooks";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import {
  Button,
  Badge,
  SkeletonCard,
  SkeletonTeacherDashboard,
  ErrorState,
  ErrorBoundary,
} from "../../components/common";
import { percent, attendanceColor } from "../../utils";
import { useTitle } from "../../hooks";

dayjs.extend(relativeTime);

// ─── Interfaces ───────────────────────────────────────────────────────────────

interface ConferenceSlot {
  id: string;
  student_name: string | null;
  date: string;
  start_time: string;
  end_time: string;
  is_booked: boolean;
}

interface InboxThread {
  partner: { id: string; name: string };
  last_message: { content: string; sent_at: string };
  unread_count: number;
}

interface AssessmentItem {
  id: number;
  title: string;
  subject_name: string;
  classroom_name: string;
  due_date: string;
  assessment_type: string;
  pending_count?: number;
}

interface DashboardStats {
  attendance_week?: { day: string; present: number; absent: number }[];
}

// ─── QuickAccessCard ──────────────────────────────────────────────────────────

function QuickAccessCard({
  title,
  value,
  icon: Icon,
  accent,
  to,
  subtitle,
}: {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  accent: string;
  to: string;
  subtitle?: string;
}) {
  return (
    <Link
      to={to}
      className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm dark:shadow-none p-4 flex items-center gap-3 transition-all duration-200 hover:shadow-md hover:border-indigo-200 dark:hover:border-indigo-700 hover:-translate-y-0.5"
    >
      <div
        className={`flex h-10 w-10 items-center justify-center rounded-xl ${accent} flex-shrink-0`}
      >
        <Icon className="h-5 w-5 text-white" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-xl font-bold text-slate-900 dark:text-white">{value}</p>
        <p className="text-xs text-slate-500 dark:text-slate-400">{title}</p>
        {subtitle && (
          <p className="text-[10px] text-slate-400 dark:text-slate-500 mt-0.5 truncate">
            {subtitle}
          </p>
        )}
      </div>
    </Link>
  );
}

// ─── Main Dashboard ───────────────────────────────────────────────────────────

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

  const [pageLoaded, setPageLoaded] = React.useState(false);

  // ── Today's schedule ────────────────────────────────────────────────────

  const {
    data: todaySlots,
    isLoading: slotsLoading,
    isError: slotsError,
    refetch: refetchSlots,
  } = useQuery({
    queryKey: ["teacher-today-slots", user?.id, academicYear?.id],
    queryFn: () =>
      api.get<any[]>("/timetable/slots/teacher-schedule/", { academic_year_id: academicYear?.id }),
    enabled: !!user && !!academicYear,
  });

  // ── Attendance summaries ────────────────────────────────────────────────

  const { data: attendanceSummaries } = useQuery({
    queryKey: ["teacher-today-attendance", classrooms.map((c) => c.id), todayStr],
    queryFn: async () => {
      if (!classrooms.length) return [];
      const results = await Promise.allSettled(
        classrooms.map((c) =>
          api
            .get<any>("/attendance/classroom-summary/", { classroom_id: c.id, date: todayStr })
            .then((d) => ({ ...d, classroom: c })),
        ),
      );
      return results.filter((r) => r.status === "fulfilled").map((r) => (r as any).value);
    },
    enabled: classrooms.length > 0,
  });

  // ── Weekly attendance trend (school-wide, staff-accessible analytics) ───

  const { data: weeklyAttendance, isLoading: weekAttLoading } = useQuery<DashboardStats>({
    queryKey: ["dashboard-stats"],
    queryFn: () => api.get("/reporting/dashboard-stats/"),
    staleTime: 5 * 60 * 1000,
  });

  const attendanceWeek = weeklyAttendance?.attendance_week ?? [];

  // ── Pending grading ─────────────────────────────────────────────────────

  const { data: assessmentsData, isLoading: assessLoading } = useQuery({
    queryKey: ["teacher-assessments-ungraded"],
    queryFn: async () => {
      const res = await api.get<{ results: AssessmentItem[] }>("/gradebook/assessments/");
      // For each assessment, fetch submission count via the submissions endpoint
      const assessments = res.results ?? [];
      const pendingCounts = await Promise.allSettled(
        assessments.map(async (a) => {
          try {
            const subs = await api.get<{ results: any[] }>("/gradebook/submissions/", {
              assessment: a.id,
            });
            const pending = subs.results.filter((s) => s.marks_obtained == null).length;
            return { id: a.id, pending };
          } catch {
            return { id: a.id, pending: 0 };
          }
        }),
      );
      const countMap: Record<number, number> = {};
      pendingCounts.forEach((r) => {
        if (r.status === "fulfilled") countMap[r.value.id] = r.value.pending;
      });
      return assessments.map((a) => ({ ...a, pending_count: countMap[a.id] ?? 0 }));
    },
    enabled: !!user,
    staleTime: 30_000,
  });

  const totalPending = useMemo(
    () => (assessmentsData ?? []).reduce((s, a) => s + (a.pending_count ?? 0), 0),
    [assessmentsData],
  );

  const pendingAssessments = useMemo(
    () => (assessmentsData ?? []).filter((a) => (a.pending_count ?? 0) > 0).slice(0, 4),
    [assessmentsData],
  );

  // ── Upcoming conferences ────────────────────────────────────────────────

  const { data: conferenceSlots = [], isLoading: confLoading } = useQuery({
    queryKey: ["teacher-dashboard-conferences", todayStr],
    queryFn: async () => {
      const res = await api.get<{ results: ConferenceSlot[] }>("/conferences/conference-slots/", {
        date: todayStr,
      });
      return (res.results ?? []).filter((s) => s.is_booked);
    },
    enabled: !!user,
  });

  // ── Recent messages ─────────────────────────────────────────────────────

  const { data: inbox = [], isLoading: inboxLoading } = useQuery({
    queryKey: ["teacher-inbox-preview"],
    queryFn: () => api.get<InboxThread[]>("/communication/messages/inbox/"),
    enabled: !!user,
    staleTime: 30_000,
  });

  const recentThreads = inbox.slice(0, 4);
  const totalUnread = inbox.reduce((s, t) => s + t.unread_count, 0);

  const todaySchedule = (todaySlots ?? []).filter(
    (s: Record<string, unknown>) => s.day_of_week === dayIndex,
  );
  const avgAttendance = attendanceSummaries?.length
    ? attendanceSummaries.reduce(
        (s: number, a: Record<string, any>) =>
          s + (a.breakdown?.present / (a.total_students || 1)) * 100,
        0,
      ) / attendanceSummaries.length
    : null;

  // ── Loading / Error ─────────────────────────────────────────────────────

  React.useEffect(() => {
    if (!slotsLoading && classrooms.length > 0) setPageLoaded(true);
  }, [slotsLoading, classrooms.length]);

  const mainLoading = !pageLoaded && (slotsLoading || classrooms.length === 0);
  if (mainLoading) return <SkeletonTeacherDashboard />;
  if (slotsError) return <ErrorState onRetry={() => refetchSlots()} />;

  // ── Render ──────────────────────────────────────────────────────────────

  return (
    <div className="space-y-6">
      {/* Greeting */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
            Good {today.hour() < 12 ? "morning" : "afternoon"}, {user?.first_name}! 👋
          </h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
            {today.format("dddd, MMMM D YYYY")}
          </p>
        </div>
        {avgAttendance !== null && (
          <div className="hidden sm:flex items-center gap-1.5 text-xs text-slate-500 bg-white dark:bg-slate-800 rounded-lg px-3 py-1.5 border border-slate-200 dark:border-slate-700">
            <CheckCircleIcon className="h-4 w-4" />
            Avg attendance:{" "}
            <span className={`font-semibold ${attendanceColor(avgAttendance)}`}>
              {percent(avgAttendance)}
            </span>
          </div>
        )}
      </div>

      {/* Quick-access cards row */}
      <ErrorBoundary>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <QuickAccessCard
            title="My Classes"
            value={classrooms.length}
            icon={UsersIcon}
            accent="bg-gradient-to-br from-indigo-500 to-indigo-600"
            to="/teacher/attendance"
            subtitle={
              classrooms.length > 0
                ? `${classrooms[0]?.grade_name} ${classrooms[0]?.name}`
                : undefined
            }
          />
          <QuickAccessCard
            title="Today's Periods"
            value={todaySchedule.length}
            icon={BookOpenIcon}
            accent="bg-gradient-to-br from-violet-500 to-violet-600"
            to="/teacher/timetable"
            subtitle={
              todaySchedule.length > 0
                ? `Next: ${todaySchedule[0]?.subject_name ?? ""}`
                : "No classes"
            }
          />
          <QuickAccessCard
            title="Pending Grading"
            value={totalPending}
            icon={ClipboardDocumentCheckIcon}
            accent={
              totalPending > 0
                ? "bg-gradient-to-br from-amber-500 to-amber-600"
                : "bg-gradient-to-br from-emerald-500 to-emerald-600"
            }
            to="/teacher/gradebook"
            subtitle={
              totalPending > 0
                ? `${pendingAssessments.length} assessments need grading`
                : "All graded ✓"
            }
          />
          <QuickAccessCard
            title="Unread Messages"
            value={totalUnread}
            icon={ChatBubbleLeftEllipsisIcon}
            accent={
              totalUnread > 0
                ? "bg-gradient-to-br from-red-500 to-red-600"
                : "bg-gradient-to-br from-slate-400 to-slate-500"
            }
            to="/teacher/messages"
            subtitle={totalUnread > 0 ? `${recentThreads.length} conversations` : "Inbox clear"}
          />
        </div>
      </ErrorBoundary>

      {/* 3-column secondary cards: Pending Grading / Conferences / Messages */}
      <ErrorBoundary>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          {/* ─── Card 1: Pending Grading ─────────────────────────────────────── */}
          <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm dark:shadow-none">
            <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
              <h2 className="text-base font-semibold text-slate-800 dark:text-white flex items-center gap-2">
                <StarIcon className="h-4 w-4 text-amber-500" />
                Pending Grading
              </h2>
              <Badge color={totalPending > 0 ? "amber" : "green"}>{totalPending} pending</Badge>
            </div>
            <div className="p-5">
              {assessLoading ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <div
                      key={i}
                      className="h-10 bg-slate-100 dark:bg-slate-700 rounded-lg animate-pulse"
                    />
                  ))}
                </div>
              ) : pendingAssessments.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 text-slate-400 dark:text-slate-500">
                  <CheckCircleIcon className="h-10 w-10 mb-2 opacity-30" />
                  <p className="text-sm font-medium">All caught up!</p>
                  <p className="text-xs mt-1 text-slate-400">No submissions pending grading</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {pendingAssessments.map((a) => (
                    <div
                      key={a.id}
                      className="flex items-center justify-between rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3 transition-colors hover:bg-amber-50 dark:hover:bg-amber-900/20"
                    >
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-slate-800 dark:text-white truncate">
                          {a.title}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                          {a.classroom_name} · Due {dayjs(a.due_date).format("MMM D")}
                        </p>
                      </div>
                      <span className="ml-3 flex h-6 w-6 items-center justify-center rounded-full bg-amber-100 dark:bg-amber-900/40 text-xs font-bold text-amber-700 dark:text-amber-300">
                        {a.pending_count}
                      </span>
                    </div>
                  ))}
                </div>
              )}
              <Link
                to="/teacher/gradebook"
                className="mt-4 inline-flex items-center gap-1 text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors"
              >
                Go to Gradebook <ChevronRightIcon className="h-3 w-3" />
              </Link>
            </div>
          </div>

          {/* ─── Card 2: Upcoming Conferences ────────────────────────────────── */}
          <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm dark:shadow-none">
            <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
              <h2 className="text-base font-semibold text-slate-800 dark:text-white flex items-center gap-2">
                <CalendarDaysIcon className="h-4 w-4 text-indigo-500" />
                Today&apos;s Conferences
              </h2>
              <Badge color="indigo">{conferenceSlots.length} booked</Badge>
            </div>
            <div className="p-5">
              {confLoading ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <div
                      key={i}
                      className="h-12 bg-slate-100 dark:bg-slate-700 rounded-lg animate-pulse"
                    />
                  ))}
                </div>
              ) : conferenceSlots.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 text-slate-400 dark:text-slate-500">
                  <CalendarDaysIcon className="h-10 w-10 mb-2 opacity-30" />
                  <p className="text-sm font-medium">No conferences today</p>
                  <p className="text-xs mt-1 text-slate-400">Check back later or create slots</p>
                </div>
              ) : (
                <div className="space-y-2">
                  {conferenceSlots.map((slot) => (
                    <div
                      key={slot.id}
                      className="flex items-center gap-3 rounded-lg bg-indigo-50 dark:bg-indigo-900/20 p-3"
                    >
                      <div className="text-center w-14 flex-shrink-0">
                        <p className="text-sm font-bold text-indigo-700 dark:text-indigo-300">
                          {slot.start_time}
                        </p>
                        <p className="text-[10px] text-indigo-500 dark:text-indigo-400">
                          {slot.end_time}
                        </p>
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm font-medium text-indigo-800 dark:text-indigo-200 truncate">
                          {slot.student_name ?? "—"}
                        </p>
                        <p className="text-xs text-indigo-500 dark:text-indigo-400">
                          Parent conference
                        </p>
                      </div>
                      <span className="h-2 w-2 rounded-full bg-indigo-500 animate-pulse flex-shrink-0" />
                    </div>
                  ))}
                </div>
              )}
              <Link
                to="/teacher/conferences"
                className="mt-4 inline-flex items-center gap-1 text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors"
              >
                Manage Slots <ChevronRightIcon className="h-3 w-3" />
              </Link>
            </div>
          </div>

          {/* ─── Card 3: Recent Messages ──────────────────────────────────────── */}
          <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm dark:shadow-none">
            <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
              <h2 className="text-base font-semibold text-slate-800 dark:text-white flex items-center gap-2">
                <ChatBubbleLeftEllipsisIcon className="h-4 w-4 text-purple-500" />
                Recent Messages
              </h2>
              {totalUnread > 0 && (
                <span className="flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
                  {totalUnread > 9 ? "9+" : totalUnread}
                </span>
              )}
            </div>
            <div className="p-5">
              {inboxLoading ? (
                <div className="space-y-2">
                  {[1, 2, 3].map((i) => (
                    <div
                      key={i}
                      className="h-12 bg-slate-100 dark:bg-slate-700 rounded-lg animate-pulse"
                    />
                  ))}
                </div>
              ) : recentThreads.length === 0 ? (
                <div className="flex flex-col items-center justify-center py-8 text-slate-400 dark:text-slate-500">
                  <ChatBubbleLeftEllipsisIcon className="h-10 w-10 mb-2 opacity-30" />
                  <p className="text-sm font-medium">No messages yet</p>
                  <p className="text-xs mt-1 text-slate-400">
                    Messages from students and parents appear here
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  {recentThreads.map((t) => (
                    <div
                      key={t.partner.id}
                      className="flex items-center gap-3 rounded-lg bg-slate-50 dark:bg-slate-700/50 p-3 transition-colors hover:bg-purple-50 dark:hover:bg-purple-900/20"
                    >
                      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-indigo-100 dark:bg-indigo-900/40 text-xs font-bold text-indigo-600 dark:text-indigo-300 flex-shrink-0">
                        {t.partner.name.charAt(0).toUpperCase()}
                      </div>
                      <div className="min-w-0 flex-1">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-slate-800 dark:text-white truncate">
                            {t.partner.name}
                          </p>
                          <p className="text-[10px] text-slate-400 dark:text-slate-500 ml-2 flex-shrink-0">
                            {dayjs(t.last_message.sent_at).fromNow()}
                          </p>
                        </div>
                        <p className="text-xs text-slate-500 dark:text-slate-400 truncate">
                          {t.last_message.content}
                        </p>
                      </div>
                      {t.unread_count > 0 && (
                        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-purple-600 text-[10px] font-bold text-white flex-shrink-0">
                          {t.unread_count}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
              <Link
                to="/teacher/messages"
                className="mt-4 inline-flex items-center gap-1 text-xs font-medium text-indigo-600 dark:text-indigo-400 hover:text-indigo-700 dark:hover:text-indigo-300 transition-colors"
              >
                View All Messages <ChevronRightIcon className="h-3 w-3" />
              </Link>
            </div>
          </div>
        </div>
      </ErrorBoundary>

      {/* Today's Schedule + Weekly Attendance */}
      <ErrorBoundary>
        <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
          <div className="lg:col-span-2 bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm dark:shadow-none">
            <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
              <h2 className="text-base font-semibold text-slate-800 dark:text-white">
                Today&apos;s Schedule
              </h2>
              <Badge color="blue">{today.format("dddd")}</Badge>
            </div>
            <div className="p-5">
              {slotsLoading ? (
                <div className="p-4">
                  <SkeletonCard />
                </div>
              ) : todaySchedule.length === 0 ? (
                <div className="text-center py-10 text-slate-400 dark:text-slate-500">
                  <BookOpenIcon className="h-10 w-10 mx-auto mb-2 opacity-30" />
                  <p>No classes scheduled today</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {todaySchedule.map(
                    (
                      slot: {
                        start_time?: string;
                        end_time?: string;
                        subject_name?: string;
                        classroom_name?: string;
                        room?: string;
                      },
                      i: number,
                    ) => (
                      <div
                        key={i}
                        className="flex items-center gap-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-700/50 hover:bg-indigo-50/60 dark:hover:bg-indigo-900/20 transition-colors"
                      >
                        <div className="text-center w-16 flex-shrink-0">
                          <p className="text-xs font-bold text-indigo-600 dark:text-indigo-400">
                            {slot.start_time?.slice(0, 5)}
                          </p>
                          <p className="text-xs text-slate-400 dark:text-slate-500">
                            {slot.end_time?.slice(0, 5)}
                          </p>
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-semibold text-slate-900 dark:text-white">
                            {slot.subject_name}
                          </p>
                          <p className="text-xs text-slate-500 dark:text-slate-400">
                            {slot.classroom_name} · {slot.room ?? "Room TBD"}
                          </p>
                        </div>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => navigate("/teacher/attendance")}
                        >
                          Take Attendance
                        </Button>
                      </div>
                    ),
                  )}
                </div>
              )}
            </div>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm dark:shadow-none">
            <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
              <h2 className="text-base font-semibold text-slate-800 dark:text-white">
                Weekly Attendance
              </h2>
            </div>
            <div className="p-5">
              {weekAttLoading ? (
                <div className="h-[180px] rounded-lg bg-slate-100 dark:bg-slate-700/50 animate-pulse" />
              ) : attendanceWeek.length === 0 ? (
                <p className="text-sm text-slate-400 dark:text-slate-500 text-center py-16">
                  No attendance recorded yet
                </p>
              ) : (
                <ResponsiveContainer width="100%" height={180}>
                  <BarChart
                    data={attendanceWeek}
                    margin={{ top: 4, right: 4, left: -20, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                    <XAxis
                      dataKey="day"
                      tick={{ fontSize: 11 }}
                      axisLine={false}
                      tickLine={false}
                    />
                    <YAxis
                      tick={{ fontSize: 11 }}
                      axisLine={false}
                      tickLine={false}
                      unit="%"
                      domain={[0, 100]}
                    />
                    <Tooltip formatter={(v) => [`${v}%`, "Attendance"]} />
                    <Bar dataKey="present" fill="#6366f1" radius={[4, 4, 0, 0]} name="Attendance" />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </div>
        </div>
      </ErrorBoundary>

      {/* Today's Class Attendance */}
      <ErrorBoundary>
        {(attendanceSummaries?.length ?? 0) > 0 && (
          <div className="bg-white dark:bg-slate-800 rounded-2xl border border-slate-100 dark:border-slate-700 shadow-sm dark:shadow-none">
            <div className="px-5 py-4 border-b border-slate-100 dark:border-slate-700 flex items-center justify-between">
              <h2 className="text-base font-semibold text-slate-800 dark:text-white">
                Today&apos;s Class Attendance
              </h2>
            </div>
            <div className="p-5">
              <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
                {attendanceSummaries?.map(
                  (
                    summary: {
                      classroom?: { grade_name?: string; name?: string };
                      total_students?: number;
                      breakdown?: { present: number; absent: number };
                      not_recorded?: number;
                    },
                    i: number,
                  ) => {
                    const totalStudents = summary.total_students ?? 0;
                    const pct =
                      totalStudents > 0
                        ? ((summary.breakdown?.present ?? 0) / totalStudents) * 100
                        : 0;
                    return (
                      <div
                        key={i}
                        className="p-4 rounded-xl border border-slate-100 dark:border-slate-700 bg-slate-50 dark:bg-slate-700/30 hover:border-indigo-200 dark:hover:border-indigo-700 transition-colors"
                      >
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <p className="text-sm font-semibold text-slate-800 dark:text-white">
                              {summary.classroom?.grade_name} {summary.classroom?.name}
                            </p>
                            <p className="text-xs text-slate-500 dark:text-slate-400">
                              {summary.total_students} students
                            </p>
                          </div>
                          <span className={`text-lg font-bold ${attendanceColor(pct)}`}>
                            {percent(pct)}
                          </span>
                        </div>
                        <div className="flex gap-2 text-xs">
                          <span className="text-green-600 dark:text-green-400 font-medium">
                            ✓ {summary.breakdown?.present} Present
                          </span>
                          <span className="text-red-600 dark:text-red-400 font-medium">
                            ✗ {summary.breakdown?.absent} Absent
                          </span>
                          {(summary.not_recorded ?? 0) > 0 && (
                            <span className="text-amber-600 dark:text-amber-400">
                              ⚠ {summary.not_recorded} Unrecorded
                            </span>
                          )}
                        </div>
                        <div className="mt-2 h-1.5 bg-slate-200 dark:bg-slate-600 rounded-full overflow-hidden">
                          <div
                            className="h-full bg-indigo-500 rounded-full transition-all duration-500"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    );
                  },
                )}
              </div>
            </div>
          </div>
        )}
      </ErrorBoundary>
    </div>
  );
}
