/**
 * Admin LibraryPage — smoke tests
 *
 * Renders the Library Center with a URL-dispatched mocked api client and
 * verifies the heading renders and a book card displays.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LibraryPage from "./LibraryPage";
import { api } from "../../api/client";
import { queryClient, renderWithProviders } from "../../testUtils";

// ─── Mocks ────────────────────────────────────────────────────────────────────

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockBooks = {
  count: 1,
  results: [
    {
      id: "1",
      title: "The Great Gatsby",
      author: "F. Scott Fitzgerald",
      isbn: "9780743273565",
      shelf_location: "A-12",
      available_copies: 3,
      total_copies: 5,
      is_active: true,
    },
  ],
};

describe("Admin LibraryPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    (api.get as jest.Mock).mockImplementation((url: string) =>
      url.includes("books")
        ? Promise.resolve(mockBooks)
        : Promise.resolve({ count: 0, results: [] }),
    );
  });

  test("renders the heading and the book list", async () => {
    renderWithProviders(<LibraryPage />);
    expect(screen.getByRole("heading", { name: "Library Center" })).toBeInTheDocument();
    expect(await screen.findByText("The Great Gatsby")).toBeInTheDocument();
    expect(screen.getAllByText("F. Scott Fitzgerald").length).toBeGreaterThan(0);
  });

  test("switches to the Fines tab and shows the empty state", async () => {
    const user = userEvent.setup();
    renderWithProviders(<LibraryPage />);
    await screen.findByText("The Great Gatsby");
    await user.click(screen.getByRole("button", { name: "Fines" }));
    expect(await screen.findByText("No fines found")).toBeInTheDocument();
  });
});
