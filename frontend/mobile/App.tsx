/**
 * EduSphere Mobile — Root App entry point
 * Wraps navigation with QueryClient and auth state, and initializes
 * push notification handling on startup.
 */

import React, { useEffect, useRef } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StatusBar } from "expo-status-bar";
import * as Sentry from "@sentry/react-native";
import { navigationRef } from "./src/services/navigation";

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

// ─── Sentry (error tracking) ────────────────────────────────────────────────
// Guarded by EXPO_PUBLIC_SENTRY_DSN — when unset, Sentry is completely off and
// nothing is bundled. `enableNative: false` keeps JS-level capture working in
// Expo Go / managed workflows (no native RNSentry module present). When an EAS
// native build is added, add the `@sentry/react-native/expo` config plugin and
// drop the `enableNative` flag to enable native crash reporting.
const sentryDsn = process.env.EXPO_PUBLIC_SENTRY_DSN;
if (sentryDsn) {
  Sentry.init({
    dsn: sentryDsn,
    enabled: !__DEV__, // keep development noise out of the project
    enableNative: false, // JS-level capture only (works in Expo Go)
    tracesSampleRate: 0.1,
  });
}

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 min — baseline; per-query overrides in hooks
      gcTime: 30 * 60 * 1000, // keep stale data 30 min for instant back-nav
      retry: 1,
      refetchOnWindowFocus: false,
      refetchOnReconnect: true, // revalidate after network comes back
      networkMode: "offlineFirst", // prefer cache when offline
    },
  },
});

// ─── Push Notification Initializer ───────────────────────────────────────────
// This inner component has access to the auth store and runs side effects.

function NotificationInitializer({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const initRef = useRef(false);
  const cleanupRef = useRef<(() => void) | null>(null);

  useEffect(() => {
    // Reset ref on logout so re-login re-registers the token
    if (!isAuthenticated) {
      initRef.current = false;
      cleanupRef.current?.();
      cleanupRef.current = null;
      return;
    }

    const init = async () => {
      if (initRef.current) return;
      initRef.current = true;

      const token = await registerForPushNotifications();
      if (token) await syncPushTokenToBackend(token);

      const unsubForeg = onForegroundNotification(() => {});
      const unsubTap = onNotificationTapped((response) => {
        const data = response.notification.request.content.data;
        // Navigate to the screen specified in the notification payload
        if (data?.route && navigationRef.isReady()) {
          navigationRef.navigate(data.route, data.params || {});
        }
      });

      cleanupRef.current = () => {
        unsubForeg();
        unsubTap();
      };
    };

    init();

    return () => {
      cleanupRef.current?.();
      cleanupRef.current = null;
    };
  }, [isAuthenticated]);

  return <>{children}</>;
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <StatusBar style="light" />
      <NotificationInitializer>
        <RootNavigator />
      </NotificationInitializer>
    </QueryClientProvider>
  );
}

// Wrap the root component so Sentry tracks component render errors; when the
// SDK is disabled (no DSN) the wrapper is a no-op.
export default sentryDsn ? Sentry.wrap(App) : App;
