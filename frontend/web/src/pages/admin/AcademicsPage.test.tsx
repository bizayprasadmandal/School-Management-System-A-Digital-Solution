/**
 * Admin AcademicsPage — smoke tests
 *
 * Renders the Academics Hub with mocked api client and verifies the heading,
 * tab bar, and that an entity section loads after switching tabs.
 */
import React from "react";
import { screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import AcademicsPage from "./AcademicsPage";
import { api } from "../../api/client";
import { queryClient, renderWithProviders } from "../../testUtils";

// ─── Mocks ────────────────────────────────────────────────────────────────────

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockSubjects = {
  count: 2,
  results: [
    {
      id: "11111111-1111-1111-1111-111111111111",
      name: "Mathematics",
      code: "MATH101",
      grade_name: "Grade 5",
      is_core: true,
      is_elective: false,
      max_marks: 100,
      pass_marks: 40,
      is_active: true,
    },
    {
      id: "22222222-2222-2222-2222-222222222222",
      name: "English",
      code: "ENG101",
      grade_name: "Grade 5",
      is_core: true,
      is_elective: false,
      max_marks: 100,
      pass_marks: 40,
      is_active: true,
    },
  ],
};

describe("Admin AcademicsPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    (api.get as jest.Mock).mockImplementation((url: string) =>
      url.includes("subjects")
        ? Promise.resolve(mockSubjects)
        : Promise.resolve({ count: 0, results: [] }),
    );
  });

  test("renders the heading and subject tab content", async () => {
    renderWithProviders(<AcademicsPage />);
    expect(screen.getByRole("heading", { name: "Academics Hub" })).toBeInTheDocument();
    expect(await screen.findByText("Mathematics")).toBeInTheDocument();
    expect(screen.getByText("English")).toBeInTheDocument();
  });

  test("switches tabs when a different entity is clicked", async () => {
    renderWithProviders(<AcademicsPage />);
    await userEvent.click(screen.getByRole("button", { name: "Syllabus" }));
    expect(api.get).toHaveBeenCalledWith(expect.stringContaining("/academics/syllabi/"), {
      page_size: 200,
    });
    await waitFor(() => {
      expect(screen.getByText("No syllabus found")).toBeInTheDocument();
    });
  });
});
