/**
 * Mobile API Service — Centralized HTTP client with JWT auth, token refresh,
 * and request/response interceptors for the EduSphere mobile app.
 */

import axios, {
  AxiosInstance,
  AxiosError,
  InternalAxiosRequestConfig,
} from "axios";
import { useAuthStore } from "../hooks/useAuthStore";

const API_BASE = process.env.EXPO_PUBLIC_API_URL ?? "http://localhost:8000/api/v1";

/** Axios instance pre-configured with base URL and JSON headers. */
const api: AxiosInstance = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
  timeout: 15_000,
});

// ─── Request interceptor: inject JWT access token ──────────────────────────

api.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const { tokens } = useAuthStore.getState();
    if (tokens?.access) {
      config.headers.Authorization = `Bearer ${tokens.access}`;
    }
    return config;
  },
  (error: AxiosError) => Promise.reject(error),
);

// ─── Response interceptor: auto-refresh on 401 ─────────────────────────────

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

function processQueue(error: unknown, token: string | null = null): void {
  failedQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else if (token) resolve(token);
  });
  failedQueue = [];
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    // Only attempt refresh on 401 and if we haven't already retried
    if (error.response?.status !== 401 || originalRequest._retry) {
      return Promise.reject(error);
    }

    if (isRefreshing) {
      // Queue requests while refresh is in flight
      return new Promise<string>((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then((token) => {
        originalRequest.headers.Authorization = `Bearer ${token}`;
        return api(originalRequest);
      });
    }

    originalRequest._retry = true;
    isRefreshing = true;

    try {
      const { tokens } = useAuthStore.getState();
      if (!tokens?.refresh) {
        throw new Error("No refresh token available");
      }

      const { data } = await axios.post(`${API_BASE}/auth/token/refresh/`, {
        refresh: tokens.refresh,
      });

      const newAccessToken = data.access;
      useAuthStore.getState().setAuth(
        useAuthStore.getState().user,
        { access: newAccessToken, refresh: tokens.refresh },
      );

      processQueue(null, newAccessToken);
      originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
      return api(originalRequest);
    } catch (refreshError) {
      processQueue(refreshError, null);
      useAuthStore.getState().logout();
      return Promise.reject(refreshError);
    } finally {
      isRefreshing = false;
    }
  },
);

// ─── Auth endpoints ──────────────────────────────────────────────────────────

export const authApi = {
  login: (email: string, password: string) =>
    api.post("/auth/login/", { email, password }),

  refresh: (refreshToken: string) =>
    api.post("/auth/token/refresh/", { refresh: refreshToken }),

  logout: (refreshToken: string) =>
    api.post("/auth/logout/", { refresh: refreshToken }),

  me: () => api.get("/auth/me/"),

  updateProfile: (data: Record<string, unknown>) =>
    api.patch("/auth/profile/", data),

  changePassword: (oldPassword: string, newPassword: string) =>
    api.post("/auth/change-password/", {
      old_password: oldPassword,
      new_password: newPassword,
    }),

  setup2FA: () => api.post("/auth/setup-2fa/"),

  verify2FA: (code: string) =>
    api.post("/auth/verify-2fa/", { code }),
};

// ─── Student endpoints ───────────────────────────────────────────────────────

export const studentApi = {
  list: (params?: Record<string, unknown>) =>
    api.get("/students/", { params }),

  detail: (id: string) => api.get(`/students/${id}/`),

  attendanceSummary: (id: string) =>
    api.get(`/students/${id}/attendance-summary/`),

  myDashboard: () => api.get("/students/my-dashboard/"),
};

// ─── Attendance endpoints ────────────────────────────────────────────────────

export const attendanceApi = {
  bulkRecord: (data: Record<string, unknown>) =>
    api.post("/attendance/bulk-record/", data),

  classroomSummary: (classroomId: number, date: string) =>
    api.get("/attendance/classroom-summary/", {
      params: { classroom_id: classroomId, date },
    }),

  studentReport: (studentId: string, month: number, year: number) =>
    api.get("/attendance/student-report/", {
      params: { student_id: studentId, month, year },
    }),

  streak: (studentId: string) =>
    api.get("/attendance/streak/", {
      params: { student_id: studentId },
    }),
};

// ─── Gradebook endpoints ─────────────────────────────────────────────────────

export const gradebookApi = {
  exams: (params?: Record<string, unknown>) =>
    api.get("/gradebook/exams/", { params }),

  grades: (params?: Record<string, unknown>) =>
    api.get("/gradebook/grades/", { params }),

  submitBulk: (data: Record<string, unknown>) =>
    api.post("/gradebook/grades/bulk/", data),

  reportCards: (params?: Record<string, unknown>) =>
    api.get("/gradebook/report-cards/", { params }),

  leaderboard: (examId: string) =>
    api.get(`/gradebook/exams/${examId}/leaderboard/`),
};

// ─── Timetable endpoints ─────────────────────────────────────────────────────

export const timetableApi = {
  slots: (params?: Record<string, unknown>) =>
    api.get("/timetable/slots/", { params }),

  mySchedule: () => api.get("/timetable/my-schedule/"),

  events: (params?: Record<string, unknown>) =>
    api.get("/timetable/events/", { params }),

  upcomingEvents: () => api.get("/timetable/events/upcoming/"),
};

// ─── Communication endpoints ─────────────────────────────────────────────────

export const communicationApi = {
  announcements: (params?: Record<string, unknown>) =>
    api.get("/communication/announcements/", { params }),

  notifications: (params?: Record<string, unknown>) =>
    api.get("/communication/notifications/", { params }),

  unreadCount: () => api.get("/communication/notifications/unread-count/"),

  markAllRead: () => api.post("/communication/notifications/mark-all-read/"),

  messages: (params?: Record<string, unknown>) =>
    api.get("/communication/messages/", { params }),

  sendMessage: (recipient: string, content: string) =>
    api.post("/communication/messages/", { recipient, content }),

  conversation: (userId: string) =>
    api.get(`/communication/messages/conversation/${userId}/`),

  inbox: () => api.get("/communication/messages/inbox/"),
};

// ─── Fees endpoints ──────────────────────────────────────────────────────────

export const feesApi = {
  invoices: (params?: Record<string, unknown>) =>
    api.get("/fees/invoices/", { params }),

  payments: (params?: Record<string, unknown>) =>
    api.get("/fees/payments/", { params }),

  recordPayment: (data: Record<string, unknown>) =>
    api.post("/fees/payments/", data),
};

// ─── Dashboard endpoints ─────────────────────────────────────────────────────

export const dashboardApi = {
  stats: () => api.get("/reporting/dashboard-stats/"),
};

export default api;
