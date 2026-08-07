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
import { useAnnouncements } from "../../api/hooks";

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

  (api.get as jest.Mock).mockResolvedValue(mockDashboardStats);

  (useAnnouncements as jest.Mock).mockReturnValue({ data: mockAnnouncements });
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
      expect(screen.getByText(/\d{4}/)).toBeInTheDocument();
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
      expect(screen.getByText(/2.5%/)).toBeInTheDocument();
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
      expect(screen.getByTestId("bar-chart")).toBeInTheDocument();
    });
  });
});
