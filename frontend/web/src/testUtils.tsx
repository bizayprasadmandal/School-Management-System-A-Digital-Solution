/**
 * Shared test utilities — fixtures and providers for component tests.
 * Mirrors the e2e helper extraction: one source of truth for the user
 * fixture, the QueryClient, and the router/query provider wrapper.
 */
import React from "react";
import { render } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { User } from "./types";

/** QueryClient with retries disabled so mocked failures surface immediately. */
export const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
});

/** Minimal authenticated user fixture. */
export function makeUser(overrides: Partial<User> = {}): User {
  return {
    id: "1",
    email: "admin@demo.edusphere.school",
    first_name: "Admin",
    last_name: "User",
    full_name: "Admin User",
    role: "school_admin",
    is_active: true,
    email_verified: true,
    two_factor_enabled: false,
    backup_codes_remaining: null,
    notify_email: true,
    notify_sms: false,
    notify_push: true,
    date_joined: "2024-01-01T00:00:00Z",
    ...overrides,
  };
}

/** Render `ui` inside the router + QueryClient providers used by page tests. */
export function renderWithProviders(ui: React.ReactElement) {
  return render(
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>
    </BrowserRouter>,
  );
}
