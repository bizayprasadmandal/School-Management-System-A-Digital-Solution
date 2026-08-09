/**
 * Admin ExamsPage — smoke tests
 *
 * Renders with a mocked current academic year and exams list; verifies the
 * heading and that exam rows/cards render.
 */
import React from "react";
import { screen } from "@testing-library/react";
import ExamsPage from "./ExamsPage";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { useCurrentAcademicYear } from "../../api/hooks";
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
  useCurrentAcademicYear: jest.fn(),
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

describe("Admin ExamsPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser() });
    (useCurrentAcademicYear as jest.Mock).mockReturnValue({ data: mockYear, isLoading: false });
    (api.get as jest.Mock).mockResolvedValue(mockExams);
  });

  test("renders the heading and the exam list", async () => {
    renderWithProviders(<ExamsPage />);
    expect(screen.getByRole("heading", { name: "Examinations" })).toBeInTheDocument();
    expect(await screen.findByText("Midterm 2026")).toBeInTheDocument();
  });
});
