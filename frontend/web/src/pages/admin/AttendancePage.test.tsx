/**
 * Admin AttendancePage — smoke tests
 *
 * Renders with mocked classroom/academic-year hooks; verifies the heading,
 * the classroom selector options, and that attendance rows appear after a
 * classroom is selected.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import AttendancePage from "./AttendancePage";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { useClassrooms, useCurrentAcademicYear } from "../../api/hooks";
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
  api: { get: jest.fn(), post: jest.fn() },
}));

jest.mock("../../api/hooks", () => ({
  useClassrooms: jest.fn(),
  useCurrentAcademicYear: jest.fn(),
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockClassrooms = {
  count: 1,
  results: [
    {
      id: 1,
      name: "5A",
      grade_name: "Grade 5",
      capacity: 35,
      teacher_name: "Sarah Mitchell",
      student_count: 28,
    },
  ],
};

const mockYear = { id: 1, name: "2026-27", is_current: true };

const mockSummary = {
  total_students: 28,
  recorded: 28,
  not_recorded: 0,
  breakdown: { present: 28, absent: 0, late: 0, excused: 0 },
};

const mockRecords = {
  count: 1,
  results: [{ id: "1", student_name: "Alice Johnson", status: "P", remarks: "" }],
};

describe("Admin AttendancePage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser() });
    (useClassrooms as jest.Mock).mockReturnValue({ data: mockClassrooms, isLoading: false });
    (useCurrentAcademicYear as jest.Mock).mockReturnValue({ data: mockYear, isLoading: false });
    // URL-dispatch so the classroom-summary and record list endpoints each get
    // the shape they expect (mirrors the ReportsPage test pattern).
    (api.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes("classroom-summary")) return Promise.resolve(mockSummary);
      return Promise.resolve(mockRecords);
    });
  });

  test("renders the heading and classroom selector options", () => {
    renderWithProviders(<AttendancePage />);
    expect(screen.getByRole("heading", { name: "Attendance" })).toBeInTheDocument();
    // The classroom <Select> here has no label — target it by role.
    expect(screen.getByRole("combobox")).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Grade 5 5A" })).toBeInTheDocument();
  });

  test("shows attendance records after selecting a classroom", async () => {
    renderWithProviders(<AttendancePage />);
    await userEvent.selectOptions(screen.getByRole("combobox"), "1");
    expect(await screen.findByText("Alice Johnson")).toBeInTheDocument();
  });

  test("opens the CSV import wizard from the toolbar", async () => {
    renderWithProviders(<AttendancePage />);
    await userEvent.click(screen.getByText("Import CSV"));
    // Modal opens with the upload dropzone and the attendance CSV format help
    expect(screen.getByText("Drop CSV file here or click to browse")).toBeInTheDocument();
    expect(
      screen.getByText(/admission_number,date,status,remarks,classroom_name/),
    ).toBeInTheDocument();
  });
});
