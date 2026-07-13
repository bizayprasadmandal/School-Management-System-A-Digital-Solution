/**
 * TanStack Query hooks — typed data fetching for all SMS modules
 */

import {
  useQuery,
  useMutation,
  useQueryClient,
  keepPreviousData,
} from "@tanstack/react-query";
import { api } from "./client";
import type {
  PaginatedResponse,
  StudentListItem,
  StudentDetail,
  AttendanceSummary,
  ClassroomAttendanceSummary,
  ReportCard,
  Announcement,
  Notification,
  FeeInvoice,
  Payment,
  Classroom,
  GradeLevel,
  Subject,
  TimetableSlot,
  SchoolEvent,
  Exam,
  User,
  AcademicYear,
} from "../types";

// ─── Query Key Factory ─────────────────────────────────────────────────────────

export const QK = {
  students: {
    all: ["students"] as const,
    list: (params?: object) => ["students", "list", params] as const,
    detail: (id: string) => ["students", "detail", id] as const,
    attendance: (id: string, params?: object) => ["students", id, "attendance", params] as const,
    grades: (id: string) => ["students", id, "grades"] as const,
  },
  attendance: {
    classroom: (classroomId: number, date: string) => ["attendance", "classroom", classroomId, date] as const,
    student: (studentId: string, month: number, year: number) => ["attendance", "student", studentId, month, year] as const,
  },
  gradebook: {
    exams: (academicYearId: number) => ["gradebook", "exams", academicYearId] as const,
    grades: (examId: string) => ["gradebook", "grades", examId] as const,
    reportCards: (studentId: string) => ["gradebook", "reportCards", studentId] as const,
  },
  timetable: {
    classroom: (classroomId: number, academicYearId: number) => ["timetable", classroomId, academicYearId] as const,
    teacher: (userId: string) => ["timetable", "teacher", userId] as const,
  },
  communication: {
    announcements: ["announcements"] as const,
    notifications: ["notifications"] as const,
    unreadCount: ["notifications", "unread"] as const,
  },
  fees: {
    invoices: (studentId: string) => ["fees", "invoices", studentId] as const,
  },
  classrooms: {
    all: ["classrooms"] as const,
    list: (params?: object) => ["classrooms", "list", params] as const,
  },
  grades: {
    all: ["grade-levels"] as const,
  },
  academicYears: {
    all: ["academic-years"] as const,
    current: ["academic-years", "current"] as const,
  },
  subjects: {
    byGrade: (gradeId: number) => ["subjects", gradeId] as const,
  },
} as const;

// ─── Students ─────────────────────────────────────────────────────────────────

export function useStudents(params?: {
  search?: string;
  is_active?: boolean;
  gender?: string;
  classroom?: number;
  page?: number;
}) {
  return useQuery({
    queryKey: QK.students.list(params),
    queryFn: () => api.get<PaginatedResponse<StudentListItem>>("/students/", params),
    staleTime: 3 * 60 * 1000,               // 3 min — students may be updated by admin
    placeholderData: keepPreviousData,       // show previous page while navigating
  });
}

export function useStudent(id: string) {
  return useQuery({
    queryKey: QK.students.detail(id),
    queryFn: () => api.get<StudentDetail>(`/students/${id}/`),
    enabled: !!id,
    staleTime: 2 * 60 * 1000,               // 2 min — profile edits by admin
  });
}

export function useCreateStudent() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: FormData) => api.upload<StudentDetail>("/students/", data),
    onSuccess: () => qc.invalidateQueries({ queryKey: QK.students.all }),
  });
}

export function useUpdateStudent(id: string) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<StudentDetail>) => api.patch<StudentDetail>(`/students/${id}/`, data),
    onSuccess: (updated) => {
      qc.setQueryData(QK.students.detail(id), updated);
      qc.invalidateQueries({ queryKey: QK.students.all });
    },
  });
}

export function useStudentAttendanceSummary(
  studentId: string,
  academicYearId?: number
) {
  return useQuery({
    queryKey: QK.students.attendance(studentId, { academic_year: academicYearId }),
    queryFn: () =>
      api.get<AttendanceSummary>(`/students/${studentId}/attendance-summary/`, {
        academic_year: academicYearId,
      }),
    enabled: !!studentId,
    staleTime: 60 * 1000,                   // 1 min — attendance changes daily
    gcTime: 5 * 60 * 1000,                  // keep in cache 5 min for SWR
  });
}

