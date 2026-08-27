/**
 * Custom hooks — shared across all role dashboards
 */

import { useState, useEffect, useRef, useCallback } from "react";
import { useAuthStore } from "../store/authStore";

// ─── useDebounce ─────────────────────────────────────────────────────────────

export function useDebounce<T>(value: T, delay = 400): T {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delay);
    return () => clearTimeout(t);
  }, [value, delay]);
  return debounced;
}

// ─── useWebSocket (real-time messaging) ──────────────────────────────────────

type WSStatus = "connecting" | "connected" | "disconnected" | "error";

interface UseWebSocketOptions {
  onMessage?: (data: Record<string, unknown>) => void;
  onConnect?: () => void;
  onDisconnect?: () => void;
  reconnectDelay?: number;
  maxRetries?: number;
  /** When false, the socket stays closed (e.g. no active conversation). */
  enabled?: boolean;
}

export function useWebSocket(path: string, options: UseWebSocketOptions = {}) {
  // Subscribe to tokens only — using the full store causes re-renders on
  // every state change, which recreates `connect` and triggers the useEffect
  // cleanup/re-run cycle, closing and reopening the WebSocket each time.
  const tokens = useAuthStore((s) => s.tokens);
  const wsRef = useRef<WebSocket | null>(null);
  const retryRef = useRef(0);
  const mountedRef = useRef(true);
  const [status, setStatus] = useState<WSStatus>("disconnected");

  // Use refs to hold latest callbacks WITHOUT creating new connect() on each render.
  // When onMessage/onConnect/onDisconnect are inline functions (common in React),
  // they get a new reference every render. If these are in the useCallback dep
  // array of connect(), then connect() is recreated every render, causing the
  // useEffect cleanup to close the WS and immediately reopen it — producing
  // the "WebSocket is closed before the connection is established" error.
  const optionsRef = useRef(options);
  optionsRef.current = options;

  // Guard against empty REACT_APP_WS_URL (unset build arg) — fall back to the
  // page origin so the Vite dev-server proxy (configured in vite.config.ts)
  // forwards the WebSocket upgrade to the backend. In production the env var
  // points directly at the backend host.
  const WS_BASE = (() => {
    const raw = process.env.REACT_APP_WS_URL || "";
    if (raw) return raw.replace(/^http/, "ws");
    // Fallback: derive from the page URL so the Vite proxy handles the upgrade.
    const proto = window.location.protocol === "https:" ? "wss:" : "ws:";
    return `${proto}//${window.location.host}`;
  })();

  const connect = useCallback(() => {
    if (!tokens?.access || !mountedRef.current) return;
    setStatus("connecting");
    // Send the JWT via Sec-WebSocket-Protocol instead of the query string.
    // The backend middleware reads "Bearer, <token>" from this header; query
    // string auth is deprecated because tokens in URLs leak into proxy logs.
    const ws = new WebSocket(`${WS_BASE}${path}`, ["Bearer", tokens.access]);
    wsRef.current = ws;

    ws.onopen = () => {
      retryRef.current = 0;
      setStatus("connected");
      optionsRef.current.onConnect?.();
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        optionsRef.current.onMessage?.(data);
      } catch {
        optionsRef.current.onMessage?.(event.data);
      }
    };

    ws.onclose = () => {
      setStatus("disconnected");
      optionsRef.current.onDisconnect?.();
      if (mountedRef.current && retryRef.current < (optionsRef.current.maxRetries ?? 5)) {
        retryRef.current += 1;
        setTimeout(connect, (optionsRef.current.reconnectDelay ?? 3000) * retryRef.current);
      }
    };

    ws.onerror = () => setStatus("error");
    // eslint-disable-next-line react-hooks/exhaustive-deps
    // NOTE: intentionally NOT including callback refs in deps — they're accessed
    // via optionsRef which is stable across renders.
  }, [path, tokens?.access, WS_BASE]);

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
    if (options.enabled === false) return;
    mountedRef.current = true;
    retryRef.current = 0;
    connect();
    return () => {
      mountedRef.current = false;
      wsRef.current?.close();
    };
  }, [connect, options.enabled]);

  return { status, send, disconnect, isConnected: status === "connected" };
}

