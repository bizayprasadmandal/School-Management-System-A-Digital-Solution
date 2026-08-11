/**
 * Admin ExamsPage — smoke tests
 *
 * Renders with a mocked current academic year and exams list; verifies the
 * heading and that exam rows/cards render.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import ExamsPage from "./ExamsPage";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import {
  useCurrentAcademicYear,
  useGradeChangeProposals,
  useApproveGradeChangeProposal,
  useRejectGradeChangeProposal,
} from "../../api/hooks";
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
  useCurrentAcademicYear: jest.fn(),
  useGradeChangeProposals: jest.fn(),
  useApproveGradeChangeProposal: jest.fn(),
  useRejectGradeChangeProposal: jest.fn(),
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockYear = { id: 1, name: "2026-27", is_current: true };

const mockExams = {
  count: 1,
  results: [
    {
      id: "1",
      name: "Midterm 2026",
      exam_type_name: "Term Exam",
      start_date: "2026-06-01",
      end_date: "2026-06-07",
      status: "ongoing",
    },
  ],
};

const mockProposals = {
  count: 1,
  results: [
    {
      id: "p1",
      student: "s1",
      student_name: "Jane Doe",
      admission_number: "ADM-001",
      exam_schedule: 1,
      subject: "Mathematics",
      exam: "Midterm 2026",
      max_marks: 100,
      action: "update",
      status: "proposed",
      marks_obtained_new: 90,
      marks_obtained_current: 50,
      is_absent_new: false,
      remarks_new: "",
      reason: "Recheck found a totaling error",
      proposed_by: "Sarah Teacher",
      proposed_at: "2026-08-10T10:00:00Z",
      reviewed_by: null,
      reviewed_at: null,
      review_notes: "",
    },
  ],
};

describe("Admin ExamsPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser() });
    (useCurrentAcademicYear as jest.Mock).mockReturnValue({ data: mockYear, isLoading: false });
    (api.get as jest.Mock).mockResolvedValue(mockExams);
    (useGradeChangeProposals as jest.Mock).mockReturnValue({
      data: { count: 0, results: [] },
      isLoading: false,
    });
    (useApproveGradeChangeProposal as jest.Mock).mockReturnValue({
      mutate: jest.fn(),
      isPending: false,
    });
    (useRejectGradeChangeProposal as jest.Mock).mockReturnValue({
      mutate: jest.fn(),
      isPending: false,
    });
  });

  test("renders the heading and the exam list", async () => {
    renderWithProviders(<ExamsPage />);
    expect(screen.getByRole("heading", { name: "Examinations" })).toBeInTheDocument();
    expect(await screen.findByText("Midterm 2026")).toBeInTheDocument();
  });

  test("shows empty state when no proposals are pending", async () => {
    renderWithProviders(<ExamsPage />);
    expect(await screen.findByText("No grade changes awaiting approval")).toBeInTheDocument();
  });

  test("renders pending proposals with current/new marks", async () => {
    (useGradeChangeProposals as jest.Mock).mockReturnValue({
      data: mockProposals,
      isLoading: false,
    });
    renderWithProviders(<ExamsPage />);
    expect(await screen.findByText("Jane Doe")).toBeInTheDocument();
    expect(screen.getByText("Mathematics — Midterm 2026")).toBeInTheDocument();
    expect(screen.getByText("1 awaiting review")).toBeInTheDocument();
    // current → new marks render as separate spans
    expect(screen.getByText("50")).toBeInTheDocument();
    expect(screen.getByText("90")).toBeInTheDocument();
  });

  test("approving a proposal calls the approve mutation", async () => {
    (useGradeChangeProposals as jest.Mock).mockReturnValue({
      data: mockProposals,
      isLoading: false,
    });
    const approveMutate = jest.fn();
    (useApproveGradeChangeProposal as jest.Mock).mockReturnValue({
      mutate: approveMutate,
      isPending: false,
    });
    renderWithProviders(<ExamsPage />);
    await screen.findByText("Jane Doe");
    await userEvent.click(screen.getByText("Approve"));
    expect(approveMutate).toHaveBeenCalledWith("p1", expect.any(Object));
  });

  test("rejecting a proposal records the review note", async () => {
    (useGradeChangeProposals as jest.Mock).mockReturnValue({
      data: mockProposals,
      isLoading: false,
    });
    const rejectMutate = jest.fn();
    (useRejectGradeChangeProposal as jest.Mock).mockReturnValue({
      mutate: rejectMutate,
      isPending: false,
    });
    window.prompt = jest.fn(() => "Incorrect re-mark") as any;
    renderWithProviders(<ExamsPage />);
    await screen.findByText("Jane Doe");
    await userEvent.click(screen.getByText("Reject"));
    expect(rejectMutate).toHaveBeenCalledWith(
      { id: "p1", notes: "Incorrect re-mark" },
      expect.any(Object),
    );
  });
});
