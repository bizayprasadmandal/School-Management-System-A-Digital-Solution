/**
 * Platform Audit Logs — cross-school audit trail for the platform console.
 * Super admins see every school's actions; school-filterable.
 */
import React, { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { Input, SkeletonCard } from "../../components/common";
import { useTitle } from "../../hooks";

interface AuditRow {
  id: string;
  school: string | null;
  school_name?: string;
  user_name: string | null;
  user_email: string | null;
  action: string;
  resource_type: string;
  resource_id: string;
  ip_address: string | null;
  timestamp: string;
}

export default function PlatformAuditPage() {
  useTitle("Platform Audit Logs");
  const [search, setSearch] = useState("");

  const { data, isLoading } = useQuery({
    queryKey: ["platform-audit", search],
    queryFn: () =>
      api.get<{ results: AuditRow[]; count: number }>("/auth/audit-log/", {
        search: search || undefined,
        page_size: 50,
      }),
  });

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Audit Logs</h1>
        <p className="text-sm text-slate-500 mt-0.5">Cross-school trail of privileged actions</p>
      </div>

      <div className="bg-white rounded-2xl border border-slate-100 shadow-sm dark:bg-slate-800 dark:border-slate-700 dark:shadow-none">
        <div className="p-4 border-b border-slate-100 dark:border-slate-700">
          <Input
            placeholder="Search action, resource, user, IP…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            aria-label="Search audit logs"
          />
        </div>

        {isLoading || !data ? (
          <div className="p-4">
            <SkeletonCard />
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm" aria-label="Audit log entries">
              <thead>
                <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-100 dark:border-slate-700">
                  <th scope="col" className="px-5 py-3 font-medium">
                    When
                  </th>
                  <th scope="col" className="px-3 py-3 font-medium">
                    School
                  </th>
                  <th scope="col" className="px-3 py-3 font-medium">
                    User
                  </th>
                  <th scope="col" className="px-3 py-3 font-medium">
                    Action
                  </th>
                  <th scope="col" className="px-3 py-3 font-medium">
                    Resource
                  </th>
                  <th scope="col" className="px-5 py-3 font-medium">
                    IP
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                {data.results.map((row) => (
                  <tr key={row.id} className="hover:bg-slate-50 dark:hover:bg-slate-700/40">
                    <td className="px-5 py-2.5 text-slate-500 dark:text-slate-400 whitespace-nowrap">
                      {new Date(row.timestamp).toLocaleString()}
                    </td>
                    <td className="px-3 py-2.5 text-slate-700 dark:text-slate-200">
                      {row.school_name ?? (row.school ? row.school.slice(0, 8) : "—")}
                    </td>
                    <td className="px-3 py-2.5 text-slate-700 dark:text-slate-200">
                      {row.user_name}
                      <span className="ml-1 text-xs text-slate-400">{row.user_email}</span>
                    </td>
                    <td className="px-3 py-2.5">
                      <span className="inline-block rounded bg-indigo-50 px-1.5 py-0.5 text-xs font-medium text-indigo-700 dark:bg-indigo-900/40 dark:text-indigo-300">
                        {row.action}
                      </span>
                    </td>
                    <td className="px-3 py-2.5 text-slate-600 dark:text-slate-300">
                      {row.resource_type}
                      <span className="ml-1 text-xs text-slate-400">
                        {row.resource_id.slice(0, 8)}
                      </span>
                    </td>
                    <td className="px-5 py-2.5 text-slate-400 text-xs">{row.ip_address ?? "—"}</td>
                  </tr>
                ))}
                {data.results.length === 0 && (
                  <tr>
                    <td colSpan={6} className="px-5 py-8 text-center text-slate-400">
                      No audit entries match.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
