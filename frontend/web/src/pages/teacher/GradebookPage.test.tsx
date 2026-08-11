/**
 * Teacher GradebookPage — smoke + grade-change approval banner tests
 *
 * Verifies the page renders, the subject selector is driven by exam
 * schedules, and that submitting grades for a published exam surfaces the
 * "awaiting admin approval" banner + toast instead of a plain save.
 */
import React from "react";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import GradebookPage from "./GradebookPage";
import { api } from "../../api/client";
import { useCurrentAcademicYear, useExams, useClassrooms, useSubmitGrades } from "../../api/hooks";
import { queryClient, renderWithProviders } from "../../testUtils";

// ─── Mocks ────────────────────────────────────────────────────────────────────

jest.mock("react-hot-toast", () => ({
  __esModule: true,
  default: { success: jest.fn(), error: jest.fn() },
}));

jest.mock("../../api/client", () => ({
  api: { get: jest.fn() },
}));

jest.mock("../../api/hooks", () => ({
  useCurrentAcademicYear: jest.fn(),
  useExams: jest.fn(),
  useClassrooms: jest.fn(),
  useSubmitGrades: jest.fn(),
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockYear = { id: 1, name: "2026-27", is_current: true };

const mockExams = {
  results: [{ id: "exam-1", name: "Midterm 2026", exam_type_name: "Term Exam" }],
};

const mockClassrooms = {
  results: [{ id: 5, name: "5A", grade_name: "Grade 5" }],
};

const mockSchedules = [
  {
    id: 101,
    subject_name: "Mathematics",
    subject: 3,
    classroom: 5,
    classroom_name: "Grade 5 5A",
    max_marks: "100.00",
    passing_marks: "40.00",
  },
];

const mockStudents = [{ id: "stu-1", full_name: "Alice Johnson", admission_number: "ADM-001" }];

const submitGrades = jest.fn();

describe("Teacher GradebookPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    (useCurrentAcademicYear as jest.Mock).mockReturnValue({ data: mockYear, isLoading: false });
    (useExams as jest.Mock).mockReturnValue({ data: mockExams, isLoading: false });
    (useClassrooms as jest.Mock).mockReturnValue({ data: mockClassrooms, isLoading: false });
    (useSubmitGrades as jest.Mock).mockReturnValue({
      mutateAsync: submitGrades,
      isPending: false,
    });
    (api.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes("/schedules/")) return Promise.resolve(mockSchedules);
      if (url.includes("/students/")) return Promise.resolve(mockStudents);
      return Promise.resolve([]);
    });
  });

  test("renders the heading and subject selector options", async () => {
    renderWithProviders(<GradebookPage />);
    expect(screen.getByRole("heading", { name: "Gradebook" })).toBeInTheDocument();

    const selects = screen.getAllByRole("combobox");
    // Exam, Classroom, Subject (in DOM order)
    await userEvent.selectOptions(selects[0], "exam-1");
    await userEvent.selectOptions(selects[1], "5");
    await waitFor(() => {
      expect(screen.getByRole("option", { name: "Mathematics" })).toBeInTheDocument();
    });
  });

  test("shows pending-approval banner when grades land on a published exam", async () => {
    submitGrades.mockResolvedValue({ graded: 1, pending_approval: 1 });

    renderWithProviders(<GradebookPage />);
    const selects = screen.getAllByRole("combobox");
    await userEvent.selectOptions(selects[0], "exam-1");
    await userEvent.selectOptions(selects[1], "5");
    await waitFor(() => screen.getByRole("option", { name: "Mathematics" }));
    await userEvent.selectOptions(selects[2], "101");

    // Wait for the student row, enter marks, and save.
    const marksInput = await screen.findByPlaceholderText("—");
    await userEvent.type(marksInput, "85");
    await userEvent.click(screen.getByText("Save Grades"));

    expect(submitGrades).toHaveBeenCalledWith({
      exam_schedule_id: 101,
      grades: [expect.objectContaining({ student_id: "stu-1", marks_obtained: 85 })],
    });

    await waitFor(() => {
      expect(screen.getByText("1 grade change awaiting admin approval")).toBeInTheDocument();
    });
  });
});