// ─── useNotificationSocket ────────────────────────────────────────────────────

export function useNotificationSocket(
  onNewNotification?: (notif: {
    id: string;
    title: string;
    body: string;
    created_at: string;
    read_at: string | null;
  }) => void,
) {
  const [unreadCount, setUnreadCount] = useState(0);

  const { send, status } = useWebSocket("/ws/notifications/", {
    onMessage: (data) => {
      if (data.type === "notification")
        onNewNotification?.(
          data.notification as {
            id: string;
            title: string;
            body: string;
            created_at: string;
            read_at: string | null;
          },
        );
      if (data.type === "unread_count") setUnreadCount(data.count as number);
    },
  });

  const markRead = useCallback(
    (notificationId: string) => {
      send({ type: "mark_read", notification_id: notificationId });
    },
    [send],
  );

  return { unreadCount, markRead, status };
}

// ─── useChatSocket ────────────────────────────────────────────────────────────

export function useChatSocket(
  recipientId: string,
  onMessage?: (msg: {
    id: string;
    content: string;
    sender_id: string;
    sender_name: string;
    status: string;
    sent_at: string;
  }) => void,
  enabled = true,
) {
  const [isTyping, setIsTyping] = useState(false);
  const typingTimeoutRef = useRef<ReturnType<typeof setTimeout>>();

  const { status, send } = useWebSocket(`/ws/chat/${recipientId}/`, {
    enabled: enabled && !!recipientId,
    onMessage: (data) => {
      if (data.type === "chat_message")
        onMessage?.(
          data.message as {
            id: string;
            content: string;
            sender_id: string;
            sender_name: string;
            status: string;
            sent_at: string;
          },
        );
      if (data.type === "typing_indicator") {
        setIsTyping(data.is_typing as boolean);
        clearTimeout(typingTimeoutRef.current);
        if (data.is_typing) {
          typingTimeoutRef.current = setTimeout(() => setIsTyping(false), 3000);
        }
      }
    },
  });

  const sendMessage = useCallback(
    (content: string) => {
      send({ type: "message", content });
    },
    [send],
  );

  const sendTyping = useCallback(
    (isTypingNow: boolean) => {
      send({ type: "typing", is_typing: isTypingNow });
    },
    [send],
  );

  return { status, sendMessage, sendTyping, isTyping };
}

// ─── useTitle ────────────────────────────────────────────────────────────────

export function useTitle(title: string) {
  useEffect(() => {
    const prev = document.title;
    document.title = `${title} — EduSphere`;
    return () => {
      document.title = prev;
    };
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

// ─── useAttendanceSocket (real-time attendance updates) ──────────────────────

interface AttendanceUpdate {
  student_id: string;
  student_name: string;
  status: string;
  recorded_at: string;
  action: "create" | "update";
}

interface AttendanceSnapshot {
  date: string;
  total_students: number;
  records: AttendanceUpdate[];
}

export function useAttendanceSocket(
  classroomId: number,
  date: string,
  onUpdate?: (record: AttendanceUpdate) => void,
  onSnapshot?: (snapshot: AttendanceSnapshot) => void,
  enabled = true,
) {
  const [records, setRecords] = useState<AttendanceUpdate[]>([]);
  const [totalStudents, setTotalStudents] = useState(0);

  const { status } = useWebSocket(`/ws/attendance/${classroomId}/${date}/`, {
    enabled: enabled && !!classroomId && !!date,
    onMessage: (data) => {
      if (data.type === "snapshot") {
        const snapshot = data.data as AttendanceSnapshot;
        setRecords(snapshot.records);
        setTotalStudents(snapshot.total_students);
        onSnapshot?.(snapshot);
      }
      if (data.type === "attendance_update") {
        const record = data.record as AttendanceUpdate;
        setRecords((prev) => {
          const idx = prev.findIndex((r) => r.student_id === record.student_id);
          if (idx >= 0) {
            const updated = [...prev];
            updated[idx] = record;
            return updated;
          }
          return [...prev, record];
        });
        onUpdate?.(record);
      }
    },
  });

  return { status, records, totalStudents };
}
