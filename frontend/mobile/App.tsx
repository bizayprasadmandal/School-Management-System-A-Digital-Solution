/**
 * EduSphere Mobile — Root App entry point
 * Wraps navigation with QueryClient and auth state, and initializes
 * push notification handling on startup.
 */

import React, { useEffect, useRef } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StatusBar } from "expo-status-bar";

// ─── Global dayjs configuration ─────────────────────────────────────────────
// Extend dayjs with plugins at the entry point so all screens that import dayjs
// directly inherit the extended methods (e.g., .fromNow()).
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
dayjs.extend(relativeTime);

import RootNavigator from "./src/navigation/RootNavigator";
import {
  registerForPushNotifications,
  syncPushTokenToBackend,
  onForegroundNotification,
  onNotificationTapped,
} from "./src/services/notifications";
import { useAuthStore } from "./src/hooks/useAuthStore";

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000,       // 5 min — baseline; per-query overrides in hooks
      gcTime: 30 * 60 * 1000,          // keep stale data 30 min for instant back-nav
      retry: 1,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true,        // revalidate after network comes back
      networkMode: "offlineFirst",     // prefer cache when offline
    },
  },
});

// ─── Push Notification Initializer ───────────────────────────────────────────
// This inner component has access to the auth store and runs side effects.

function NotificationInitializer({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const initRef = useRef(false);

  useEffect(() => {
    // Reset ref on logout so re-login re-registers the token
    if (!isAuthenticated) {
      initRef.current = false;
      return;
    }

    const init = async () => {
      // Prevent double-initialization
      if (initRef.current) return;
      initRef.current = true;

      const token = await registerForPushNotifications();
      if (token) {
        await syncPushTokenToBackend(token);
      }

      // Subscribe to foreground notifications (in-app alerts)
      const unsubForeground = onForegroundNotification((notification) => {
        // The system shows the notification via the handler configured in
        // notifications.ts. Additional in-app UI updates can go here.
      });

      // Subscribe to notification taps (user tapped a push notification)
      const unsubTap = onNotificationTapped((response) => {
        const data = response.notification.request.content.data;
        // Future: navigate to the relevant screen based on data.route
        // e.g., if (data.route) navigation.navigate(data.route);
      });

      return () => {
        unsubForeground();
        unsubTap();
      };
    };

    init();
  }, [isAuthenticated]);

  return <>{children}</>;
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <StatusBar style="light" />
      <NotificationInitializer>
        <RootNavigator />
      </NotificationInitializer>
    </QueryClientProvider>
  );
}
