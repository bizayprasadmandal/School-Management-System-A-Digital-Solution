/**
 * Admin BehaviorPage — smoke tests
 *
 * Renders the Behavior Center with a URL-dispatched mocked api client and
 * verifies the heading renders and incident rows display.
 */
import React from "react";
import { screen } from "@testing-library/react";
import BehaviorPage from "./BehaviorPage";
import { api } from "../../api/client";
import { queryClient, renderWithProviders } from "../../testUtils";

// ─── Mocks ────────────────────────────────────────────────────────────────────

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockIncidents = {
  count: 1,
  results: [
    {
      id: "11111111-1111-1111-1111-111111111111",
      title: "Classroom disruption",
      student_name: "Alex Rivera",
      category_name: "Disruption",
      severity: "medium",
      severity_display: "Medium",
      status_display: "Open",
      incident_date: "2026-09-01T10:00:00Z",
      location: "Room 204",
    },
  ],
};

describe("Admin BehaviorPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    (api.get as jest.Mock).mockImplementation((url: string) =>
      url.includes("incidents")
        ? Promise.resolve(mockIncidents)
        : Promise.resolve({ count: 0, results: [] }),
    );
  });

  test("renders the heading and incident content", async () => {
    renderWithProviders(<BehaviorPage />);
    expect(screen.getByRole("heading", { name: "Behavior Center" })).toBeInTheDocument();
    expect(await screen.findByText("Classroom disruption")).toBeInTheDocument();
    expect(screen.getByText("Alex Rivera")).toBeInTheDocument();
  });
});
