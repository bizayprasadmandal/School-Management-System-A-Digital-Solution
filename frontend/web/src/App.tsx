/**
 * App.tsx — Root router with role-based layout switching
 */

import React, { Suspense } from "react";
import {
  BrowserRouter,
  Routes,
  Route,
  Navigate,
  Outlet,
} from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import { useAuthStore } from "./store/authStore";
import { ErrorBoundary } from "./components/common/ErrorBoundary";
import RouteProgressBar from "./components/common/RouteProgressBar";
import type { UserRole } from "./types";

// Lazy-loaded layouts
const AdminLayout    = React.lazy(() => import("./components/layout/AdminLayout"));
const TeacherLayout  = React.lazy(() => import("./components/layout/TeacherLayout"));
const StudentLayout  = React.lazy(() => import("./components/layout/StudentLayout"));
const ParentLayout   = React.lazy(() => import("./components/layout/ParentLayout"));

// Auth pages
const LoginPage           = React.lazy(() => import("./pages/auth/LoginPage"));
const ForgotPasswordPage  = React.lazy(() => import("./pages/auth/ForgotPasswordPage"));
const ResetPasswordPage   = React.lazy(() => import("./pages/auth/ResetPasswordPage"));

// Admin pages
const AdminDashboard      = React.lazy(() => import("./pages/admin/Dashboard"));
const StudentsPage        = React.lazy(() => import("./pages/admin/StudentsPage"));
const StudentDetailPage   = React.lazy(() => import("./pages/admin/StudentDetailPage"));
const TeachersPage        = React.lazy(() => import("./pages/admin/TeachersPage"));
const ClassroomsPage      = React.lazy(() => import("./pages/admin/ClassroomsPage"));
const TimetablePage       = React.lazy(() => import("./pages/admin/TimetablePage"));
const AttendancePage      = React.lazy(() => import("./pages/admin/AttendancePage"));
const ExamsPage           = React.lazy(() => import("./pages/admin/ExamsPage"));
const ReportCardsPage     = React.lazy(() => import("./pages/admin/ReportCardsPage"));
const AnnouncementsPage   = React.lazy(() => import("./pages/admin/AnnouncementsPage"));
const FeesPage            = React.lazy(() => import("./pages/admin/FeesPage"));
const SettingsPage        = React.lazy(() => import("./pages/admin/SettingsPage"));
const ReportsPage         = React.lazy(() => import("./pages/admin/ReportsPage"));

// Teacher pages
const TeacherDashboard    = React.lazy(() => import("./pages/teacher/Dashboard"));
const TeacherAttendance   = React.lazy(() => import("./pages/teacher/AttendancePage"));
const TeacherGradebook    = React.lazy(() => import("./pages/teacher/GradebookPage"));
const TeacherTimetable    = React.lazy(() => import("./pages/teacher/TimetablePage"));
const TeacherMessages     = React.lazy(() => import("./pages/teacher/MessagesPage"));
const TeacherLessonPlans  = React.lazy(() => import("./pages/teacher/LessonPlansPage"));

import { ErrorRoutes } from "./config/errorRoutes";

// Student pages
const StudentDashboard    = React.lazy(() => import("./pages/student/Dashboard"));
const StudentAttendance   = React.lazy(() => import("./pages/student/AttendancePage"));
const StudentGrades       = React.lazy(() => import("./pages/student/GradesPage"));
const StudentTimetable    = React.lazy(() => import("./pages/student/TimetablePage"));
const StudentMessages     = React.lazy(() => import("./pages/student/MessagesPage"));
const StudentFees         = React.lazy(() => import("./pages/student/FeesPage"));

// Parent pages
const ParentDashboard     = React.lazy(() => import("./pages/parent/Dashboard"));
const ParentChildren      = React.lazy(() => import("./pages/parent/ChildrenPage"));
const ParentAttendance    = React.lazy(() => import("./pages/parent/AttendancePage"));
const ParentGrades        = React.lazy(() => import("./pages/parent/GradesPage"));
const ParentFees          = React.lazy(() => import("./pages/parent/FeesPage"));
const ParentMessages      = React.lazy(() => import("./pages/parent/MessagesPage"));

// ─── React Query client ───────────────────────────────────────────────────────

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,       // 5 min — per-query overrides below
      gcTime: 30 * 60 * 1000,          // keep stale data 30 min for SWR
      retry: 1,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,        // revalidate after network comes back
    },
  },
});

// ─── Guard components ─────────────────────────────────────────────────────────

function RequireAuth({ allowedRoles }: { allowedRoles?: UserRole[] }) {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) return <Navigate to="/login" replace />;
  if (allowedRoles && user && !allowedRoles.includes(user.role)) {
    return <Navigate to="/unauthorized" replace />;
  }
  return <Outlet />;
}

