/**
 * Counselor Dashboard — smoke + KPI render tests.
 * Verifies greeting, counseling KPIs, the referral badges and the
 * quick-action cards.
 */
import React from "react";
import { screen } from "@testing-library/react";
import CounselorDashboard from "./Dashboard";
import { useAuthStore } from "../../store/authStore";
import { useCounselorDashboardStats } from "../../api/hooks";
import { queryClient, makeUser, renderWithProviders } from "../../testUtils";

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => jest.fn(),
}));

jest.mock("../../api/hooks", () => ({
  useCounselorDashboardStats: jest.fn(),
}));

const mockStats = {
  today_appointments: 3,
  upcoming_appointments: 7,
  appointments_completed: 41,
  pending_referrals: 5,
  urgent_referrals: 2,
  total_appointments: 120,
  total_referrals: 32,
  referrals_resolved: 27,
};

describe("Counselor Dashboard", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "counselor" }) });
    (useCounselorDashboardStats as jest.Mock).mockReturnValue({
      data: mockStats,
      isLoading: false,
      isError: false,
      refetch: jest.fn(),
    });
  });

  test("renders greeting and counseling KPI cards", async () => {
    renderWithProviders(<CounselorDashboard />);
    expect(await screen.findByText(/Good morning, Admin/)).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(screen.getByText("appointments scheduled")).toBeInTheDocument();
    expect(screen.getByText("7")).toBeInTheDocument();
    expect(screen.getByText("future appointments")).toBeInTheDocument();
    expect(screen.getByText("41")).toBeInTheDocument();
    expect(screen.getByText("5")).toBeInTheDocument();
    expect(screen.getByText("2 urgent")).toBeInTheDocument();
  });

  test("renders secondary metrics and quick-action cards", async () => {
    renderWithProviders(<CounselorDashboard />);
    expect(await screen.findByText("Total Appointments")).toBeInTheDocument();
    expect(screen.getByText("Total Referrals")).toBeInTheDocument();
    expect(screen.getByText("Referrals Resolved")).toBeInTheDocument();
    expect(screen.getByText("Appointments")).toBeInTheDocument();
    expect(screen.getByText("Student Referrals")).toBeInTheDocument();
    expect(screen.getByText("Behavior Records")).toBeInTheDocument();
    expect(screen.getByText("View School Announcements")).toBeInTheDocument();
  });

  test("shows the error state when the stats request fails", async () => {
    (useCounselorDashboardStats as jest.Mock).mockReturnValue({
      data: undefined,
      isLoading: false,
      isError: true,
      error: new Error("boom"),
      refetch: jest.fn(),
    });
    renderWithProviders(<CounselorDashboard />);
    expect(await screen.findByText(/failed to load data/i)).toBeInTheDocument();
  });
});
