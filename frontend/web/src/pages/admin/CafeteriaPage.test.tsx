/**
 * Admin CafeteriaPage — smoke tests
 *
 * Renders with mocked menus/plans/bookings queries (URL-dispatched
 * api.get); verifies the heading and that a menu card renders.
 */
import React from "react";
import { screen } from "@testing-library/react";
import CafeteriaPage from "./CafeteriaPage";
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

const mockMenu = {
  id: "1",
  name: "Grilled Chicken",
  date: "2026-08-09",
  meal_type_display: "Lunch",
  items: "Grilled chicken, rice, salad",
  price: "250",
  is_vegetarian: false,
  is_vegan: false,
  is_gluten_free: false,
};

const mockByUrl: Record<string, { results: unknown[] }> = {
  "/cafeteria/menus/": { results: [mockMenu] },
  "/cafeteria/plans/": { results: [] },
  "/cafeteria/bookings/": { results: [] },
  "/cafeteria/dietary/": { results: [] },
};

describe("Admin CafeteriaPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "school_admin" }) });
    (api.get as jest.Mock).mockImplementation((url: string) =>
      Promise.resolve(mockByUrl[url] ?? { results: [] }),
    );
  });

  test("renders the heading and the menu list", async () => {
    renderWithProviders(<CafeteriaPage />);
    expect(screen.getByRole("heading", { name: "Cafeteria & Meals" })).toBeInTheDocument();
    expect(await screen.findByText("Grilled Chicken")).toBeInTheDocument();
    expect(screen.getByText("Lunch")).toBeInTheDocument();
  });
});
