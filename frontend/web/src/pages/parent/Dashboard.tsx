/**
 * Parent Dashboard — quick overview of all children with live stats
 */
import React from "react";
import { useQuery, useQueries } from "@tanstack/react-query";
import { useNavigate } from "react-router-dom";
import { api } from "../../api/client";
import { useAuthStore } from "../../store/authStore";
import { useUnreadNotificationCount } from "../../api/hooks";
import { Avatar, Badge, SkeletonCard } from "../../components/common";
import { useTitle } from "../../hooks";
import { BellIcon, AcademicCapIcon, ArrowRightIcon } from "@heroicons/react/24/outline";
import dayjs from "dayjs";
import { percent, attendanceColor } from "../../utils";

interface AttendanceSummary {
  attendance_percentage: number;
  total_days: number;
  present: number;
}

interface LatestGrade {
  percentage: number;
  grade_letter: string;
  exam_name: string;
}

interface ChildListItem {
  id: string;
  full_name: string;
  avatar?: string;
  is_active: boolean;
  current_class?: string;
  admission_number: string;
  email: string;
}

export default function ParentDashboard() {
  useTitle("Dashboard");
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const { data: unread } = useUnreadNotificationCount();

  const { data: children, isLoading } = useQuery({
    queryKey: ["parent-children"],
    queryFn: () => api.get<any>("/students/"),
  });

  const { data: notifications } = useQuery({
    queryKey: ["parent-notifications"],
    queryFn: () => api.get<any>("/communication/notifications/?channel=in_app&page_size=5"),
    refetchInterval: 30_000,
  });

  const childList = (children?.results ?? []) as ChildListItem[];
  const notifList = notifications?.results ?? [];

  // Stable useQueries — always returns the same number of results
  const attendanceResults = useQueries({
    queries: (childList ?? []).map((child) => ({
      queryKey: ["parent-dash-att", child.id],
      queryFn: () =>
        api.get<AttendanceSummary>(`/students/${child.id}/attendance-summary/`),
      enabled: !!child.id,
    })),
  });

  const gradeResults = useQueries({
    queries: (childList ?? []).map((child) => ({
      queryKey: ["parent-dash-grade", child.id],
      queryFn: () =>
        api
          .get<any>(`/gradebook/report-cards/?student=${child.id}&page_size=1`)
          .then((r) => r.results?.[0] as LatestGrade | undefined),
      enabled: !!child.id,
    })),
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Hello, {user?.first_name}! 👋</h1>
          <p className="text-sm text-slate-500 mt-1">{dayjs().format("dddd, MMMM D YYYY")}</p>
        </div>
        <div
          onClick={() => navigate("/parent/messages")}
          className="flex items-center gap-2 rounded-xl bg-white border border-slate-200 px-4 py-2.5 shadow-sm cursor-pointer hover:bg-slate-50 transition-colors"
        >
          <BellIcon className="h-5 w-5 text-slate-500" />
          <span className="text-sm font-medium text-slate-700">{unread ?? 0} unread</span>
        </div>
      </div>

      {/* Children overview */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-base font-semibold text-slate-800">My Children</h2>
          {childList.length > 0 && (
            <button
              onClick={() => navigate("/parent/children")}
              className="text-xs font-semibold text-violet-600 hover:text-violet-700 flex items-center gap-1"
            >
              View all <ArrowRightIcon className="h-3 w-3" />
            </button>
          )}
        </div>
        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <SkeletonCard />
            <SkeletonCard />
          </div>
        ) : childList.length === 0 ? (
          <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-8 text-center text-slate-400">
            <AcademicCapIcon className="h-10 w-10 mx-auto mb-2 opacity-30" />
            <p className="text-sm">No children linked to your account yet. Contact your school admin.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {childList.map((child, i) => (
              <div
                key={child.id}
                onClick={() => navigate("/parent/children")}
                className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-5 hover:border-violet-200 hover:shadow-md transition-all duration-200 cursor-pointer group"
              >
                <div className="flex items-center gap-4">
                  <Avatar
                    name={child.full_name}
                    src={child.avatar}
                    className="h-14 w-14 text-lg flex-shrink-0"
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-bold text-slate-900 truncate group-hover:text-violet-700 transition-colors">
                        {child.full_name}
                      </p>
                      <Badge color={child.is_active ? "green" : "slate"} dot>
                        {child.is_active ? "Active" : "Inactive"}
                      </Badge>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {child.current_class ?? "—"} · {child.admission_number}
                    </p>
                  </div>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-3">
                  {/* Attendance stat */}
                  <div className="rounded-lg bg-slate-50 p-3 text-center">
                    <p
                      className={`text-lg font-bold ${
                        attendanceResults[i]?.data?.attendance_percentage != null
                          ? attendanceColor(attendanceResults[i].data!.attendance_percentage)
                          : "text-slate-400"
                      }`}
                    >
                      {attendanceResults[i]?.data?.attendance_percentage != null
                        ? percent(attendanceResults[i].data!.attendance_percentage)
                        : "—"}
                    </p>
                    <p className="text-xs text-slate-500 mt-0.5">Attendance</p>
                  </div>

                  {/* Latest grade stat */}
                  <div className="rounded-lg bg-slate-50 p-3 text-center">
                    <p
                      className={`text-lg font-bold ${
                        gradeResults[i]?.data ? "text-slate-700" : "text-slate-400"
                      }`}
                    >
                      {gradeResults[i]?.data?.grade_letter ?? "—"}
                    </p>
                    <p className="text-xs text-slate-500 mt-0.5">
                      {gradeResults[i]?.data?.exam_name ?? "Latest Grade"}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Quick action links */}
      {childList.length > 0 && (
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-5">
          <h2 className="text-base font-semibold text-slate-800 mb-3">Quick Actions</h2>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
            {[
              { label: "View Attendance", path: "/parent/attendance", color: "bg-green-50 text-green-700 hover:bg-green-100" },
              { label: "Check Grades",    path: "/parent/grades",      color: "bg-blue-50 text-blue-700 hover:bg-blue-100" },
              { label: "Pay Fees",        path: "/parent/fees",         color: "bg-amber-50 text-amber-700 hover:bg-amber-100" },
              { label: "Send Message",    path: "/parent/messages",    color: "bg-violet-50 text-violet-700 hover:bg-violet-100" },
            ].map(({ label, path, color }) => (
              <button
                key={path}
                onClick={() => navigate(path)}
                className={`rounded-xl px-4 py-3 text-sm font-semibold text-center transition-colors ${color}`}
              >
                {label}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Recent notifications */}
      {notifList.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-base font-semibold text-slate-800">Recent Notifications</h2>
            {notifList.length > 0 && (
              <button
                onClick={() => navigate("/parent/messages")}
                className="text-xs font-semibold text-violet-600 hover:text-violet-700"
              >
                View all
              </button>
            )}
          </div>
          <div className="space-y-2">
            {notifList.map(
              (n: {
                id: string;
                title: string;
                body: string;
                read_at: string | null;
                created_at: string;
              }) => (
                <div
                  key={n.id}
                  className={`bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-4 flex items-start gap-3 ${
                    !n.read_at ? "border-violet-200 bg-violet-50/30" : ""
                  }`}
                >
                  {!n.read_at && (
                    <div className="mt-1.5 h-2 w-2 rounded-full bg-violet-500 flex-shrink-0" />
                  )}
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-slate-800">{n.title}</p>
                    <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{n.body}</p>
                    <p className="text-xs text-slate-400 mt-1">{dayjs(n.created_at).fromNow()}</p>
                  </div>
                </div>
              )
            )}
          </div>
        </div>
      )}
    </div>
  );
}
