/**
 * Librarian Dashboard — smoke + KPI render tests.
 * Verifies greeting, library KPIs from dashboard-stats and the
 * quick-action cards.
 */
import React from "react";
import { screen } from "@testing-library/react";
import LibrarianDashboard from "./Dashboard";
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

describe("Librarian Dashboard", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "librarian" }) });
    (api.get as jest.Mock).mockResolvedValue(mockStats);
  });

  test("renders greeting and the four KPI cards", async () => {
    renderWithProviders(<LibrarianDashboard />);
    expect(await screen.findByText(/Good morning, Admin/)).toBeInTheDocument();
    expect(screen.getByText("Total Students")).toBeInTheDocument();
    expect(screen.getByText("450")).toBeInTheDocument();
    expect(screen.getByText("Today's Attendance")).toBeInTheDocument();
    expect(screen.getByText("92.4%")).toBeInTheDocument();
    expect(screen.getByText("Teachers")).toBeInTheDocument();
    expect(screen.getByText("Classrooms")).toBeInTheDocument();
    expect(screen.getByText("18")).toBeInTheDocument();
  });

  test("renders the quick-action cards", async () => {
    renderWithProviders(<LibrarianDashboard />);
    expect(await screen.findByText("Library Management")).toBeInTheDocument();
    expect(screen.getByText("Announcements")).toBeInTheDocument();
  });

  test("shows the error state when the stats request fails", async () => {
    (api.get as jest.Mock).mockRejectedValueOnce(new Error("boom"));
    renderWithProviders(<LibrarianDashboard />);
    expect(await screen.findByText(/failed to load data/i)).toBeInTheDocument();
  });
});
