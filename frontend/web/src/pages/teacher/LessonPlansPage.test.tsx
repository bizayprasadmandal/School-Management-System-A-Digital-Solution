/**
 * Teacher LessonPlansPage — smoke + creation tests.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import LessonPlansPage from "./LessonPlansPage";
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
}));
import toast from "react-hot-toast";
const mockToast = jest.mocked(toast);

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

const mockPlans = {
  count: 1,
  results: [
    {
      id: "1",
      title: "Fractions Introduction",
      status: "draft",
      subject_name: "Mathematics",
      classroom_name: "Grade 5 5A",
      date: "2024-06-10",
      duration_minutes: 45,
      topic: "Adding and subtracting fractions",
    },
  ],
};

describe("Teacher LessonPlansPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "teacher" }) });
    (api.get as jest.Mock).mockResolvedValue(mockPlans);
    (api.post as jest.Mock).mockResolvedValue({});
  });

  test("renders lesson plan list with plan details", async () => {
    renderWithProviders(<LessonPlansPage />);
    expect(screen.getByRole("heading", { name: "Lesson Plans" })).toBeInTheDocument();
    expect(await screen.findByText("Fractions Introduction")).toBeInTheDocument();
    expect(screen.getByText(/Adding and subtracting fractions/)).toBeInTheDocument();
  });

  test("creates a new lesson plan", async () => {
    const user = userEvent.setup();
    renderWithProviders(<LessonPlansPage />);
    await screen.findByText("Fractions Introduction");

    await user.click(screen.getByRole("button", { name: "New Plan" }));
    await user.type(screen.getByLabelText("Title"), "Quadratic Equations");
    await user.type(screen.getByLabelText("Topic"), "Solving quadratics");
    await user.click(screen.getByRole("button", { name: "Save Plan" }));

    expect(api.post).toHaveBeenCalledWith(
      "/academics/lesson-plans/",
      expect.objectContaining({ title: "Quadratic Equations", topic: "Solving quadratics" }),
    );
    expect(mockToast.success).toHaveBeenCalledWith("Lesson plan created");
  });
});
