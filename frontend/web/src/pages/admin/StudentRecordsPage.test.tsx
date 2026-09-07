/**
 * Admin StudentRecordsPage — smoke tests
 *
 * Renders the Student Records page with a URL-dispatched mocked api client
 * and verifies the heading renders and classroom rows display.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import StudentRecordsPage from "./StudentRecordsPage";
import { api } from "../../api/client";
import { queryClient, renderWithProviders } from "../../testUtils";

// ─── Mocks ────────────────────────────────────────────────────────────────────

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockClassrooms = {
  count: 1,
  results: [
    {
      id: "55555555-5555-5555-5555-555555555555",
      name: "Grade 10 - A",
      grade: "g1",
      capacity: 35,
      room_number: "204",
    },
  ],
};

describe("Admin StudentRecordsPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    (api.get as jest.Mock).mockImplementation((url: string) =>
      url.includes("classrooms")
        ? Promise.resolve(mockClassrooms)
        : Promise.resolve({ count: 0, results: [] }),
    );
  });

  test("renders the heading and classroom content", async () => {
    renderWithProviders(<StudentRecordsPage />);
    expect(screen.getByRole("heading", { name: "Student Records" })).toBeInTheDocument();
    expect(await screen.findByText("Grade 10 - A")).toBeInTheDocument();
    expect(screen.getByText("204")).toBeInTheDocument();
  });

  test("switches to the Grades tab and shows the empty state", async () => {
    const user = userEvent.setup();
    renderWithProviders(<StudentRecordsPage />);
    await screen.findByText("Grade 10 - A");
    await user.click(screen.getByRole("button", { name: "Grades" }));
    expect(await screen.findByText("No grades found")).toBeInTheDocument();
  });
});
