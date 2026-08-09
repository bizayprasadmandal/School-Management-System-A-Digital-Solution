/**
 * Admin ReportsPage — smoke tests
 *
 * Renders with a mocked academic year and reporting API responses; verifies
 * the heading and the KPI summary cards.
 */
import React from "react";
import { screen } from "@testing-library/react";
import ReportsPage from "./ReportsPage";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { useCurrentAcademicYear } from "../../api/hooks";
import { queryClient, makeUser, renderWithProviders } from "../../testUtils";

// ─── Mocks ────────────────────────────────────────────────────────────────────

const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

jest.mock("react-hot-toast", () => ({
  __esModule: true,
  default: { success: jest.fn(), error: jest.fn() },
}));

jest.mock("../../api/client", () => ({
  api: { get: jest.fn() },
}));

jest.mock("../../api/hooks", () => ({
  useCurrentAcademicYear: jest.fn(),
}));

// Mock recharts to avoid rendering issues in test environment
jest.mock("recharts", () => ({
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  LineChart: ({ children }: any) => <div data-testid="line-chart">{children}</div>,
  Line: () => <div data-testid="line" />,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  Cell: () => <div data-testid="cell" />,
  XAxis: () => <div data-testid="xaxis" />,
  YAxis: () => <div data-testid="yaxis" />,
  CartesianGrid: () => <div data-testid="grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  Legend: () => <div data-testid="legend" />,
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockYear = { id: 1, name: "2026-27", is_current: true };

const mockDashStats = {
  total_students: 120,
  total_teachers: 8,
  attendance_today_pct: 92.5,
  fees_collected_month: 7000,
  total_classrooms: 6,
  fees_outstanding: 8000,
};

const mockFeeReport = {
  total_invoiced: 15000,
  total_collected: 7000,
  total_outstanding: 8000,
  total_overdue: 5000,
  collection_rate: 46.7,
  by_status: [
    { status: "paid", amount: 7000, total: 7000, count: 1 },
    { status: "partial", amount: 3000, total: 3000, count: 1 },
    { status: "overdue", amount: 5000, total: 5000, count: 1 },
  ],
  monthly: [{ month: "Jan", invoiced: 5000, collected: 5000, outstanding: 0 }],
  recent_payments: [],
};

describe("Admin ReportsPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser() });
    (useCurrentAcademicYear as jest.Mock).mockReturnValue({ data: mockYear, isLoading: false });
    (api.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes("dashboard-stats")) return Promise.resolve(mockDashStats);
      if (url.includes("attendance-report")) return Promise.resolve({ daily: [] });
      return Promise.resolve(mockFeeReport);
    });
  });

  test("renders the heading and KPI summary cards", async () => {
    renderWithProviders(<ReportsPage />);
    // The page renders a skeleton grid until the queries resolve — wait for the
    // loaded state before asserting the heading.
    expect(await screen.findByRole("heading", { name: "Reports & Analytics" })).toBeInTheDocument();
    // "Total Students"/"120" appear in the KPI card and a detail section.
    expect(screen.getAllByText("Total Students").length).toBeGreaterThan(0);
    expect(screen.getAllByText("120").length).toBeGreaterThan(0);
    expect(screen.getAllByText("Monthly Fees").length).toBeGreaterThan(0);
  });
});
