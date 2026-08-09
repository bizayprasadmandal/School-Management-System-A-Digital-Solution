/**
 * Admin TimetablePage — smoke tests
 *
 * Renders with mocked classrooms/academic year; verifies the heading and that
 * weekly slots load after a classroom is selected.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import TimetablePage from "./TimetablePage";
import { api } from "../../api/client";
import { useClassrooms, useCurrentAcademicYear } from "../../api/hooks";
import { queryClient, renderWithProviders } from "../../testUtils";

// ─── Mocks ────────────────────────────────────────────────────────────────────

jest.mock("../../api/client", () => ({
  api: { get: jest.fn() },
}));

jest.mock("../../api/hooks", () => ({
  useClassrooms: jest.fn(),
  useCurrentAcademicYear: jest.fn(),
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockClassrooms = {
  count: 1,
  results: [
    {
      id: 1,
      name: "5A",
      grade_name: "Grade 5",
      capacity: 35,
      teacher_name: "Sarah Mitchell",
      student_count: 28,
    },
  ],
};

const mockYear = { id: 1, name: "2026-27", is_current: true };

const mockWeekly = {
  Monday: [
    {
      subject_name: "Math",
      period_name: "Period 1",
      start_time: "09:00",
      end_time: "09:45",
      teacher_name: "John Davis",
      classroom_name: "5A",
      room: "101",
    },
  ],
};

describe("Admin TimetablePage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    (useClassrooms as jest.Mock).mockReturnValue({ data: mockClassrooms, isLoading: false });
    (useCurrentAcademicYear as jest.Mock).mockReturnValue({ data: mockYear, isLoading: false });
    (api.get as jest.Mock).mockResolvedValue(mockWeekly);
  });

  test("renders the heading and classroom selector options", () => {
    renderWithProviders(<TimetablePage />);
    expect(screen.getByRole("heading", { name: "Timetable" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Grade 5 5A" })).toBeInTheDocument();
  });

  test("shows weekly slots after selecting a classroom", async () => {
    renderWithProviders(<TimetablePage />);
    await userEvent.selectOptions(screen.getByLabelText("Select Classroom"), "1");
    expect(await screen.findByText("Math")).toBeInTheDocument();
  });
});
