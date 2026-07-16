/**
 * Axios API Client — JWT refresh interceptor, base URL, error normalization
 */

import axios, { AxiosError, type InternalAxiosRequestConfig } from "axios";
import { useAuthStore } from "../store/authStore";

const BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1";

export const apiClient = axios.create({
  baseURL: BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 30_000,
});

// ─── Request interceptor — attach JWT ─────────────────────────────────────────

apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const tokens = useAuthStore.getState().tokens;
    if (tokens?.access) {
      config.headers.Authorization = `Bearer ${tokens.access}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ─── Response interceptor — token refresh ─────────────────────────────────────

let isRefreshing = false;
let refreshQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  refreshQueue.forEach(({ resolve, reject }) => {
    if (error) reject(error);
    else resolve(token!);
  });
  refreshQueue = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config as InternalAxiosRequestConfig & {
      _retry?: boolean;
    };

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        // Queue the request until refresh completes
        return new Promise((resolve, reject) => {
          refreshQueue.push({
            resolve: (token) => {
              originalRequest.headers.Authorization = `Bearer ${token}`;
              resolve(apiClient(originalRequest));
            },
            reject,
          });
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = useAuthStore.getState().tokens?.refresh;
      if (!refreshToken) {
        useAuthStore.getState().logout();
        return Promise.reject(error);
      }

      try {
        const { data } = await axios.post(`${BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });
        const newTokens = {
          access: data.access,
          refresh: data.refresh || refreshToken,
        };
        useAuthStore.getState().setTokens(newTokens);
        processQueue(null, data.access);
        originalRequest.headers.Authorization = `Bearer ${data.access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        useAuthStore.getState().logout();
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(normalizeError(error));
  }
);

// ─── Error normalization ───────────────────────────────────────────────────────

export interface NormalizedError {
  message: string;
  fieldErrors?: Record<string, string[]>;
  status?: number;
}

function normalizeError(error: AxiosError): NormalizedError {
  const status = error.response?.status;
  const data = error.response?.data as Record<string, unknown> | undefined;

  if (!data) {
    return { message: "Network error — please check your connection.", status };
  }

  if (data.detail && typeof data.detail === "string") {
    return { message: data.detail, status };
  }

  // DRF field-level errors
  const fieldErrors: Record<string, string[]> = {};
  let hasFieldErrors = false;
  for (const [key, val] of Object.entries(data)) {
    if (Array.isArray(val)) {
      fieldErrors[key] = val as string[];
      hasFieldErrors = true;
    }
  }

  if (hasFieldErrors) {
    return {
      message: "Please correct the errors below.",
      fieldErrors,
      status,
    };
  }

  return { message: "An unexpected error occurred.", status };
}

// ─── Typed helpers ─────────────────────────────────────────────────────────────

export const api = {
  get: <T>(url: string, params?: object) =>
    apiClient.get<T>(url, { params }).then((r) => r.data),

  post: <T>(url: string, data?: unknown) =>
    apiClient.post<T>(url, data).then((r) => r.data),

  patch: <T>(url: string, data?: unknown) =>
    apiClient.patch<T>(url, data).then((r) => r.data),

  put: <T>(url: string, data?: unknown) =>
    apiClient.put<T>(url, data).then((r) => r.data),

  delete: <T = void>(url: string) =>
    apiClient.delete<T>(url).then((r) => r.data),

  upload: <T>(url: string, formData: FormData) =>
    // Don't set Content-Type manually — axios detects FormData and sets the
    // correct multipart/form-data header WITH the boundary param automatically.
    apiClient.post<T>(url, formData).then((r) => r.data),
};
