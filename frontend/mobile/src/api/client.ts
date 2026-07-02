/**
 * Mobile API Client — Axios instance with JWT refresh for React Native
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from "axios";
import * as SecureStore from "expo-secure-store";
import { useAuthStore } from "../hooks/useAuthStore";

const BASE_URL = process.env.EXPO_PUBLIC_API_URL ?? "https://api.edusphere.school/api/v1";

export const mobileApiClient = axios.create({
  baseURL: BASE_URL,
  headers: { "Content-Type": "application/json" },
  timeout: 30_000,
});

// ─── Request interceptor ─────────────────────────────────────────────────────

mobileApiClient.interceptors.request.use(
  async (config: InternalAxiosRequestConfig) => {
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
let refreshQueue: Array<{ resolve: (token: string) => void; reject: (err: unknown) => void }> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  refreshQueue.forEach(({ resolve, reject }) => (error ? reject(error) : resolve(token!)));
  refreshQueue = [];
};

mobileApiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as InternalAxiosRequestConfig & { _retry?: boolean };

    if (error.response?.status === 401 && !original._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          refreshQueue.push({
            resolve: (token) => {
              original.headers.Authorization = `Bearer ${token}`;
              resolve(mobileApiClient(original));
            },
            reject,
          });
        });
      }

      original._retry = true;
      isRefreshing = true;

      const refreshToken = useAuthStore.getState().tokens?.refresh;
      if (!refreshToken) {
        useAuthStore.getState().logout();
        return Promise.reject(error);
      }

      try {
        const { data } = await axios.post(`${BASE_URL}/auth/token/refresh/`, { refresh: refreshToken });
        const newTokens = { access: data.access, refresh: data.refresh ?? refreshToken };
        useAuthStore.getState().setAuth(useAuthStore.getState().user!, newTokens);

        // Persist to secure storage
        await SecureStore.setItemAsync("sms_tokens", JSON.stringify(newTokens));

        processQueue(null, data.access);
        original.headers.Authorization = `Bearer ${data.access}`;
        return mobileApiClient(original);
      } catch (refreshError) {
        processQueue(refreshError, null);
        useAuthStore.getState().logout();
        await SecureStore.deleteItemAsync("sms_tokens");
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// ─── Typed helpers ─────────────────────────────────────────────────────────────

export const mobileApi = {
  get:    <T>(url: string, params?: object) =>
    mobileApiClient.get<T>(url, { params }).then(r => r.data),
  post:   <T>(url: string, data?: unknown) =>
    mobileApiClient.post<T>(url, data).then(r => r.data),
  patch:  <T>(url: string, data?: unknown) =>
    mobileApiClient.patch<T>(url, data).then(r => r.data),
  delete: <T = void>(url: string) =>
    mobileApiClient.delete<T>(url).then(r => r.data),
  upload: <T>(url: string, formData: FormData) =>
    mobileApiClient.post<T>(url, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    }).then(r => r.data),
};