function RedirectIfAuth() {
  const { isAuthenticated, user } = useAuthStore();
  if (!isAuthenticated) return <Outlet />;

  const role = user?.role;
  if (role === "school_admin" || role === "super_admin") return <Navigate to="/admin" replace />;
  if (role === "teacher") return <Navigate to="/teacher" replace />;
  if (role === "student") return <Navigate to="/student" replace />;
  if (role === "parent") return <Navigate to="/parent" replace />;
  return <Navigate to="/login" replace />;
}

// ─── Loading fallback ─────────────────────────────────────────────────────────

function PageLoader() {
  return (
    <div className="flex h-screen items-center justify-center bg-slate-50">
      <div className="flex flex-col items-center gap-3">
        <div className="h-10 w-10 animate-spin rounded-full border-4 border-indigo-600 border-t-transparent" />
        <p className="text-sm text-slate-500">Loading…</p>
      </div>
    </div>
  );
}

// ─── App ──────────────────────────────────────────────────────────────────────

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ErrorBoundary>
          <RouteProgressBar />
          <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* ── Public routes ─────────────────────────── */}
            <Route element={<RedirectIfAuth />}>
              <Route path="/login" element={<LoginPage />} />
              <Route path="/forgot-password" element={<ForgotPasswordPage />} />
              <Route path="/reset-password/:token" element={<ResetPasswordPage />} />
            </Route>

            {/* ── Admin routes ──────────────────────────── */}
            <Route
              element={
                <RequireAuth allowedRoles={["super_admin", "school_admin", "accountant"]} />
              }
            >
              <Route path="/admin" element={<AdminLayout />}>
                <Route index element={<AdminDashboard />} />
                <Route path="students" element={<StudentsPage />} />
                <Route path="students/:id" element={<StudentDetailPage />} />
                <Route path="teachers" element={<TeachersPage />} />
                <Route path="classrooms" element={<ClassroomsPage />} />
                <Route path="timetable" element={<TimetablePage />} />
                <Route path="attendance" element={<AttendancePage />} />
                <Route path="exams" element={<ExamsPage />} />
                <Route path="report-cards" element={<ReportCardsPage />} />
                <Route path="announcements" element={<AnnouncementsPage />} />
                <Route path="fees" element={<FeesPage />} />
                <Route path="reports" element={<ReportsPage />} />
                <Route path="settings" element={<SettingsPage />} />
              </Route>
            </Route>

            {/* ── Teacher routes ────────────────────────── */}
            <Route element={<RequireAuth allowedRoles={["teacher"]} />}>
              <Route path="/teacher" element={<TeacherLayout />}>
                <Route index element={<TeacherDashboard />} />
                <Route path="attendance" element={<TeacherAttendance />} />
                <Route path="gradebook" element={<TeacherGradebook />} />
                <Route path="timetable" element={<TeacherTimetable />} />
                <Route path="messages" element={<TeacherMessages />} />
                <Route path="lesson-plans" element={<TeacherLessonPlans />} />
              </Route>
            </Route>

            {/* ── Student routes ────────────────────────── */}
            <Route element={<RequireAuth allowedRoles={["student"]} />}>
              <Route path="/student" element={<StudentLayout />}>
                <Route index element={<StudentDashboard />} />
                <Route path="attendance" element={<StudentAttendance />} />
                <Route path="grades" element={<StudentGrades />} />
                <Route path="timetable" element={<StudentTimetable />} />
                <Route path="messages" element={<StudentMessages />} />
                <Route path="fees" element={<StudentFees />} />
              </Route>
            </Route>

            {/* ── Parent routes ─────────────────────────── */}
            <Route element={<RequireAuth allowedRoles={["parent"]} />}>
              <Route path="/parent" element={<ParentLayout />}>
                <Route index element={<ParentDashboard />} />
                <Route path="children" element={<ParentChildren />} />
                <Route path="attendance" element={<ParentAttendance />} />
                <Route path="grades" element={<ParentGrades />} />
                <Route path="fees" element={<ParentFees />} />
                <Route path="messages" element={<ParentMessages />} />
              </Route>
            </Route>

            {/* ── Fallbacks ─────────────────────────────── */}
            <Route path="/" element={<Navigate to="/login" replace />} />
            {ErrorRoutes}
          </Routes>
        </Suspense>
        </ErrorBoundary>
      </BrowserRouter>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: { borderRadius: "8px", fontSize: "14px" },
          success: { iconTheme: { primary: "#22c55e", secondary: "#fff" } },
          error: { iconTheme: { primary: "#ef4444", secondary: "#fff" } },
        }}
      />
    </QueryClientProvider>
  );
}
