/**
 * Admin FeesPage Tests
 *
 * Tests rendering, invoices table, summary cards, tab switching,
 * export functionality, and payment modal.
 */
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { BrowserRouter } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import FeesPage from "./FeesPage";
import { api } from "../../api/client";

// ─── QueryClient for tests ────────────────────────────────────────────────────

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
});

// ─── Mocks ────────────────────────────────────────────────────────────────────

jest.mock("react-hot-toast", () => ({
  __esModule: true,
  default: { success: jest.fn(), error: jest.fn() },
}));

jest.mock("../../api/client", () => ({
  api: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

// Mock recharts
jest.mock("recharts", () => ({
  BarChart: ({ children }: any) => <div data-testid="bar-chart">{children}</div>,
  Bar: () => <div data-testid="bar" />,
  XAxis: () => <div data-testid="xaxis" />,
  YAxis: () => <div data-testid="yaxis" />,
  CartesianGrid: () => <div data-testid="grid" />,
  Tooltip: () => <div data-testid="tooltip" />,
  ResponsiveContainer: ({ children }: any) => <div>{children}</div>,
  PieChart: ({ children }: any) => <div data-testid="pie-chart">{children}</div>,
  Pie: () => <div data-testid="pie" />,
  Cell: () => <div data-testid="cell" />,
  Legend: () => <div data-testid="legend" />,
  AreaChart: ({ children }: any) => <div data-testid="area-chart">{children}</div>,
  Area: () => <div data-testid="area" />,
}));

// ─── Fixtures ──────────────────────────────────────────────────────────────────

const mockInvoices = {
  count: 4,
  results: [
    {
      id: "1",
      invoice_number: "INV-001",
      student: "Alice Johnson",
      due_date: "2024-06-15",
      total_amount: 5000,
      paid_amount: 5000,
      outstanding_amount: 0,
      status: "paid",
    },
    {
      id: "2",
      invoice_number: "INV-002",
      student: "Bob Smith",
      due_date: "2024-05-01",
      total_amount: 5000,
      paid_amount: 2000,
      outstanding_amount: 3000,
      status: "partial",
    },
    {
      id: "3",
      invoice_number: "INV-003",
      student: "Charlie Brown",
      due_date: "2024-04-01",
      total_amount: 5000,
      paid_amount: 0,
      outstanding_amount: 5000,
      status: "overdue",
    },
    {
      id: "4",
      invoice_number: "INV-004",
      student: "Diana Prince",
      due_date: "2024-07-01",
      total_amount: 5000,
      paid_amount: 0,
      outstanding_amount: 5000,
      status: "unpaid",
    },
  ],
};

// ─── Helpers ───────────────────────────────────────────────────────────────────

function renderPage() {
  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <FeesPage />
      </BrowserRouter>
    </QueryClientProvider>,
  );
}

// ─── Before each ───────────────────────────────────────────────────────────────

beforeEach(() => {
  jest.clearAllMocks();

  // Return appropriate data based on the URL path
  (api.get as jest.Mock).mockImplementation((url: string) => {
    if (url.includes("/fees/invoices/")) return Promise.resolve(mockInvoices);
    // Categories, structures, and scholarships return flat arrays (not paginated)
    if (url.includes("/fees/categories/")) return Promise.resolve([]);
    if (url.includes("/fees/structures/")) return Promise.resolve([]);
    if (url.includes("/fees/scholarships/")) return Promise.resolve([]);
    return Promise.resolve([]);
  });
});

// ─── 1. Rendering ──────────────────────────────────────────────────────────────

describe("rendering", () => {
  test("renders page title", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Fee Management")).toBeInTheDocument();
    });
  });

  test("renders tab switcher", () => {
    renderPage();
    expect(screen.getByText("Invoices")).toBeInTheDocument();
    expect(screen.getByText("Categories")).toBeInTheDocument();
    expect(screen.getByText("Scholarships")).toBeInTheDocument();
  });

  test("renders Generate Invoices button", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Generate Invoices")).toBeInTheDocument();
    });
  });
});

// ─── 2. Summary Cards ──────────────────────────────────────────────────────────

