/**
 * TeacherLayout — Sidebar shell for teachers
 */

import React, { useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import {
  HomeIcon,
  ClipboardDocumentCheckIcon,
  BookOpenIcon,
  CalendarDaysIcon,
  ChatBubbleLeftRightIcon,
  DocumentTextIcon,
  AcademicCapIcon,
  Bars3Icon,
  XMarkIcon,
  UsersIcon,
  ArrowRightOnRectangleIcon,
  SunIcon,
  MoonIcon,
  Cog6ToothIcon,
} from "@heroicons/react/24/outline";
import CommandPalette from "../common/CommandPalette";
import clsx from "clsx";
import { useAuthStore } from "../../store/authStore";
import NotificationBell from "../../components/common/NotificationBell";
import { AnimatedOutlet } from "../../components/common/AnimatedOutlet";
import EmailVerificationBanner from "../../components/common/EmailVerificationBanner";
import BackupCodeWarningBanner from "../../components/common/BackupCodeWarningBanner";
import UserMenuDropdown from "../../components/common/UserMenuDropdown";
import { useDarkMode } from "../../hooks/useDarkMode";
import SidebarNav, { flattenSections } from "./SidebarNav";
import NotificationPanel from "./NotificationPanel";

const NAV_SECTIONS = [
  { label: "Dashboard", to: "/teacher", icon: HomeIcon },
  {
    title: "Teaching",
    icon: AcademicCapIcon,
    items: [
      { label: "Attendance", to: "/teacher/attendance", icon: ClipboardDocumentCheckIcon },
      { label: "Gradebook", to: "/teacher/gradebook", icon: BookOpenIcon },
      { label: "Assignments", to: "/teacher/assignments", icon: DocumentTextIcon },
      { label: "Timetable", to: "/teacher/timetable", icon: CalendarDaysIcon },
      { label: "Lesson Plans", to: "/teacher/lesson-plans", icon: DocumentTextIcon },
      { label: "Conferences", to: "/teacher/conferences", icon: UsersIcon },
    ],
  },
  { label: "Messages", to: "/teacher/messages", icon: ChatBubbleLeftRightIcon },
  { label: "Settings", to: "/teacher/settings", icon: Cog6ToothIcon },
];

export default function TeacherLayout() {
  const [open, setOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const [isDark, toggleDark] = useDarkMode();
  const commandItems = useMemo(() => flattenSections(NAV_SECTIONS), []);

  return (
    <div className="flex h-screen bg-slate-100 dark:bg-slate-900 overflow-hidden transition-colors duration-200">
      {open && (
        <div className="fixed inset-0 z-20 bg-black/50 lg:hidden" onClick={() => setOpen(false)} />
      )}
      <aside
        className={clsx(
          "fixed inset-y-0 left-0 z-30 flex w-64 flex-col bg-emerald-900 dark:bg-emerald-950 transition-transform duration-300 lg:static lg:translate-x-0",
          open ? "translate-x-0" : "-translate-x-full",
        )}
      >
        <div className="flex h-16 items-center justify-between px-5 border-b border-emerald-800 dark:border-emerald-900">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white dark:bg-emerald-200">
              <AcademicCapIcon className="h-5 w-5 text-emerald-700 dark:text-emerald-900" />
            </div>
            <span className="text-lg font-bold text-white">EduSphere</span>
          </div>
          <button
            className="lg:hidden text-emerald-300"
            onClick={() => setOpen(false)}
            aria-label="Close navigation menu"
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
        <div className="mx-4 mt-4 rounded-lg bg-emerald-800/60 dark:bg-emerald-900/80 px-3 py-2">
          <p className="text-xs text-emerald-300 dark:text-emerald-400">Signed in as</p>
          <p className="text-sm font-medium text-white truncate">{user?.full_name}</p>
          <p className="text-xs text-emerald-400">Teacher</p>
        </div>
        <nav className="mt-4 flex-1 overflow-y-auto px-3 pb-4">
          <SidebarNav sections={NAV_SECTIONS} onNavigate={() => setOpen(false)} />
        </nav>
        <div className="border-t border-emerald-800 dark:border-emerald-900 p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-emerald-600 text-white font-semibold text-sm">
              {user?.first_name?.[0]}
              {user?.last_name?.[0]}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate flex items-center gap-1.5">
                {user?.full_name}
                {user &&
                  (user.email_verified ? (
                    <span
                      className="inline-block h-2 w-2 rounded-full shrink-0 bg-green-400 shadow-[0_0_4px_rgba(74,222,128,0.5)]"
                      title="Email verified"
                    />
                  ) : (
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigate("/teacher/verify-email");
                      }}
                      className="inline-block h-2 w-2 rounded-full shrink-0 bg-amber-400 shadow-[0_0_4px_rgba(251,191,36,0.5)] cursor-pointer hover:bg-amber-300 transition-colors"
                      title="Verify now"
                    />
                  ))}
              </p>
            </div>
            <button
              onClick={() => {
                logout();
                navigate("/login");
              }}
              aria-label="Sign out"
              className="text-emerald-400 hover:text-white"
            >
              <ArrowRightOnRectangleIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </aside>

      <div className="flex flex-1 flex-col min-w-0 overflow-hidden">
        <header className="flex h-16 items-center justify-between bg-white dark:bg-slate-800 px-4 shadow-sm border-b border-slate-200 dark:border-slate-700 z-10 transition-colors duration-200">
          <button
            className="lg:hidden text-slate-500 dark:text-slate-400"
            onClick={() => setOpen(true)}
            aria-label="Open navigation menu"
            aria-expanded={open}
          >
            <Bars3Icon className="h-6 w-6" />
          </button>
          <div className="flex-1" />
          <div className="flex items-center gap-2">
            {/* Command palette */}
            <CommandPalette items={commandItems} accent="emerald" />

            {/* Dark mode toggle */}
            <button
              onClick={toggleDark}
              title={isDark ? "Switch to light mode" : "Switch to dark mode"}
              className="rounded-lg p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white transition-all duration-200"
            >
              {isDark ? <SunIcon className="h-5 w-5" /> : <MoonIcon className="h-5 w-5" />}
            </button>

            {/* Email verification badge */}
            {user && !user.email_verified && (
              <button
                onClick={() => navigate("/teacher/verify-email")}
                title="Email not verified — click to verify"
                className="relative rounded-lg p-2 text-amber-500 hover:bg-amber-50 dark:hover:bg-amber-900/30 hover:text-amber-700 dark:hover:text-amber-300 transition-colors"
              >
                <svg
                  className="h-5 w-5"
                  fill="none"
                  viewBox="0 0 24 24"
                  strokeWidth={1.5}
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75"
                  />
                </svg>
                <span className="absolute -top-0.5 -right-0.5 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-amber-500 text-[8px] font-bold text-white">
                  !
                </span>
              </button>
            )}

            <NotificationBell onClick={() => setNotifOpen((v) => !v)} />
            <UserMenuDropdown verifyEmailPath="/teacher/verify-email" accent="emerald" />
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6 dark:text-slate-200">
          <EmailVerificationBanner />
          <BackupCodeWarningBanner managePath="/teacher/setup-2fa" />
          <AnimatedOutlet />
        </main>
      </div>

      {/* Notification slide-in panel — fixed position, outside main content flow */}
      <NotificationPanel open={notifOpen} onClose={() => setNotifOpen(false)} />
    </div>
  );
}
