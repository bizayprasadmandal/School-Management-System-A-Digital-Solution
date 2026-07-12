/**
 * Student Dashboard — Personal overview for students
 */

import React from "react";
import {
  ClipboardDocumentCheckIcon,
  BookOpenIcon,
  CalendarDaysIcon,
  BanknotesIcon,
  BellIcon,
  TrophyIcon,
} from "@heroicons/react/24/outline";
import { RadialBarChart, RadialBar, PolarAngleAxis, ResponsiveContainer } from "recharts";
import dayjs from "dayjs";
import { useAuthStore } from "../../store/authStore";
import {
  useStudentAttendanceSummary,
  useCurrentAcademicYear,
  useNotifications,
  useStudentInvoices,
} from "../../api/hooks";
import { SkeletonStudentDashboard } from "../../components/common";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import type { StudentDetail } from "../../types";

function InfoCard({ label, value, icon: Icon, accent }: {
  label: string; value: string; icon: React.ComponentType<{className?: string}>; accent: string;
}) {
  return (
    <div className={`rounded-xl p-4 ${accent} flex items-center gap-4`}>
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

export default function StudentDashboard() {
  const { user } = useAuthStore();

  const { data: profile, isLoading: profileLoading } = useQuery<StudentDetail>({
    queryKey: ["student-profile"],
    queryFn: () => api.get("/students/me/"),
  });

  const { data: academicYear } = useCurrentAcademicYear();

  const { data: attendanceSummary, isLoading: attLoading } = useStudentAttendanceSummary(
    profile?.id ?? "",
    academicYear?.id
  );

  const { data: notifications } = useNotifications();
  const unread = notifications?.results.filter((n) => !n.read_at) ?? [];

  const { data: invoices, isLoading: invLoading } = useStudentInvoices(profile?.id ?? "");
  const unpaidAmount = invoices?.results
    .filter((i) => i.status === "unpaid" || i.status === "overdue")
    .reduce((sum, i) => sum + i.outstanding_amount, 0) ?? 0;

  if (profileLoading || attLoading || invLoading) {
    return <SkeletonStudentDashboard />;
  }

  const attendancePct = attendanceSummary?.attendance_percentage ?? 0;
  const attendanceColor =
    attendancePct >= 90 ? "#22c55e" : attendancePct >= 75 ? "#f59e0b" : "#ef4444";

  const gaugeData = [{ value: attendancePct, fill: attendanceColor }];

  return (
    <div className="space-y-6">
      {/* Greeting */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Hello, {user?.first_name}! 👋
        </h1>
        <p className="text-sm text-slate-500 mt-1">{dayjs().format("dddd, MMMM D YYYY")}</p>
      </div>

      {/* Quick info grid */}
      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <InfoCard
          label="Current Class"
          value={profile?.enrollments?.[0]?.classroom_name ?? "—"}
          icon={BookOpenIcon}
          accent="bg-indigo-500"
        />
        <InfoCard
          label="Admission No."
          value={profile?.admission_number ?? "—"}
          icon={ClipboardDocumentCheckIcon}
          accent="bg-violet-500"
        />
        <InfoCard
          label="Notifications"
          value={String(unread.length)}
          icon={BellIcon}
          accent={unread.length > 0 ? "bg-red-500" : "bg-slate-400"}
        />
        <InfoCard
          label="Fees Due"
          value={unpaidAmount > 0 ? `$${unpaidAmount.toLocaleString()}` : "Paid ✓"}
          icon={BanknotesIcon}
          accent={unpaidAmount > 0 ? "bg-amber-500" : "bg-emerald-500"}
        />
      </div>

      {/* Main content */}
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Attendance gauge */}
        <div className="rounded-xl bg-white p-5 shadow-sm border border-slate-100 flex flex-col items-center">
          <h2 className="text-base font-semibold text-slate-800 self-start mb-2">My Attendance</h2>
          <ResponsiveContainer width="100%" height={180}>
            <RadialBarChart
              cx="50%"
              cy="70%"
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
            <p className="text-xs text-slate-500 mt-0.5">
              {attendanceSummary?.present ?? 0} / {attendanceSummary?.total_days ?? 0} days
            </p>
          </div>
          <div className="mt-4 w-full grid grid-cols-3 gap-2 text-center text-xs">
            <div className="rounded-lg bg-green-50 py-2">
              <p className="font-bold text-green-700">{attendanceSummary?.present ?? 0}</p>
              <p className="text-green-600">Present</p>
            </div>
            <div className="rounded-lg bg-red-50 py-2">
              <p className="font-bold text-red-700">{attendanceSummary?.absent ?? 0}</p>
              <p className="text-red-600">Absent</p>
            </div>
            <div className="rounded-lg bg-amber-50 py-2">
              <p className="font-bold text-amber-700">{attendanceSummary?.late ?? 0}</p>
              <p className="text-amber-600">Late</p>
            </div>
          </div>
        </div>

        {/* Recent notifications */}
        <div className="lg:col-span-2 rounded-xl bg-white p-5 shadow-sm border border-slate-100">
          <h2 className="text-base font-semibold text-slate-800 mb-4">Recent Notifications</h2>
          {unread.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-10 text-slate-400">
              <BellIcon className="h-10 w-10 mb-2 opacity-30" />
              <p className="text-sm">You&apos;re all caught up!</p>
            </div>
          ) : (
            <ul className="space-y-3">
              {unread.slice(0, 6).map((notif) => (
                <li key={notif.id} className="flex items-start gap-3 rounded-lg bg-slate-50 p-3">
                  <div className="mt-0.5 h-2 w-2 flex-shrink-0 rounded-full bg-indigo-500" />
                  <div>
                    <p className="text-sm font-medium text-slate-800">{notif.title}</p>
                    <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">{notif.body}</p>
                    <p className="text-xs text-slate-400 mt-1">{dayjs(notif.created_at).fromNow()}</p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>

      {/* Fee summary */}
      {unpaidAmount > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <BanknotesIcon className="h-6 w-6 text-amber-500" />
            <div>
              <p className="text-sm font-semibold text-amber-800">Outstanding Fee Balance</p>
              <p className="text-xs text-amber-600">
                ${unpaidAmount.toLocaleString()} pending. Please pay before the due date.
              </p>
            </div>
          </div>
          <a
            href="/student/fees"
            className="rounded-lg bg-amber-500 px-4 py-2 text-xs font-semibold text-white hover:bg-amber-600 transition-colors"
          >
            Pay Now
          </a>
        </div>
      )}
    </div>
  );
}
