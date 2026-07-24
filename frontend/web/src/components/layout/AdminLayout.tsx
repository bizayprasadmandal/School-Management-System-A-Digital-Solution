/**
 * AdminLayout — Sidebar + topbar shell for administrators
 */

import React, { useState, useCallback } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import {
  HomeIcon,
  UsersIcon,
  AcademicCapIcon,
  ClipboardDocumentCheckIcon,
  CalendarDaysIcon,
  BookOpenIcon,
  ChartBarIcon,
  MegaphoneIcon,
  BanknotesIcon,
  Cog6ToothIcon,
  ArrowRightOnRectangleIcon,
  Bars3Icon,
  XMarkIcon,
  BuildingLibraryIcon,
  DocumentChartBarIcon,
  SunIcon,
  MoonIcon,
  ExclamationTriangleIcon,
  VideoCameraIcon,
  PaperAirplaneIcon,
  ShieldExclamationIcon,
  BriefcaseIcon,
  TruckIcon,
  CubeIcon,
  BuildingOffice2Icon,
  TrophyIcon,
  HeartIcon,
  GlobeAltIcon,
  DocumentTextIcon,
  GlobeAmericasIcon,
  // Cafeteria uses existing BookOpenIcon
} from "@heroicons/react/24/outline";
import CommandPalette from "../common/CommandPalette";
import SchoolSwitcher from "../common/SchoolSwitcher";
import { useAuthStore } from "../../store/authStore";
import { useSchoolContextStore } from "../../store/schoolContextStore";
import NotificationBell from "../../components/common/NotificationBell";
import { useDarkMode } from "../../hooks/useDarkMode";
import { AnimatedOutlet } from "../../components/common/AnimatedOutlet";
import EmailVerificationBanner from "../../components/common/EmailVerificationBanner";
import BackupCodeWarningBanner from "../../components/common/BackupCodeWarningBanner";
import UserMenuDropdown from "../../components/common/UserMenuDropdown";
import clsx from "clsx";
import NotificationPanel from "./NotificationPanel";

interface NavItem {
  label: string;
  to: string;
  icon: React.ComponentType<{ className?: string }>;
  badge?: number;
}

const NAV_ITEMS: NavItem[] = [
  { label: "Dashboard",      to: "/admin",              icon: HomeIcon },
  { label: "Students",       to: "/admin/students",     icon: UsersIcon },
  { label: "Teachers",       to: "/admin/teachers",     icon: AcademicCapIcon },
  { label: "Classrooms",     to: "/admin/classrooms",   icon: BuildingLibraryIcon },
  { label: "Timetable",      to: "/admin/timetable",    icon: CalendarDaysIcon },
  { label: "Attendance",     to: "/admin/attendance",   icon: ClipboardDocumentCheckIcon },
  { label: "Examinations",   to: "/admin/exams",        icon: BookOpenIcon },
  { label: "Report Cards",   to: "/admin/report-cards", icon: DocumentChartBarIcon },
  { label: "Announcements",  to: "/admin/announcements",icon: MegaphoneIcon },
  { label: "Bulk Messages",  to: "/admin/bulk-messages",icon: PaperAirplaneIcon },
  { label: "Fee Management", to: "/admin/fees",         icon: BanknotesIcon },
  { label: "Event Calendar", to: "/admin/events",       icon: CalendarDaysIcon },
  { label: "Library",        to: "/admin/library",      icon: BookOpenIcon },
  { label: "Behavior",       to: "/admin/behavior",     icon: ExclamationTriangleIcon },
  { label: "Conferences",    to: "/admin/conferences",  icon: VideoCameraIcon },
  { label: "Analytics",      to: "/admin/reports",      icon: ChartBarIcon },
  { label: "HR & Payroll",      to: "/admin/hr",            icon: BriefcaseIcon },
  { label: "Transportation",    to: "/admin/transport",      icon: TruckIcon },
  { label: "Inventory & Store",  to: "/admin/inventory",      icon: CubeIcon },
  { label: "Hostel",              to: "/admin/hostel",         icon: BuildingOffice2Icon },
  { label: "Sports",               to: "/admin/sports",          icon: TrophyIcon },
  { label: "Health",               to: "/admin/health",          icon: HeartIcon },
  { label: "Alumni",               to: "/admin/alumni",          icon: GlobeAltIcon },
  { label: "Cafeteria",            to: "/admin/cafeteria",       icon: BookOpenIcon },
  { label: "Admissions",           to: "/admin/admissions",      icon: DocumentTextIcon },
  { label: "Zoom Integration",  to: "/admin/zoom-integration", icon: VideoCameraIcon },
  { label: "Audit Log",         to: "/admin/audit-logs",     icon: ShieldExclamationIcon },
  { label: "Settings",       to: "/admin/settings",     icon: Cog6ToothIcon },
];

