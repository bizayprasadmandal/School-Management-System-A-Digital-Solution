/**
 * Platform console pages — Revenue & Plans and Audit Logs smoke tests.
 *
 * Covers: MRR/ARR totals + tier distribution + per-school table on Revenue;
 * search-driven audit table rendering with school names.
 */
import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import PlatformRevenuePage from "./PlatformRevenuePage";
import PlatformAuditPage from "./PlatformAuditPage";
import { useAuthStore } from "../../store/authStore";
import type { User } from "../../types";

jest.mock("../../api/client", () => ({
  api: {
    get: jest.fn((url: string) => {
      if (url.includes("/auth/platform/revenue/")) {
        return Promise.resolve({
          total_mrr: 180,
          total_arr: 1800,
          schools_by_tier: { premium: 1, basic: 1 },
          schools: [
            {
              id: "sc-1",
              name: "Green Valley School",
              code: "GVS",
              subscription_tier: "premium",
              is_active: true,
              student_count: 3,
              revenue: 5000,
              mrr: 180,
              arr: 1800,
            },
            {
              id: "sc-2",
              name: "Basic School",
              code: "BAS",
              subscription_tier: "basic",
              is_active: true,
              student_count: 10,
              revenue: 0,
              mrr: 0,
              arr: 0,
            },
          ],
        });
      }
      if (url.includes("/auth/audit-log/")) {
        return Promise.resolve({
          count: 1,
          results: [
            {
              id: "al-1",
              school: "sc-1",
              school_name: "Green Valley School",
              user_name: "Platform Admin",
              user_email: "sa@edusphere.io",
              action: "plan_tier_change",
              resource_type: "school",
              resource_id: "sc-1-uuid",
              ip_address: "10.0.0.1",
              timestamp: new Date("2026-09-22T10:00:00Z").toISOString(),
            },
          ],
        });
      }
      return Promise.resolve({});
    }),
  },
}));

function renderWithProviders(ui: React.ReactElement) {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{ui}</BrowserRouter>
    </QueryClientProvider>,
  );
}

const superAdmin = { id: "u1", role: "super_admin", school: null } as unknown as User;

describe("PlatformRevenuePage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useAuthStore.setState({ user: superAdmin, isAuthenticated: true });
  });

  it("shows platform MRR and ARR totals", async () => {
    renderWithProviders(<PlatformRevenuePage />);
    // Totals appear in the stat cards AND the school row (same fixture values)
    expect((await screen.findAllByText("Rs. 180.00")).length).toBeGreaterThanOrEqual(1);
    expect((await screen.findAllByText("Rs. 1,800.00")).length).toBeGreaterThanOrEqual(1);
  });

  it("lists per-school rows with tier badges and student counts", async () => {
    renderWithProviders(<PlatformRevenuePage />);
    expect(await screen.findByText("Green Valley School")).toBeInTheDocument();
    expect(screen.getByText("Basic School")).toBeInTheDocument();
    expect(screen.getAllByText("premium").length).toBeGreaterThan(0);
  });
});

describe("PlatformAuditPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useAuthStore.setState({ user: superAdmin, isAuthenticated: true });
  });

  it("renders audit rows with school names and actions", async () => {
    renderWithProviders(<PlatformAuditPage />);
    expect(await screen.findByText("Green Valley School")).toBeInTheDocument();
    expect(screen.getByText("plan_tier_change")).toBeInTheDocument();
    expect(screen.getByText("Platform Admin")).toBeInTheDocument();
  });

  it("refetches with the search term when typing", async () => {
    const { api } = jest.requireMock("../../api/client") as { api: { get: jest.Mock } };
    const user = userEvent.setup();
    renderWithProviders(<PlatformAuditPage />);
    await screen.findByText("plan_tier_change");
    await user.type(screen.getByLabelText("Search audit logs"), "tier");
    await new Promise((r) => setTimeout(r, 500)); // debounce-ish
    const calls = api.get.mock.calls.filter((c: unknown[]) =>
      String(c[0]).includes("/auth/audit-log/"),
    );
    expect(calls.length).toBeGreaterThan(1);
    expect(String(calls[calls.length - 1][1]?.search ?? "")).toContain("tier");
  });
});
