/**
 * AccessDeniedPage Tests
 *
 * Tests rendering, role-aware suggestion cards, navigation links,
 * and unauthenticated fallback behavior.
 */
import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import AccessDeniedPage from "./AccessDeniedPage";
import { useAuthStore } from "../store/authStore";
import type { User } from "../types";

// ─── Mocks ────────────────────────────────────────────────────────────────────

const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

function makeUser(overrides: Partial<User> = {}): User {
  return {
    id: "1",
    email: "admin@school.edu",
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

// ─── Helpers ───────────────────────────────────────────────────────────────────

function renderPage() {
  return render(
    <BrowserRouter>
      <AccessDeniedPage />
    </BrowserRouter>
  );
}

// ─── Before each ───────────────────────────────────────────────────────────────

beforeEach(() => {
  jest.clearAllMocks();
  useAuthStore.setState({
    user: null,
    tokens: null,
    isAuthenticated: false,
    isLoading: false,
  });
});

// ─── 1. Rendering ──────────────────────────────────────────────────────────────

describe("rendering", () => {
  test("renders the 403 graphic and heading", () => {
    renderPage();
    expect(screen.getByText("403")).toBeInTheDocument();
    expect(screen.getByText("Access denied")).toBeInTheDocument();
  });

  test("renders the permission description", () => {
    renderPage();
    expect(
      screen.getByText(/you don't have the necessary permissions/i)
    ).toBeInTheDocument();
  });

  test("renders the copyright footer", () => {
    renderPage();
    expect(
      screen.getByText(new RegExp(`© ${new Date().getFullYear()} EduSphere`))
    ).toBeInTheDocument();
  });
});

// ─── 2. Unauthenticated user ───────────────────────────────────────────────────

describe("unauthenticated user", () => {
  test("shows Go to Dashboard and Go Back only (no Contact Admin)", () => {
    renderPage();

    // Two suggestion cards: Go to Dashboard, Go Back
    expect(screen.getByText("Go to Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Go Back")).toBeInTheDocument();
    expect(screen.queryByText("Contact Support")).not.toBeInTheDocument();
    expect(screen.queryByText("Contact Admin")).not.toBeInTheDocument();
  });

  test("Go to Dashboard links to /login when unauthenticated", () => {
    renderPage();
    const link = screen.getByText("Go to Dashboard").closest("a");
    expect(link).toHaveAttribute("href", "/login");
  });
});

// ─── 3. Admin users ────────────────────────────────────────────────────────────

describe.each([
  "school_admin" as const,
  "super_admin" as const,
  "accountant" as const,
])("admin user (%s)", (role) => {
  beforeEach(() => {
    useAuthStore.setState({
      user: makeUser({ role }),
      isAuthenticated: true,
    });
  });

  test("shows all three suggestion cards", () => {
    renderPage();
    expect(screen.getByText("Go to Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Go Back")).toBeInTheDocument();
    expect(screen.getByText("Contact Support")).toBeInTheDocument();
  });

  test("Go to Dashboard links to /admin", () => {
    renderPage();
    const link = screen.getByText("Go to Dashboard").closest("a");
    expect(link).toHaveAttribute("href", "/admin");
  });

  test("Contact Support links to /admin/settings", () => {
    renderPage();
    const link = screen.getByText("Contact Support").closest("a");
    expect(link).toHaveAttribute("href", "/admin/settings");
  });
});

// ─── 4. Teacher user ───────────────────────────────────────────────────────────

describe("teacher user", () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: makeUser({ role: "teacher", email: "teacher@school.edu" }),
      isAuthenticated: true,
    });
  });

  test("shows all three suggestion cards", () => {
    renderPage();
    expect(screen.getByText("Go to Dashboard")).toBeInTheDocument();
    expect(screen.getByText("Go Back")).toBeInTheDocument();
    expect(screen.getByText("Contact Admin")).toBeInTheDocument();
  });

  test("Go to Dashboard links to /teacher", () => {
    renderPage();
    const link = screen.getByText("Go to Dashboard").closest("a");
    expect(link).toHaveAttribute("href", "/teacher");
  });

  test("Contact Admin links to /teacher/messages", () => {
    renderPage();
    const link = screen.getByText("Contact Admin").closest("a");
    expect(link).toHaveAttribute("href", "/teacher/messages");
  });
});

// ─── 5. Student user ───────────────────────────────────────────────────────────

describe("student user", () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: makeUser({ role: "student", email: "student@school.edu" }),
      isAuthenticated: true,
    });
  });

  test("Go to Dashboard links to /student", () => {
    renderPage();
    const link = screen.getByText("Go to Dashboard").closest("a");
    expect(link).toHaveAttribute("href", "/student");
  });

  test("Contact Admin links to /student/messages", () => {
    renderPage();
    const link = screen.getByText("Contact Admin").closest("a");
    expect(link).toHaveAttribute("href", "/student/messages");
  });
});

// ─── 6. Parent user ────────────────────────────────────────────────────────────

describe("parent user", () => {
  beforeEach(() => {
    useAuthStore.setState({
      user: makeUser({ role: "parent", email: "parent@school.edu" }),
      isAuthenticated: true,
    });
  });

  test("Go to Dashboard links to /parent", () => {
    renderPage();
    const link = screen.getByText("Go to Dashboard").closest("a");
    expect(link).toHaveAttribute("href", "/parent");
  });

  test("Contact Admin links to /parent/messages", () => {
    renderPage();
    const link = screen.getByText("Contact Admin").closest("a");
    expect(link).toHaveAttribute("href", "/parent/messages");
  });
});

// ─── 7. Navigation ─────────────────────────────────────────────────────────────

describe("navigation", () => {
  test("Go Back button calls navigate(-1) on click", async () => {
    useAuthStore.setState({
      user: makeUser({ role: "teacher" }),
      isAuthenticated: true,
    });

    renderPage();
    const user = userEvent.setup();
    const backBtn = screen.getByText("Go Back");
    await user.click(backBtn);

    expect(mockNavigate).toHaveBeenCalledWith(-1);
  });
});