export default function AdminLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();
  const [isDark, toggleDark] = useDarkMode();
  const isSuperAdmin = user?.role === "super_admin";
  const activeSchool = useSchoolContextStore((s) => s.activeSchool);
  const activeSchoolName = activeSchool?.name || user?.school?.name;

  const PLATFORM_NAV_ITEMS: NavItem[] = [
    { label: "Platform Dashboard", to: "/admin/platform",           icon: ChartBarIcon },
    { label: "Schools",             to: "/admin/platform/schools",   icon: BuildingOffice2Icon },
  ];

  const handleLogout = useCallback(() => {
    logout();
    navigate("/login");
  }, [logout, navigate]);

  return (
    <div className="flex h-screen bg-slate-100 dark:bg-slate-900 overflow-hidden transition-colors duration-200">
      {/* ── Mobile overlay ───────────────────────────────────────────────── */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-20 bg-black/50 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* ── Sidebar ──────────────────────────────────────────────────────── */}
      <aside
        className={clsx(
          "fixed inset-y-0 left-0 z-30 flex w-64 flex-col bg-indigo-900 dark:bg-indigo-950 transition-transform duration-300 lg:static lg:translate-x-0",
          sidebarOpen ? "translate-x-0" : "-translate-x-full"
        )}
      >
        {/* Logo */}
        <div className="flex h-16 items-center justify-between px-5 border-b border-indigo-800 dark:border-indigo-900">
          <div className="flex items-center gap-3">
            <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-white dark:bg-indigo-200">
              <AcademicCapIcon className="h-5 w-5 text-indigo-700 dark:text-indigo-900" />
            </div>
            <span className="text-lg font-bold text-white tracking-tight">EduSphere</span>
          </div>
          <button
            className="lg:hidden text-indigo-300 hover:text-white"
            onClick={() => setSidebarOpen(false)}
          >
            <XMarkIcon className="h-5 w-5" />
          </button>
        </div>

        {/* School badge — shows active context for super admin */}
        {activeSchoolName && (
          <div className="mx-4 mt-4 rounded-lg bg-indigo-800/60 dark:bg-indigo-900/80 px-3 py-2">
            <p className="text-xs text-indigo-300 dark:text-indigo-400">
              {activeSchool ? "Active School" : "School"}
            </p>
            <p className="text-sm font-medium text-white truncate flex items-center gap-1.5">
              {activeSchoolName}
              {activeSchool && (
                <span className="inline-block h-1.5 w-1.5 rounded-full bg-emerald-400" title="Context switched" />
              )}
            </p>
          </div>
        )}

        {/* Nav links */}
        <nav className="mt-4 flex-1 overflow-y-auto px-3 pb-4 space-y-0.5">
          {NAV_ITEMS.map(({ label, to, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/admin"}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                clsx(
                  "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                  isActive
                    ? "bg-white/10 text-white"
                    : "text-indigo-300 hover:bg-white/5 hover:text-white"
                )
              }
            >
              <Icon className="h-5 w-5 flex-shrink-0" />
              {label}
            </NavLink>
          ))}

          {/* ── Platform Management (Super Admin only) ────────────── */}
          {isSuperAdmin && (
            <>
              <div className="flex items-center gap-2 pt-4 pb-1">
                <GlobeAmericasIcon className="h-4 w-4 text-indigo-400" />
                <span className="text-[11px] font-semibold uppercase tracking-widest text-indigo-400">
                  Platform
                </span>
                <div className="flex-1 border-t border-indigo-800/50" />
              </div>
              {PLATFORM_NAV_ITEMS.map(({ label, to, icon: Icon }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === "/admin/platform"}
                  onClick={() => setSidebarOpen(false)}
                  className={({ isActive }) =>
                    clsx(
                      "flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors",
                      isActive
                        ? "bg-purple-500/20 text-purple-200"
                        : "text-indigo-300 hover:bg-white/5 hover:text-white"
                    )
                  }
                >
                  <Icon className="h-5 w-5 flex-shrink-0" />
                  {label}
                </NavLink>
              ))}
            </>
          )}
        </nav>

        {/* User info */}
        <div className="border-t border-indigo-800 dark:border-indigo-900 p-4">
          <div className="flex items-center gap-3">
            {user?.avatar ? (
              <img src={user.avatar} alt="" loading="lazy" className="h-9 w-9 rounded-full object-cover" />
            ) : (
              <div className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-600 text-white font-semibold text-sm">
                {user?.first_name?.[0]}{user?.last_name?.[0]}
              </div>
            )}
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-white truncate flex items-center gap-1.5">
                {user?.full_name}
                {user && (
                  user.email_verified ? (
                    <span
                      className="inline-block h-2 w-2 rounded-full shrink-0 bg-green-400 shadow-[0_0_4px_rgba(74,222,128,0.5)]"
                      title="Email verified"
                    />
                  ) : (
                    <button
                      onClick={(e) => { e.stopPropagation(); navigate("/admin/settings?tab=security"); }}
                      className="inline-block h-2 w-2 rounded-full shrink-0 bg-amber-400 shadow-[0_0_4px_rgba(251,191,36,0.5)] cursor-pointer hover:bg-amber-300 transition-colors"
                      title="Verify now"
                    />
                  )
                )}
              </p>
              <p className="text-xs text-indigo-300 dark:text-indigo-400 capitalize">{user?.role?.replace("_", " ")}</p>
            </div>
            <button
              onClick={handleLogout}
              title="Sign out"
              className="text-indigo-400 hover:text-white transition-colors"
            >
              <ArrowRightOnRectangleIcon className="h-5 w-5" />
            </button>
          </div>
        </div>
      </aside>

      {/* ── Main content ─────────────────────────────────────────────────── */}
      <div className="flex flex-1 flex-col min-w-0 overflow-hidden">
        {/* Topbar */}
        <header className="flex h-16 items-center justify-between bg-white dark:bg-slate-800 px-4 shadow-sm z-10 border-b border-slate-200 dark:border-slate-700 transition-colors duration-200">
          <button
            className="lg:hidden text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white"
            onClick={() => setSidebarOpen(true)}
          >
            <Bars3Icon className="h-6 w-6" />
          </button>

          <div className="flex-1 lg:pl-0" />

          <div className="flex items-center gap-2">
            {/* Command palette */}
            <CommandPalette items={NAV_ITEMS} accent="indigo" />

            {/* School switcher (super admin only) */}
            {isSuperAdmin && <SchoolSwitcher />}

            {/* Dark mode toggle */}
            <button
              onClick={toggleDark}
              title={isDark ? "Switch to light mode" : "Switch to dark mode"}
              className="rounded-lg p-2 text-slate-500 dark:text-slate-400 hover:bg-slate-100 dark:hover:bg-slate-700 hover:text-slate-900 dark:hover:text-white transition-all duration-200"
            >
              {isDark ? (
                <SunIcon className="h-5 w-5" />
              ) : (
                <MoonIcon className="h-5 w-5" />
              )}
            </button>

            {/* Email verification badge */}
            {user && !user.email_verified && (
              <button
                onClick={() => navigate("/admin/verify-email")}
                title="Email not verified — click to verify"
                className="relative rounded-lg p-2 text-amber-500 hover:bg-amber-50 dark:hover:bg-amber-900/30 hover:text-amber-700 dark:hover:text-amber-300 transition-colors"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21.75 6.75v10.5a2.25 2.25 0 01-2.25 2.25h-15a2.25 2.25 0 01-2.25-2.25V6.75m19.5 0A2.25 2.25 0 0019.5 4.5h-15a2.25 2.25 0 00-2.25 2.25m19.5 0v.243a2.25 2.25 0 01-1.07 1.916l-7.5 4.615a2.25 2.25 0 01-2.36 0L3.32 8.91a2.25 2.25 0 01-1.07-1.916V6.75" />
                </svg>
                <span className="absolute -top-0.5 -right-0.5 flex h-3.5 w-3.5 items-center justify-center rounded-full bg-amber-500 text-[8px] font-bold text-white">
                  !
                </span>
              </button>
            )}

            {/* Notifications bell */}
            <NotificationBell onClick={() => setNotifOpen(v => !v)} />

            {/* Avatar with dropdown */}
            <UserMenuDropdown verifyEmailPath="/admin/verify-email" profilePath="/admin/settings?tab=security" />
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-y-auto p-6 dark:text-slate-200">
          <EmailVerificationBanner />
          <BackupCodeWarningBanner managePath="/admin/setup-2fa" />
          <AnimatedOutlet />
        </main>
        </div>

        {/* Notification slide-in panel — fixed position, outside main content flow */}
        <NotificationPanel open={notifOpen} onClose={() => setNotifOpen(false)} />
      </div>
  );
}
