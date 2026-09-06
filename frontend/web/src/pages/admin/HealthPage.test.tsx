/**
 * Admin HealthPage — smoke tests
 *
 * Renders the Health Center with a URL-dispatched mocked api client and
 * verifies the heading renders and a health record card displays.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import HealthPage from "./HealthPage";
import { api } from "../../api/client";
import { queryClient, renderWithProviders } from "../../testUtils";

// ─── Mocks ────────────────────────────────────────────────────────────────────

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockRecords = {
  count: 1,
  results: [
    {
      id: "1",
      student: "22222222-2222-2222-2222-222222222222",
      student_name: "Emma Johnson",
      blood_type: "O+",
      height_cm: 160,
      weight_kg: 52,
      emergency_contact_name: "Jane Johnson",
      doctor_name: "Dr. Patel",
    },
  ],
};

describe("Admin HealthPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    (api.get as jest.Mock).mockImplementation((url: string) =>
      url.includes("records")
        ? Promise.resolve(mockRecords)
        : Promise.resolve({ count: 0, results: [] }),
    );
  });

  test("renders the heading and health record content", async () => {
    renderWithProviders(<HealthPage />);
    expect(screen.getByRole("heading", { name: "Health Center" })).toBeInTheDocument();
    expect(await screen.findByText("Emma Johnson")).toBeInTheDocument();
    expect(screen.getAllByText("Dr. Patel").length).toBeGreaterThan(0);
  });

  test("switches to the Nurse Visits tab and shows the empty state", async () => {
    const user = userEvent.setup();
    renderWithProviders(<HealthPage />);
    await screen.findByText("Emma Johnson");
    await user.click(screen.getByRole("button", { name: "Nurse Visits" }));
    expect(await screen.findByText("No nurse visits found")).toBeInTheDocument();
  });
});
