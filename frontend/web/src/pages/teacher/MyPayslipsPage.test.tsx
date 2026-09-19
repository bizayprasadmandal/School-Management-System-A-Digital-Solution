/**
 * MyPayslipsPage — employee self-service payslip tests.
 *
 * Mocks the scoped /hr/payslips/ endpoint; verifies list rendering, the
 * selected-slip breakdown (earnings, deductions, net), empty state, and
 * the print view content.
 */
import React from "react";
import { fireEvent, screen } from "@testing-library/react";
import MyPayslipsPage from "./MyPayslipsPage";
import { api } from "../../api/client";
import { renderWithProviders } from "../../testUtils";

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

const ok = (data: unknown) => Promise.resolve(data);

const SLIPS = [
  {
    id: "s-1",
    period_start: "2026-09-01",
    period_end: "2026-09-30",
    status: "paid",
    basic_salary: "30000.00",
    housing_allowance: "5000.00",
    transport_allowance: "2000.00",
    medical_allowance: "1000.00",
    other_allowances: "0.00",
    tax_deduction: "3000.00",
    pension_deduction: "1500.00",
    other_deductions: "500.00",
    gross_pay: "38000.00",
    total_deductions: "5000.00",
    net_pay: "33000.00",
    payment_date: "2026-10-01",
    payment_method: "bank_transfer",
  },
  {
    id: "s-2",
    period_start: "2026-08-01",
    period_end: "2026-08-31",
    status: "paid",
    gross_pay: "38000.00",
    total_deductions: "5000.00",
    net_pay: "33000.00",
  },
];

describe("MyPayslipsPage", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (api.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes("/hr/payslips")) {
        return ok({ count: SLIPS.length, results: SLIPS });
      }
      return ok({ count: 0, results: [] });
    });
  });

  test("renders slip list and shows breakdown for the selected slip", async () => {
    renderWithProviders(<MyPayslipsPage />);
    expect(await screen.findByText("2026-09-01 → 2026-09-30")).toBeInTheDocument();

    // No selection initially
    expect(screen.getByTestId("no-selection")).toBeInTheDocument();

    fireEvent.click(screen.getByText("2026-09-01 → 2026-09-30"));
    const detail = screen.getByTestId("payslip-detail");
    expect(detail).toHaveTextContent("Basic salary");
    expect(detail).toHaveTextContent("30,000.00");
    expect(detail).toHaveTextContent("Tax (PAYE)");
    expect(detail).toHaveTextContent("3,000.00");
    expect(detail).toHaveTextContent("Gross pay");
    expect(detail).toHaveTextContent("38,000.00");
    expect(detail).toHaveTextContent("Total deductions");
    expect(detail).toHaveTextContent("5,000.00");
    expect(detail).toHaveTextContent("Net pay");
    expect(detail).toHaveTextContent("33,000.00");
  });

  test("shows the empty state when the employee has no payslips", async () => {
    (api.get as jest.Mock).mockResolvedValue({ count: 0, results: [] });
    renderWithProviders(<MyPayslipsPage />);
    expect(await screen.findByTestId("no-payslips")).toBeInTheDocument();
  });

  test("print view contains the full slip breakdown", async () => {
    const writeMock = jest.fn();
    const fakeWin = {
      document: { write: writeMock, close: jest.fn() },
      focus: jest.fn(),
      print: jest.fn(),
    } as unknown as Window;
    jest.spyOn(window, "open").mockReturnValue(fakeWin);

    renderWithProviders(<MyPayslipsPage />);
    fireEvent.click(await screen.findByText("2026-09-01 → 2026-09-30"));
    fireEvent.click(screen.getByLabelText("Print this payslip"));

    const html = writeMock.mock.calls[0][0] as string;
    expect(html).toContain("Payslip");
    expect(html).toContain("Earnings");
    expect(html).toContain("Deductions");
    expect(html).toContain("33,000.00");
    expect(html).toContain("bank_transfer");
    expect(fakeWin.print).toHaveBeenCalled();
  });
});
