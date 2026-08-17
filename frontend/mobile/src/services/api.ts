/**
 * Mobile API Service — Unifies the HTTP client from api/client.ts with
 * organized, typed endpoint modules for every SMS backend service.
 *
 * Screens should import from this file instead of making raw endpoint calls.
 *
 * Usage:
 *   import { mobileApi, studentApi, attendanceApi } from "../../services/api";
 *   const { data } = await studentApi.me();
 *   const { data } = await attendanceApi.studentReport(id, month, year);
 */

// Re-export the typed HTTP helper (mobileApi.get / post / patch / etc.)
// This is the same instance from api/client.ts with JWT interceptors + refresh.
export { mobileApi, mobileApiClient } from "../api/client";

import { mobileApiClient } from "../api/client";

// ─── Auth ─────────────────────────────────────────────────────────────────────

export const authApi = {
  login: (email: string, password: string) =>
    mobileApiClient.post("/auth/login/", { email, password }).then((r) => r.data),

  me: () => mobileApiClient.get("/auth/me/").then((r) => r.data),

  profile: () => mobileApiClient.get("/auth/profile/").then((r) => r.data),

  updateProfile: (data: Record<string, unknown>) =>
    mobileApiClient.patch("/auth/profile/", data).then((r) => r.data),

  changePassword: (oldPassword: string, newPassword: string) =>
    mobileApiClient
      .post("/auth/change-password/", { old_password: oldPassword, new_password: newPassword })
      .then((r) => r.data),
};

// ─── Students ─────────────────────────────────────────────────────────────────

export const studentApi = {
  me: () => mobileApiClient.get("/students/me/").then((r) => r.data),

  list: (params?: Record<string, unknown>) =>
    mobileApiClient.get("/students/", { params }).then((r) => r.data),

  detail: (id: string) => mobileApiClient.get(`/students/${id}/`).then((r) => r.data),

  attendanceSummary: (id: string, academicYearId?: number) =>
    mobileApiClient
      .get(`/students/${id}/attendance-summary/`, {
        params: { academic_year: academicYearId },
      })
      .then((r) => r.data),
};

// ─── Attendance ───────────────────────────────────────────────────────────────

export const attendanceApi = {
  studentReport: (studentId: string, month: number, year: number) =>
    mobileApiClient
      .get("/attendance/student-report/", {
        params: { student_id: studentId, month, year },
      })
      .then((r) => r.data),

  classroomSummary: (classroomId: number, date: string) =>
    mobileApiClient
      .get("/attendance/classroom-summary/", {
        params: { classroom_id: classroomId, date },
      })
      .then((r) => r.data),

  streak: (studentId: string) =>
    mobileApiClient
      .get("/attendance/streak/", { params: { student_id: studentId } })
      .then((r) => r.data),
};

// ─── Gradebook ────────────────────────────────────────────────────────────────

export const gradebookApi = {
  reportCards: (studentId: string) =>
    mobileApiClient
      .get("/gradebook/report-cards/", { params: { student: studentId } })
      .then((r) => r.data),

  exams: (params?: Record<string, unknown>) =>
    mobileApiClient.get("/gradebook/exams/", { params }).then((r) => r.data),

  leaderboard: (examId: string) =>
    mobileApiClient.get(`/gradebook/exams/${examId}/leaderboard/`).then((r) => r.data),
};

// ─── Timetable ────────────────────────────────────────────────────────────────

export const timetableApi = {
  mySchedule: () => mobileApiClient.get("/timetable/my-schedule/").then((r) => r.data),

  events: (params?: Record<string, unknown>) =>
    mobileApiClient.get("/timetable/events/", { params }).then((r) => r.data),

  upcomingEvents: () => mobileApiClient.get("/timetable/events/upcoming/").then((r) => r.data),
};

// ─── Communication ────────────────────────────────────────────────────────────

export const communicationApi = {
  notifications: (params?: Record<string, unknown>) =>
    mobileApiClient.get("/communication/notifications/", { params }).then((r) => r.data),

  unreadCount: () =>
    mobileApiClient.get("/communication/notifications/unread-count/").then((r) => r.data),

  markAllRead: () =>
    mobileApiClient.post("/communication/notifications/mark-all-read/").then((r) => r.data),

  inbox: () => mobileApiClient.get("/communication/messages/inbox/").then((r) => r.data),

  conversation: (userId: string) =>
    mobileApiClient.get(`/communication/messages/conversation/${userId}/`).then((r) => r.data),
};

// ─── Fees ─────────────────────────────────────────────────────────────────────

export const feesApi = {
  invoices: (studentId: string) =>
    mobileApiClient.get("/fees/invoices/", { params: { student: studentId } }).then((r) => r.data),
};

// ─── Classrooms / Structure ──────────────────────────────────────────────────

export const structureApi = {
  classrooms: (params?: Record<string, unknown>) =>
    mobileApiClient.get("/students/classrooms/", { params }).then((r) => r.data),
};

// ─── Library ──────────────────────────────────────────────────────────────────

export const libraryApi = {
  books: (params?: Record<string, unknown>) =>
    mobileApiClient.get("/library/books/", { params }).then((r) => r.data),
};

// ─── Counseling ───────────────────────────────────────────────────────────────

export const counselingApi = {
  dashboardStats: () => mobileApiClient.get("/counseling/dashboard/stats/").then((r) => r.data),

  appointments: (params?: Record<string, unknown>) =>
    mobileApiClient.get("/counseling/appointments/", { params }).then((r) => r.data),

  referrals: (params?: Record<string, unknown>) =>
    mobileApiClient.get("/counseling/referrals/", { params }).then((r) => r.data),
};
