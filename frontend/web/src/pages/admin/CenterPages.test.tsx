/**
 * Reporting/Conferences/Auth/Fees Center pages — smoke tests.
 *
 * Each page renders with a URL-dispatched mocked api client; verifies the
 * heading renders and the first tab's data displays.
 */
import React from "react";
import { screen } from "@testing-library/react";
import ReportingCenterPage from "./ReportingCenterPage";
import ConferencesCenterPage from "./ConferencesCenterPage";
import AuthCenterPage from "./AuthCenterPage";
import FeesCenterPage from "./FeesCenterPage";
import HRCenterPage from "./HRCenterPage";
import GradebookCenterPage from "./GradebookCenterPage";
import TransportationCenterPage from "./TransportationCenterPage";
import HostelCenterPage from "./HostelCenterPage";
import { api } from "../../api/client";
import { queryClient, renderWithProviders } from "../../testUtils";

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

const ok = (data: unknown) => Promise.resolve(data);

describe("Admin center pages", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    (api.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes("academic-performance")) {
        return ok({
          count: 1,
          results: [
            {
              id: "1",
              title: "Term 3 Performance",
              academic_year: "2026",
              grade: "10",
              average_score: 88.5,
            },
          ],
        });
      }
      if (url.includes("availability")) {
        return ok({
          count: 1,
          results: [
            {
              id: "2",
              teacher: "Mr. Chen",
              day_of_week: "1",
              start_time: "09:00",
              end_time: "12:00",
            },
          ],
        });
      }
      if (url.includes("a-p-i-key")) {
        return ok({
          count: 1,
          results: [
            {
              id: "3",
              name: "Portal key",
              user_email: "dev@school.edu",
              status: "active",
              key_prefix: "sk_live",
            },
          ],
        });
      }
      if (url.includes("accounting-entry")) {
        return ok({
          count: 1,
          results: [
            {
              id: "4",
              entry_type: "debit",
              account_name: "Tuition Account",
              amount: 1200,
            },
          ],
        });
      }
      if (url.includes("accountant-profiles")) {
        return ok({
          count: 1,
          results: [
            {
              id: "5",
              user_name: "Jane Doe",
              qualification: "CPA",
              experience_years: 8,
            },
          ],
        });
      }
      if (url.includes("/transport/attendance")) {
        return ok({
          count: 1,
          results: [
            {
              id: "7",
              student: "Alex Mercer",
              route: "Route 12",
              vehicle: "BUS-07",
              status: "present",
            },
          ],
        });
      }
      if (url.includes("/hostel/allocations")) {
        return ok({
          count: 1,
          results: [
            {
              id: "8",
              student: "Jamie Fox",
              room: "B-204",
              status: "active",
            },
          ],
        });
      }
      if (url.includes("/assessments")) {
        return ok({
          count: 1,
          results: [
            {
              id: "6",
              title: "Algebra Quiz 3",
              assessment_type: "quiz",
              max_marks: 20,
            },
          ],
        });
      }
      return ok({ count: 0, results: [] });
    });
  });

  test("ReportingCenterPage renders heading and first-tab data", async () => {
    renderWithProviders(<ReportingCenterPage />);
    expect(screen.getByRole("heading", { name: "Reporting Center" })).toBeInTheDocument();
    expect(await screen.findByText("Term 3 Performance")).toBeInTheDocument();
  });

  test("ConferencesCenterPage renders heading and first-tab data", async () => {
    renderWithProviders(<ConferencesCenterPage />);
    expect(screen.getByRole("heading", { name: "Conferences Center" })).toBeInTheDocument();
    expect(await screen.findByText(/Chen/)).toBeInTheDocument();
  });

  test("AuthCenterPage renders heading and first-tab data", async () => {
    renderWithProviders(<AuthCenterPage />);
    expect(screen.getByRole("heading", { name: "Access & Security Center" })).toBeInTheDocument();
    expect(await screen.findByText("Portal key")).toBeInTheDocument();
  });

  test("FeesCenterPage renders heading and first-tab data", async () => {
    renderWithProviders(<FeesCenterPage />);
    expect(screen.getByRole("heading", { name: "Finance Center" })).toBeInTheDocument();
    expect(await screen.findByText("debit")).toBeInTheDocument();
  });

  test("HRCenterPage renders heading and first-tab data", async () => {
    renderWithProviders(<HRCenterPage />);
    expect(screen.getByRole("heading", { name: "HR Center" })).toBeInTheDocument();
    expect(await screen.findByText("Jane Doe")).toBeInTheDocument();
  });

  test("GradebookCenterPage renders heading and first-tab data", async () => {
    renderWithProviders(<GradebookCenterPage />);
    expect(screen.getByRole("heading", { name: "Gradebook Center" })).toBeInTheDocument();
    expect(await screen.findByText("Algebra Quiz 3")).toBeInTheDocument();
  });

  test("TransportationCenterPage renders heading and first-tab data", async () => {
    renderWithProviders(<TransportationCenterPage />);
    expect(screen.getByRole("heading", { name: "Transportation Center" })).toBeInTheDocument();
    expect(await screen.findByText("Alex Mercer")).toBeInTheDocument();
  });

  test("HostelCenterPage renders heading and first-tab data", async () => {
    renderWithProviders(<HostelCenterPage />);
    expect(screen.getByRole("heading", { name: "Hostel Center" })).toBeInTheDocument();
    expect(await screen.findByText("Jamie Fox")).toBeInTheDocument();
  });
});
