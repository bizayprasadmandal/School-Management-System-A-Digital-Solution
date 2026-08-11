/**
 * Teacher SettingsPage — smoke + teaching-profile save tests.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import TeacherSettingsPage from "./SettingsPage";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { useProfile } from "../../api/hooks";
import { queryClient, makeUser, renderWithProviders } from "../../testUtils";

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => jest.fn(),
}));

jest.mock("react-hot-toast", () => ({
  __esModule: true,
  default: { success: jest.fn(), error: jest.fn() },
}));
import toast from "react-hot-toast";
const mockToast = jest.mocked(toast);

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

jest.mock("../../api/hooks", () => ({
  useProfile: jest.fn(),
}));

const mockTeacherProfile = {
  id: "tp1",
  qualification: "bachelor",
  specialization: "Mathematics",
  department: "Science",
  experience_years: 5,
  bio: "Dedicated math teacher",
};

describe("Teacher SettingsPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "teacher" }) });
    (useProfile as jest.Mock).mockReturnValue({
      data: makeUser({ role: "teacher" }),
      isLoading: false,
    });
    (api.get as jest.Mock).mockResolvedValue(mockTeacherProfile);
    (api.patch as jest.Mock).mockResolvedValue({});
  });

  test("renders the settings heading and teaching profile section", async () => {
    renderWithProviders(<TeacherSettingsPage />);
    expect(screen.getByRole("heading", { name: "Settings" })).toBeInTheDocument();
    expect(await screen.findByText("Teaching Profile")).toBeInTheDocument();
    // Existing profile data loads into the form (async — profile query resolves)
    expect(await screen.findByDisplayValue("Mathematics")).toBeInTheDocument();
    expect(screen.getByDisplayValue("Science")).toBeInTheDocument();
  });

  test("saves updated teaching profile fields", async () => {
    const user = userEvent.setup();
    renderWithProviders(<TeacherSettingsPage />);
    await screen.findByText("Teaching Profile");

    const spec = await screen.findByLabelText("Specialization");
    await user.clear(spec);
    await user.type(spec, "Physics");
    await user.click(screen.getByRole("button", { name: "Save Teaching Profile" }));

    expect(api.patch).toHaveBeenCalledWith(
      "/academics/teacher-profiles/me/",
      expect.objectContaining({ specialization: "Physics", experience_years: 5 }),
    );
    expect(mockToast.success).toHaveBeenCalledWith("Teacher profile updated!");
  });
});
