/**
 * Admin LibraryPage — smoke tests
 *
 * Renders with mocked books/checkouts queries (URL-dispatched api.get);
 * verifies the heading and that a book card renders.
 */
import React from "react";
import { screen } from "@testing-library/react";
import LibraryPage from "./LibraryPage";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
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

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockBook = {
  id: "1",
  title: "The Great Gatsby",
  author: "F. Scott Fitzgerald",
  isbn: "9780743273565",
  available_copies: 3,
  total_copies: 5,
};

const mockByUrl: Record<string, { results: unknown[] }> = {
  "/library/books/": { results: [mockBook] },
  "/library/checkouts/": { results: [] },
  "/students/students/": { results: [] },
};

describe("Admin LibraryPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "school_admin" }) });
    (api.get as jest.Mock).mockImplementation((url: string) =>
      Promise.resolve(mockByUrl[url] ?? { results: [] }),
    );
  });

  test("renders the heading and the book list", async () => {
    renderWithProviders(<LibraryPage />);
    expect(screen.getByRole("heading", { name: "Library Management" })).toBeInTheDocument();
    expect(await screen.findByText("The Great Gatsby")).toBeInTheDocument();
    expect(screen.getByText("F. Scott Fitzgerald")).toBeInTheDocument();
  });
});
