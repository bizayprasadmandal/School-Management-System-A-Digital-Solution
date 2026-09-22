/**
 * App.tsx — Root router with role-based layout switching
 */

import React, { Suspense } from "react";
import * as Sentry from "@sentry/react";
import { BrowserRouter, Routes, Route, Navigate, Outlet } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "react-hot-toast";
import { useAuthStore } from "./store/authStore";
import { ErrorBoundary } from "./components/common/ErrorBoundary";
import RouteProgressBar from "./components/common/RouteProgressBar";
import NotificationWebSocketSync from "./components/common/NotificationWebSocketSync";
import type { UserRole } from "./types";

// Lazy-loaded layouts
const AdminLayout = React.lazy(() => import("./components/layout/AdminLayout"));
const TeacherLayout = React.lazy(() => import("./components/layout/TeacherLayout"));
const StudentLayout = React.lazy(() => import("./components/layout/StudentLayout"));
const ParentLayout = React.lazy(() => import("./components/layout/ParentLayout"));
const AccountantLayout = React.lazy(() => import("./components/layout/AccountantLayout"));
const LibrarianLayout = React.lazy(() => import("./components/layout/LibrarianLayout"));
const CounselorLayout = React.lazy(() => import("./components/layout/CounselorLayout"));

// Auth pages
const LoginPage = React.lazy(() => import("./pages/auth/LoginPage"));
const ForgotPasswordPage = React.lazy(() => import("./pages/auth/ForgotPasswordPage"));
const ResetPasswordPage = React.lazy(() => import("./pages/auth/ResetPasswordPage"));
const VerifyEmailPage = React.lazy(() => import("./pages/auth/VerifyEmailPage"));
const Verify2FALoginPage = React.lazy(() => import("./pages/auth/Verify2FALoginPage"));

// Admin pages
const AdminDashboard = React.lazy(() => import("./pages/admin/Dashboard"));
const PlatformDashboard = React.lazy(() => import("./pages/admin/PlatformDashboard"));
const PlatformSchoolsPage = React.lazy(() => import("./pages/admin/PlatformSchoolsPage"));
const PlatformSchoolDetail = React.lazy(() => import("./pages/admin/PlatformSchoolDetailPage"));
const PlatformRevenuePage = React.lazy(() => import("./pages/admin/PlatformRevenuePage"));
const PlatformAuditPage = React.lazy(() => import("./pages/admin/PlatformAuditPage"));
const StudentsPage = React.lazy(() => import("./pages/admin/StudentsPage"));
const StudentDetailPage = React.lazy(() => import("./pages/admin/StudentDetailPage"));
const TeachersPage = React.lazy(() => import("./pages/admin/TeachersPage"));
const ClassroomsPage = React.lazy(() => import("./pages/admin/ClassroomsPage"));
const TimetablePage = React.lazy(() => import("./pages/admin/TimetablePage"));
const AttendancePage = React.lazy(() => import("./pages/admin/AttendancePage"));
const ExamsPage = React.lazy(() => import("./pages/admin/ExamsPage"));
const ReportCardsPage = React.lazy(() => import("./pages/admin/ReportCardsPage"));
const AcademicsPage = React.lazy(() => import("./pages/admin/AcademicsPage"));
const AnnouncementsPage = React.lazy(() => import("./pages/admin/AnnouncementsPage"));
const FeesPage = React.lazy(() => import("./pages/admin/FeesPage"));
const SettingsPage = React.lazy(() => import("./pages/admin/SettingsPage"));
const PlanBillingPage = React.lazy(() => import("./pages/admin/PlanBillingPage"));
const ZoomIntegrationPage = React.lazy(() => import("./pages/admin/ZoomIntegrationPage"));
const ReportsPage = React.lazy(() => import("./pages/admin/ReportsPage"));
const EventsCalendarPage = React.lazy(() => import("./pages/admin/EventsCalendarPage"));
const BehaviorPage = React.lazy(() => import("./pages/admin/BehaviorPage"));
const LibraryPage = React.lazy(() => import("./pages/admin/LibraryPage"));
const AdminConferences = React.lazy(() => import("./pages/admin/ConferencesPage"));
const BulkMessagesPage = React.lazy(() => import("./pages/admin/BulkMessagesPage"));
const AuditLogsPage = React.lazy(() => import("./pages/admin/AuditLogsPage"));
const HRPage = React.lazy(() => import("./pages/admin/HRPage"));
const TransportationPage = React.lazy(() => import("./pages/admin/TransportationPage"));
const InventoryPage = React.lazy(() => import("./pages/admin/InventoryPage"));
const HostelPage = React.lazy(() => import("./pages/admin/HostelPage"));
const SportsPage = React.lazy(() => import("./pages/admin/SportsPage"));
const HealthPage = React.lazy(() => import("./pages/admin/HealthPage"));
const AlumniPage = React.lazy(() => import("./pages/admin/AlumniPage"));
const CounselingCenterPage = React.lazy(() => import("./pages/admin/CounselingCenterPage"));
const StudentRecordsPage = React.lazy(() => import("./pages/admin/StudentRecordsPage"));
const ReportingCenterPage = React.lazy(() => import("./pages/admin/ReportingCenterPage"));
const HRCenterPage = React.lazy(() => import("./pages/admin/HRCenterPage"));
const GradebookCenterPage = React.lazy(() => import("./pages/admin/GradebookCenterPage"));
const TransportationCenterPage = React.lazy(() => import("./pages/admin/TransportationCenterPage"));
const HostelCenterPage = React.lazy(() => import("./pages/admin/HostelCenterPage"));
const InventoryCenterPage = React.lazy(() => import("./pages/admin/InventoryCenterPage"));
const AdmissionsCenterPage = React.lazy(() => import("./pages/admin/AdmissionsCenterPage"));
const AttendanceCenterPage = React.lazy(() => import("./pages/admin/AttendanceCenterPage"));
const ConferencesCenterPage = React.lazy(() => import("./pages/admin/ConferencesCenterPage"));
const AuthCenterPage = React.lazy(() => import("./pages/admin/AuthCenterPage"));
const FeesCenterPage = React.lazy(() => import("./pages/admin/FeesCenterPage"));
const CafeteriaPage = React.lazy(() => import("./pages/admin/CafeteriaPage"));
const AdmissionsPage = React.lazy(() => import("./pages/admin/AdmissionsPage"));
const InfrastructurePage = React.lazy(() => import("./pages/admin/InfrastructurePage"));
const AccessControlPage = React.lazy(() => import("./pages/admin/AccessControlPage"));
const AccountSecurityPage = React.lazy(() => import("./pages/admin/AccountSecurityPage"));
const CommunicationPage = React.lazy(() => import("./pages/admin/CommunicationPage"));

