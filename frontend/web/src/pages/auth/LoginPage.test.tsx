/**
 * LoginPage Tests
 *
 * Tests form rendering, validation, password toggle, successful login,
 * failed login with 401, and rate-limit (429) error handling.
 */
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import toast from "react-hot-toast";
import LoginPage from "./LoginPage";
import { api } from "../../api/client";
import { useAuthStore } from "../../store/authStore";

// ─── Mocks ────────────────────────────────────────────────────────────────────

// Mock react-router-dom's useNavigate
const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

// Mock react-hot-toast
jest.mock("react-hot-toast", () => ({
  __esModule: true,
  default: {
    success: jest.fn(),
    error: jest.fn(),
  },
}));

// Mock api client
jest.mock("../../api/client", () => ({
  api: {
    post: jest.fn(),
  },
}));

// ─── Helpers ───────────────────────────────────────────────────────────────────

const renderLoginPage = () =>
  render(
    <BrowserRouter>
      <LoginPage />
    </BrowserRouter>
  );

// ─── Before each ───────────────────────────────────────────────────────────────

beforeEach(() => {
  jest.clearAllMocks();

  // Reset auth store to default state
  useAuthStore.setState({
    user: null,
    tokens: null,
    isAuthenticated: false,
    isLoading: false,
  });
});

// ─── 1. Rendering ──────────────────────────────────────────────────────────────

describe("rendering", () => {
  test("renders the logo and heading", () => {
    renderLoginPage();
    expect(screen.getByText("EduSphere")).toBeInTheDocument();
    expect(screen.getByText("School Management System")).toBeInTheDocument();
  });

  test("renders the form card with welcome text", () => {
    renderLoginPage();
    expect(screen.getByText("Welcome back")).toBeInTheDocument();
    expect(
      screen.getByText("Sign in to your account to continue")
    ).toBeInTheDocument();
  });

  test("renders email and password fields", () => {
    renderLoginPage();
    expect(
      screen.getByPlaceholderText("you@school.edu")
    ).toBeInTheDocument();
    expect(
      screen.getByPlaceholderText("••••••••••")
    ).toBeInTheDocument();
  });

  test("renders the sign in button", () => {
    renderLoginPage();
    expect(
      screen.getByRole("button", { name: /sign in/i })
    ).toBeInTheDocument();
  });

  test("renders the forgot password link", () => {
    renderLoginPage();
    const link = screen.getByText(/forgot password/i);
    expect(link).toBeInTheDocument();
    expect(link).toHaveAttribute("href", "/forgot-password");
  });

  test("renders the remember me checkbox", () => {
    renderLoginPage();
    expect(
      screen.getByLabelText(/keep me signed in/i)
    ).toBeInTheDocument();
  });

  test("renders demo credentials section", () => {
    renderLoginPage();
    expect(screen.getByText("Demo Credentials")).toBeInTheDocument();
    expect(screen.getByText(/admin@school.edu/)).toBeInTheDocument();
    expect(screen.getByText(/teacher@school.edu/)).toBeInTheDocument();
    expect(screen.getByText(/student@school.edu/)).toBeInTheDocument();
  });
});

// ─── 2. Form Validation ────────────────────────────────────────────────────────

