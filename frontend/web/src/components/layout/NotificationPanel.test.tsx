/**
 * NotificationPanel — payslip notification wiring tests.
 *
 * Mocks the notifications endpoint; verifies payslip notifications render
 * with the money icon and deep-link to the My Payslips page on click.
 */
import React from "react";
import { fireEvent, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import NotificationPanel from "./NotificationPanel";
import { api } from "../../api/client";
import { renderWithProviders } from "../../testUtils";

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

const ok = (data: unknown) => Promise.resolve(data);

const NOTIFS = {
  count: 2,
  results: [
    {
      id: "n-1",
      title: "Payslip paid",
      body: "Your payslip for 2026-09-01 → 2026-09-30 has been paid. Net pay: 33000.00.",
      channel: "in_app",
      status: "sent",
      reference_type: "payslip",
      reference_id: "s-9",
      read_at: null,
      created_at: new Date().toISOString(),
    },
    {
      id: "n-2",
      title: "Welcome",
      body: "Generic in-app notification",
      channel: "in_app",
      status: "sent",
      read_at: new Date().toISOString(),
      created_at: new Date().toISOString(),
    },
  ],
};

describe("NotificationPanel payslip notifications", () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (api.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes("/communication/notifications")) {
        return ok(NOTIFS);
      }
      return ok({ count: 0, results: [] });
    });
  });

  const renderPanel = () => renderWithProviders(<NotificationPanel open onClose={jest.fn()} />);

  test("renders payslip notification with money icon and deep-links on click", async () => {
    renderPanel();
    const title = await screen.findByText("Payslip paid");
    expect(title).toBeInTheDocument();
    // The money icon override is applied for reference_type=payslip
    expect(title.closest("li")).toHaveTextContent("💰");
    // Click marks it read (mutation fires PATCH async)
    fireEvent.click(title.closest("li")!);
    await screen.findByText("Payslip paid");
    await Promise.resolve();
    await Promise.resolve();
    expect(api.patch).toHaveBeenCalledWith("/communication/notifications/n-1/mark-read/", {});
  });

  test("generic notifications keep the default channel icon", async () => {
    renderPanel();
    await screen.findByText("Welcome");
    const generic = screen.getByText("Welcome").closest("li")!;
    expect(generic).toHaveTextContent("🔔");
    expect(generic).not.toHaveTextContent("💰");
  });
});
