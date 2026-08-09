/**
 * Admin HostelPage — smoke tests
 *
 * Renders with mocked hostel/rooms queries (URL-dispatched api.get);
 * verifies the heading and that a room card renders.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import HostelPage from "./HostelPage";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { queryClient, makeUser, renderWithProviders } from "../../testUtils";

// ─── Mocks ────────────────────────────────────────────────────────────────────

jest.mock("react-hot-toast", () => ({
  __esModule: true,
  default: { success: jest.fn(), error: jest.fn() },
}));

jest.mock("../../api/client", () => ({
  api: { get: jest.fn() },
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockRoom = {
  id: "1",
  room_number: "H-101",
  hostel_name: "Sunrise Hostel",
  floor: 1,
  room_type_display: "Double",
  occupied_beds: 2,
  capacity: 4,
  has_ac: true,
  is_furnished: false,
};

const mockByUrl: Record<string, { results: unknown[] }> = {
  "/hostel/hostels/": { results: [] },
  "/hostel/rooms/": { results: [mockRoom] },
  "/hostel/allocations/": { results: [] },
  "/hostel/fees/": { results: [] },
  "/hostel/visitors/": { results: [] },
  "/students/": { results: [] },
};

describe("Admin HostelPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "school_admin" }) });
    (api.get as jest.Mock).mockImplementation((url: string) =>
      Promise.resolve(mockByUrl[url] ?? { results: [] }),
    );
  });

  test("renders the heading and the room list on the Rooms tab", async () => {
    const user = userEvent.setup();
    renderWithProviders(<HostelPage />);
    expect(screen.getByRole("heading", { name: "Hostel & Accommodation" })).toBeInTheDocument();

    // Rooms live on their own tab (default is Hostels).
    await user.click(screen.getByRole("button", { name: "Rooms" }));
    expect(await screen.findByText("H-101")).toBeInTheDocument();
    expect(screen.getByText(/Sunrise Hostel/)).toBeInTheDocument();
  });
});
