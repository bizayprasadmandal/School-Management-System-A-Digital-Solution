/**
 * Admin SportsPage — smoke tests
 *
 * Renders the Sports Center with a URL-dispatched mocked api client and
 * verifies the heading renders and sport rows display.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import SportsPage from "./SportsPage";
import { api } from "../../api/client";
import { queryClient, renderWithProviders } from "../../testUtils";

// ─── Mocks ────────────────────────────────────────────────────────────────────

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockSports = {
  count: 2,
  results: [
    {
      id: "33333333-3333-3333-3333-333333333333",
      name: "Basketball",
      category: "sport",
      category_display: "Sport",
      description: "Varsity basketball program",
      min_players: 5,
      max_players: 15,
      team_count: 3,
      is_active: true,
    },
    {
      id: "44444444-4444-4444-4444-444444444444",
      name: "Track & Field",
      category: "sport",
      category_display: "Sport",
      description: "Track and field program",
      min_players: 1,
      max_players: 40,
      team_count: 2,
      is_active: true,
    },
  ],
};

describe("Admin SportsPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    (api.get as jest.Mock).mockImplementation((url: string) =>
      url.includes("/sports/sports/")
        ? Promise.resolve(mockSports)
        : Promise.resolve({ count: 0, results: [] }),
    );
  });

  test("renders the heading and sport content", async () => {
    renderWithProviders(<SportsPage />);
    expect(screen.getByRole("heading", { name: "Sports Center" })).toBeInTheDocument();
    expect(await screen.findByText("Basketball")).toBeInTheDocument();
    expect(screen.getByText("Track & Field")).toBeInTheDocument();
  });

  test("switches to the Teams tab and shows the empty state", async () => {
    const user = userEvent.setup();
    renderWithProviders(<SportsPage />);
    await screen.findByText("Basketball");
    await user.click(screen.getByRole("button", { name: "Teams" }));
    expect(await screen.findByText("No teams found")).toBeInTheDocument();
  });
});
