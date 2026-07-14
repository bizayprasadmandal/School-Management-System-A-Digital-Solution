/**
 * Parent Children Page — full profile view for each child with live stats
 */
import React from "react";
import { useNavigate } from "react-router-dom";
import { useQuery, useQueries } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Avatar, Badge, EmptyState, SkeletonCard } from "../../components/common";
import { fmt, attendanceColor, percent, currency } from "../../utils";
import { useTitle } from "../../hooks";
import type { PaginatedResponse, StudentDetail, FeeInvoice } from "../../types";
import {
  UsersIcon,
  ClipboardDocumentCheckIcon,
  BookOpenIcon,
  BanknotesIcon,
  ChatBubbleLeftRightIcon,
} from "@heroicons/react/24/outline";

interface AttendanceSummary {
  attendance_percentage: number;
  total_days: number;
  present: number;
}

interface ChildWithStats extends StudentDetail {
  current_class?: string;
  attendancePct?: number;
  feesDue?: number;
}

export default function ParentChildrenPage() {
  useTitle("My Children");
  const navigate = useNavigate();

  const { data: children, isLoading } = useQuery({
    queryKey: ["parent-children-full"],
    queryFn: () => api.get<PaginatedResponse<ChildWithStats>>("/students/"),
  });
  const childList = children?.results ?? [];

  // Stable useQueries — always returns same number of results regardless of data
  const attendanceResults = useQueries({
    queries: (childList ?? []).map((child) => ({
      queryKey: ["parent-child-att-summary", child.id],
      queryFn: () =>
        api.get<AttendanceSummary>(`/students/${child.id}/attendance-summary/`),
      enabled: !!child.id,
    })),
  });

  const feesResults = useQueries({
    queries: (childList ?? []).map((child) => ({
      queryKey: ["parent-child-fees-summary", child.id],
      queryFn: () =>
        api
          .get<PaginatedResponse<FeeInvoice>>(`/fees/invoices/?student=${child.id}`)
          .then(
            (r) =>
              r.results
                .filter((i) => ["unpaid", "overdue", "partial"].includes(i.status))
                .reduce((sum, i) => sum + Number(i.outstanding_amount), 0) as number
          ),
      enabled: !!child.id,
    })),
  });

  if (isLoading) return <div className="p-4"><SkeletonCard /></div>;

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">My Children</h1>
        <p className="text-sm text-slate-500 mt-1">
          {childList.length} {childList.length === 1 ? "child" : "children"} linked to your account
        </p>
      </div>

      {childList.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-8">
          <EmptyState
            icon={UsersIcon}
            title="No children linked"
            description="Contact your school administrator to link your children to this parent account."
          />
        </div>
      ) : (
        childList.map((child, i) => (
          <div
            key={child.id}
            className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none overflow-hidden"
          >
            {/* Profile header */}
            <div className="p-5 flex flex-col sm:flex-row gap-5">
              <Avatar
                name={child.full_name}
                src={child.avatar}
                className="h-20 w-20 text-2xl flex-shrink-0"
              />
              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center gap-3 mb-1">
                  <h2 className="text-xl font-bold text-slate-900">{child.full_name}</h2>
                  <Badge color={child.is_active ? "green" : "slate"} dot>
                    {child.is_active ? "Active" : "Inactive"}
                  </Badge>
                </div>
                <p className="text-sm text-slate-500">{child.email}</p>
                <div className="mt-3 flex flex-wrap gap-5 text-sm">
                  {[
                    ["Admission #", child.admission_number],
                    ["Class", child.current_class ?? "—"],
                    ["Date of Birth", child.date_of_birth ? fmt.date(child.date_of_birth) : "—"],
                    ["Gender", child.gender === "M" ? "Male" : child.gender === "F" ? "Female" : "—"],
                    ["Blood Group", child.blood_group || "—"],
                  ].map(([l, v]) => (
                    <div key={String(l)}>
                      <span className="text-slate-500 text-xs font-medium">{l}</span>
                      <p className="font-semibold text-slate-800 mt-0.5">{v}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Live stats */}
            <div className="border-t border-slate-100 px-5 py-4 grid grid-cols-2 sm:grid-cols-4 gap-4">
              <div className="bg-slate-50 rounded-xl p-3 text-center">
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

              <div className="bg-slate-50 rounded-xl p-3 text-center">
                <p
                  className={`text-lg font-bold ${
                    feesResults[i]?.data != null && feesResults[i].data! > 0
                      ? "text-red-600"
                      : feesResults[i]?.data === 0
                      ? "text-green-600"
                      : "text-slate-400"
                  }`}
                >
                  {feesResults[i]?.data != null
                    ? feesResults[i].data! > 0
                      ? currency(feesResults[i].data!)
                      : "Paid"
                    : "—"}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">Fees Due</p>
              </div>

              <div className="bg-slate-50 rounded-xl p-3 text-center">
                <p className="text-lg font-bold text-slate-700">
                  {child.admission_date ? fmt.date(child.admission_date) : "—"}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">Admission Date</p>
              </div>

              <div className="bg-slate-50 rounded-xl p-3 text-center">
                <p className="text-lg font-bold text-slate-700">{child.city || "—"}</p>
                <p className="text-xs text-slate-500 mt-0.5">City</p>
              </div>
            </div>

            {/* Action buttons */}
            <div className="border-t border-slate-100 px-5 py-3 flex flex-wrap gap-2">
              {[
                { label: "Attendance", icon: ClipboardDocumentCheckIcon, path: "/parent/attendance", color: "bg-green-50 text-green-700 hover:bg-green-100 border-green-200" },
                { label: "Grades",     icon: BookOpenIcon,                path: "/parent/grades",      color: "bg-blue-50 text-blue-700 hover:bg-blue-100 border-blue-200" },
                { label: "Fees",       icon: BanknotesIcon,               path: "/parent/fees",         color: "bg-amber-50 text-amber-700 hover:bg-amber-100 border-amber-200" },
                { label: "Message",    icon: ChatBubbleLeftRightIcon,     path: "/parent/messages",    color: "bg-violet-50 text-violet-700 hover:bg-violet-100 border-violet-200" },
              ].map(({ label, icon: Icon, path, color }) => (
                <button
                  key={label}
                  onClick={() => navigate(path)}
                  className={`inline-flex items-center gap-1.5 rounded-lg border px-3 py-1.5 text-xs font-semibold transition-colors ${color}`}
                >
                  <Icon className="h-3.5 w-3.5" />
                  {label}
                </button>
              ))}
            </div>
          </div>
        ))
      )}
    </div>
  );
}
