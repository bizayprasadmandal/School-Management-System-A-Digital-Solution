/**
 * Admin CounselingCenterPage — smoke tests
 *
 * Renders the Counseling Center with a URL-dispatched mocked api client and
 * verifies the heading renders and appointment rows display.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import CounselingCenterPage from "./CounselingCenterPage";
import { api } from "../../api/client";
import { queryClient, renderWithProviders } from "../../testUtils";

// ─── Mocks ────────────────────────────────────────────────────────────────────

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockAppointments = {
  count: 1,
  results: [
    {
      id: "22222222-2222-2222-2222-222222222222",
      student_name: "Emma Johnson",
      counselor_name: "Dr. Reyes",
      appointment_type: "academic",
      status: "scheduled",
      scheduled_date: "2026-09-10",
      scheduled_time: "10:00",
      location: "Counseling Suite B",
      reason: "Course planning for next term",
    },
  ],
};

describe("Admin CounselingCenterPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    (api.get as jest.Mock).mockImplementation((url: string) =>
      url.includes("appointments")
        ? Promise.resolve(mockAppointments)
        : Promise.resolve({ count: 0, results: [] }),
    );
  });

  test("renders the heading and appointment content", async () => {
    renderWithProviders(<CounselingCenterPage />);
    expect(screen.getByRole("heading", { name: "Counseling Center" })).toBeInTheDocument();
    expect(await screen.findByText("Emma Johnson")).toBeInTheDocument();
    expect(screen.getByText("Dr. Reyes")).toBeInTheDocument();
  });

  test("switches to the Referrals tab and shows the empty state", async () => {
    const user = userEvent.setup();
    renderWithProviders(<CounselingCenterPage />);
    await screen.findByText("Emma Johnson");
    await user.click(screen.getByRole("button", { name: "Referrals" }));
    expect(await screen.findByText("No referrals found")).toBeInTheDocument();
  });
});
