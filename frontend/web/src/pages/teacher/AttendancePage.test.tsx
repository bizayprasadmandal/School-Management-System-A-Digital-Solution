/**
 * Teacher AttendancePage — smoke tests
 *
 * Renders with mocked classrooms + bulk-record hook; verifies the heading and
 * that the student roster appears after a classroom is selected.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import TeacherAttendancePage from "./AttendancePage";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { useClassrooms, useBulkRecordAttendance } from "../../api/hooks";
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
  useClassrooms: jest.fn(),
  useBulkRecordAttendance: jest.fn(),
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

const mockStudents = [
  {
    student_id: "1",
    full_name: "Alice Johnson",
    admission_number: "A001",
    status: "P",
    remarks: "",
  },
];

describe("Teacher AttendancePage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({
      user: makeUser({ role: "teacher", email: "sarah@demo.edusphere.school" }),
    });
    (useClassrooms as jest.Mock).mockReturnValue({ data: mockClassrooms, isLoading: false });
    (useBulkRecordAttendance as jest.Mock).mockReturnValue({ mutate: jest.fn(), isPending: false });
    (api.get as jest.Mock).mockResolvedValue(mockStudents);
  });

  test("renders the heading and classroom selector options", () => {
    renderWithProviders(<TeacherAttendancePage />);
    expect(screen.getByRole("heading", { name: "Record Attendance" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Grade 5 5A" })).toBeInTheDocument();
  });

  test("shows the student roster after selecting a classroom", async () => {
    renderWithProviders(<TeacherAttendancePage />);
    await userEvent.selectOptions(screen.getByRole("combobox"), "1");
    expect(await screen.findByText("Alice Johnson")).toBeInTheDocument();
  });
});
