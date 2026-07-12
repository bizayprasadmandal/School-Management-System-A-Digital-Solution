/**
 * Custom hooks — shared across all role dashboards
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { useAuthStore } from "../store/authStore";
import type { UserRole } from "../types";

// ─── useDebounce ─────────────────────────────────────────────────────────────

export function useDebounce<T>(value: T, delay = 400): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

// ─── useLocalStorage ─────────────────────────────────────────────────────────

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [stored, setStored] = useState<T>(() => {
    try {
      const item = window.localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch {
      return initialValue;
    }
  });

  const setValue = useCallback((value: T | ((prev: T) => T)) => {
    try {
      const toStore = value instanceof Function ? value(stored) : value;
      setStored(toStore);
      window.localStorage.setItem(key, JSON.stringify(toStore));
    } catch (e) {
      console.warn("localStorage write failed:", e);
    }
  }, [key, stored]);

  return [stored, setValue] as const;
}

// ─── useWebSocket (real-time messaging) ──────────────────────────────────────

type WSStatus = "connecting" | "connected" | "disconnected" | "error";

interface UseWebSocketOptions {
  onMessage?: (data: Record<string, unknown>) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  reconnectDelay?: number;
  maxRetries?: number;
}

export function useWebSocket(path: string, options: UseWebSocketOptions = {}) {
  const { tokens } = useAuthStore();
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef(0);
  const mountedRef = useRef(true);
  const [status, setStatus] = useState<WSStatus>("disconnected");
  const { onMessage, onConnect, onDisconnect, reconnectDelay = 3000, maxRetries = 5 } = options;

  const WS_BASE = process.env.REACT_APP_WS_URL?.replace(/^http/, "ws") ?? "ws://localhost:8000";

  const connect = useCallback(() => {
    if (!tokens?.access || !mountedRef.current) return;
    const url = `${WS_BASE}${path}?token=${tokens.access}`;
    setStatus("connecting");
    const ws = new WebSocket(url);
    wsRef.current = ws;

    ws.onopen = () => {
      retryRef.current = 0;
      setStatus("connected");
      onConnect?.();
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        onMessage?.(data);
      } catch {
        onMessage?.(event.data);
      }
    };

    ws.onclose = () => {
      setStatus("disconnected");
      onDisconnect?.();
      if (mountedRef.current && retryRef.current < maxRetries) {
        retryRef.current += 1;
        setTimeout(connect, reconnectDelay * retryRef.current);
      }
    };

    ws.onerror = () => setStatus("error");
  }, [path, tokens?.access, WS_BASE, onMessage, onConnect, onDisconnect, reconnectDelay, maxRetries]);

  const send = useCallback((data: object) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data));
    }
  }, []);

  const disconnect = useCallback(() => {
    mountedRef.current = false;
    wsRef.current?.close();
  }, []);

  useEffect(() => {
    mountedRef.current = true;
    connect();
    return () => { mountedRef.current = false; wsRef.current?.close(); };
  }, [connect]);

  return { status, send, disconnect, isConnected: status === "connected" };
}

// ─── useNotificationSocket ────────────────────────────────────────────────────

export function useNotificationSocket(onNewNotification?: (notif: { id: string; title: string; body: string; created_at: string; read_at: string | null }) => void) {
  const [unreadCount, setUnreadCount] = useState(0);

  const { send } = useWebSocket("/ws/notifications/", {
    onMessage: (data) => {
      if (data.type === "notification") onNewNotification?.(data.notification as { id: string; title: string; body: string; created_at: string; read_at: string | null });
      if (data.type === "unread_count") setUnreadCount(data.count as number);
    },
  });

  const markRead = useCallback((notificationId: string) => {
    send({ type: "mark_read", notification_id: notificationId });
  }, [send]);

  return { unreadCount, markRead };
}

// ─── useChatSocket ────────────────────────────────────────────────────────────

export function useChatSocket(recipientId: string, onMessage?: (msg: { id: string; content: string; sender_id: string; sender_name: string; status: string; sent_at: string }) => void) {
  const [isTyping, setIsTyping] = useState(false);
  const typingTimeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const { status, send } = useWebSocket(`/ws/chat/${recipientId}/`, {
    onMessage: (data) => {
      if (data.type === "chat_message") onMessage?.(data.message as { id: string; content: string; sender_id: string; sender_name: string; status: string; sent_at: string });
      if (data.type === "typing_indicator") {
        setIsTyping(data.is_typing as boolean);
        clearTimeout(typingTimeoutRef.current);
        if (data.is_typing) {
          typingTimeoutRef.current = setTimeout(() => setIsTyping(false), 3000);
        }
      }
    },
  });

  const sendMessage = useCallback((content: string) => {
    send({ type: "message", content });
  }, [send]);

  const sendTyping = useCallback((isTypingNow: boolean) => {
    send({ type: "typing", is_typing: isTypingNow });
  }, [send]);

  return { status, sendMessage, sendTyping, isTyping };
}

// ─── usePermission ────────────────────────────────────────────────────────────

const ROLE_HIERARCHY: Record<UserRole, number> = {
  super_admin: 100, school_admin: 80, accountant: 60,
  teacher: 50, counselor: 45, librarian: 40, student: 20, parent: 20,
};

export function usePermission() {
  const { user } = useAuthStore();

  const hasRole = useCallback((...roles: UserRole[]) => {
    return !!user && roles.includes(user.role);
  }, [user]);

  const hasMinRole = useCallback((minRole: UserRole) => {
    if (!user) return false;
    return ROLE_HIERARCHY[user.role] >= ROLE_HIERARCHY[minRole];
  }, [user]);

  const isAdmin = hasRole("school_admin", "super_admin");
  const isTeacher = hasRole("teacher");
  const isStudent = hasRole("student");
  const isParent = hasRole("parent");

  return { hasRole, hasMinRole, isAdmin, isTeacher, isStudent, isParent, user };
}

// ─── usePagination ───────────────────────────────────────────────────────────

export function usePagination(initialPage = 1, pageSize = 25) {
  const [page, setPage] = useState(initialPage);
  const reset = useCallback(() => setPage(1), []);
  const next = useCallback(() => setPage(p => p + 1), []);
  const prev = useCallback(() => setPage(p => Math.max(1, p - 1)), []);
  return { page, setPage, reset, next, prev, pageSize };
}

// ─── useTitle ────────────────────────────────────────────────────────────────

export function useTitle(title: string) {
  useEffect(() => {
    const prev = document.title;
    document.title = `${title} — EduSphere`;
    return () => { document.title = prev; };
  }, [title]);
}

// ─── useClickOutside ─────────────────────────────────────────────────────────

export function useClickOutside<T extends HTMLElement>(handler: () => void) {
  const ref = useRef<T>(null);
  useEffect(() => {
    const listener = (e: MouseEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) handler();
    };
    document.addEventListener("mousedown", listener);
    return () => document.removeEventListener("mousedown", listener);
  }, [handler]);
  return ref;
}
