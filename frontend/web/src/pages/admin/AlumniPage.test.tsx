/**
 * Admin AlumniPage — smoke tests
 *
 * Renders the Alumni Center with a URL-dispatched mocked api client and
 * verifies the heading renders and profile rows display.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import AlumniPage from "./AlumniPage";
import { api } from "../../api/client";
import { queryClient, renderWithProviders } from "../../testUtils";

// ─── Mocks ────────────────────────────────────────────────────────────────────

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockProfiles = {
  count: 1,
  results: [
    {
      id: "11111111-1111-1111-1111-111111111111",
      user_name: "Emma Johnson",
      user_email: "emma.johnson@example.com",
      graduation_year: 2015,
      occupation: "Software Engineer",
      employer: "Tech Corp",
      employment_status: "employed",
      city: "Portland",
      country: "USA",
      engagement_score: 87,
      is_visible_to_public: true,
    },
  ],
};

describe("Admin AlumniPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    (api.get as jest.Mock).mockImplementation((url: string) =>
      url.includes("profiles")
        ? Promise.resolve(mockProfiles)
        : Promise.resolve({ count: 0, results: [] }),
    );
  });

  test("renders the heading and profile content", async () => {
    renderWithProviders(<AlumniPage />);
    expect(screen.getByRole("heading", { name: "Alumni Center" })).toBeInTheDocument();
    expect(await screen.findByText("Emma Johnson")).toBeInTheDocument();
    expect(screen.getByText("Software Engineer")).toBeInTheDocument();
  });

  test("switches to the Events tab and shows the empty state", async () => {
    const user = userEvent.setup();
    renderWithProviders(<AlumniPage />);
    await screen.findByText("Emma Johnson");
    await user.click(screen.getByRole("button", { name: "Events" }));
    expect(await screen.findByText("No events found")).toBeInTheDocument();
  });
});