export function usePromoteStudents() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      student_ids: string[];
      target_classroom_id: number;
      academic_year_id: number;
    }) => api.post("/students/promote/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: QK.students.all });
      qc.invalidateQueries({ queryKey: QK.classrooms.all });
    },
  });
}

// ─── Attendance ────────────────────────────────────────────────────────────────

export function useClassroomAttendance(classroomId: number, date: string) {
  return useQuery({
    queryKey: QK.attendance.classroom(classroomId, date),
    queryFn: () =>
      api.get<ClassroomAttendanceSummary>("/attendance/classroom-summary/", {
        classroom_id: classroomId,
        date,
      }),
    enabled: !!classroomId,
    staleTime: 60 * 1000,                   // 1 min — teachers update attendance live
    gcTime: 10 * 60 * 1000,                 // keep stale 10 min
  });
}

export function useStudentMonthlyAttendance(
  studentId: string,
  month: number,
  year: number
) {
  return useQuery({
    queryKey: QK.attendance.student(studentId, month, year),
    queryFn: () =>
      api.get(`/attendance/student-report/`, { student_id: studentId, month, year }),
    enabled: !!studentId,
    staleTime: 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

export function useBulkRecordAttendance() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      classroom_id: number;
      date: string;
      records: Array<{ student_id: string; status: string; remarks?: string }>;
    }) => api.post("/attendance/bulk-record/", data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["attendance"] }),
  });
}

// ─── Gradebook ────────────────────────────────────────────────────────────────

export function useExams(academicYearId: number) {
  return useQuery({
    queryKey: QK.gradebook.exams(academicYearId),
    queryFn: () =>
      api.get<PaginatedResponse<Exam>>("/gradebook/exams/", { academic_year: academicYearId }),
    enabled: !!academicYearId,
    staleTime: 5 * 60 * 1000,               // 5 min
    placeholderData: keepPreviousData,
  });
}

export function useReportCards(studentId: string) {
  return useQuery({
    queryKey: QK.gradebook.reportCards(studentId),
    queryFn: () =>
      api.get<PaginatedResponse<ReportCard>>("/gradebook/report-cards/", { student: studentId }),
    enabled: !!studentId,
    staleTime: 10 * 60 * 1000,              // 10 min — report cards stable once published
  });
}

export function useSubmitGrades() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: {
      exam_schedule_id: number;
      grades: Array<{ student_id: string; marks_obtained: number | null; is_absent: boolean; remarks?: string }>;
    }) => api.post("/gradebook/grades/bulk/", data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["gradebook"] }),
  });
}

