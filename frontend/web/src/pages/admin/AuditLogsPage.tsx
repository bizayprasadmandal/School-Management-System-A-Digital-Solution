/** Audit Log Viewer — Search, filter, and inspect security audit logs */

import React, { useState, useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import {
  MagnifyingGlassIcon, FunnelIcon, ChevronDownIcon, ChevronRightIcon,
  ShieldExclamationIcon, ArrowPathIcon,
} from "@heroicons/react/24/outline";
import { api } from "../../api/client";
import { EmptyState, Pagination } from "../../components/common";
import type { AuditLogEntry, PaginatedResponse } from "../../types";

const ACTION_LABELS: Record<string, string> = {
  login: "Login",
  logout: "Logout",
  password_change: "Password Change",
  send_verification_email: "Sent Verification Email",
  confirm_email_verification: "Email Verified",
  regenerate_backup_codes: "Regenerated Backup Codes",
};

const ACTION_COLORS: Record<string, string> = {
  login: "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300",
  logout: "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400",
  password_change: "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300",
  send_verification_email: "bg-purple-100 text-purple-700 dark:bg-purple-900/40 dark:text-purple-300",
  confirm_email_verification: "bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300",
  regenerate_backup_codes: "bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300",
};

function ActionBadge({ action }: { action: string }) {
  const color = ACTION_COLORS[action] || "bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400";
  const label = ACTION_LABELS[action] || action.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
  return <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium ${color}`}>{label}</span>;
}

export default function AuditLogsPage() {
  const [search, setSearch] = useState("");
  const [actionFilter, setActionFilter] = useState<string>("all");
  const [page, setPage] = useState(1);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ["audit-logs", page, actionFilter, search],
    queryFn: () => api.get<PaginatedResponse<AuditLogEntry>>("/auth/audit-logs/", {
      page,
      action: actionFilter === "all" ? undefined : actionFilter,
      search: search || undefined,
      page_size: 25,
    }),
    placeholderData: (prev) => prev,
  });

  const logs = data?.results ?? [];
  const total = data?.count ?? 0;

  const uniqueActions = useMemo(() => {
    const actions = new Set<string>();
    logs.forEach(l => actions.add(l.action));
    return Array.from(actions).sort();
  }, [logs]);

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Audit Log</h1>
          <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">Security audit trail for all sensitive operations</p>
        </div>
        <button onClick={() => refetch()}
          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-sm font-medium text-slate-600 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 transition-colors">
          <ArrowPathIcon className="h-4 w-4" /> Refresh
        </button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-3 flex-wrap">
        <div className="relative flex-1 max-w-sm">
          <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <input value={search} onChange={e => { setSearch(e.target.value); setPage(1); }}
            className="w-full pl-9 pr-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm dark:text-slate-200"
            placeholder="Search by user, action, or resource..." />
        </div>
        <FunnelIcon className="h-4 w-4 text-slate-400" />
        <select value={actionFilter} onChange={e => { setActionFilter(e.target.value); setPage(1); }}
          className="rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 px-3 py-2 text-sm dark:text-slate-200">
          <option value="all">All Actions</option>
          {uniqueActions.map(a => (
            <option key={a} value={a}>{ACTION_LABELS[a] || a}</option>
          ))}
        </select>
      </div>

      {/* Table */}
      {isLoading ? (
        <div className="space-y-2">{[1,2,3,4,5].map(i => <div key={i} className="h-14 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse" />)}</div>
      ) : isError ? (
        <div className="flex flex-col items-center justify-center py-16 text-center text-slate-400">
          <ShieldExclamationIcon className="h-12 w-12 mb-3 opacity-30" />
          <p className="text-base font-medium">Failed to load audit log</p>
          <button onClick={() => refetch()} className="mt-3 text-sm text-indigo-600 hover:text-indigo-700">Try again</button>
        </div>
      ) : logs.length === 0 ? (
        <EmptyState icon={ShieldExclamationIcon} title="No audit log entries"
          description={search ? "Try a different search term" : "No audit events have been recorded yet"} />
      ) : (
        <div className="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-slate-50 dark:bg-slate-800/80 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase">
                <th className="px-4 py-3 w-8"></th>
                <th className="px-4 py-3">Action</th>
                <th className="px-4 py-3">User</th>
                <th className="px-4 py-3">Resource</th>
                <th className="px-4 py-3">IP Address</th>
                <th className="px-4 py-3">Timestamp</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
              {logs.map(entry => (
                <React.Fragment key={entry.id}>
                  <tr className="hover:bg-slate-50 dark:hover:bg-slate-700/50 cursor-pointer transition-colors"
                    onClick={() => setExpandedId(expandedId === entry.id ? null : entry.id)}>
                    <td className="px-4 py-3">
                      {expandedId === entry.id
                        ? <ChevronDownIcon className="h-4 w-4 text-slate-400" />
                        : <ChevronRightIcon className="h-4 w-4 text-slate-400" />
                      }
                    </td>
                    <td className="px-4 py-3"><ActionBadge action={entry.action} /></td>
                    <td className="px-4 py-3">
                      <div>
                        <p className="font-medium text-slate-900 dark:text-white">{entry.user_name || "—"}</p>
                        {entry.user_email && <p className="text-xs text-slate-400">{entry.user_email}</p>}
                      </div>
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs font-mono text-slate-500">{entry.resource_type}</span>
                      {entry.resource_id && <p className="text-xs text-slate-400 font-mono truncate max-w-[120px]">{entry.resource_id}</p>}
                    </td>
                    <td className="px-4 py-3">
                      <span className="text-xs font-mono text-slate-500">{entry.ip_address || "—"}</span>
                    </td>
                    <td className="px-4 py-3 text-slate-500 text-xs">
                      {dayjs(entry.timestamp).format("MMM D, YYYY")}
                      <p className="text-slate-400">{dayjs(entry.timestamp).format("h:mm:ss A")}</p>
                    </td>
                  </tr>
                  {expandedId === entry.id && (
                    <tr className="bg-slate-50/50 dark:bg-slate-800/30">
                      <td colSpan={6} className="px-4 py-4">
                        <div className="grid grid-cols-2 gap-4 text-sm">
                          <div>
                            <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">Changes</p>
                            <pre className="text-xs bg-slate-100 dark:bg-slate-700 rounded p-2 overflow-x-auto max-h-32">
                              {JSON.stringify(entry.changes, null, 2) || "{}"}
                            </pre>
                          </div>
                          <div>
                            <p className="text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">User Agent</p>
                            <p className="text-xs text-slate-600 dark:text-slate-400 break-words">{entry.user_agent || "—"}</p>
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              ))}
            </tbody>
          </table>
          <Pagination page={page} total={total} pageSize={25} onChange={setPage} />
        </div>
      )}
    </div>
  );
}
