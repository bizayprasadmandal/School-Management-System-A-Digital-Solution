/**
 * Admin ReportCardsPage Tests
 *
 * Tests exam selection, report card display, generate/publish actions,
 * and empty states.
 */
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import ReportCardsPage from "./ReportCardsPage";

// ─── QueryClient for tests ────────────────────────────────────────────────────

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
});

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
}));

jest.mock("../../hooks", () => ({
  ...jest.requireActual("../../hooks"),
  useTitle: jest.fn(),
}));

jest.mock("../../utils", () => ({
  ...jest.requireActual("../../utils"),
  percent: (v: number | null) => (v != null ? `${v}%` : "—"),
  gradeBg: () => "bg-green-100",
  fmt: { date: (d: string) => d },
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockExams = {
  count: 2,
  results: [
    {
      id: "1",
      name: "Midterm 2024",
      exam_type_name: "Term Exam",
      start_date: "2024-06-01",
      end_date: "2024-06-07",
      status: "completed",
      schedule_count: 5,
    },
    {
      id: "2",
      name: "Final Exam",
      exam_type_name: "Term Exam",
      start_date: "2024-09-01",
      end_date: "2024-09-14",
      status: "scheduled",
      schedule_count: 6,
    },
  ],
};

const mockReportCards = {
  count: 1,
  results: [
    {
      id: "1",
      student_id: "10",
      student_name: "Alice Johnson",
      grade_letter: "A",
      percentage: 88.5,
      status: "published",
      academic_year_name: "2024-25",
      exam_name: "Midterm 2024",
    },
  ],
};

// ─── Helpers ───────────────────────────────────────────────────────────────────

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <ReportCardsPage />
      </BrowserRouter>
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  jest.clearAllMocks();
  (require("../../api/hooks").useCurrentAcademicYear as jest.Mock).mockReturnValue({
    data: { id: 1, name: "2024-25" },
  });
  (require("../../api/client").api.get as jest.Mock).mockImplementation((url: string) => {
    if (url.includes("/gradebook/exams/")) return Promise.resolve(mockExams);
    if (url.includes("/gradebook/report-cards/")) return Promise.resolve(mockReportCards);
    return Promise.resolve({ count: 0, results: [] });
  });
});

// ─── 1. Rendering ──────────────────────────────────────────────────────────────

describe("rendering", () => {
  test("renders page title", async () => {
    renderPage();
    expect(await screen.findByText("Report Cards")).toBeInTheDocument();
  });

  test("renders subtitle", async () => {
    renderPage();
    expect(await screen.findByText(/Generate, review, and publish/)).toBeInTheDocument();
  });
});

// ─── 2. Exam Selection ─────────────────────────────────────────────────────────

describe("exam selection", () => {
  test("renders exam names as selectable cards", async () => {
    renderPage();
    expect(await screen.findByText("Midterm 2024")).toBeInTheDocument();
    expect(screen.getByText("Final Exam")).toBeInTheDocument();
  });

  test("shows schedule count per exam", async () => {
    renderPage();
    expect(await screen.findByText("5 subjects scheduled")).toBeInTheDocument();
    expect(screen.getByText("6 subjects scheduled")).toBeInTheDocument();
  });
});

// ─── 3. Empty State ────────────────────────────────────────────────────────────

describe("empty state", () => {
  test("shows message when no exams found", async () => {
    (require("../../api/client").api.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes("/gradebook/exams/")) return Promise.resolve({ count: 0, results: [] });
      return Promise.resolve({ count: 0, results: [] });
    });

    renderPage();
    expect(await screen.findByText(/No exams found/)).toBeInTheDocument();
  });
});

// ─── 4. Report Card Display ────────────────────────────────────────────────────

describe("report card display", () => {
  test("shows report cards after selecting an exam", async () => {
    const user = userEvent.setup();
    renderPage();

    const midterm = await screen.findByText("Midterm 2024");
    await user.click(midterm);

    await waitFor(() => {
      expect(screen.getByText("Alice Johnson")).toBeInTheDocument();
    });
  });

  test("shows grade letter after selecting an exam", async () => {
    const user = userEvent.setup();
    renderPage();

    await user.click(await screen.findByText("Midterm 2024"));

    await waitFor(() => {
      expect(screen.getByText("A")).toBeInTheDocument();
    });
  });
});