// Teacher pages
const TeacherDashboard = React.lazy(() => import("./pages/teacher/Dashboard"));
const TeacherAttendance = React.lazy(() => import("./pages/teacher/AttendancePage"));
const TeacherGradebook = React.lazy(() => import("./pages/teacher/GradebookPage"));
const TeacherAssignments = React.lazy(() => import("./pages/teacher/AssignmentsPage"));
const TeacherTimetable = React.lazy(() => import("./pages/teacher/TimetablePage"));
const TeacherMessages = React.lazy(() => import("./pages/teacher/MessagesPage"));
const TeacherLessonPlans = React.lazy(() => import("./pages/teacher/LessonPlansPage"));
const TeacherConferences = React.lazy(() => import("./pages/teacher/ConferencesPage"));
const TeacherSettings = React.lazy(() => import("./pages/teacher/SettingsPage"));
const TeacherHealth = React.lazy(() => import("./pages/teacher/HealthPage"));
const TeacherLibrary = React.lazy(() => import("./pages/teacher/LibraryPage"));
const TeacherSports = React.lazy(() => import("./pages/teacher/SportsPage"));
const TeacherBehavior = React.lazy(() => import("./pages/teacher/BehaviorPage"));
const TeacherCounseling = React.lazy(() => import("./pages/teacher/CounselingPage"));
const TeacherMyPayslips = React.lazy(() => import("./pages/teacher/MyPayslipsPage"));

// Shared pages
const VerifyEmailSettingsPage = React.lazy(() => import("./pages/shared/VerifyEmailSettingsPage"));
const Setup2FAPage = React.lazy(() => import("./pages/shared/Setup2FAPage"));

// Public pages (no auth required)
const PublicApplyPage = React.lazy(() => import("./pages/public/PublicApplyPage"));
const PublicStatusPage = React.lazy(() => import("./pages/public/PublicStatusPage"));

import { ErrorRoutes } from "./config/errorRoutes";

