/**
 * Admin TransportationPage — smoke tests
 *
 * Renders with mocked vehicles/drivers/routes queries (URL-dispatched
 * api.get); verifies the heading and that a vehicle card renders.
 */
import React from "react";
import { screen } from "@testing-library/react";
import TransportationPage from "./TransportationPage";
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

const mockVehicle = {
  id: "1",
  plate_number: "BA 1 KA 1234",
  vehicle_type_display: "Bus",
  model_name: "Toyota",
  year: 2020,
  status_display: "Active",
  capacity: 40,
  route_count: 2,
};

const mockByUrl: Record<string, { results: unknown[] }> = {
  "/transport/vehicles/": { results: [mockVehicle] },
  "/transport/drivers/": { results: [] },
  "/transport/routes/": { results: [] },
  "/transport/student-routes/": { results: [] },
  "/transport/maintenance/": { results: [] },
  "/students/": { results: [] },
};

describe("Admin TransportationPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "school_admin" }) });
    (api.get as jest.Mock).mockImplementation((url: string) =>
      Promise.resolve(mockByUrl[url] ?? { results: [] }),
    );
  });

  test("renders the heading and the vehicle list", async () => {
    renderWithProviders(<TransportationPage />);
    expect(screen.getByRole("heading", { name: "Transportation Management" })).toBeInTheDocument();
    expect(await screen.findByText("BA 1 KA 1234")).toBeInTheDocument();
    expect(screen.getByText(/Toyota/)).toBeInTheDocument();
  });
});
