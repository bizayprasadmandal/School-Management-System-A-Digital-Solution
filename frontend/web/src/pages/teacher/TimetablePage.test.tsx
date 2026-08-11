/**
 * Teacher TimetablePage — smoke + schedule-render tests.
 */
import React from "react";
import { screen } from "@testing-library/react";
import TeacherTimetablePage from "./TimetablePage";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { useCurrentAcademicYear } from "../../api/hooks";
import { queryClient, makeUser, renderWithProviders } from "../../testUtils";

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => jest.fn(),
}));

jest.mock("react-hot-toast", () => ({
  __esModule: true,
  default: { success: jest.fn(), error: jest.fn() },
}));

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

jest.mock("../../api/hooks", () => ({
  useCurrentAcademicYear: jest.fn(),
}));

const mockSlots = [
  {
    id: 1,
    subject_name: "Mathematics",
    classroom_name: "Grade 5 5A",
    room: "R12",
    day_of_week: 0,
    start_time: "09:00:00",
    end_time: "09:45:00",
  },
  {
    id: 2,
    subject_name: "English",
    classroom_name: "Grade 5 5B",
    room: "R14",
    day_of_week: 1,
    start_time: "10:00:00",
    end_time: "10:45:00",
  },
];

describe("Teacher TimetablePage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "teacher" }) });
    (useCurrentAcademicYear as jest.Mock).mockReturnValue({ data: { id: 1, name: "2026-27" } });
    (api.get as jest.Mock).mockResolvedValue(mockSlots);
  });

  test("renders the timetable heading with the academic year", async () => {
    renderWithProviders(<TeacherTimetablePage />);
    // isLoading renders a skeleton first — wait for the heading
    expect(await screen.findByRole("heading", { name: "My Timetable" })).toBeInTheDocument();
    expect(screen.getByText(/2026-27/)).toBeInTheDocument();
  });

  test("groups slots under their weekdays", async () => {
    renderWithProviders(<TeacherTimetablePage />);
    expect(await screen.findByText("Mathematics")).toBeInTheDocument();
    expect(screen.getByText("English")).toBeInTheDocument();
    expect(screen.getByText("Monday")).toBeInTheDocument();
    expect(screen.getByText("Tuesday")).toBeInTheDocument();
  });
});