describe("form validation", () => {
  test("shows error for empty email on submit", async () => {
    renderLoginPage();
    const user = userEvent.setup();
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(
        screen.getByText("Please enter a valid email address")
      ).toBeInTheDocument();
    });
  });

  test("shows error for invalid email format", async () => {
    renderLoginPage();
    const user = userEvent.setup();
    await user.type(screen.getByPlaceholderText("you@school.edu"), "not-an-email");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(
        screen.getByText("Please enter a valid email address")
      ).toBeInTheDocument();
    });
  });

  test("shows error for empty password", async () => {
    renderLoginPage();
    const user = userEvent.setup();
    await user.type(screen.getByPlaceholderText("you@school.edu"), "admin@school.edu");
    // password left empty
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(
        screen.getByText("Password is required")
      ).toBeInTheDocument();
    });
  });

  test("clears validation errors after fixing input", async () => {
    renderLoginPage();
    const user = userEvent.setup();

    // Submit empty form to trigger errors
    await user.click(screen.getByRole("button", { name: /sign in/i }));
    await waitFor(() => {
      expect(
        screen.getByText("Please enter a valid email address")
      ).toBeInTheDocument();
    });

    // Fix the email
    const emailInput = screen.getByPlaceholderText("you@school.edu");
    await user.type(emailInput, "admin@school.edu");
    await user.tab(); // trigger validation on blur

    await waitFor(() => {
      expect(
        screen.queryByText("Please enter a valid email address")
      ).not.toBeInTheDocument();
    });
  });
});

// ─── 3. Password Visibility Toggle ─────────────────────────────────────────────

describe("password visibility toggle", () => {
  test("password field type is password by default", () => {
    renderLoginPage();
    const input = screen.getByPlaceholderText("••••••••••");
    expect(input).toHaveAttribute("type", "password");
  });

  test("clicking eye icon shows password", async () => {
    const { container } = renderLoginPage();
    const user = userEvent.setup();

    // Find the toggle button (the only button[tabindex="-1"] is the eye icon toggle)
    const toggleBtn = container.querySelector('button[tabindex="-1"]')!;
    await user.click(toggleBtn);

    const input = screen.getByPlaceholderText("••••••••••");
    expect(input).toHaveAttribute("type", "text");
  });

  test("clicking eye icon twice hides password", async () => {
    const { container } = renderLoginPage();
    const user = userEvent.setup();

    const toggleBtn = container.querySelector('button[tabindex="-1"]')!;
    await user.click(toggleBtn);
    await user.click(toggleBtn);

    const input = screen.getByPlaceholderText("••••••••••");
    expect(input).toHaveAttribute("type", "password");
  });
});

// ─── 4. Successful Login ───────────────────────────────────────────────────────

describe("successful login", () => {
  const mockUser = {
    id: "1",
    email: "admin@school.edu",
    first_name: "Admin",
    last_name: "User",
    full_name: "Admin User",
    role: "school_admin",
    is_active: true,
    email_verified: true,
    two_factor_enabled: false,
    notify_email: true,
    notify_sms: false,
    notify_push: true,
    date_joined: "2024-01-01T00:00:00Z",
  };

  const mockTokens = {
    access: "mock-access-token",
    refresh: "mock-refresh-token",
  };

  beforeEach(() => {
    (api.post as jest.Mock).mockResolvedValue({
      user: mockUser,
      access: mockTokens.access,
      refresh: mockTokens.refresh,
    });
  });

  test("calls api.post with correct credentials", async () => {
    renderLoginPage();
    const user = userEvent.setup();

    await user.type(screen.getByPlaceholderText("you@school.edu"), "admin@school.edu");
    await user.type(screen.getByPlaceholderText("••••••••••"), "Admin@1234");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith("/auth/login/", {
        email: "admin@school.edu",
        password: "Admin@1234",
      });
    });
  });

  test("sets auth state on success", async () => {
    renderLoginPage();
    const user = userEvent.setup();

    await user.type(screen.getByPlaceholderText("you@school.edu"), "admin@school.edu");
    await user.type(screen.getByPlaceholderText("••••••••••"), "Admin@1234");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      const state = useAuthStore.getState();
      expect(state.isAuthenticated).toBe(true);
      expect(state.user?.email).toBe("admin@school.edu");
    });
  });

  test("navigates to admin dashboard for school_admin role", async () => {
    renderLoginPage();
    const user = userEvent.setup();

    await user.type(screen.getByPlaceholderText("you@school.edu"), "admin@school.edu");
    await user.type(screen.getByPlaceholderText("••••••••••"), "Admin@1234");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/admin", { replace: true });
    });
  });

  test("navigates to teacher dashboard for teacher role", async () => {
    (api.post as jest.Mock).mockResolvedValue({
      user: { ...mockUser, role: "teacher", first_name: "Jane", email: "teacher@school.edu" },
      access: mockTokens.access,
      refresh: mockTokens.refresh,
    });

    renderLoginPage();
    const user = userEvent.setup();

    await user.type(screen.getByPlaceholderText("you@school.edu"), "teacher@school.edu");
    await user.type(screen.getByPlaceholderText("••••••••••"), "Teacher@1234");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/teacher", { replace: true });
    });
  });

  test("shows success toast on login", async () => {
    renderLoginPage();
    const user = userEvent.setup();

    await user.type(screen.getByPlaceholderText("you@school.edu"), "admin@school.edu");
    await user.type(screen.getByPlaceholderText("••••••••••"), "Admin@1234");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith(
        "Welcome back, Admin!"
      );
    });
  });
});

