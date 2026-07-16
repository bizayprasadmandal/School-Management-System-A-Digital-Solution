/**
 * useApi — Shared TanStack Query data-fetching hooks for mobile screens.
 *
 * Prefer these hooks over direct useQuery calls for consistent caching,
 * stale times, and error handling across the mobile app.
 */

import { useQuery } from "@tanstack/react-query";
import {
  studentApi,
  attendanceApi,
  gradebookApi,
  communicationApi,
  timetableApi,
  structureApi,
  feesApi,
} from "../services/api";

// ─── Query Key Factory ─────────────────────────────────────────────────────────

export const MQK = {
  student: {
    me: ["mob", "student", "me"] as const,
    dashboard: (id?: string) => ["mob", "student", "dashboard", id] as const,
    attendance: (id: string, month: number, year: number) =>
      ["mob", "student", "attendance", id, month, year] as const,
    grades: (id: string) => ["mob", "student", "grades", id] as const,
  },
  teacher: {
    classrooms: ["mob", "teacher", "classrooms"] as const,
  },
  parent: {
    children: ["mob", "parent", "children"] as const,
  },
  notifications: (limit?: number) => ["mob", "notifications", limit] as const,
  timetable: ["mob", "timetable"] as const,
} as const;

// ─── Student Hooks ────────────────────────────────────────────────────────────

export function useStudentProfile() {
  return useQuery({
    queryKey: MQK.student.me,
    queryFn: () => studentApi.me(),
    staleTime: 5 * 60 * 1000,       // 5 min — profile rarely changes
  });
}

export function useStudentDashboard(studentId?: string) {
  return useQuery({
    queryKey: MQK.student.dashboard(studentId),
    queryFn: () => studentApi.attendanceSummary(studentId!),
    enabled: !!studentId,
    staleTime: 60 * 1000,             // 1 min — attendance changes daily
  });
}

export function useStudentAttendance(
  studentId: string | undefined,
  month: number,
  year: number
) {
  return useQuery({
    queryKey: MQK.student.attendance(studentId ?? "", month, year),
    queryFn: () => attendanceApi.studentReport(studentId!, month, year),
    enabled: !!studentId,
    staleTime: 60 * 1000,
  });
}

export function useStudentReportCards(studentId?: string) {
  return useQuery({
    queryKey: MQK.student.grades(studentId ?? ""),
    queryFn: () => gradebookApi.reportCards(studentId!),
    enabled: !!studentId,
    staleTime: 10 * 60 * 1000,        // 10 min — report cards stable once published
  });
}

// ─── Teacher Hooks ────────────────────────────────────────────────────────────

export function useTeacherClassrooms() {
  return useQuery({
    queryKey: MQK.teacher.classrooms,
    queryFn: () => structureApi.classrooms(),
    staleTime: 10 * 60 * 1000,        // 10 min — classrooms change termly
  });
}

// ─── Parent Hooks ─────────────────────────────────────────────────────────────

export function useParentChildren() {
  return useQuery({
    queryKey: MQK.parent.children,
    queryFn: () => studentApi.list(),
    staleTime: 5 * 60 * 1000,          // 5 min — children list rarely changes
  });
}

// ─── Common Hooks ─────────────────────────────────────────────────────────────

export function useNotifications(limit: number = 5) {
  return useQuery({
    queryKey: MQK.notifications(limit),
    queryFn: () =>
      communicationApi.notifications({
        channel: "in_app",
        page_size: limit,
      }),
    staleTime: 30_000,                  // 30s — notifications are near real-time
    refetchInterval: 60_000,            // 1 min polling as fallback for WebSocket
  });
}

export function useUnreadCount() {
  return useQuery({
    queryKey: ["mob", "unread-count"],
    queryFn: () => communicationApi.unreadCount(),
    staleTime: 30_000,
    refetchInterval: 30_000,
  });
}

export function useUpcomingEvents() {
  return useQuery({
    queryKey: MQK.timetable,
    queryFn: () => timetableApi.upcomingEvents(),
    staleTime: 10 * 60 * 1000,
  });
}
