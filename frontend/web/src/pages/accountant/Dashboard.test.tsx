/**
 * Accountant Dashboard — smoke + KPI render tests.
 * Verifies greeting, fee KPIs from dashboard-stats, the collection
 * trend section and the three quick-action cards.
 */
import React from "react";
import { screen } from "@testing-library/react";
import AccountantDashboard from "./Dashboard";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { queryClient, makeUser, renderWithProviders } from "../../testUtils";

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => jest.fn(),
}));

jest.mock("../../api/client", () => ({
  api: { get: jest.fn() },
}));

const mockStats = {
  total_students: 450,
  total_teachers: 32,
  total_classrooms: 18,
  attendance_today_pct: 92.4,
  fees_collected_month: 125000,
  fees_outstanding: 48000,
};

const mockForecast = {
  forecast_90d: [{ window_start: "2026-08-17", expected: 30000, already_paid: 5000 }],
  history_3m: [
    { month: "2026-07", collected: 110000 },
    { month: "2026-06", collected: 98000 },
    { month: "2026-05", collected: 101000 },
  ],
};

describe("Accountant Dashboard", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "accountant" }) });
    (api.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes("fee-forecast")) return Promise.resolve(mockForecast);
      return Promise.resolve(mockStats);
    });
  });

  test("renders greeting and the four KPI cards", async () => {
    renderWithProviders(<AccountantDashboard />);
    expect(await screen.findByText(/Good morning, Admin/)).toBeInTheDocument();
    expect(screen.getByText("Fees Collected (Month)")).toBeInTheDocument();
    expect(screen.getByText("$125K")).toBeInTheDocument();
    expect(screen.getByText("Outstanding Fees")).toBeInTheDocument();
    expect(screen.getByText("$48K")).toBeInTheDocument();
    expect(screen.getByText("Total Students")).toBeInTheDocument();
    expect(screen.getByText("450")).toBeInTheDocument();
    expect(screen.getByText("Teachers")).toBeInTheDocument();
    expect(screen.getByText("32")).toBeInTheDocument();
  });

  test("renders the collection trend section and quick-action cards", async () => {
    renderWithProviders(<AccountantDashboard />);
    expect(await screen.findByText("Fee Collection Trend")).toBeInTheDocument();
    expect(screen.getByText("Fee Management")).toBeInTheDocument();
    expect(screen.getByText("Financial Reports")).toBeInTheDocument();
    expect(screen.getByText("Conferences")).toBeInTheDocument();
  });

  test("shows the error state when the stats request fails", async () => {
    (api.get as jest.Mock).mockRejectedValueOnce(new Error("boom"));
    renderWithProviders(<AccountantDashboard />);
    expect(await screen.findByText(/failed to load data/i)).toBeInTheDocument();
  });
});
