/**
 * Teacher ConferencesPage — smoke + slot-creation tests.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import dayjs from "dayjs";
import TeacherConferencesPage from "./ConferencesPage";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { queryClient, makeUser, renderWithProviders } from "../../testUtils";

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => jest.fn(),
}));

jest.mock("react-hot-toast", () => ({
  __esModule: true,
  default: { success: jest.fn(), error: jest.fn() },
  // ConferencesPage uses the named export
  toast: { success: jest.fn(), error: jest.fn() },
}));
import { toast } from "react-hot-toast";
const mockToast = jest.mocked(toast);

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

const mockSlots = {
  count: 2,
  results: [
    {
      id: "1",
      student_name: "Alice Johnson",
      date: "2024-06-10",
      start_time: "09:00",
      end_time: "09:30",
      is_booked: true,
      notes: "Discuss math progress",
    },
    {
      id: "2",
      student_name: null,
      date: "2024-06-10",
      start_time: "10:00",
      end_time: "10:30",
      is_booked: false,
      notes: "",
    },
  ],
};

describe("Teacher ConferencesPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "teacher" }) });
    (api.get as jest.Mock).mockResolvedValue(mockSlots);
    (api.post as jest.Mock).mockResolvedValue({});
  });

  test("renders booked and available conference slots", async () => {
    renderWithProviders(<TeacherConferencesPage />);
    expect(screen.getByRole("heading", { name: "My Conference Slots" })).toBeInTheDocument();
    expect(await screen.findByText(/Booked — Alice Johnson/)).toBeInTheDocument();
    expect(screen.getByText("Available")).toBeInTheDocument();
  });

  test("creates a new conference slot from the modal", async () => {
    const user = userEvent.setup();
    renderWithProviders(<TeacherConferencesPage />);
    await screen.findByText(/Booked — Alice Johnson/);

    await user.click(screen.getByRole("button", { name: "Add Slot" }));
    await user.type(screen.getByLabelText("Notes (optional)"), "Meeting about science fair");
    await user.click(screen.getByRole("button", { name: "Create Slot" }));

    expect(api.post).toHaveBeenCalledWith(
      "/conferences/conference-slots/",
      expect.objectContaining({
        start_time: "09:00",
        end_time: "09:30",
        notes: "Meeting about science fair",
        date: dayjs().format("YYYY-MM-DD"),
      }),
    );
    expect(mockToast.success).toHaveBeenCalledWith("Slot created");
  });
});
