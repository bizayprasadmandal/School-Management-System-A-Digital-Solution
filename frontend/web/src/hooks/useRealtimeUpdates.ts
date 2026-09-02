import { useEffect, useRef } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { useWebSocket } from "./index";

interface RealtimeUpdateOptions {
  /** WebSocket path, e.g. "/ws/counseling/sessions/" */
  wsPath: string;
  /** React Query cache key to invalidate on update */
  queryKey: string;
  /** Specific event types that trigger invalidation (empty = all) */
  events?: string[];
  /** Enable/disable the WebSocket connection */
  enabled?: boolean;
}

/**
 * Connects a WebSocket channel to React Query cache invalidation.
 * When the WebSocket pushes an update, the specified query cache is invalidated,
 * triggering a refetch of the latest data.
 *
 * Usage:
 *   useRealtimeUpdates({
 *     wsPath: "/ws/counseling/sessions/",
 *     queryKey: "counseling-sessions",
 *     events: ["session.created", "session.updated"],
 *   });
 */
export function useRealtimeUpdates({
  wsPath,
  queryKey,
  events = [],
  enabled = true,
}: RealtimeUpdateOptions) {
  const qc = useQueryClient();
  const lastUpdateRef = useRef(0);

  const { status } = useWebSocket(wsPath, {
    enabled,
    onMessage: (data) => {
      // Debounce: avoid refetching on rapid successive messages
      const now = Date.now();
      if (now - lastUpdateRef.current < 500) return;
      lastUpdateRef.current = now;

      const eventType = (data as any)?.type || (data as any)?.event || "";

      // If specific events are specified, only invalidate on those
      if (events.length > 0 && !events.includes(eventType)) {
        return;
      }

      // Invalidate the query cache to trigger a refetch
      qc.invalidateQueries({ queryKey: [queryKey] });
    },
    onConnect: () => {
      // Could log connection status or show a toast
    },
    maxRetries: 3,
    reconnectDelay: 5000,
  });

  return { wsStatus: status };
}
