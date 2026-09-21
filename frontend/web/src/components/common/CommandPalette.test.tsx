/**
 * CommandPalette — remote global-search integration tests.
 *
 * The palette merges local nav matches with record hits from
 * GET /api/v1/search/ (debounced ≥2 chars). These tests pin the merge
 * behavior, the debounce contract, and keyboard selection of a record hit.
 */
import React from "react";
import { screen, waitFor, fireEvent } from "@testing-library/react";
import CommandPalette from "./CommandPalette";
import { api } from "../../api/client";
import { queryClient, renderWithProviders } from "../../testUtils";

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

import { UserCircleIcon } from "@heroicons/react/24/outline";

const navItems = [
  { label: "Students", to: "/admin/students", icon: UserCircleIcon },
  { label: "Fees", to: "/admin/fees", icon: UserCircleIcon },
];

const ok = (data: unknown) => Promise.resolve(data);

function openPalette() {
  renderWithProviders(<CommandPalette items={navItems} />);
  fireEvent.click(screen.getByTitle(/Search pages/));
}

describe("CommandPalette remote search", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.useRealTimers();
  });

  it("does not call the API for queries shorter than 2 chars", async () => {
    openPalette();
    fireEvent.change(screen.getByPlaceholderText(/Search pages/), { target: { value: "j" } });
    jest.advanceTimersByTime(400);
    expect(api.get).not.toHaveBeenCalled();
  });

  it("debounces and merges remote hits under nav matches", async () => {
    (api.get as jest.Mock).mockImplementation((url: string) => {
      if (url === "/search/") {
        return ok({
          groups: [
            {
              key: "students",
              label: "Students",
              results: [
                {
                  id: "1",
                  title: "Marilyn Vos",
                  subtitle: "Student · ADM-0001",
                  url: "/admin/students/1",
                },
              ],
            },
          ],
        });
      }
      return ok({});
    });

    openPalette();
    const input = screen.getByPlaceholderText(/Search pages/);
    fireEvent.change(input, { target: { value: "mar" } });

    await waitFor(() => {
      expect(screen.getByText("Marilyn Vos")).toBeInTheDocument();
    });
    // Nav match for "Students" (contains "mar"? no) — but remote group header renders.
    expect(screen.getByText("Students")).toBeInTheDocument();
    expect(screen.getByText("Student · ADM-0001")).toBeInTheDocument();
    expect(api.get).toHaveBeenCalledWith("/search/", { q: "mar" });
  });

  it("navigates on Enter when a remote hit is selected", async () => {
    (api.get as jest.Mock).mockImplementation((url: string) =>
      url === "/search/"
        ? ok({
            groups: [
              {
                key: "invoices",
                label: "Invoices",
                results: [
                  {
                    id: "9",
                    title: "INV-000009",
                    subtitle: "Invoice · unpaid",
                    url: "/admin/finance-center",
                  },
                ],
              },
            ],
          })
        : ok({}),
    );

    openPalette();
    const input = screen.getByPlaceholderText(/Search pages/);
    fireEvent.change(input, { target: { value: "inv" } });

    await waitFor(() => {
      expect(screen.getByText("INV-000009")).toBeInTheDocument();
    });
    fireEvent.keyDown(input, { key: "Enter" });
    // Palette closes after navigation.
    await waitFor(() => {
      expect(screen.queryByPlaceholderText(/Search pages/)).not.toBeInTheDocument();
    });
  });

  it("clears remote results when the query is emptied", async () => {
    (api.get as jest.Mock).mockImplementation((url: string) =>
      url === "/search/"
        ? ok({
            groups: [
              {
                key: "books",
                label: "Library",
                results: [
                  {
                    id: "3",
                    title: "Quantum Gardening",
                    subtitle: "Book · L. Plant",
                    url: "/admin/library",
                  },
                ],
              },
            ],
          })
        : ok({}),
    );

    openPalette();
    const input = screen.getByPlaceholderText(/Search pages/);
    fireEvent.change(input, { target: { value: "quantum" } });
    await waitFor(() => {
      expect(screen.getByText("Quantum Gardening")).toBeInTheDocument();
    });
    fireEvent.change(input, { target: { value: "" } });
    await waitFor(() => {
      expect(screen.queryByText("Quantum Gardening")).not.toBeInTheDocument();
    });
  });
});
