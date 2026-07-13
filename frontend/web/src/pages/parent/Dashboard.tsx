/**
 * Parent Dashboard — quick overview of all children
 */
import React from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "../../api/client";
import { useAuthStore } from "../../store/authStore";
import { useUnreadNotificationCount } from "../../api/hooks";
import { Avatar, Badge, SkeletonCard } from "../../components/common";
import { useTitle } from "../../hooks";
import { BellIcon, AcademicCapIcon } from "@heroicons/react/24/outline";
import dayjs from "dayjs";

export default function ParentDashboard() {
  useTitle("Dashboard");
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

  const childList = children?.results ?? [];
  const notifList = notifications?.results ?? [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Hello, {user?.first_name}! 👋</h1>
          <p className="text-sm text-slate-500 mt-1">{dayjs().format("dddd, MMMM D YYYY")}</p>
        </div>
        <div className="flex items-center gap-2 rounded-xl bg-white border border-slate-200 px-4 py-2.5 shadow-sm">
          <BellIcon className="h-5 w-5 text-slate-500" />
          <span className="text-sm font-medium text-slate-700">{unread ?? 0} unread</span>
        </div>
      </div>

      {/* Children overview */}
      <div>
        <h2 className="text-base font-semibold text-slate-800 mb-3">My Children</h2>
        {isLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4"><SkeletonCard /><SkeletonCard /></div>
        ) : childList.length === 0 ? (
          <div className="card p-8 text-center text-slate-400">
            <AcademicCapIcon className="h-10 w-10 mx-auto mb-2 opacity-30" />
            <p className="text-sm">No children linked to your account yet. Contact your school admin.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            {childList.map((child: { id: string; full_name: string; avatar?: string; is_active: boolean; current_class?: string; admission_number: string; email: string }) => (
              <div key={child.id} className="card p-5 hover:border-violet-200 transition-colors cursor-pointer">
                <div className="flex items-center gap-4">
                  <Avatar name={child.full_name} src={child.avatar} className="h-14 w-14 text-lg flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-bold text-slate-900 truncate">{child.full_name}</p>
                      <Badge color={child.is_active ? "green" : "slate"} dot>{child.is_active ? "Active" : "Inactive"}</Badge>
                    </div>
                    <p className="text-xs text-slate-500 mt-0.5">{child.current_class ?? "—"} · {child.admission_number}</p>
                  </div>
                </div>
                <div className="mt-4 grid grid-cols-2 gap-3">
                  <div className="rounded-lg bg-slate-50 p-3 text-center">
                    <p className="text-lg font-bold text-indigo-600">—</p>
                    <p className="text-xs text-slate-500 mt-0.5">Attendance</p>
                  </div>
                  <div className="rounded-lg bg-slate-50 p-3 text-center">
                    <p className="text-lg font-bold text-slate-700">—</p>
                    <p className="text-xs text-slate-500 mt-0.5">Latest Grade</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Recent notifications */}
      {notifList.length > 0 && (
        <div>
          <h2 className="text-base font-semibold text-slate-800 mb-3">Recent Notifications</h2>
          <div className="space-y-2">
            {notifList.map((n: { id: string; title: string; body: string; read_at: string | null; created_at: string }) => (
              <div key={n.id} className={`card p-4 flex items-start gap-3 ${!n.read_at ? "border-violet-200 bg-violet-50/30" : ""}`}>
                {!n.read_at && <div className="mt-1.5 h-2 w-2 rounded-full bg-violet-500 flex-shrink-0" />}
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-semibold text-slate-800">{n.title}</p>
                  <p className="text-xs text-slate-500 mt-0.5 line-clamp-2">{n.body}</p>
                  <p className="text-xs text-slate-400 mt-1">{dayjs(n.created_at).fromNow()}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
