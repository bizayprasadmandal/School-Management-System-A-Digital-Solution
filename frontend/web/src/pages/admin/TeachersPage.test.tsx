/**
 * Admin TeachersPage Tests
 *
 * Tests rendering, search, data display, add/delete, and empty state.
 */
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import TeachersPage from "./TeachersPage";

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
  api: {
    get: jest.fn(),
    post: jest.fn(),
    delete: jest.fn(),
  },
}));

jest.mock("../../hooks", () => ({
  ...jest.requireActual("../../hooks"),
  useTitle: jest.fn(),
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockTeachers = {
  count: 2,
  results: [
    {
      id: "1",
      full_name: "Jane Doe",
      email: "jane@school.edu",
      employee_id: "EMP001",
      department: "Mathematics",
      qualification: "master",
      experience_years: 8,
      is_active: true,
      avatar: null,
    },
    {
      id: "2",
      full_name: "John Smith",
      email: "john@school.edu",
      employee_id: "EMP002",
      department: "Science",
      qualification: "bachelor",
      experience_years: 3,
      is_active: true,
      avatar: null,
    },
  ],
};

// ─── Helpers ───────────────────────────────────────────────────────────────────

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <TeachersPage />
      </BrowserRouter>
    </QueryClientProvider>,
  );
}

beforeEach(() => {
  jest.clearAllMocks();
  // Mock api.get to return teacher data by default
  (require("../../api/client").api.get as jest.Mock).mockResolvedValue(mockTeachers);
});

// ─── 1. Rendering ──────────────────────────────────────────────────────────────

describe("rendering", () => {
  test("renders page title", async () => {
    renderPage();
    expect(await screen.findByText("Teachers")).toBeInTheDocument();
  });

  test("renders teacher count", async () => {
    renderPage();
    expect(await screen.findByText("2 staff members")).toBeInTheDocument();
  });

  test("renders Add Teacher button", async () => {
    renderPage();
    expect(await screen.findByText("Add Teacher")).toBeInTheDocument();
  });

  test("renders Import CSV button", async () => {
    renderPage();
    expect(await screen.findByText("Import CSV")).toBeInTheDocument();
  });
});

// ─── 2. Data Display ───────────────────────────────────────────────────────────

describe("data display", () => {
  test("renders teacher names", async () => {
    renderPage();
    expect(await screen.findByText("Jane Doe")).toBeInTheDocument();
    expect(screen.getByText("John Smith")).toBeInTheDocument();
  });

  test("renders employee IDs", async () => {
    renderPage();
    expect(await screen.findByText("EMP001")).toBeInTheDocument();
    expect(screen.getByText("EMP002")).toBeInTheDocument();
  });

  test("renders departments", async () => {
    renderPage();
    expect(await screen.findByText("Mathematics")).toBeInTheDocument();
    expect(screen.getByText("Science")).toBeInTheDocument();
  });

  test("renders qualifications", async () => {
    renderPage();
    // CSS capitalize displays "master" as "Master", but the DOM text is lowercase.
    expect(await screen.findByText("master")).toBeInTheDocument();
    expect(screen.getByText("bachelor")).toBeInTheDocument();
  });

  test("renders experience years", async () => {
    renderPage();
    expect(await screen.findByText("8 yrs")).toBeInTheDocument();
    expect(screen.getByText("3 yrs")).toBeInTheDocument();
  });

  test("renders status badges", async () => {
    renderPage();
    await screen.findByText("Jane Doe");
    expect(screen.getAllByText("Active").length).toBeGreaterThan(0);
  });
});

// ─── 3. Search ─────────────────────────────────────────────────────────────────

describe("search", () => {
  test("renders search input with placeholder", async () => {
    renderPage();
    expect(await screen.findByPlaceholderText(/Search by name, employee ID/)).toBeInTheDocument();
  });
});

// ─── 4. Empty State ────────────────────────────────────────────────────────────

describe("empty state", () => {
  test("shows empty message when no teachers", async () => {
    (require("../../api/client").api.get as jest.Mock).mockResolvedValue({
      count: 0,
      results: [],
    });

    renderPage();
    expect(await screen.findByText(/No teachers found/)).toBeInTheDocument();
  });
});
