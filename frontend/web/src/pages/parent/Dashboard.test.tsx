/**
 * Parent Dashboard — smoke + data-render tests.
 * Verifies greeting, unread badge, children cards with attendance/grades,
 * quick actions and recent notifications.
 */
import React from "react";
import { screen } from "@testing-library/react";
import ParentDashboard from "./Dashboard";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { useUnreadNotificationCount } from "../../api/hooks";
import { queryClient, makeUser, renderWithProviders } from "../../testUtils";

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => jest.fn(),
}));

jest.mock("../../api/client", () => ({
  api: { get: jest.fn() },
}));

jest.mock("../../api/hooks", () => ({
  useUnreadNotificationCount: jest.fn(),
}));

const child = {
  id: "c1",
  full_name: "Rohan Shrestha",
  avatar: null,
  is_active: true,
  current_class: "Grade 5 5A",
  admission_number: "S-001",
  email: "rohan@school.edu",
};

const notif = {
  id: "n1",
  title: "Fee Reminder",
  body: "Term 2 fees are due soon.",
  read_at: null,
  created_at: "2026-08-15T10:00:00Z",
};

describe("Parent Dashboard", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "parent" }) });
    (useUnreadNotificationCount as jest.Mock).mockReturnValue({ data: 3 });
    (api.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes("attendance-summary")) return Promise.resolve({ attendance_percentage: 88 });
      if (url.includes("report-cards"))
        return Promise.resolve({ results: [{ grade_letter: "A", exam_name: "Midterm" }] });
      if (url.includes("notifications")) return Promise.resolve({ results: [notif] });
      return Promise.resolve({ results: [child] });
    });
  });

  test("renders greeting, unread badge and children list", async () => {
    renderWithProviders(<ParentDashboard />);
    expect(await screen.findByText(/Hello, Admin!/)).toBeInTheDocument();
    expect(screen.getByText("3 unread")).toBeInTheDocument();
    expect(screen.getByText("My Children")).toBeInTheDocument();
    expect(await screen.findByText("Rohan Shrestha")).toBeInTheDocument();
    expect(screen.getByText("Active")).toBeInTheDocument();
    expect(screen.getByText(/Grade 5 5A · S-001/)).toBeInTheDocument();
  });

  test("renders per-child attendance and latest grade", async () => {
    renderWithProviders(<ParentDashboard />);
    expect(await screen.findByText("Rohan Shrestha")).toBeInTheDocument();
    expect(await screen.findByText("88.0%")).toBeInTheDocument();
    expect(screen.getByText("Attendance")).toBeInTheDocument();
    expect(await screen.findByText("A")).toBeInTheDocument();
    expect(screen.getByText("Midterm")).toBeInTheDocument();
  });

  test("renders quick actions and recent notifications", async () => {
    renderWithProviders(<ParentDashboard />);
    expect(await screen.findByText("Quick Actions")).toBeInTheDocument();
    expect(screen.getByText("View Attendance")).toBeInTheDocument();
    expect(screen.getByText("Check Grades")).toBeInTheDocument();
    expect(screen.getByText("Pay Fees")).toBeInTheDocument();
    expect(screen.getByText("Send Message")).toBeInTheDocument();
    expect(screen.getByText("Recent Notifications")).toBeInTheDocument();
    expect(screen.getByText("Fee Reminder")).toBeInTheDocument();
    expect(screen.getByText("Term 2 fees are due soon.")).toBeInTheDocument();
  });

  test("shows the empty state when no children are linked", async () => {
    (api.get as jest.Mock).mockResolvedValue({ results: [] });
    renderWithProviders(<ParentDashboard />);
    expect(await screen.findByText(/No children linked to your account yet/i)).toBeInTheDocument();
  });
});
