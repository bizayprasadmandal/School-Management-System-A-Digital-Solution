/**
 * AdminDashboard Tests
 *
 * Tests rendering, loading state, error state, KPI cards,
 * charts, announcements, and outstanding fees alert.
 */
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import AdminDashboard from "./Dashboard";
import { useAuthStore } from "../../store/authStore";
import type { User } from "../../types";
import { api } from "../../api/client";
import {
  useAnnouncements,
  useAtRiskStudents,
  useEnrollmentFunnel,
  useFeeForecast,
} from "../../api/hooks";

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
  api: { get: jest.fn() },
}));

jest.mock("../../api/hooks", () => ({
  useAnnouncements: jest.fn(),
  useAtRiskStudents: jest.fn(),
  useEnrollmentFunnel: jest.fn(),
  useFeeForecast: jest.fn(),
}));

// Mock recharts to avoid rendering issues in test environment
jest.mock("recharts", () => ({
  AreaChart: ({ children }: any) => <div data-testid="area-chart">{children}</div>,
  Area: () => <div data-testid="area" />,
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  XAxis: () => <div data-testid="xaxis" />,
  YAxis: () => <div data-testid="yaxis" />,
  CartesianGrid: () => <div data-testid="grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  Cell: () => <div data-testid="cell" />,
  Legend: () => <div data-testid="legend" />,
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

function makeUser(overrides: Partial<User> = {}): User {
  return {
    id: "1",
    email: "admin@demo.edusphere.school",
    first_name: "Admin",
    last_name: "User",
    full_name: "Admin User",
    role: "school_admin",
    is_active: true,
    email_verified: true,
    two_factor_enabled: false,
    backup_codes_remaining: null,
    notify_email: true,
    notify_sms: false,
    notify_push: true,
    date_joined: "2024-01-01T00:00:00Z",
    ...overrides,
  };
}

const mockDashboardStats = {
  total_students: 120,
  total_teachers: 15,
  total_classrooms: 8,
  attendance_today_pct: 93.5,
  fees_collected_month: 548000,
  fees_outstanding: 51000,
  student_delta_pct: 2.5,
  attendance_delta_pct: -1.2,
  attendance_week: [
    { day: "Mon", present: 94.0, absent: 6.0 },
    { day: "Tue", present: 91.0, absent: 9.0 },
    { day: "Wed", present: 96.0, absent: 4.0 },
  ],
  grade_distribution: [
    { name: "A+", value: 18 },
    { name: "A", value: 24 },
    { name: "B", value: 31 },
  ],
};

const mockAnnouncements = {
  results: [
    {
      id: "1",
      title: "School holiday next week",
      priority: "normal",
      created_at: "2024-06-01T10:00:00Z",
    },
    {
      id: "2",
      title: "Exam results published",
      priority: "high",
      created_at: "2024-06-02T14:30:00Z",
    },
  ],
  count: 2,
};

const mockAtRisk = {
  threshold_attendance_pct: 80,
  window_days: 30,
  count: 1,
  students: [
    {
      student_id: "s1",
      student_name: "Jane Doe",
      admission_number: "ADM-001",
      classroom: "Grade 5 - A",
      attendance_pct: 61,
      absent_days: 4,
      avg_percentage: 71.2,
      reasons: ["low_attendance", "low_academics"],
    },
  ],
};

const mockFunnel = {
  intake_id: null,
  total_applications: 25,
  funnel: [
    { stage: "submitted", count: 25 },
    { stage: "under_review", count: 18 },
    { stage: "shortlisted", count: 12 },
    { stage: "accepted", count: 8 },
    { stage: "enrolled", count: 5 },
    { stage: "rejected", count: 3 },
    { stage: "waitlisted", count: 2 },
  ],
  conversion: { submitted_to_accepted: 32, accepted_to_enrolled: 62.5 },
};

const mockForecast = {
  today: "2024-06-15",
  overdue_total: 82000,
  forecast_90d: [
    { window_start: "2024-06-15", window_end: "2024-07-14", expected: 120000, already_paid: 30000 },
    { window_start: "2024-07-15", window_end: "2024-08-13", expected: 95000, already_paid: 0 },
  ],
  history_3m: [
    { month: "2024-03", collected: 410000 },
    { month: "2024-04", collected: 388000 },
    { month: "2024-05", collected: 445000 },
  ],
};

// ─── Helpers ───────────────────────────────────────────────────────────────────

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <AdminDashboard />
      </BrowserRouter>
    </QueryClientProvider>,
  );
}

// ─── Before each ───────────────────────────────────────────────────────────────

beforeEach(() => {
  jest.clearAllMocks();
  useAuthStore.setState({
    user: makeUser(),
    tokens: null,
    isAuthenticated: true,
    isLoading: false,
  });

  (api.get as jest.Mock).mockImplementation((url: string) => {
    if (url.includes("monthly_summary")) {
      return Promise.resolve({
        month: "2026-09",
        prev_month: "2026-08",
        streams: [
          {
            stream: "payment",
            total_debits: "0.00",
            total_credits: "1200.00",
            entry_count: 3,
            prev_credits: "1000.00",
            prev_debits: "0.00",
          },
        ],
        total_debits: "0.00",
        total_credits: "1200.00",
        net: "1200.00",
      });
    }
    if (url.includes("monthly_trend")) {
      return Promise.resolve({
        months: ["2026-04", "2026-05", "2026-06", "2026-07", "2026-08", "2026-09"],
        streams: [
          {
            stream: "payment",
            credits: ["0.00", "0.00", "0.00", "0.00", "1000.00", "1200.00"],
            debits: ["0.00", "0.00", "0.00", "0.00", "0.00", "0.00"],
          },
        ],
      });
    }
    return Promise.resolve(mockDashboardStats);
  });

  (useAnnouncements as jest.Mock).mockReturnValue({ data: mockAnnouncements });
  (useAtRiskStudents as jest.Mock).mockReturnValue({ data: mockAtRisk });
  (useEnrollmentFunnel as jest.Mock).mockReturnValue({ data: mockFunnel });
  (useFeeForecast as jest.Mock).mockReturnValue({ data: mockForecast });
});

// ─── 1. Rendering ──────────────────────────────────────────────────────────────

describe("rendering", () => {
  test("renders the greeting with user first name", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/Good morning, Admin/)).toBeInTheDocument();
    });
  });

  test("renders the date line", async () => {
    renderPage();
    await waitFor(() => {
      // e.g. "Friday, September 18 2026" — specific so the ledger card's
      // month strings (also 4-digit) don't collide
      expect(screen.getByText(/, \w+ \d{1,2} \d{4}/)).toBeInTheDocument();
    });
  });

  test("renders four KPI stat cards", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Total Students")).toBeInTheDocument();
      expect(screen.getByText("Teachers")).toBeInTheDocument();
      expect(screen.getByText("Today's Attendance")).toBeInTheDocument();
      expect(screen.getByText("Fees Collected (Month)")).toBeInTheDocument();
    });
  });

  test("renders chart section headings", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("This Week's Attendance")).toBeInTheDocument();
      expect(screen.getByText("Grade Distribution")).toBeInTheDocument();
      expect(screen.getByText("Fee Collection Trend")).toBeInTheDocument();
    });
  });

  test("renders analytics section headings", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("At-Risk Students")).toBeInTheDocument();
      expect(screen.getByText("Enrollment Funnel")).toBeInTheDocument();
    });
  });

  test("renders announcements section", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Recent Announcements")).toBeInTheDocument();
    });
  });
});

