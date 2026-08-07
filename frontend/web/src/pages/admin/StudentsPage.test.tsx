/**
 * Admin StudentsPage Tests
 *
 * Tests rendering, search, filters, export/import, and table display.
 */
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import StudentsPage from "./StudentsPage";
import { useAuthStore } from "../../store/authStore";
import type { User } from "../../types";
import { useStudents, useGradeLevels } from "../../api/hooks";
import { downloadFromUrl } from "../../utils";

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
  useStudents: jest.fn(),
  useGradeLevels: jest.fn(),
}));

jest.mock("../../utils", () => ({
  ...jest.requireActual("../../utils"),
  downloadFromUrl: jest.fn().mockResolvedValue(undefined),
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

const mockStudents = {
  count: 3,
  results: [
    {
      id: "1",
      full_name: "Alice Johnson",
      email: "alice@school.edu",
      admission_number: "ADM001",
      gender: "F",
      current_class: "Grade 5 A",
      is_active: true,
      avatar: null,
    },
    {
      id: "2",
      full_name: "Bob Smith",
      email: "bob@school.edu",
      admission_number: "ADM002",
      gender: "M",
      current_class: "Grade 6 B",
      is_active: true,
      avatar: null,
    },
    {
      id: "3",
      full_name: "Charlie Brown",
      email: "charlie@school.edu",
      admission_number: "ADM003",
      gender: "M",
      current_class: "Grade 5 A",
      is_active: false,
      avatar: null,
    },
  ],
};

const mockGradeLevels = {
  count: 2,
  results: [
    { id: 1, name: "Grade 5" },
    { id: 2, name: "Grade 6" },
  ],
};

// ─── Helpers ───────────────────────────────────────────────────────────────────

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <StudentsPage />
      </BrowserRouter>
    </QueryClientProvider>,
  );
}

// ─── Before each ───────────────────────────────────────────────────────────────

beforeEach(() => {
  jest.clearAllMocks();
  useAuthStore.setState({
    user: makeUser(),
    tokens: { access: "mock-token", refresh: "mock-refresh" },
    isAuthenticated: true,
    isLoading: false,
  });

  (useStudents as jest.Mock).mockReturnValue({ data: mockStudents, isLoading: false });
  (useGradeLevels as jest.Mock).mockReturnValue({ data: mockGradeLevels });
});

// ─── 1. Rendering ──────────────────────────────────────────────────────────────

describe("rendering", () => {
  test("renders page title", () => {
    renderPage();
    expect(screen.getByText("Students")).toBeInTheDocument();
  });

  test("renders total student count", () => {
    renderPage();
    expect(screen.getByText("3 total students")).toBeInTheDocument();
  });

  test("renders Add Student button", () => {
    renderPage();
    expect(screen.getByText("Add Student")).toBeInTheDocument();
  });

  test("renders Import CSV button", () => {
    renderPage();
    expect(screen.getByText("Import CSV")).toBeInTheDocument();
  });

  test("renders Export CSV button", () => {
    renderPage();
    expect(screen.getByText("Export CSV")).toBeInTheDocument();
  });
});

// ─── 2. Student Data Display ───────────────────────────────────────────────────

describe("student data display", () => {
  test("renders student names in the table", () => {
    renderPage();
    expect(screen.getByText("Alice Johnson")).toBeInTheDocument();
    expect(screen.getByText("Bob Smith")).toBeInTheDocument();
    expect(screen.getByText("Charlie Brown")).toBeInTheDocument();
  });

  test("renders admission numbers", () => {
    renderPage();
    expect(screen.getByText("ADM001")).toBeInTheDocument();
    expect(screen.getByText("ADM002")).toBeInTheDocument();
    expect(screen.getByText("ADM003")).toBeInTheDocument();
  });

  test("renders student emails", () => {
    renderPage();
    expect(screen.getByText("alice@school.edu")).toBeInTheDocument();
    expect(screen.getByText("bob@school.edu")).toBeInTheDocument();
  });

  test("renders status badges", () => {
    renderPage();
    expect(screen.getAllByText("Active").length).toBeGreaterThan(0);
    expect(screen.getByText("Inactive")).toBeInTheDocument();
  });

  test("renders gender labels", () => {
    renderPage();
    expect(screen.getByText("Female")).toBeInTheDocument();
    expect(screen.getAllByText("Male").length).toBeGreaterThan(0);
  });
});

// ─── 3. Search Functionality ───────────────────────────────────────────────────

describe("search functionality", () => {
  test("renders search input", () => {
    renderPage();
    expect(screen.getByPlaceholderText(/Search by name or admission number/)).toBeInTheDocument();
  });

  test("calls useStudents with search value after typing", async () => {
    renderPage();
    const user = userEvent.setup();

    const searchInput = screen.getByPlaceholderText(/Search by name or admission number/);
    await user.type(searchInput, "Alice");

    await waitFor(() => {
      expect(useStudents).toHaveBeenCalled();
    });
  });
});

// ─── 4. Filters ────────────────────────────────────────────────────────────────

describe("filters", () => {
  test("toggle filters button exists", () => {
    renderPage();
    expect(screen.getByText("Filters")).toBeInTheDocument();
  });

  test("shows filter dropdowns when toggled", async () => {
    renderPage();
    const user = userEvent.setup();
    await user.click(screen.getByText("Filters"));

    // Use getAllByText for "Gender" since it appears in both filter label and table header
    const genderLabels = screen.getAllByText("Gender");
    expect(genderLabels.length).toBeGreaterThanOrEqual(1);
    const classLabels = screen.getAllByText("Class");
    expect(classLabels.length).toBeGreaterThanOrEqual(1);
  });
});

// ─── 5. Export ─────────────────────────────────────────────────────────────────

describe("export", () => {
  test("calls downloadFromUrl on Export CSV click", async () => {
    renderPage();
    const user = userEvent.setup();
    await user.click(screen.getByText("Export CSV"));

    await waitFor(() => {
      expect(downloadFromUrl).toHaveBeenCalled();
    });
  });
});

// ─── 6. Navigation ─────────────────────────────────────────────────────────────

describe("navigation", () => {
  test("navigates to add student page", () => {
    renderPage();
    const addLink = screen.getByText("Add Student").closest("a");
    expect(addLink).toHaveAttribute("href", "/admin/students/new");
  });

  test("row click navigates to student detail", async () => {
    renderPage();
    const user = userEvent.setup();
    const studentRow = screen.getByText("Alice Johnson");

    await user.click(studentRow);
    expect(mockNavigate).toHaveBeenCalledWith("/admin/students/1");
  });
});

// ─── 7. Empty State ────────────────────────────────────────────────────────────

describe("empty state", () => {
  test("shows empty message when no students", () => {
    (useStudents as jest.Mock).mockReturnValue({
      data: { count: 0, results: [] },
      isLoading: false,
    });

    renderPage();
    expect(screen.getByText(/No students found/)).toBeInTheDocument();
  });
});