// Student pages
const StudentDashboard = React.lazy(() => import("./pages/student/Dashboard"));
const StudentAttendance = React.lazy(() => import("./pages/student/AttendancePage"));
const StudentGrades = React.lazy(() => import("./pages/student/GradesPage"));
const StudentAssignments = React.lazy(() => import("./pages/student/AssignmentsPage"));
const StudentTimetable = React.lazy(() => import("./pages/student/TimetablePage"));
const StudentMessages = React.lazy(() => import("./pages/student/MessagesPage"));
const StudentFees = React.lazy(() => import("./pages/student/FeesPage"));
const StudentConferences = React.lazy(() => import("./pages/student/ConferencesPage"));
const StudentSettings = React.lazy(() => import("./pages/student/SettingsPage"));
const StudentHealth = React.lazy(() => import("./pages/student/HealthPage"));
const StudentLibrary = React.lazy(() => import("./pages/student/LibraryPage"));
const StudentCafeteria = React.lazy(() => import("./pages/student/CafeteriaPage"));
const StudentSports = React.lazy(() => import("./pages/student/SportsPage"));
const StudentBehavior = React.lazy(() => import("./pages/student/BehaviorPage"));
const StudentCounseling = React.lazy(() => import("./pages/student/CounselingPage"));
const StudentHostel = React.lazy(() => import("./pages/student/HostelPage"));
const StudentTransport = React.lazy(() => import("./pages/student/TransportPage"));

// Payment callback page
const PaymentCallbackPage = React.lazy(() => import("./pages/fees/PaymentCallbackPage"));

// Accountant pages
const AccountantDashboard = React.lazy(() => import("./pages/accountant/Dashboard"));
const AccountantFeeReports = React.lazy(() => import("./pages/accountant/FeeReportsPage"));
const AccountantPaymentHistory = React.lazy(() => import("./pages/accountant/PaymentHistoryPage"));
const AccountantRefundManagement = React.lazy(
  () => import("./pages/accountant/RefundManagementPage"),
);
const AccountantSettings = React.lazy(() => import("./pages/accountant/SettingsPage"));
const AccountantBudget = React.lazy(() => import("./pages/accountant/BudgetPage"));
const AccountantPurchaseOrders = React.lazy(() => import("./pages/accountant/PurchaseOrdersPage"));
const AccountantInvoices = React.lazy(() => import("./pages/accountant/InvoicesPage"));

// Librarian pages
const LibrarianDashboard = React.lazy(() => import("./pages/librarian/Dashboard"));
const LibrarianBooks = React.lazy(() => import("./pages/librarian/BookManagementPage"));
const LibrarianCheckouts = React.lazy(() => import("./pages/librarian/BookCheckoutPage"));
const LibrarianFines = React.lazy(() => import("./pages/librarian/FinesPage"));
const LibrarianSettings = React.lazy(() => import("./pages/librarian/SettingsPage"));
const LibrarianBookClubs = React.lazy(() => import("./pages/librarian/BookClubsPage"));
const LibrarianAcquisitions = React.lazy(() => import("./pages/librarian/AcquisitionsPage"));
const LibrarianReadingLists = React.lazy(() => import("./pages/librarian/ReadingListsPage"));

// Counselor pages
const CounselorDashboard = React.lazy(() => import("./pages/counselor/Dashboard"));
const CounselorAppointmentsPage = React.lazy(
  () => import("./pages/counselor/CounselorAppointmentsPage"),
);
const CounselorReferralsPage = React.lazy(() => import("./pages/counselor/CounselorReferralsPage"));
const CounselorSurveysPage = React.lazy(() => import("./pages/counselor/SurveysPage"));
const CounselorWorkshopsPage = React.lazy(() => import("./pages/counselor/WorkshopsPage"));
const CounselorSELPage = React.lazy(() => import("./pages/counselor/SELPage"));
const CounselorPeerMentoringPage = React.lazy(() => import("./pages/counselor/PeerMentoringPage"));
const CounselorSettings = React.lazy(() => import("./pages/counselor/SettingsPage"));

// Parent pages
const ParentDashboard = React.lazy(() => import("./pages/parent/Dashboard"));
const ParentChildren = React.lazy(() => import("./pages/parent/ChildrenPage"));
const ParentAttendance = React.lazy(() => import("./pages/parent/AttendancePage"));
const ParentGrades = React.lazy(() => import("./pages/parent/GradesPage"));
const ParentFees = React.lazy(() => import("./pages/parent/FeesPage"));
const ParentMessages = React.lazy(() => import("./pages/parent/MessagesPage"));
const ParentSettings = React.lazy(() => import("./pages/parent/SettingsPage"));
const ParentHealth = React.lazy(() => import("./pages/parent/HealthPage"));
const ParentLibrary = React.lazy(() => import("./pages/parent/LibraryPage"));
const ParentCafeteria = React.lazy(() => import("./pages/parent/CafeteriaPage"));
const ParentSports = React.lazy(() => import("./pages/parent/SportsPage"));
const ParentBehavior = React.lazy(() => import("./pages/parent/BehaviorPage"));
const ParentCounseling = React.lazy(() => import("./pages/parent/CounselingPage"));
const ParentConferences = React.lazy(() => import("./pages/parent/ConferencesPage"));