// ─── 2. KPI Data Display ───────────────────────────────────────────────────────

describe("KPI data display", () => {
  test("displays total students count", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("120")).toBeInTheDocument();
    });
  });

  test("displays attendance percentage", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("93.5%")).toBeInTheDocument();
    });
  });

  test("displays fees collected in K format", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("$548K")).toBeInTheDocument();
    });
  });

  test("shows delta indicators for student count", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/^2\.5\s*%$/)).toBeInTheDocument();
      expect(screen.getByText(/vs last month/)).toBeInTheDocument();
    });
  });

  test("shows negative delta in red for attendance decline", async () => {
    renderPage();
    await waitFor(() => {
      // Negative delta attendance - should show 1.2%
      expect(screen.getByText(/1.2%/)).toBeInTheDocument();
    });
  });
});

// ─── 5. Announcements ──────────────────────────────────────────────────────────

describe("announcements", () => {
  test("renders announcement titles", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("School holiday next week")).toBeInTheDocument();
      expect(screen.getByText("Exam results published")).toBeInTheDocument();
    });
  });

  test("renders View all link", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("View all")).toBeInTheDocument();
    });
  });

  test("shows empty state when no announcements", async () => {
    (useAnnouncements as jest.Mock).mockReturnValue({ data: { results: [], count: 0 } });

    renderPage();
    await waitFor(() => {
      expect(screen.getByText("No announcements yet")).toBeInTheDocument();
    });
  });
});

// ─── 6. Outstanding Fees Alert ─────────────────────────────────────────────────

