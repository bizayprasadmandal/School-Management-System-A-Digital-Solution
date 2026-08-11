/**
 * Teacher AssignmentsPage — smoke + grading-modal tests.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import AssignmentsPage from "./AssignmentsPage";
import { useAuthStore } from "../../store/authStore";
import {
  useTeacherAssignmentList,
  useTeacherAssessments,
  useCreateAssessment,
  useAssignmentSubmissions,
  useGradeSubmission,
} from "../../api/hooks";
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
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn() },
}));

jest.mock("../../api/hooks", () => ({
  useTeacherAssignmentList: jest.fn(),
  useTeacherAssessments: jest.fn(),
  useCreateAssessment: jest.fn(),
  useAssignmentSubmissions: jest.fn(),
  useGradeSubmission: jest.fn(),
}));

const mockAssessment = {
  id: 1,
  title: "Algebra Quiz",
  subject_name: "Mathematics",
  classroom_name: "Grade 5 5A",
  due_date: "2024-06-20",
  assessment_type: "quiz",
};

describe("Teacher AssignmentsPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "teacher" }) });
    (useTeacherAssignmentList as jest.Mock).mockReturnValue({ data: [] });
    (useTeacherAssessments as jest.Mock).mockReturnValue({
      data: { results: [mockAssessment] },
      isLoading: false,
    });
    (useCreateAssessment as jest.Mock).mockReturnValue({ mutate: jest.fn(), isPending: false });
    (useAssignmentSubmissions as jest.Mock).mockReturnValue({
      data: { results: [] },
      isLoading: false,
    });
    (useGradeSubmission as jest.Mock).mockReturnValue({
      mutateAsync: jest.fn().mockResolvedValue({}),
      isPending: false,
    });
  });

  test("renders the heading and lists teacher assessments", async () => {
    renderWithProviders(<AssignmentsPage />);
    expect(screen.getByRole("heading", { name: "Assignments" })).toBeInTheDocument();
    expect(await screen.findByText("Algebra Quiz")).toBeInTheDocument();
  });

  /** Expand the assessment row so the Grade Submissions action appears. */
  async function openGradeModal(user: ReturnType<typeof userEvent.setup>) {
    await user.click(await screen.findByRole("button", { name: /Algebra Quiz/i }));
    await user.click(await screen.findByRole("button", { name: /Grade Submissions/i }));
  }

  test("opens the grade modal and shows the empty submission state", async () => {
    const user = userEvent.setup();
    renderWithProviders(<AssignmentsPage />);
    await openGradeModal(user);
    // Heading role avoids the now-hidden "Grade Submissions" action button
    expect(screen.getByRole("heading", { name: "Grade Submissions" })).toBeInTheDocument();
    expect(await screen.findByText("No submissions yet")).toBeInTheDocument();
  });

  test("grades a submission with marks and feedback", async () => {
    const grade = jest.fn().mockResolvedValue({});
    (useGradeSubmission as jest.Mock).mockReturnValue({ mutateAsync: grade, isPending: false });
    (useAssignmentSubmissions as jest.Mock).mockReturnValue({
      data: {
        results: [
          {
            id: 9,
            student_name: "Alice Johnson",
            status: "submitted",
            marks_obtained: null,
            submitted_at: "2024-06-19T10:00:00Z",
          },
        ],
      },
      isLoading: false,
    });

    const user = userEvent.setup();
    renderWithProviders(<AssignmentsPage />);
    await openGradeModal(user);

    await screen.findByRole("heading", { name: "Grade Submissions" });
    // The ungraded marks cell is the only number input while the modal is open
    const marksInput = document.querySelector('input[type="number"]') as HTMLInputElement;
    await user.type(marksInput, "85");
    await user.click(screen.getByRole("button", { name: "Grade" }));

    expect(grade).toHaveBeenCalledWith(expect.objectContaining({ id: 9, marks_obtained: 85 }));
  });
});
