/**
 * TeacherLayout — Sidebar shell for teachers
 */

import React, { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  HomeIcon, ClipboardDocumentCheckIcon, BookOpenIcon,
  CalendarDaysIcon, ChatBubbleLeftRightIcon, DocumentTextIcon,
  AcademicCapIcon, Bars3Icon, XMarkIcon, BellIcon,
  ArrowRightOnRectangleIcon, SunIcon, MoonIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import { useAuthStore } from "../../store/authStore";
import { useUnreadNotificationCount } from "../../api/hooks";
import { AnimatedOutlet } from "../../components/common/AnimatedOutlet";
import { useDarkMode } from "../../hooks/useDarkMode";

const NAV = [
  { label: "Dashboard",    to: "/teacher",              icon: HomeIcon },
  { label: "Attendance",   to: "/teacher/attendance",   icon: ClipboardDocumentCheckIcon },
  { label: "Gradebook",    to: "/teacher/gradebook",    icon: BookOpenIcon },
  { label: "Timetable",    to: "/teacher/timetable",    icon: CalendarDaysIcon },
  { label: "Messages",     to: "/teacher/messages",     icon: ChatBubbleLeftRightIcon },
  { label: "Lesson Plans", to: "/teacher/lesson-plans", icon: DocumentTextIcon },
];

export default function TeacherLayout() {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const { data: unread = 0 } = useUnreadNotificationCount();
  const [isDark, toggleDark] = useDarkMode();

  return (
    <div className="flex h-screen bg-slate-100 dark:bg-slate-900 overflow-hidden transition-colors duration-200">
      {open && (
        <div className="fixed inset-0 z-20 bg-black/50 lg:hidden" onClick={() => setOpen(false)} />
      )}
      <aside className={clsx(
        "fixed inset-y-0 left-0 z-30 flex w-64 flex-col bg-emerald-900 dark:bg-emerald-950 transition-transform duration-300 lg:static lg:translate-x-0",
        open ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex h-16 items-center justify-between px-5 border-b border-emerald-800 dark:border-emerald-900">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white dark:bg-emerald-200">
              <AcademicCapIcon className="h-5 w-5 text-emerald-700 dark:text-emerald-900" />
            </div>
            <span className="text-lg font-bold text-white">EduSphere</span>
          </div>
          <button className="lg:hidden text-emerald-300" onClick={() => setOpen(false)}>
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
        <div className="mx-4 mt-4 rounded-lg bg-emerald-800/60 dark:bg-emerald-900/80 px-3 py-2">
          <p className="text-xs text-emerald-300 dark:text-emerald-400">Signed in as</p>
          <p className="text-sm font-medium text-white truncate">{user?.full_name}</p>
          <p className="text-xs text-emerald-400">Teacher</p>
        </div>
        <nav className="mt-4 flex-1 overflow-y-auto px-3 pb-4 space-y-0.5">
          {NAV.map(({ label, to, icon: Icon }) => (
            <NavLink key={to} to={to} end={to === "/teacher"} onClick={() => setOpen(false)}
              className={({ isActive }) => clsx(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive ? "bg-white/10 text-white" : "text-emerald-300 hover:bg-white/5 hover:text-white"
              )}>
              <Icon className="h-5 w-5 flex-shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-emerald-800 dark:border-emerald-900 p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-600 text-white font-semibold text-sm">
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.full_name}</p>
            </div>
            <button onClick={() => { logout(); navigate("/login"); }} className="text-emerald-400 hover:text-white">
              <ArrowRightOnRectangleIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </aside>

      <div className="flex flex-1 flex-col min-w-0 overflow-hidden">
        <header className="flex h-16 items-center justify-between bg-white dark:bg-slate-800 px-4 shadow-sm border-b border-slate-200 dark:border-slate-700 z-10 transition-colors duration-200">
          <button className="lg:hidden text-slate-500 dark:text-slate-400" onClick={() => setOpen(true)}>
            <Bars3Icon className="h-6 w-6" />
          </button>
          <div className="flex-1" />
          <div className="flex items-center gap-2">
            {/* Dark mode toggle */}
            <button
              onClick={toggleDark}
              title={isDark ? "Switch to light mode" : "Switch to dark mode"}
              className="rounded-lg p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white transition-all duration-200"
            >
              {isDark ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
            </button>
            <button className="relative rounded-lg p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700">
              <BellIcon className="h-5 w-5" />
              {unread > 0 && (
                <span className="absolute -top-0.5 -right-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white">
                  {unread > 9 ? "9+" : unread}
                </span>
              )}
            </button>
            <div className="flex h-8 w-8 items-center justify-center rounded-full bg-emerald-600 text-white text-xs font-semibold">
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </div>
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6 dark:text-slate-200">
          <AnimatedOutlet />
        </main>
      </div>
    </div>
  );
}