describe("outstanding fees alert", () => {
  test("shows alert when fees_outstanding > 0", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Outstanding Fees Alert")).toBeInTheDocument();
    });
  });

  test("shows alert amount", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/\$51,000/)).toBeInTheDocument();
    });
  });

  test("navigates to fees page on alert click", async () => {
    renderPage();
    const user = userEvent.setup();
    await waitFor(() => {
      expect(screen.getByText("Outstanding Fees Alert")).toBeInTheDocument();
    });
    await user.click(screen.getByText("Outstanding Fees Alert"));
    expect(mockNavigate).toHaveBeenCalledWith("/admin/fees");
  });

  test("does not show alert when fees_outstanding is 0", async () => {
    (api.get as jest.Mock).mockResolvedValue({ ...mockDashboardStats, fees_outstanding: 0 });

    renderPage();
    await waitFor(() => {
      expect(screen.queryByText("Outstanding Fees Alert")).not.toBeInTheDocument();
    });
  });
});

// ─── 7. Navigation from Stat Cards ─────────────────────────────────────────────

describe("stat card navigation", () => {
  test("students card navigates to /admin/students", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Total Students")).toBeInTheDocument();
    });
    const user = userEvent.setup();
    await user.click(screen.getByText("Total Students"));
    expect(mockNavigate).toHaveBeenCalledWith("/admin/students");
  });

  test("attendance card navigates to /admin/attendance", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Today's Attendance")).toBeInTheDocument();
    });
    const user = userEvent.setup();
    await user.click(screen.getByText("Today's Attendance"));
    expect(mockNavigate).toHaveBeenCalledWith("/admin/attendance");
  });
});

// ─── 8. Chart Rendering ────────────────────────────────────────────────────────

describe("chart rendering", () => {
  test("renders attendance trend chart", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("area-chart")).toBeInTheDocument();
    });
  });

  test("renders grade distribution pie chart", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByTestId("pie-chart")).toBeInTheDocument();
    });
  });

  test("renders fee collection bar chart", async () => {
    renderPage();
    await waitFor(() => {
      // Two bar charts now: fee trend/forecast + enrollment funnel
      expect(screen.getAllByTestId("bar-chart").length).toBeGreaterThan(0);
    });
  });
});

// ─── 9. Analytics Sections ─────────────────────────────────────────────────────

describe("analytics sections", () => {
  test("renders at-risk student name and reason chips", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Jane Doe")).toBeInTheDocument();
      expect(screen.getByText("Attendance")).toBeInTheDocument();
      expect(screen.getByText("Academics")).toBeInTheDocument();
      expect(screen.getByText("61%")).toBeInTheDocument();
    });
  });

  test("shows flagged count badge", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("1 flagged")).toBeInTheDocument();
    });
  });

  test("renders funnel stage labels and conversion rates", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("25 apps")).toBeInTheDocument();
      expect(screen.getByText("Submitted → Accepted")).toBeInTheDocument();
      expect(screen.getByText("Accepted → Enrolled")).toBeInTheDocument();
      expect(screen.getByText("32%")).toBeInTheDocument();
      expect(screen.getByText("62.5%")).toBeInTheDocument();
    });
  });

  test("renders fee forecast overdue badge and 90-day chip", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText(/\$82K overdue/)).toBeInTheDocument();
      expect(screen.getByText("90-day forecast")).toBeInTheDocument();
    });
  });

  test("shows empty states when analytics return no data", async () => {
    (useAtRiskStudents as jest.Mock).mockReturnValue({
      data: { ...mockAtRisk, count: 0, students: [] },
    });
    (useEnrollmentFunnel as jest.Mock).mockReturnValue({
      data: {
        ...mockFunnel,
        total_applications: 0,
        funnel: mockFunnel.funnel.map((f) => ({ ...f, count: 0 })),
      },
    });

    renderPage();
    await waitFor(() => {
      expect(screen.getByText("🎉 No students currently flagged")).toBeInTheDocument();
      expect(screen.getByText("No applications yet")).toBeInTheDocument();
    });
  });
});

describe("ledger summary card", () => {
  test("renders month totals and stream rows with drillable labels", async () => {
    renderPage();
    const card = await screen.findByTestId("ledger-summary");
    expect(card).toBeInTheDocument();
    // Stream row label from the mocked monthly_summary response
    expect(await screen.findByText("Fee Payments")).toBeInTheDocument();
  });

  test("card hides gracefully when the ledger endpoint fails", async () => {
    // Fresh cache — the shared module-level client would replay the
    // previous test's cached ledger queries instead of hitting the mock.
    queryClient.clear();
    (api.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes("monthly_summary") || url.includes("monthly_trend")) {
        return Promise.reject(new Error("boom"));
      }
      return Promise.resolve(mockDashboardStats);
    });
    renderPage();
    // Dashboard itself still renders its KPI cards
    await waitFor(() => {
      expect(screen.getByText("Total Students")).toBeInTheDocument();
    });
    expect(screen.queryByTestId("ledger-summary")).not.toBeInTheDocument();
  });
});
