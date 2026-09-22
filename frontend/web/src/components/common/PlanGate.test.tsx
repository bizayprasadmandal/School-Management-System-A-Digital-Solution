/**
 * PlanGate components — badges and upgrade prompts for tiered features.
 *
 * Covers the store plumbing (useFeatureLocked fail-open semantics) and the
 * three render surfaces: PlanBadge chip, FeatureLockNotice panel, and the
 * PremiumGate / PlanLockedSection gates.
 */
import React from "react";
import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { FeatureLockNotice, PlanBadge, PlanLockedSection, PremiumGate } from "./PlanGate";
import { useAuthStore, type PlanFeatures } from "../../store/authStore";

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  Link: ({ children, to }: { children: React.ReactNode; to: string }) => (
    <a href={to}>{children}</a>
  ),
}));

const PREMIUM: PlanFeatures = {
  plan: "premium",
  features: [
    "accounting_ledger",
    "advanced_analytics",
    "finance_overview",
    "live_transport_tracking",
  ],
  is_premium: true,
};

const STANDARD: PlanFeatures = {
  plan: "standard",
  features: ["finance_overview"],
  is_premium: false,
};

function setState(partial: { user?: unknown; planFeatures?: PlanFeatures | null }) {
  useAuthStore.setState({
    user: { role: "school_admin" } as never,
    planFeatures: null,
    ...partial,
  } as never);
}

describe("PlanBadge", () => {
  it("renders the current plan with premium styling", () => {
    setState({ planFeatures: PREMIUM });
    render(<PlanBadge />);
    const badge = screen.getByTitle("Current plan: premium");
    expect(badge).toHaveTextContent("premium");
  });

  it("falls back to basic when plan features have not loaded", () => {
    setState({ planFeatures: null });
    render(<PlanBadge />);
    expect(screen.getByTitle("Current plan: basic")).toBeInTheDocument();
  });
});

describe("FeatureLockNotice", () => {
  it("explains the locked feature and links to upgrade", () => {
    setState({ planFeatures: STANDARD });
    render(
      <MemoryRouter>
        <FeatureLockNotice featureKey="accounting_ledger" />
      </MemoryRouter>,
    );
    expect(screen.getByRole("status")).toHaveAttribute(
      "aria-label",
      "Premium feature locked: the accounting ledger (monthly summary & trend)",
    );
    expect(screen.getByText(/Upgrade plan/i)).toBeInTheDocument();
    expect(screen.getByText(/standard/i)).toBeInTheDocument();
  });
});

describe("PremiumGate", () => {
  it("renders children when the feature is unlocked", () => {
    setState({ planFeatures: PREMIUM });
    render(
      <PremiumGate featureKey="accounting_ledger">
        <div>ledger content</div>
      </PremiumGate>,
    );
    expect(screen.getByText("ledger content")).toBeInTheDocument();
  });

  it("renders the lock notice instead of children when locked", () => {
    setState({ planFeatures: STANDARD });
    render(
      <MemoryRouter>
        <PremiumGate featureKey="accounting_ledger">
          <div>ledger content</div>
        </PremiumGate>
      </MemoryRouter>,
    );
    expect(screen.queryByText("ledger content")).not.toBeInTheDocument();
    expect(screen.getByText(/requires a plan upgrade/i)).toBeInTheDocument();
  });

  it("always renders children for super admins", () => {
    setState({ planFeatures: STANDARD, user: { role: "super_admin" } as never });
    render(
      <PremiumGate featureKey="accounting_ledger">
        <div>ledger content</div>
      </PremiumGate>,
    );
    expect(screen.getByText("ledger content")).toBeInTheDocument();
  });
});

describe("PlanLockedSection (fail-open)", () => {
  it("renders children with no notice while plan is unknown", () => {
    setState({ planFeatures: null });
    render(
      <MemoryRouter>
        <PlanLockedSection featureKey="advanced_analytics">
          <div>analytics content</div>
        </PlanLockedSection>
      </MemoryRouter>,
    );
    expect(screen.getByText("analytics content")).toBeInTheDocument();
    expect(screen.queryByText(/requires a plan upgrade/i)).not.toBeInTheDocument();
  });

  it("adds a compact banner above children when locked (banner mode)", () => {
    setState({ planFeatures: STANDARD });
    render(
      <MemoryRouter>
        <PlanLockedSection featureKey="advanced_analytics">
          <div>analytics content</div>
        </PlanLockedSection>
      </MemoryRouter>,
    );
    expect(screen.getByText(/requires a plan upgrade/i)).toBeInTheDocument();
    expect(screen.getByText("analytics content")).toBeInTheDocument();
  });

  it("replaces children when locked in replace mode", () => {
    setState({ planFeatures: STANDARD });
    render(
      <MemoryRouter>
        <PlanLockedSection featureKey="advanced_analytics" replace>
          <div>analytics content</div>
        </PlanLockedSection>
      </MemoryRouter>,
    );
    expect(screen.queryByText("analytics content")).not.toBeInTheDocument();
    expect(screen.getByText(/requires a plan upgrade/i)).toBeInTheDocument();
  });
});