// ─── 5. Failed Login ───────────────────────────────────────────────────────────

describe("failed login", () => {
  test("shows field error on 401 Unauthorized", async () => {
    const error = new Error("Unauthorized");
    (error as any).status = 401;
    (error as any).message = "Invalid credentials";
    (api.post as jest.Mock).mockRejectedValue(error);

    renderLoginPage();
    const user = userEvent.setup();

    await user.type(screen.getByPlaceholderText("you@school.edu"), "admin@school.edu");
    await user.type(screen.getByPlaceholderText("••••••••••"), "wrongpassword");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(
        screen.getByText("Incorrect email or password")
      ).toBeInTheDocument();
    });
  });

  test("shows toast message on 429 rate limit", async () => {
    const error = new Error("Too many requests");
    (error as any).status = 429;
    (api.post as jest.Mock).mockRejectedValue(error);

    renderLoginPage();
    const user = userEvent.setup();

    await user.type(screen.getByPlaceholderText("you@school.edu"), "admin@school.edu");
    await user.type(screen.getByPlaceholderText("••••••••••"), "Admin@1234");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        "Too many attempts. Please wait 30 minutes."
      );
    });
  });

  test("shows generic toast for other errors", async () => {
    const error = new Error("Network error");
    (error as any).status = 500;
    (api.post as jest.Mock).mockRejectedValue(error);

    renderLoginPage();
    const user = userEvent.setup();

    await user.type(screen.getByPlaceholderText("you@school.edu"), "admin@school.edu");
    await user.type(screen.getByPlaceholderText("••••••••••"), "Admin@1234");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("Network error");
    });
  });

  test("does not navigate on failed login", async () => {
    (api.post as jest.Mock).mockRejectedValue(new Error("error"));

    renderLoginPage();
    const user = userEvent.setup();

    await user.type(screen.getByPlaceholderText("you@school.edu"), "admin@school.edu");
    await user.type(screen.getByPlaceholderText("••••••••••"), "wrong");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(mockNavigate).not.toHaveBeenCalled();
    });
  });
});

// ─── 6. Submit Button State ────────────────────────────────────────────────────

describe("submit button state", () => {
  test("button shows loading text during submission", async () => {
    // Make the API call never resolve
    (api.post as jest.Mock).mockImplementation(
      () => new Promise(() => {}) // never resolves
    );

    renderLoginPage();
    const user = userEvent.setup();

    await user.type(screen.getByPlaceholderText("you@school.edu"), "admin@school.edu");
    await user.type(screen.getByPlaceholderText("••••••••••"), "Admin@1234");
    await user.click(screen.getByRole("button", { name: /sign in/i }));

    await waitFor(() => {
      expect(
        screen.getByText("Signing in…")
      ).toBeInTheDocument();
    });

    // Button should be disabled during submission
    expect(
      screen.getByRole("button", { name: /signing in/i })
    ).toBeDisabled();
  });
});
