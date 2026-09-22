/**
 * Plan & Billing page — smoke tests.
 *
 * Covers: tier card reflects the plan, matrix rows render per-tier
 * availability, premium state hides the upgrade CTA, standard admins get
 * an upgrade button that fires the change-tier call, and non-admins see
 * the "managed by administrators" note instead.
 */
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import PlanBillingPage from "./PlanBillingPage";
import { useAuthStore } from "../../store/authStore";
import type { User } from "../../types";

jest.mock("../../api/client", () => ({
  api: {
    get: jest.fn((url: string) => {
      if (url.includes("/auth/plan/")) {
        return Promise.resolve({
          plan: "standard",
          is_premium: false,
          school_name: "Bright Future Academy",
          features: ["finance_overview"],
          can_manage: true,
          pricing: {
            basic: { currency: "NPR", per_student_month: 0, per_student_year: 0 },
            standard: { currency: "NPR", per_student_month: 30, per_student_year: 300 },
            premium: { currency: "NPR", per_student_month: 60, per_student_year: 600 },
          },
          matrix: [
            {
              key: "accounting_ledger",
              label: "Double-entry accounting ledger",
              basic: false,
              standard: false,
              premium: true,
            },
            {
              key: "advanced_analytics",
              label: "Advanced analytics & custom reports",
              basic: false,
              standard: false,
              premium: true,
            },
            {
              key: "finance_overview",
              label: "Finance & operations overview cards",
              basic: false,
              standard: true,
              premium: true,
            },
            {
              key: "live_transport_tracking",
              label: "Live GPS tracking, geofencing & ETAs",
              basic: false,
              standard: false,
              premium: true,
            },
          ],
        });
      }
      if (url.includes("/auth/me/")) {
        return Promise.resolve({
          plan_features: {
            plan: "premium",
            features: [
              "accounting_ledger",
              "advanced_analytics",
              "finance_overview",
              "live_transport_tracking",
            ],
            is_premium: true,
          },
        });
      }
      return Promise.resolve({});
    }),
    post: jest.fn(() => Promise.resolve({ detail: "ok", plan: "premium" })),
  },
}));

const { api } = jest.requireMock("../../api/client") as {
  api: { get: jest.Mock; post: jest.Mock };
};

const premiumUser = {
  id: "u1",
  role: "school_admin",
  school: { id: "s1", name: "Bright Future Academy" },
} as unknown as User;

function renderPage() {
  const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } });
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <PlanBillingPage />
      </BrowserRouter>
    </QueryClientProvider>,
  );
}

describe("PlanBillingPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    useAuthStore.setState({ user: premiumUser, planFeatures: null, isAuthenticated: true });
  });

  it("shows the current tier and school", async () => {
    renderPage();
    expect(await screen.findByText("Bright Future Academy")).toBeInTheDocument();
    // tier badge + matrix column header both say "Standard"
    expect(screen.getAllByText("Standard").length).toBeGreaterThan(0);
  });

  it("renders the full feature matrix with per-tier availability", async () => {
    renderPage();
    expect(await screen.findByText("Feature comparison")).toBeInTheDocument();
    expect(screen.getByText("Double-entry accounting ledger")).toBeInTheDocument();
    expect(screen.getByText("Advanced analytics & custom reports")).toBeInTheDocument();
    expect(screen.getByText("Finance & operations overview cards")).toBeInTheDocument();
    // the standard row is included in the current plan
    expect(screen.getByText("· included in your plan")).toBeInTheDocument();
  });

  it("offers an upgrade CTA to premium for standard-school admins", async () => {
    renderPage();
    expect(await screen.findByRole("button", { name: /upgrade to premium/i })).toBeInTheDocument();
  });

  it("shows per-tier pricing cards with the current tier highlighted", async () => {
    renderPage();
    expect(await screen.findByText("Rs. 30.00")).toBeInTheDocument();
    expect(screen.getByText("Rs. 60.00")).toBeInTheDocument();
    expect(screen.getAllByText("Free").length).toBeGreaterThanOrEqual(1);
    expect(screen.getAllByText("/student/mo").length).toBeGreaterThanOrEqual(2);
    expect(screen.getByText("current")).toBeInTheDocument();
  });

  it("includes the price on the upgrade CTA", async () => {
    renderPage();
    const btn = await screen.findByRole("button", { name: /upgrade to premium/i });
    expect(btn.textContent).toContain("Rs. 60.00");
  });

  it("fires the change-tier call and refreshes plan data on upgrade", async () => {
    const user = userEvent.setup();
    renderPage();
    window.confirm = jest.fn(() => true);

    await user.click(await screen.findByRole("button", { name: /upgrade to premium/i }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/auth/plan/change-tier/", { tier: "premium" });
    });
    // /auth/me/ refetched to sync plan_features into the auth store
    await waitFor(() => {
      expect(api.get).toHaveBeenCalledWith("/auth/me/");
    });
  });

  it("hides the upgrade CTA when already premium", async () => {
    api.get.mockImplementation((url: string) =>
      Promise.resolve(
        url.includes("/auth/plan/")
          ? {
              plan: "premium",
              is_premium: true,
              school_name: "Bright Future Academy",
              features: [
                "accounting_ledger",
                "advanced_analytics",
                "finance_overview",
                "live_transport_tracking",
              ],
              can_manage: true,
              pricing: {
                basic: { currency: "NPR", per_student_month: 0, per_student_year: 0 },
                standard: { currency: "NPR", per_student_month: 30, per_student_year: 300 },
                premium: { currency: "NPR", per_student_month: 60, per_student_year: 600 },
              },
              matrix: [
                {
                  key: "accounting_ledger",
                  label: "Double-entry accounting ledger",
                  basic: false,
                  standard: false,
                  premium: true,
                },
                {
                  key: "finance_overview",
                  label: "Finance & operations overview cards",
                  basic: false,
                  standard: true,
                  premium: true,
                },
              ],
            }
          : { plan_features: null },
      ),
    );
    renderPage();
    // tier badge + matrix column header both say "Premium"
    expect(await screen.findAllByText("Premium")).toBeTruthy();
    expect(screen.queryByRole("button", { name: /upgrade to/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /switch to/i })).not.toBeInTheDocument();
  });

  it("shows the non-admin note instead of CTA for teachers", async () => {
    api.get.mockImplementation((url: string) =>
      Promise.resolve(
        url.includes("/auth/plan/")
          ? {
              plan: "standard",
              is_premium: false,
              school_name: "Bright Future Academy",
              features: ["finance_overview"],
              can_manage: false,
              pricing: {
                basic: { currency: "NPR", per_student_month: 0, per_student_year: 0 },
                standard: { currency: "NPR", per_student_month: 30, per_student_year: 300 },
                premium: { currency: "NPR", per_student_month: 60, per_student_year: 600 },
              },
              matrix: [
                {
                  key: "finance_overview",
                  label: "Finance & operations overview cards",
                  basic: false,
                  standard: true,
                  premium: true,
                },
              ],
            }
          : { plan_features: null },
      ),
    );
    useAuthStore.setState({ user: { ...premiumUser, role: "teacher" } as unknown as User });
    renderPage();
    expect(
      await screen.findByText(/plan changes are managed by your school's administrators/i),
    ).toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /upgrade/i })).not.toBeInTheDocument();
  });
});