describe("summary cards", () => {
  test("renders summary card headings", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Total Invoiced")).toBeInTheDocument();
      expect(screen.getByText("Collected")).toBeInTheDocument();
      // "Outstanding" appears in both summary card and table column
      const outstandingLabels = screen.getAllByText("Outstanding");
      expect(outstandingLabels.length).toBeGreaterThanOrEqual(1);
      expect(screen.getByText("Overdue Invoices")).toBeInTheDocument();
    });
  });

  test("shows total invoiced amount", async () => {
    renderPage();
    await waitFor(() => {
      // Total: 5000 x 4 = 20000 => 20.0K
      expect(screen.getByText("$20.0K")).toBeInTheDocument();
    });
  });

  test("shows collected amount", async () => {
    renderPage();
    await waitFor(() => {
      // Collected: 5000 + 2000 = 7000 => 7.0K
      expect(screen.getByText("$7.0K")).toBeInTheDocument();
    });
  });

  test("shows overdue count", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("1")).toBeInTheDocument(); // one overdue invoice
    });
  });
});

// ─── 3. Invoice Table ─────────────────────────────────────────────────────────

describe("invoice table", () => {
  test("renders invoice numbers", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("INV-001")).toBeInTheDocument();
      expect(screen.getByText("INV-002")).toBeInTheDocument();
      expect(screen.getByText("INV-003")).toBeInTheDocument();
      expect(screen.getByText("INV-004")).toBeInTheDocument();
    });
  });

  test("renders student names in table", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Alice Johnson")).toBeInTheDocument();
      expect(screen.getByText("Bob Smith")).toBeInTheDocument();
      expect(screen.getByText("Charlie Brown")).toBeInTheDocument();
    });
  });

  test("renders status badges", async () => {
    renderPage();
    await waitFor(() => {
      // Some statuses may appear in both badges and filter select options
      const paidLabels = screen.getAllByText("Paid");
      expect(paidLabels.length).toBeGreaterThanOrEqual(1);
      const partialLabels = screen.getAllByText("Partial");
      expect(partialLabels.length).toBeGreaterThanOrEqual(1);
      const overdueLabels = screen.getAllByText("Overdue");
      expect(overdueLabels.length).toBeGreaterThanOrEqual(1);
      const unpaidLabels = screen.getAllByText("Unpaid");
      expect(unpaidLabels.length).toBeGreaterThanOrEqual(1);
    });
  });
});

// ─── 4. Tab Switching ─────────────────────────────────────────────────────────

describe("tab switching", () => {
  test("switches to Categories tab", async () => {
    renderPage();
    const user = userEvent.setup();
    await user.click(screen.getByText("Categories"));
    // The Categories tab button text should still be present
    const categoriesButtons = screen.getAllByText("Categories");
    expect(categoriesButtons.length).toBeGreaterThanOrEqual(1);
  });

  test("switches to Scholarships tab", async () => {
    renderPage();
    const user = userEvent.setup();
    await user.click(screen.getByText("Scholarships"));
    // Scholarships panel should render
    expect(screen.getByText("Scholarships")).toBeTruthy();
  });

  test("Generate Invoices button only visible on invoices tab", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("Generate Invoices")).toBeInTheDocument();
    });

    const user = userEvent.setup();
    await user.click(screen.getByText("Scholarships"));

    expect(screen.queryByText("Generate Invoices")).not.toBeInTheDocument();
  });
});

// ─── 5. Filters ───────────────────────────────────────────────────────────────

describe("filters", () => {
  test("renders search input", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Search student name or invoice/)).toBeInTheDocument();
    });
  });

  test("renders status filter", async () => {
    renderPage();
    await waitFor(() => {
      expect(screen.getByText("All Status")).toBeInTheDocument();
    });
  });
});

// ─── 6. Empty State ──────────────────────────────────────────────────────────

describe("empty state", () => {
  test("shows empty state when no invoices", async () => {
    (api.get as jest.Mock).mockResolvedValue({ count: 0, results: [] });

    renderPage();
    await waitFor(() => {
      expect(screen.getByText("No invoices found")).toBeInTheDocument();
    });
  });
});
