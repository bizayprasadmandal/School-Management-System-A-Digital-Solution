/**
 * Admin AdmissionsPage — CRM pipeline tests
 *
 * Renders with URL-dispatched api.get mocks and verifies the per-application
 * pipeline actions (schedule tour, send offer, enroll) hit the right endpoints.
 */
import React from "react";
import { screen, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import AdmissionsPage from "./AdmissionsPage";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { queryClient, makeUser, renderWithProviders } from "../../testUtils";

// ─── Mocks ────────────────────────────────────────────────────────────────────

jest.mock("react-hot-toast", () => ({
  __esModule: true,
  default: { success: jest.fn(), error: jest.fn() },
}));

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockApp = {
  id: "app-1",
  application_number: "APP-202608-ABC123",
  full_name: "Jane Doe",
  first_name: "Jane",
  last_name: "Doe",
  email: "jane@example.com",
  phone: "+1-555-1234",
  date_of_birth: "2012-04-01",
  gender: "female",
  applying_for_grade: "Grade 7",
  status: "shortlisted",
  status_display: "Shortlisted",
  intake: "intake-1",
  intake_name: "Fall 2026",
  submitted_at: "2026-08-01T10:00:00Z",
  tour_date: null,
  toured_at: null,
  offer_sent_at: null,
  offer_accepted_at: null,
  linked_student: null,
  timeline: [
    {
      id: "t1",
      stage: "created",
      stage_display: "Application Created",
      note: "",
      created_by_name: "Admin User",
      created_at: "2026-08-01T10:00:00Z",
    },
  ],
};

const mockByUrl: Record<string, { results: unknown[] }> = {
  "/admissions/applications/": { results: [mockApp] },
  "/admissions/intakes/": { results: [] },
  "/admissions/reviews/": { results: [] },
  "/students/classrooms/": { results: [{ id: 1, name: "A", grade_name: "Grade 7" }] },
};

describe("Admin AdmissionsPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "school_admin" }) });
    (api.get as jest.Mock).mockImplementation((url: string) =>
      Promise.resolve(mockByUrl[url] ?? { results: [] }),
    );
    (api.post as jest.Mock).mockResolvedValue({});
  });

  test("renders the heading and application with a pipeline trail", async () => {
    renderWithProviders(<AdmissionsPage />);
    expect(screen.getByRole("heading", { name: "Admissions & Enrollment" })).toBeInTheDocument();
    expect(await screen.findByText("Jane Doe")).toBeInTheDocument();
    expect(screen.getAllByText("Shortlisted").length).toBeGreaterThan(0);
  });

  test("send-offer button posts to the send-offer endpoint for shortlisted apps", async () => {
    const user = userEvent.setup();
    renderWithProviders(<AdmissionsPage />);
    const sendOffer = await screen.findByRole("button", { name: /Send Offer/ });
    await user.click(sendOffer);
    await waitFor(() =>
      expect(api.post).toHaveBeenCalledWith("/admissions/applications/app-1/send-offer/", {}),
    );
  });

  test("expanded card schedules a tour through the tour modal", async () => {
    const user = userEvent.setup();
    renderWithProviders(<AdmissionsPage />);
    await user.click(await screen.findByText("Jane Doe"));
    await user.click(screen.getAllByRole("button", { name: /Schedule Tour/ })[0]);
    // The modal shows a date input and a confirm button (scoped by modal heading)
    const heading = screen.getByRole("heading", { name: /Schedule Tour —/ });
    const dialog = heading.closest("div")?.parentElement?.parentElement as HTMLElement;
    expect(within(dialog).getByLabelText(/Tour Date/)).toBeInTheDocument();
    await user.type(within(dialog).getByLabelText(/Tour Date/), "2026-09-15");
    await user.click(within(dialog).getByRole("button", { name: "Schedule Tour" }));
    await waitFor(() =>
      expect(api.post).toHaveBeenCalledWith("/admissions/applications/app-1/schedule-tour/", {
        tour_date: "2026-09-15",
      }),
    );
  });

  test("enroll opens the classroom picker and posts with the selected classroom", async () => {
    const user = userEvent.setup();
    const offeredApp = {
      ...mockApp,
      status: "accepted",
      status_display: "Accepted",
      offer_sent_at: "2026-08-10T10:00:00Z",
    };
    (api.get as jest.Mock).mockImplementation((url: string) =>
      Promise.resolve(
        url === "/admissions/applications/"
          ? { results: [offeredApp] }
          : mockByUrl[url] ?? { results: [] },
      ),
    );
    (api.post as jest.Mock).mockResolvedValue({
      status: "enrolled",
      linked_student: "stu-9",
      generated_password: "Tmp@Password1",
    });

    renderWithProviders(<AdmissionsPage />);
    const enroll = await screen.findByRole("button", { name: /Enroll/ });
    await user.click(enroll);
    await waitFor(() => expect(screen.getByLabelText(/Classroom/)).toBeInTheDocument());
    await user.selectOptions(screen.getByLabelText(/Classroom/), "1");
    await user.click(screen.getByRole("button", { name: "Enroll Student" }));
    await waitFor(() =>
      expect(api.post).toHaveBeenCalledWith("/admissions/applications/app-1/enroll/", {
        classroom_id: "1",
      }),
    );
  });
});
