/**
 * Student Dashboard — smoke + data-render tests.
 * Verifies the greeting, info cards, attendance chip and notification
 * count from mocked hooks.
 */
import React from "react";
import { screen } from "@testing-library/react";
import StudentDashboard from "./Dashboard";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import {
  useStudentAttendanceSummary,
  useCurrentAcademicYear,
  useNotifications,
  useStudentInvoices,
  useSchoolEvents,
  useStudentAssessments,
} from "../../api/hooks";
import { queryClient, makeUser, renderWithProviders } from "../../testUtils";

jest.mock("../../api/client", () => ({
  api: { get: jest.fn() },
}));

jest.mock("../../api/hooks", () => ({
  useStudentAttendanceSummary: jest.fn(),
  useCurrentAcademicYear: jest.fn(),
  useNotifications: jest.fn(),
  useStudentInvoices: jest.fn(),
  useSchoolEvents: jest.fn(),
  useStudentAssessments: jest.fn(),
}));

const mockProfile = {
  id: "s1",
  admission_number: "S-001",
  enrollments: [{ classroom_name: "Grade 5 5A" }],
};

describe("Student Dashboard", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "student" }) });
    (api.get as jest.Mock).mockResolvedValue(mockProfile);
    (useStudentAttendanceSummary as jest.Mock).mockReturnValue({
      data: { attendance_percentage: 90.5 },
      isLoading: false,
    });
    (useCurrentAcademicYear as jest.Mock).mockReturnValue({ data: { id: 1 } });
    (useNotifications as jest.Mock).mockReturnValue({
      data: { results: [{ id: "n1", title: "T", body: "B", read_at: null }] },
      isLoading: false,
    });
    (useStudentInvoices as jest.Mock).mockReturnValue({ data: { results: [] }, isLoading: false });
    (useSchoolEvents as jest.Mock).mockReturnValue({ data: { results: [] }, isLoading: false });
    (useStudentAssessments as jest.Mock).mockReturnValue({
      data: { results: [] },
      isLoading: false,
    });
  });

  test("renders greeting and the info cards", async () => {
    renderWithProviders(<StudentDashboard />);
    expect(await screen.findByText(/Hello, Admin!/)).toBeInTheDocument();
    expect(screen.getByText("Current Class")).toBeInTheDocument();
    expect(screen.getByText("Grade 5 5A")).toBeInTheDocument();
    expect(screen.getByText("Admission No.")).toBeInTheDocument();
    expect(screen.getByText("S-001")).toBeInTheDocument();
    expect(screen.getByText("Notifications")).toBeInTheDocument();
    expect(screen.getByText("1")).toBeInTheDocument();
  });

  test("renders the overall attendance chip from the summary", async () => {
    renderWithProviders(<StudentDashboard />);
    expect(await screen.findByText(/Overall attendance:/)).toBeInTheDocument();
    // 90.5% appears in the attendance chip and the radial gauge center
    expect(screen.getAllByText("90.5%").length).toBeGreaterThan(0);
  });

  test("renders the fee summary section from invoices", async () => {
    (useStudentInvoices as jest.Mock).mockReturnValue({
      data: {
        results: [
          {
            id: "inv1",
            invoice_number: "INV-001",
            status: "paid",
            paid_amount: "1000",
            outstanding_amount: "0",
            due_date: "2026-09-01",
          },
        ],
      },
      isLoading: false,
    });
    renderWithProviders(<StudentDashboard />);
    expect(await screen.findByText("Fee Summary")).toBeInTheDocument();
    // Pie legend shows the paid amount; "Paid" also appears as a stat badge
    expect(screen.getByText("$1,000")).toBeInTheDocument();
    expect(screen.getAllByText("Paid").length).toBeGreaterThan(0);
  });
});
