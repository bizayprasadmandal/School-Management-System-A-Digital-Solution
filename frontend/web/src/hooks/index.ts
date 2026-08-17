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
  const { tokens } = useAuthStore();
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

  // Guard against empty REACT_APP_WS_URL (unset build arg) — fall back to localhost.
  const WS_BASE =
    (process.env.REACT_APP_WS_URL || "").replace(/^http/, "ws") || "ws://localhost:8000";

  const connect = useCallback(() => {
    if (!tokens?.access || !mountedRef.current) return;
    const url = `${WS_BASE}${path}?token=${tokens.access}`;
    setStatus("connecting");
    const ws = new WebSocket(url);
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