// ─── React Query client ───────────────────────────────────────────────────────

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 min — per-query overrides below
      gcTime: 30 * 60 * 1000, // keep stale data 30 min for SWR
      retry: 1,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true, // revalidate after network comes back
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

  // Unverified users stay on the login page so the verification banner (with
  // its resend action) can prompt them — LoginPage deliberately returns without
  // navigating when email_verified is false. Only verified sessions redirect
  // to their role dashboard.
  if (user && !user.email_verified) return <Outlet />;

  const role = user?.role;
  if (role === "school_admin" || role === "super_admin") return <Navigate to="/admin" replace />;
  if (role === "teacher") return <Navigate to="/teacher" replace />;
  if (role === "student") return <Navigate to="/student" replace />;
  if (role === "parent") return <Navigate to="/parent" replace />;
  if (role === "accountant") return <Navigate to="/accountant" replace />;
  if (role === "librarian") return <Navigate to="/librarian" replace />;
  if (role === "counselor") return <Navigate to="/counselor" replace />;
  return <Navigate to="/login" replace />;
}

/**
 * Admin index — super admins (who have no school of their own) land on the
 * cross-school Platform Dashboard; school admins get the school dashboard.
 */
function AdminIndex() {
  const { user } = useAuthStore();
  return user?.role === "super_admin" ? <PlatformDashboard /> : <AdminDashboard />;
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

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <NotificationWebSocketSync />
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

              {/* ── Email verification (public, no auth needed) ── */}
              {/* Token-less /verify-email renders the missing-token error state
                instead of falling through to a blank page. */}
              <Route path="/verify-email" element={<VerifyEmailPage />} />
              <Route path="/verify-email/:token" element={<VerifyEmailPage />} />

              {/* ── Payment callback (public — receives gateway redirect) ── */}
              <Route path="/fees/callback" element={<PaymentCallbackPage />} />

              {/* ── Public admissions portal (no auth required) ── */}
              <Route path="/apply" element={<PublicApplyPage />} />
              <Route path="/apply/status" element={<PublicStatusPage />} />

              {/* ── 2FA verification (step 2 of login, no auth yet) ── */}
              <Route path="/verify-2fa" element={<Verify2FALoginPage />} />

              {/* ── Admin routes ──────────────────────────── */}
              <Route element={<RequireAuth allowedRoles={["super_admin", "school_admin"]} />}>
                <Route path="/admin" element={<AdminLayout />}>
                  <Route index element={<AdminIndex />} />
                  <Route path="students" element={<StudentsPage />} />
                  <Route path="student-records" element={<StudentRecordsPage />} />
                  <Route path="reporting-center" element={<ReportingCenterPage />} />
                  <Route path="conferences-center" element={<ConferencesCenterPage />} />
                  <Route path="security-center" element={<AuthCenterPage />} />
                  <Route path="finance-center" element={<FeesCenterPage />} />
                  <Route path="students/:id" element={<StudentDetailPage />} />
                  <Route path="teachers" element={<TeachersPage />} />
                  <Route path="classrooms" element={<ClassroomsPage />} />
                  <Route path="timetable" element={<TimetablePage />} />
                  <Route path="attendance" element={<AttendancePage />} />
                  <Route path="exams" element={<ExamsPage />} />
                  <Route path="assignments" element={<TeacherAssignments />} />
                  <Route path="report-cards" element={<ReportCardsPage />} />
                  <Route path="academics" element={<AcademicsPage />} />
                  <Route path="announcements" element={<AnnouncementsPage />} />
                  <Route path="fees" element={<FeesPage />} />
                  <Route path="reports" element={<ReportsPage />} />
                  <Route path="verify-email" element={<VerifyEmailSettingsPage />} />
                  <Route path="setup-2fa" element={<Setup2FAPage />} />
                  <Route path="events" element={<EventsCalendarPage />} />
                  <Route path="behavior" element={<BehaviorPage />} />
                  <Route path="library" element={<LibraryPage />} />
                  <Route path="conferences" element={<AdminConferences />} />
                  <Route path="bulk-messages" element={<BulkMessagesPage />} />
                  <Route path="hr" element={<HRPage />} />
                  <Route path="hr-center" element={<HRCenterPage />} />
                  <Route path="gradebook-center" element={<GradebookCenterPage />} />
                  <Route path="transportation-center" element={<TransportationCenterPage />} />
                  <Route path="hostel-center" element={<HostelCenterPage />} />
                  <Route path="inventory-center" element={<InventoryCenterPage />} />
                  <Route path="admissions-center" element={<AdmissionsCenterPage />} />
                  <Route path="attendance-center" element={<AttendanceCenterPage />} />
                  <Route path="transport" element={<TransportationPage />} />
                  <Route path="inventory" element={<InventoryPage />} />
                  <Route path="hostel" element={<HostelPage />} />
                  <Route path="sports" element={<SportsPage />} />
                  <Route path="health" element={<HealthPage />} />
                  <Route path="alumni" element={<AlumniPage />} />
                  <Route path="counseling" element={<CounselingCenterPage />} />
                  <Route path="cafeteria" element={<CafeteriaPage />} />
                  <Route path="admissions" element={<AdmissionsPage />} />
                  <Route path="infrastructure" element={<InfrastructurePage />} />
                  <Route path="audit-logs" element={<AuditLogsPage />} />
                  <Route path="access-control" element={<AccessControlPage />} />
                  <Route path="account-security" element={<AccountSecurityPage />} />
                  <Route path="communication" element={<CommunicationPage />} />
                  <Route path="zoom-integration" element={<ZoomIntegrationPage />} />
                  {/* Platform Management (super admin only) */}
                  <Route path="platform" element={<PlatformDashboard />} />
                  <Route path="platform/schools" element={<PlatformSchoolsPage />} />
                  <Route path="platform/schools/:id" element={<PlatformSchoolDetail />} />
                  <Route path="platform/revenue" element={<PlatformRevenuePage />} />
                  <Route path="platform/audit" element={<PlatformAuditPage />} />
                  <Route path="settings" element={<SettingsPage />} />
                  <Route path="plan-billing" element={<PlanBillingPage />} />
                </Route>
              </Route>

              {/* ── Teacher routes ────────────────────────── */}
              <Route element={<RequireAuth allowedRoles={["teacher"]} />}>
                <Route path="/teacher" element={<TeacherLayout />}>
                  <Route index element={<TeacherDashboard />} />
                  <Route path="attendance" element={<TeacherAttendance />} />
                  <Route path="gradebook" element={<TeacherGradebook />} />
                  <Route path="assignments" element={<TeacherAssignments />} />
                  <Route path="timetable" element={<TeacherTimetable />} />
                  <Route path="messages" element={<TeacherMessages />} />
                  <Route path="verify-email" element={<VerifyEmailSettingsPage />} />
                  <Route path="setup-2fa" element={<Setup2FAPage />} />
                  <Route path="lesson-plans" element={<TeacherLessonPlans />} />
                  <Route path="conferences" element={<TeacherConferences />} />
                  <Route path="settings" element={<TeacherSettings />} />
                  <Route path="health" element={<TeacherHealth />} />
                  <Route path="library" element={<TeacherLibrary />} />
                  <Route path="sports" element={<TeacherSports />} />
                  <Route path="behavior" element={<TeacherBehavior />} />
                  <Route path="counseling" element={<TeacherCounseling />} />
                  <Route path="my-payslips" element={<TeacherMyPayslips />} />
                </Route>
              </Route>

              {/* ── Student routes ────────────────────────── */}
              <Route element={<RequireAuth allowedRoles={["student"]} />}>
                <Route path="/student" element={<StudentLayout />}>
                  <Route index element={<StudentDashboard />} />
                  <Route path="attendance" element={<StudentAttendance />} />
                  <Route path="grades" element={<StudentGrades />} />
                  <Route path="assignments" element={<StudentAssignments />} />
                  <Route path="timetable" element={<StudentTimetable />} />
                  <Route path="messages" element={<StudentMessages />} />
                  <Route path="verify-email" element={<VerifyEmailSettingsPage />} />
                  <Route path="setup-2fa" element={<Setup2FAPage />} />
                  <Route path="fees" element={<StudentFees />} />
                  <Route path="conferences" element={<StudentConferences />} />
                  <Route path="settings" element={<StudentSettings />} />
                  <Route path="health" element={<StudentHealth />} />
                  <Route path="library" element={<StudentLibrary />} />
                  <Route path="cafeteria" element={<StudentCafeteria />} />
                  <Route path="sports" element={<StudentSports />} />
                  <Route path="behavior" element={<StudentBehavior />} />
                  <Route path="counseling" element={<StudentCounseling />} />
                  <Route path="hostel" element={<StudentHostel />} />
                  <Route path="transport" element={<StudentTransport />} />
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
                  <Route path="verify-email" element={<VerifyEmailSettingsPage />} />
                  <Route path="setup-2fa" element={<Setup2FAPage />} />
                  <Route path="messages" element={<ParentMessages />} />
                  <Route path="conferences" element={<ParentConferences />} />
                  <Route path="settings" element={<ParentSettings />} />
                  <Route path="health" element={<ParentHealth />} />
                  <Route path="library" element={<ParentLibrary />} />
                  <Route path="cafeteria" element={<ParentCafeteria />} />
                  <Route path="sports" element={<ParentSports />} />
                  <Route path="behavior" element={<ParentBehavior />} />
                  <Route path="counseling" element={<ParentCounseling />} />
                </Route>
              </Route>

              {/* ── Accountant routes ──────────────────────── */}
              <Route element={<RequireAuth allowedRoles={["accountant"]} />}>
                <Route path="/accountant" element={<AccountantLayout />}>
                  <Route index element={<AccountantDashboard />} />
                  <Route path="fees" element={<FeesPage />} />
                  <Route path="payments" element={<AccountantPaymentHistory />} />
                  <Route path="refunds" element={<AccountantRefundManagement />} />
                  <Route path="reports" element={<AccountantFeeReports />} />
                  <Route path="conferences" element={<AdminConferences />} />
                  <Route path="verify-email" element={<VerifyEmailSettingsPage />} />
                  <Route path="setup-2fa" element={<Setup2FAPage />} />
                  <Route path="budget" element={<AccountantBudget />} />
                  <Route path="purchase-orders" element={<AccountantPurchaseOrders />} />
                  <Route path="invoices" element={<AccountantInvoices />} />
                  <Route path="settings" element={<AccountantSettings />} />
                </Route>
              </Route>

              {/* ── Librarian routes ───────────────────────── */}
              <Route element={<RequireAuth allowedRoles={["librarian"]} />}>
                <Route path="/librarian" element={<LibrarianLayout />}>
                  <Route index element={<LibrarianDashboard />} />
                  <Route path="books" element={<LibrarianBooks />} />
                  <Route path="checkouts" element={<LibrarianCheckouts />} />
                  <Route path="fines" element={<LibrarianFines />} />
                  <Route path="library" element={<LibraryPage />} />
                  <Route path="announcements" element={<AnnouncementsPage />} />
                  <Route path="verify-email" element={<VerifyEmailSettingsPage />} />
                  <Route path="setup-2fa" element={<Setup2FAPage />} />
                  <Route path="book-clubs" element={<LibrarianBookClubs />} />
                  <Route path="reading-lists" element={<LibrarianReadingLists />} />
                  <Route path="acquisitions" element={<LibrarianAcquisitions />} />
                  <Route path="settings" element={<LibrarianSettings />} />
                </Route>
              </Route>

              {/* ── Counselor routes ───────────────────────── */}
              <Route element={<RequireAuth allowedRoles={["counselor"]} />}>
                <Route path="/counselor" element={<CounselorLayout />}>
                  <Route index element={<CounselorDashboard />} />
                  <Route path="appointments" element={<CounselorAppointmentsPage />} />
                  <Route path="referrals" element={<CounselorReferralsPage />} />
                  <Route path="surveys" element={<CounselorSurveysPage />} />
                  <Route path="workshops" element={<CounselorWorkshopsPage />} />
                  <Route path="sel" element={<CounselorSELPage />} />
                  <Route path="peer-mentoring" element={<CounselorPeerMentoringPage />} />
                  <Route path="behavior" element={<BehaviorPage />} />
                  <Route path="announcements" element={<AnnouncementsPage />} />
                  <Route path="verify-email" element={<VerifyEmailSettingsPage />} />
                  <Route path="setup-2fa" element={<Setup2FAPage />} />
                  <Route path="settings" element={<CounselorSettings />} />
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

const SentryApp = Sentry.withProfiler(App);
export default SentryApp;
