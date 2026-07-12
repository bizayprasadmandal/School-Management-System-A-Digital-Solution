/**
 * NotFoundPage — Polished 404 error page with branding,
 * helpful suggestions, and a link back to the dashboard.
 */

import React from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { AcademicCapIcon, HomeIcon, ArrowLeftIcon, MagnifyingGlassIcon } from "@heroicons/react/24/outline";
import { useAuthStore } from "../store/authStore";

function getRoleSuggestions(userRole?: string) {
  const suggestions: { label: string; icon: typeof HomeIcon; to: string; action?: "back" }[] = [
    { label: "Go to Dashboard", icon: HomeIcon, to: "/" },
    { label: "Go Back", icon: ArrowLeftIcon, to: "", action: "back" },
  ];

  if (userRole === "school_admin" || userRole === "super_admin" || userRole === "accountant") {
    suggestions.push({ label: "Manage Students", icon: MagnifyingGlassIcon, to: "/admin/students" });
  } else if (userRole === "teacher") {
    suggestions.push({ label: "My Classes", icon: MagnifyingGlassIcon, to: "/teacher" });
  } else if (userRole === "student") {
    suggestions.push({ label: "My Grades", icon: MagnifyingGlassIcon, to: "/student/grades" });
  } else if (userRole === "parent") {
    suggestions.push({ label: "My Children", icon: MagnifyingGlassIcon, to: "/parent/children" });
  }

  return suggestions;
}

export default function NotFoundPage() {
  const navigate = useNavigate();
  const { user } = useAuthStore();

  const getDashboardUrl = () => {
    if (!user) return "/login";
    const role = user.role;
    if (role === "school_admin" || role === "super_admin" || role === "accountant") return "/admin";
    if (role === "teacher") return "/teacher";
    if (role === "student") return "/student";
    if (role === "parent") return "/parent";
    return "/login";
  };

  const suggestions = getRoleSuggestions(user?.role);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-indigo-50 dark:from-slate-950 dark:to-indigo-950 flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="w-full max-w-lg text-center"
      >
        {/* Large 404 graphic */}
        <div className="relative mb-8 select-none">
          <div className="text-[140px] sm:text-[180px] font-black leading-none text-indigo-600/10 dark:text-indigo-400/10 select-none">
            404
          </div>
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="bg-white dark:bg-slate-800 rounded-full p-5 shadow-xl border border-slate-100 dark:border-slate-700">
              <AcademicCapIcon className="h-14 w-14 text-indigo-600 dark:text-indigo-400" />
            </div>
          </div>
        </div>

        {/* Title & description */}
        <h1 className="text-3xl sm:text-4xl font-bold text-slate-900 dark:text-white mb-3">
          Page not found
        </h1>
        <p className="text-slate-500 dark:text-slate-400 text-base max-w-sm mx-auto leading-relaxed">
          The page you&apos;re looking for doesn&apos;t exist or has been moved.
          Let&apos;s get you back on track.
        </p>

        {/* Suggestion cards */}
        <div className="mt-8 grid grid-cols-1 sm:grid-cols-3 gap-3 max-w-md mx-auto">
          {suggestions.map((s) =>
            s.action === "back" ? (
              <button
                key={s.label}
                onClick={() => navigate(-1)}
                className="flex flex-col items-center gap-2 rounded-2xl bg-white dark:bg-slate-800 p-4 shadow-sm border border-slate-100 dark:border-slate-700 hover:border-indigo-200 dark:hover:border-indigo-700 hover:shadow-md transition-all duration-200 group"
              >
                <s.icon className="h-6 w-6 text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors" />
                <span className="text-xs font-semibold text-slate-600 dark:text-slate-300 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                  {s.label}
                </span>
              </button>
            ) : (
              <Link
                key={s.label}
                to={s.to === "/" ? getDashboardUrl() : s.to}
                className="flex flex-col items-center gap-2 rounded-2xl bg-white dark:bg-slate-800 p-4 shadow-sm border border-slate-100 dark:border-slate-700 hover:border-indigo-200 dark:hover:border-indigo-700 hover:shadow-md transition-all duration-200 group"
              >
                <s.icon className="h-6 w-6 text-slate-400 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors" />
                <span className="text-xs font-semibold text-slate-600 dark:text-slate-300 group-hover:text-indigo-600 dark:group-hover:text-indigo-400 transition-colors">
                  {s.label}
                </span>
              </Link>
            )
          )}
        </div>

        {/* Footer */}
        <p className="mt-10 text-xs text-slate-400 dark:text-slate-500">
          © {new Date().getFullYear()} EduSphere School Management System
        </p>
      </motion.div>
    </div>
  );
}
