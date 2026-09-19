/**
 * Reporting/Conferences/Auth/Fees Center pages — smoke tests.
 *
 * Each page renders with a URL-dispatched mocked api client; verifies the
 * heading renders and the first tab's data displays.
 */
import React from "react";
import { fireEvent, screen } from "@testing-library/react";
import ReportingCenterPage from "./ReportingCenterPage";
import ConferencesCenterPage from "./ConferencesCenterPage";
import AuthCenterPage from "./AuthCenterPage";
import FeesCenterPage from "./FeesCenterPage";
import HRCenterPage from "./HRCenterPage";
import GradebookCenterPage from "./GradebookCenterPage";
import TransportationCenterPage from "./TransportationCenterPage";
import HostelCenterPage from "./HostelCenterPage";
import InventoryCenterPage from "./InventoryCenterPage";
import AdmissionsCenterPage from "./AdmissionsCenterPage";
import AttendanceCenterPage from "./AttendanceCenterPage";
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
      if (url.includes("monthly_summary")) {
        return ok({
          month: "2026-09",
          prev_month: "2026-08",
          streams: [
            {
              stream: "payment",
              total_debits: "0.00",
              total_credits: "1200.00",
              entry_count: 3,
              prev_debits: "0.00",
              prev_credits: "1000.00",
            },
            {
              stream: "purchase_order",
              total_debits: "250.00",
              total_credits: "250.00",
              entry_count: 6,
              prev_debits: "100.00",
              prev_credits: "100.00",
            },
          ],
          total_debits: "0.00",
          total_credits: "1200.00",
          net: "1200.00",
          prev_total_debits: "0.00",
          prev_total_credits: "1000.00",
          prev_net: "1000.00",
        });
      }
      if (url.includes("monthly_trend")) {
        // Honor the months param so range-toggle tests see matching series
        const mParam = parseInt(
          new URLSearchParams(url.split("?")[1] || "").get("months") || "6",
          10,
        );
        const m = Math.min(Math.max(Number.isNaN(mParam) ? 6 : mParam, 1), 12);
        const months = Array.from({ length: m }, (_, i) => {
          const d = new Date(2026, 8 - (m - 1 - i), 1); // trailing months ending 2026-09
          return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
        });
        return ok({
          months,
          streams: [
            {
              stream: "payment",
              credits: months.map((_, i) =>
                i === m - 1 ? "1200.00" : i === m - 2 ? "1000.00" : "0.00",
              ),
              debits: months.map(() => "0.00"),
            },
            {
              stream: "purchase_order",
              credits: months.map(() => "0.00"),
              // Spike: current month 250 vs trailing avg 40 (0,0,0,100,100)
              debits: months.map((_, i) =>
                i === m - 1 ? "250.00" : i >= m - 3 ? "100.00" : "0.00",
              ),
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
      if (url.includes("/payslips")) {
        return ok({
          count: 3,
          results: [
            {
              id: 11,
              employee_name: "Alex Rivera",
              status: "draft",
              net_pay: "5000.00",
              gross_pay: "6000.00",
              department_name: "Science",
              period_start: "2026-10-01",
              period_end: "2026-10-31",
            },
            {
              id: 12,
              employee_name: "Maria Lopez",
              status: "approved",
              net_pay: "6000.00",
              gross_pay: "7000.00",
              department_name: "Science",
              period_start: "2026-10-01",
              period_end: "2026-10-31",
            },
            {
              id: 13,
              employee_name: "John Smith",
              status: "paid",
              net_pay: "4500.00",
              gross_pay: "5000.00",
              department_name: "Mathematics",
              period_start: "2026-09-01",
              period_end: "2026-09-30",
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
      if (url.includes("/inventory/asset-tag")) {
        return ok({
          count: 1,
          results: [
            {
              id: "9",
              item: "Projector P-77",
              tag_number: "TAG-0091",
              status: "active",
            },
          ],
        });
      }
      if (url.includes("/admissions/admission-agreement")) {
        return ok({
          count: 1,
          results: [
            {
              id: "10",
              name: "Enrollment Agreement 2026",
              status: "active",
            },
          ],
        });
      }
      if (url.includes("/attendance/archives")) {
        return ok({
          count: 1,
          results: [
            {
              id: "11",
              academic_year: "2025/2026",
              archive_type: "daily",
              record_count: 1240,
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

  test("ledger card: range toggle refetches trend, CSV export carries streams", async () => {
    renderWithProviders(<FeesCenterPage />);
    fireEvent.click(await screen.findByRole("button", { name: "Accounting Entry" }));
    expect(await screen.findByTestId("ledger-summary")).toBeInTheDocument();
    expect(api.get).toHaveBeenCalledWith("/fees/accounting-entry/monthly_trend/?months=6");

    fireEvent.click(screen.getByRole("button", { name: "12m" }));
    expect(api.get).toHaveBeenCalledWith("/fees/accounting-entry/monthly_trend/?months=12");
    expect(screen.getByTestId("ledger-summary")).toBeInTheDocument();
    // Wait for the 12-month trend data to land before exporting
    await screen.findAllByTitle(/Last 12 months/);

    // jsdom lacks URL.createObjectURL/revokeObjectURL — stub both before clicking
    const createObjectURL = jest.fn((_blob: Blob) => "blob:mock");
    Object.defineProperty(URL, "createObjectURL", {
      value: createObjectURL,
      configurable: true,
      writable: true,
    });
    Object.defineProperty(URL, "revokeObjectURL", {
      value: jest.fn(),
      configurable: true,
      writable: true,
    });
    fireEvent.click(screen.getByTestId("export-csv"));
    expect(createObjectURL).toHaveBeenCalledTimes(1);
    const blob = createObjectURL.mock.calls[0][0] as Blob;
    // jsdom Blob has no .text() — read through FileReader
    const text = await new Promise<string>((resolve) => {
      const fr = new FileReader();
      fr.onload = () => resolve(String(fr.result));
      fr.readAsText(blob);
    });
    expect(text).toContain("stream,credits,debits,entry_count,prev_credits,prev_debits");
    expect(text).toContain("payment,1200.00,0.00,3,1000.00,0.00");
    expect(text).toContain("cr_2026-04");
    Object.defineProperty(URL, "createObjectURL", { value: undefined, configurable: true });
    Object.defineProperty(URL, "revokeObjectURL", { value: undefined, configurable: true });
  });

  test("ledger card: clicking a stream drills down to its filtered entries", async () => {
    renderWithProviders(<FeesCenterPage />);
    fireEvent.click(await screen.findByRole("button", { name: "Accounting Entry" }));
    expect(await screen.findByTestId("ledger-summary")).toBeInTheDocument();

    // Stream label is a drill-down button; clicking filters the entries below
    fireEvent.click(screen.getByTestId("drill-payment"));
    const searchInput = screen.getByPlaceholderText(/Search/);
    expect(searchInput).toHaveValue("payment");
    // The mocked entry has no reference_type, so the stream filter empties the list
    expect(await screen.findByText(/No accounting entry found/i)).toBeInTheDocument();
  });

  test("ledger card: flags streams whose debits spike vs trailing average", async () => {
    renderWithProviders(<FeesCenterPage />);
    fireEvent.click(screen.getByRole("button", { name: "Accounting Entry" }));
    expect(await screen.findByTestId("ledger-summary")).toBeInTheDocument();
    // Mock: purchase_order debits 250 vs trailing avg 40 → flagged; payment has none
    expect(await screen.findByTestId("ledger-spike-count")).toHaveTextContent("1 spike");
    expect(screen.getByText("⚠ spike")).toBeInTheDocument();
  });

  test("HRCenterPage renders heading and payroll runs panel by default", async () => {
    renderWithProviders(<HRCenterPage />);
    expect(screen.getByRole("heading", { name: "HR Center" })).toBeInTheDocument();
    // Payroll Runs is the default tab — panel renders with live counters
    expect(await screen.findByText("Run payroll")).toBeInTheDocument();
    expect(await screen.findByText("Alex Rivera")).toBeInTheDocument();
    expect(screen.getByText("Approve all drafts")).toBeEnabled();
    expect(screen.getByText("Mark all paid → ledger")).toBeEnabled();
  });

  test("HRCenterPage payroll bulk-approve sends only draft ids", async () => {
    (api.post as jest.Mock).mockResolvedValue({ approved: 1, skipped: 0 });
    renderWithProviders(<HRCenterPage />);
    fireEvent.click(await screen.findByText("Approve all drafts"));
    expect(await screen.findByText(/Approved 1 payslips/i)).toBeInTheDocument();
    expect(api.post).toHaveBeenCalledWith(
      "/hr/payslips/bulk-approve/",
      expect.objectContaining({ ids: [11] }),
    );
  });

  test("HRCenterPage payroll panel groups totals by department", async () => {
    renderWithProviders(<HRCenterPage />);
    const breakdown = await screen.findByTestId("department-breakdown");
    // Science: 5000 + 6000 net = 11,000 (2 slips); Mathematics: 4,500 (1 slip)
    expect(breakdown).toHaveTextContent("Science");
    expect(breakdown).toHaveTextContent("11,000.00");
    expect(breakdown).toHaveTextContent("Mathematics");
    expect(breakdown).toHaveTextContent("4,500.00");
    // Status mix line under each bar
    expect(breakdown).toHaveTextContent("1 draft");
    expect(breakdown).toHaveTextContent("1 approved");
    expect(breakdown).toHaveTextContent("1 paid");
  });

  test("HRCenterPage entity tabs still render after the panel tab", async () => {
    renderWithProviders(<HRCenterPage />);
    await screen.findByText("Run payroll");
    fireEvent.click(screen.getByRole("button", { name: "Accountant Profile" }));
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

  test("InventoryCenterPage renders heading and first-tab data", async () => {
    renderWithProviders(<InventoryCenterPage />);
    expect(screen.getByRole("heading", { name: "Inventory Center" })).toBeInTheDocument();
    expect(await screen.findByText("Projector P-77")).toBeInTheDocument();
  });

  test("AdmissionsCenterPage renders heading and first-tab data", async () => {
    renderWithProviders(<AdmissionsCenterPage />);
    expect(screen.getByRole("heading", { name: "Admissions Center" })).toBeInTheDocument();
    expect(await screen.findByText("Enrollment Agreement 2026")).toBeInTheDocument();
  });

  test("AttendanceCenterPage renders heading and first-tab data", async () => {
    renderWithProviders(<AttendanceCenterPage />);
    expect(screen.getByRole("heading", { name: "Attendance Center" })).toBeInTheDocument();
    expect(await screen.findByText("2025/2026")).toBeInTheDocument();
  });
});
