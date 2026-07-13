/**
 * Parent Children Page — full profile view for each child
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Avatar, Badge, EmptyState, SkeletonCard } from "../../components/common";
import { fmt, attendanceColor, percent } from "../../utils";
import { useTitle } from "../../hooks";
import type { PaginatedResponse } from "../../types";
import type { StudentDetail } from "../../types";

interface ParentChild extends StudentDetail {
  current_class?: string;
  attendance_pct?: number;
  fees_due?: number;
}
import { UsersIcon } from "@heroicons/react/24/outline";

export default function ParentChildrenPage() {
  useTitle("My Children");

  const { data: children, isLoading } = useQuery({
    queryKey: ["parent-children-full"],
    queryFn: () => api.get<PaginatedResponse<ParentChild>>("/students/"),
  });
  const childList = children?.results ?? [];

  if (isLoading) return <div className="p-4"><SkeletonCard /></div>;

  return (
    <div className="space-y-5">
      <div><h1 className="text-2xl font-bold text-slate-900">My Children</h1><p className="text-sm text-slate-500 mt-1">{childList.length} {childList.length === 1 ? "child" : "children"} linked to your account</p></div>

      {childList.length === 0
        ? <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none p-8"><EmptyState icon={UsersIcon} title="No children linked" description="Contact your school administrator to link your children to this parent account." /></div>
        : childList.map((child: ParentChild) => (
          <div key={child.id} className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
            <div className="p-5 flex flex-col sm:flex-row gap-5">
              <Avatar name={child.full_name} src={child.avatar} className="h-20 w-20 text-2xl flex-shrink-0" />
              <div className="flex-1 min-w-0">
                <div className="flex flex-wrap items-center gap-3 mb-1">
                  <h2 className="text-xl font-bold text-slate-900">{child.full_name}</h2>
                  <Badge color={child.is_active?"green":"slate"} dot>{child.is_active?"Active":"Inactive"}</Badge>
                </div>
                <p className="text-sm text-slate-500">{child.email}</p>
                <div className="mt-3 flex flex-wrap gap-5 text-sm">
                  {[
                    ["Admission #", child.admission_number],
                    ["Class", child.current_class ?? "—"],
                    ["Date of Birth", child.date_of_birth ? fmt.date(child.date_of_birth) : "—"],
                    ["Gender", child.gender === "M" ? "Male" : child.gender === "F" ? "Female" : "—"],
                    ["Blood Group", child.blood_group || "—"],
                  ].map(([l,v])=>(
                    <div key={String(l)}>
                      <span className="text-slate-500 text-xs font-medium">{l}</span>
                      <p className="font-semibold text-slate-800 mt-0.5">{v}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Quick stats */}
            <div className="border-t border-slate-100 px-5 py-4 grid grid-cols-2 sm:grid-cols-4 gap-4">
              {[
                { label:"Attendance", value:child.attendance_pct != null ? percent(child.attendance_pct) : "—", color: child.attendance_pct != null ? attendanceColor(child.attendance_pct) : "text-slate-500" },
                { label:"Fees Due", value: child.fees_due != null && child.fees_due > 0 ? `$${Number(child.fees_due).toFixed(2)}` : "Paid", color: child.fees_due != null && child.fees_due > 0 ? "text-red-600" : "text-green-600" },
                { label:"Admission Date", value: child.admission_date ? fmt.date(child.admission_date) : "—", color:"text-slate-700" },
                { label:"City", value: child.city || "—", color:"text-slate-700" },
              ].map(({label,value,color})=>(
                <div key={label} className="bg-slate-50 rounded-xl p-3 text-center">
                  <p className={`text-lg font-bold ${color}`}>{value}</p>
                  <p className="text-xs text-slate-500 mt-0.5">{label}</p>
                </div>
              ))}
            </div>
          </div>
        ))
      }
    </div>
  );
}
