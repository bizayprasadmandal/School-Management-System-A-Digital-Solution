/**
 * EduSphere Mobile — Root App entry point
 * Wraps navigation with QueryClient and auth state
 */

import React from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { StatusBar } from "expo-status-bar";

// ─── Global dayjs configuration ─────────────────────────────────────────────
// Extend dayjs with plugins at the entry point so all screens that import dayjs
// directly inherit the extended methods (e.g., .fromNow()).
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
dayjs.extend(relativeTime);

import RootNavigator from "./src/navigation/RootNavigator";

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

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <StatusBar style="light" />
      <RootNavigator />
    </QueryClientProvider>
  );
}
