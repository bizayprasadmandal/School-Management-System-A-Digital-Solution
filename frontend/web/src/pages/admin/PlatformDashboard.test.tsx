/**
 * PlatformDashboard smoke test — pins the backend → UI wiring for the
 * super-admin platform console landing page: stat cards, tier distribution,
 * recent-school rows (with the annotated student count) and top-school
 * revenue are all rendered from `/auth/platform/stats/`.
 */
import React from "react";
import { render, screen } from "@testing-library/react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter } from "react-router-dom";
import PlatformDashboard from "./PlatformDashboard";

const STATS = {
  total_schools: 6,
  active_schools: 5,
  total_users: 2281,
  total_students: 427,
  total_teachers: 135,
  total_revenue: 1250,
  schools_by_tier: { premium: 3, standard: 3 },
  recent_schools: [
    {
      id: "sc-1",
      name: "Green Valley School",
      code: "GVS",
      subdomain: "greenvalley",
      is_active: true,
      subscription_tier: "premium",
      student_count: 219,
    },
  ],
  top_schools: [{ id: "sc-1", name: "Green Valley School", code: "GVS", revenue: 1250 }],
};

jest.mock("../../api/client", () => ({
  api: {
    get: jest.fn(() => Promise.resolve(STATS)),
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

describe("PlatformDashboard", () => {
  beforeEach(() => jest.clearAllMocks());

  it("renders aggregate stats, tier distribution and recent schools", async () => {
    renderWithProviders(<PlatformDashboard />);

    expect(await screen.findByText("Platform Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Total Schools")).toBeInTheDocument();
    expect(screen.getByText("5 active")).toBeInTheDocument();
    // Total Revenue card + top-school row both show the same formatted amount
    expect(screen.getAllByText("$1,250").length).toBeGreaterThanOrEqual(1);

    // tier pills
    expect(screen.getByText("premium")).toBeInTheDocument();
    expect(screen.getByText("standard")).toBeInTheDocument();

    // recent school row carries the annotated student count
    expect(screen.getAllByText("Green Valley School").length).toBeGreaterThanOrEqual(1);
    expect(screen.getByText(/219 students/)).toBeInTheDocument();

    // top schools section renders revenue
    expect(screen.getByText("Top Schools by Revenue")).toBeInTheDocument();
  });

  it("shows the failure state when the stats request fails", async () => {
    const { api } = jest.requireMock("../../api/client") as { api: { get: jest.Mock } };
    api.get.mockRejectedValueOnce(new Error("boom"));

    renderWithProviders(<PlatformDashboard />);

    expect(await screen.findByText("Failed to load platform data.")).toBeInTheDocument();
  });
});