export function useGenerateReportCards() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (examId: string) =>
      api.post(`/gradebook/exams/${examId}/generate-report-cards/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["gradebook"] }),
  });
}

// ─── Timetable ────────────────────────────────────────────────────────────────

export function useClassroomTimetable(classroomId: number, academicYearId: number) {
  return useQuery({
    queryKey: QK.timetable.classroom(classroomId, academicYearId),
    queryFn: () =>
      api.get<TimetableSlot[]>("/timetable/slots/", {
        classroom: classroomId,
        academic_year: academicYearId,
      }),
    enabled: !!classroomId && !!academicYearId,
    staleTime: 15 * 60 * 1000,              // 15 min — timetable is semester-stable
  });
}

export function useSchoolEvents() {
  return useQuery({
    queryKey: ["school-events"],
    queryFn: () => api.get<PaginatedResponse<SchoolEvent>>("/timetable/events/"),
    staleTime: 10 * 60 * 1000,               // 10 min
  });
}

// ─── Communication ────────────────────────────────────────────────────────────

export function useAnnouncements() {
  return useQuery({
    queryKey: QK.communication.announcements,
    queryFn: () => api.get<PaginatedResponse<Announcement>>("/communication/announcements/"),
    staleTime: 60 * 1000,                    // 1 min — announcements are time-sensitive
    gcTime: 5 * 60 * 1000,
    refetchInterval: 2 * 60 * 1000,          // poll every 2 min
  });
}

export function useNotifications() {
  return useQuery({
    queryKey: QK.communication.notifications,
    queryFn: () => api.get<PaginatedResponse<Notification>>("/communication/notifications/"),
    refetchInterval: 30_000, // Poll every 30s
  });
}

export function useUnreadNotificationCount() {
  return useQuery({
    queryKey: QK.communication.unreadCount,
    queryFn: () =>
      api
        .get<{ count: number }>("/communication/notifications/unread-count/")
        .then((r) => r.count),
    refetchInterval: 30_000,
  });
}

export function useMarkNotificationRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: string) =>
      api.patch(`/communication/notifications/${id}/mark-read/`, {}),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: QK.communication.notifications });
      qc.invalidateQueries({ queryKey: QK.communication.unreadCount });
    },
  });
}

export function useSendAnnouncement() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<Announcement> & { is_draft: boolean }) =>
      api.post<Announcement>("/communication/announcements/", data),
    onSuccess: () => qc.invalidateQueries({ queryKey: QK.communication.announcements }),
  });
}

// ─── Fees ────────────────────────────────────────────────────────────────────

export function useStudentInvoices(studentId: string) {
  return useQuery({
    queryKey: QK.fees.invoices(studentId),
    queryFn: () =>
      api.get<PaginatedResponse<FeeInvoice>>("/fees/invoices/", { student: studentId }),
    enabled: !!studentId,
    staleTime: 2 * 60 * 1000,                // 2 min — payment status can change
    placeholderData: keepPreviousData,
  });
}

export function useRecordPayment() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: { invoice_id: string; amount: number; payment_method: string }) =>
      api.post<Payment>("/fees/payments/", data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["fees"] }),
  });
}

// ─── Academic Structure ───────────────────────────────────────────────────────

export function useGradeLevels() {
  return useQuery({
    queryKey: QK.grades.all,
    queryFn: () => api.get<PaginatedResponse<GradeLevel>>("/students/grades/"),
    staleTime: 30 * 60 * 1000,               // 30 min — grade levels are static
  });
}

export function useClassrooms(gradeId?: number) {
  return useQuery({
    queryKey: QK.classrooms.list({ grade: gradeId }),
    queryFn: () =>
      api.get<PaginatedResponse<Classroom>>("/students/classrooms/", { grade: gradeId }),
    staleTime: 10 * 60 * 1000,               // 10 min — classrooms change termly
    placeholderData: keepPreviousData,       // keep old list while switching grade filter
  });
}

export function useAcademicYears() {
  return useQuery({
    queryKey: QK.academicYears.all,
    queryFn: () => api.get<PaginatedResponse<AcademicYear>>("/students/academic-years/"),
    staleTime: 30 * 60 * 1000,               // 30 min — academic years are rare-changing
  });
}

export function useCurrentAcademicYear() {
  return useQuery({
    queryKey: QK.academicYears.current,
    queryFn: () =>
      api
        .get<PaginatedResponse<AcademicYear>>("/students/academic-years/", { is_current: true })
        .then((r) => r.results[0] ?? null),
    staleTime: 30 * 60 * 1000,               // 30 min — changes once a year
  });
}

export function useSubjects(gradeId: number) {
  return useQuery({
    queryKey: QK.subjects.byGrade(gradeId),
    queryFn: () =>
      api.get<PaginatedResponse<Subject>>("/academics/subjects/", { grade: gradeId }),
    enabled: !!gradeId,
    staleTime: 30 * 60 * 1000,               // 30 min — subject lists are static
    placeholderData: keepPreviousData,       // keep old subjects while switching grade
  });
}

// ─── User profile ─────────────────────────────────────────────────────────────

export function useProfile() {
  return useQuery({
    queryKey: ["profile"],
    queryFn: () => api.get<User>("/auth/profile/"),
    staleTime: 30 * 60 * 1000,               // 30 min — profile rarely changes
  });
}

export function useUpdateProfile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: Partial<User>) => api.patch<User>("/auth/profile/", data),
    onSuccess: (user) => qc.setQueryData(["profile"], user),
  });
}
