/**
 * Teacher Dashboard — smoke + data-render tests.
 * Verifies the greeting, quick-access cards, pending-grading list,
 * upcoming conferences and recent-messages preview.
 */
import React from "react";
import { screen } from "@testing-library/react";
import TeacherDashboard from "./Dashboard";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { useClassrooms, useCurrentAcademicYear } from "../../api/hooks";
import { queryClient, makeUser, renderWithProviders } from "../../testUtils";

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => jest.fn(),
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
  useCurrentAcademicYear: jest.fn(),
}));

const mockClassrooms = {
  count: 1,
  results: [
    { id: 1, name: "5A", grade_name: "Grade 5", teacher_name: "Sarah Mitchell", student_count: 28 },
  ],
};

const mockAssessment = {
  id: 1,
  title: "Algebra Quiz",
  subject_name: "Mathematics",
  classroom_name: "Grade 5 5A",
  due_date: "2024-06-20",
  assessment_type: "quiz",
};

const mockConference = {
  id: "s1",
  student_name: "Alice Johnson",
  date: "2024-06-10",
  start_time: "09:00",
  end_time: "09:30",
  is_booked: true,
};

const mockThread = {
  partner: { id: "p1", name: "Jane Smith" },
  last_message: { content: "Is the homework due Friday?", sent_at: "2024-06-09T10:00:00Z" },
  unread_count: 2,
};

describe("Teacher Dashboard", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({
      user: makeUser({ role: "teacher", email: "sarah@demo.edusphere.school" }),
    });
    (useClassrooms as jest.Mock).mockReturnValue({ data: mockClassrooms, isLoading: false });
    (useCurrentAcademicYear as jest.Mock).mockReturnValue({ data: { id: 1, name: "2026-27" } });

    // Default: everything empty so empty states render.
    const get = api.get as jest.Mock;
    get.mockImplementation((url: string) => {
      if (url.includes("teacher-schedule")) return Promise.resolve([]);
      if (url.includes("classroom-summary"))
        return Promise.resolve({ total_students: 0, breakdown: { present: 0, absent: 0 } });
      if (url.includes("gradebook/assessments")) return Promise.resolve({ results: [] });
      if (url.includes("gradebook/submissions")) return Promise.resolve({ results: [] });
      if (url.includes("conference-slots")) return Promise.resolve({ results: [] });
      if (url.includes("messages/inbox")) return Promise.resolve([]);
      // schedule + inbox expect raw arrays; anything else is a paginated list
      return Promise.resolve(
        url.includes("inbox") || url.includes("schedule") ? [] : { results: [] },
      );
    });
  });

  test("renders greeting and the four quick-access cards", async () => {
    renderWithProviders(<TeacherDashboard />);
    expect(
      await screen.findByText(/Good morning, Admin!|Good afternoon, Admin!/),
    ).toBeInTheDocument();
    expect(screen.getByText("My Classes")).toBeInTheDocument();
    expect(screen.getByText("Today's Periods")).toBeInTheDocument();
    // "Pending Grading" appears on the quick-access card and the section heading
    expect(screen.getAllByText("Pending Grading").length).toBeGreaterThan(0);
    expect(screen.getByText("Unread Messages")).toBeInTheDocument();
  });

  test("shows empty states when there is nothing to show", async () => {
    renderWithProviders(<TeacherDashboard />);
    expect(await screen.findByText("All caught up!")).toBeInTheDocument();
    expect(screen.getByText("No conferences today")).toBeInTheDocument();
    expect(screen.getByText("No messages yet")).toBeInTheDocument();
    expect(screen.getByText("No classes scheduled today")).toBeInTheDocument();
  });

  test("renders pending grading assessments with pending counts", async () => {
    (api.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes("gradebook/assessments"))
        return Promise.resolve({ results: [mockAssessment] });
      if (url.includes("gradebook/submissions")) {
        // One ungraded + one graded submission → 1 pending
        return Promise.resolve({ results: [{ marks_obtained: null }, { marks_obtained: 8 }] });
      }
      if (url.includes("teacher-schedule")) return Promise.resolve([]);
      if (url.includes("messages/inbox")) return Promise.resolve([]);
      return Promise.resolve({ results: [] });
    });
    renderWithProviders(<TeacherDashboard />);
    expect(await screen.findByText("Algebra Quiz")).toBeInTheDocument();
    expect(screen.getByText("1 pending")).toBeInTheDocument();
  });

  test("renders today's booked conferences and unread message previews", async () => {
    (api.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes("conference-slots")) return Promise.resolve({ results: [mockConference] });
      if (url.includes("messages/inbox")) return Promise.resolve([mockThread]);
      if (url.includes("teacher-schedule")) return Promise.resolve([]);
      return Promise.resolve({ results: [] });
    });
    renderWithProviders(<TeacherDashboard />);
    expect(await screen.findByText("Alice Johnson")).toBeInTheDocument();
    expect(screen.getByText("Jane Smith")).toBeInTheDocument();
    expect(screen.getByText("Is the homework due Friday?")).toBeInTheDocument();
  });
});
