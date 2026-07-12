/**
 * StudentLayout — sidebar shell for students
 */

import React, { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import {
  HomeIcon, ClipboardDocumentCheckIcon, BookOpenIcon,
  CalendarDaysIcon, ChatBubbleLeftRightIcon, BanknotesIcon,
  AcademicCapIcon, Bars3Icon, XMarkIcon, BellIcon,
  ArrowRightOnRectangleIcon, SunIcon, MoonIcon,
} from "@heroicons/react/24/outline";
import clsx from "clsx";
import { useAuthStore } from "../../store/authStore";
import { useUnreadNotificationCount } from "../../api/hooks";
import { AnimatedOutlet } from "../../components/common/AnimatedOutlet";
import { useDarkMode } from "../../hooks/useDarkMode";
import type { User } from "../../types";

const STUDENT_NAV = [
  { label: "Dashboard",  to: "/student",            icon: HomeIcon },
  { label: "Attendance", to: "/student/attendance", icon: ClipboardDocumentCheckIcon },
  { label: "My Grades",  to: "/student/grades",     icon: BookOpenIcon },
  { label: "Timetable",  to: "/student/timetable",  icon: CalendarDaysIcon },
  { label: "Messages",   to: "/student/messages",   icon: ChatBubbleLeftRightIcon },
  { label: "Fees",       to: "/student/fees",        icon: BanknotesIcon },
];

interface NavItem {
  label: string;
  to: string;
  icon: React.ComponentType<{ className?: string }>;
}

interface SidebarShellProps {
  nav: NavItem[];
  accent: string;
  open: boolean;
  setOpen: (v: boolean) => void;
  user: User | null;
  logout: () => void;
  navigate: (path: string) => void;
  unread: number;
  isDark: boolean;
  toggleDark: () => void;
}

function SidebarShell({
  nav, accent, open, setOpen, user, logout, navigate, unread, isDark, toggleDark,
}: SidebarShellProps) {
  return (
    <div className="flex h-screen bg-slate-100 dark:bg-slate-900 overflow-hidden transition-colors duration-200">
      {open && (
        <div className="fixed inset-0 z-20 bg-black/50 lg:hidden" onClick={() => setOpen(false)} />
      )}
      <aside className={clsx(
        `fixed inset-y-0 left-0 z-30 flex w-64 flex-col ${accent} dark:brightness-110 transition-transform duration-300 lg:static lg:translate-x-0`,
        open ? "translate-x-0" : "-translate-x-full"
      )}>
        <div className="flex h-16 items-center justify-between px-5 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white dark:bg-white/90">
              <AcademicCapIcon className="h-5 w-5 text-blue-700 dark:text-blue-900" />
            </div>
            <span className="text-lg font-bold text-white">EduSphere</span>
          </div>
          <button className="lg:hidden text-white/70" onClick={() => setOpen(false)}>
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>
        <div className="mx-4 mt-4 rounded-lg bg-white/10 px-3 py-2">
          <p className="text-xs text-white/60">Logged in as</p>
          <p className="text-sm font-semibold text-white truncate">{user?.full_name}</p>
        </div>
        <nav className="mt-4 flex-1 overflow-y-auto px-3 pb-4 space-y-0.5">
          {nav.map(({ label, to, icon: Icon }) => (
            <NavLink key={to} to={to} end={to.split("/").length === 2}
              onClick={() => setOpen(false)}
              className={({ isActive }) => clsx(
                "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                isActive ? "bg-white/15 text-white" : "text-white/60 hover:bg-white/10 hover:text-white"
              )}>
              <Icon className="h-5 w-5 flex-shrink-0" />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="border-t border-white/10 p-4">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-white/20 text-white font-semibold text-sm">
              {user?.first_name?.[0]}{user?.last_name?.[0]}
            </div>
            <p className="flex-1 text-sm font-medium text-white truncate">{user?.first_name}</p>
            <button onClick={() => { logout(); navigate("/login"); }} className="text-white/50 hover:text-white">
              <ArrowRightOnRectangleIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </aside>

      <div className="flex flex-1 flex-col min-w-0 overflow-hidden">
        <header className="flex h-16 items-center justify-between bg-white dark:bg-slate-800 px-4 shadow-sm border-b border-slate-200 dark:border-slate-700 transition-colors duration-200">
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
          </div>
        </header>
        <main className="flex-1 overflow-y-auto p-6 dark:text-slate-200">
          <AnimatedOutlet />
        </main>
      </div>
    </div>
  );
}

export function StudentLayout() {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const { data: unread = 0 } = useUnreadNotificationCount();
  const [isDark, toggleDark] = useDarkMode();
  return (
    <SidebarShell
      nav={STUDENT_NAV} accent="bg-blue-800" open={open}
      setOpen={setOpen} user={user} logout={logout}
      navigate={navigate} unread={unread}
      isDark={isDark} toggleDark={toggleDark}
    />
  );
}

export default StudentLayout;

// ─── Parent Layout ─────────────────────────────────────────────────────────────

const PARENT_NAV: NavItem[] = [
  { label: "Dashboard",  to: "/parent",             icon: HomeIcon },
  { label: "My Children",to: "/parent/children",    icon: AcademicCapIcon },
  { label: "Attendance", to: "/parent/attendance",  icon: ClipboardDocumentCheckIcon },
  { label: "Grades",     to: "/parent/grades",      icon: BookOpenIcon },
  { label: "Fees",       to: "/parent/fees",         icon: BanknotesIcon },
  { label: "Messages",   to: "/parent/messages",    icon: ChatBubbleLeftRightIcon },
];

export function ParentLayout() {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuthStore();
  const navigate = useNavigate();
  const { data: unread = 0 } = useUnreadNotificationCount();
  const [isDark, toggleDark] = useDarkMode();
  return (
    <SidebarShell
      nav={PARENT_NAV} accent="bg-violet-800" open={open}
      setOpen={setOpen} user={user} logout={logout}
      navigate={navigate} unread={unread}
      isDark={isDark} toggleDark={toggleDark}
    />
  );
}
