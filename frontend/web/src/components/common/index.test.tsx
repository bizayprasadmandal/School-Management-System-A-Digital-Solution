/**
 * Common UI Components — Button, Modal, DataTable
 *
 * Covers the shared primitives used across every role dashboard:
 * button default-type safety, modal focus/escape behavior, and the
 * table's render/fallback/pagination contract.
 */
import React from "react";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button, Modal, DataTable } from "./index";

// ─── Button ──────────────────────────────────────────────────────────────────

describe("Button", () => {
  test("renders children and defaults to type='button'", () => {
    render(<Button>Save</Button>);
    const btn = screen.getByRole("button", { name: /save/i });
    expect(btn).toHaveAttribute("type", "button");
  });

  test("respects an explicit type prop", () => {
    render(<Button type="submit">Submit</Button>);
    expect(screen.getByRole("button", { name: /submit/i })).toHaveAttribute("type", "submit");
  });

  test("applies variant class", () => {
    render(<Button variant="danger">Delete</Button>);
    expect(screen.getByRole("button", { name: /delete/i }).className).toContain("bg-red-600");
  });

  test("shows a spinner and disables the button while loading", () => {
    render(<Button loading>Save</Button>);
    const btn = screen.getByRole("button", { name: /save/i });
    expect(btn).toBeDisabled();
    expect(btn.querySelector(".animate-spin")).toBeInTheDocument();
  });

  test("is disabled when disabled prop is set", () => {
    render(<Button disabled>Save</Button>);
    expect(screen.getByRole("button", { name: /save/i })).toBeDisabled();
  });

  test("fires onClick when clicked", async () => {
    const onClick = jest.fn();
    render(<Button onClick={onClick}>Go</Button>);
    await userEvent.click(screen.getByRole("button", { name: /go/i }));
    expect(onClick).toHaveBeenCalledTimes(1);
  });
});

// ─── Modal ───────────────────────────────────────────────────────────────────

describe("Modal", () => {
  const onClose = jest.fn();

  beforeEach(() => onClose.mockClear());

  test("renders nothing when closed", () => {
    render(
      <Modal open={false} onClose={onClose} title="Title">
        content
      </Modal>,
    );
    expect(screen.queryByRole("dialog")).not.toBeInTheDocument();
  });

  test("renders title, description and children when open", () => {
    render(
      <Modal open onClose={onClose} title="Edit student" description="Update details">
        <p>name input</p>
      </Modal>,
    );
    const dialog = screen.getByRole("dialog");
    expect(dialog).toBeInTheDocument();
    expect(screen.getByText("Edit student")).toBeInTheDocument();
    expect(screen.getByText("Update details")).toBeInTheDocument();
    expect(screen.getByText("name input")).toBeInTheDocument();
  });

  test("closes on Escape", async () => {
    render(
      <Modal open onClose={onClose} title="Title">
        content
      </Modal>,
    );
    await userEvent.keyboard("{Escape}");
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  test("does not close on Escape when disableEscape is set", async () => {
    render(
      <Modal open onClose={onClose} disableEscape title="Title">
        content
      </Modal>,
    );
    await userEvent.keyboard("{Escape}");
    expect(onClose).not.toHaveBeenCalled();
  });

  test("closes when the backdrop is clicked", async () => {
    render(
      <Modal open onClose={onClose} title="Title">
        content
      </Modal>,
    );
    const backdrop = document.querySelector(".bg-black\\/50");
    expect(backdrop).not.toBeNull();
    await userEvent.click(backdrop as Element);
    expect(onClose).toHaveBeenCalledTimes(1);
  });

  test("renders the footer", () => {
    render(
      <Modal open onClose={onClose} title="Title" footer={<button>Confirm</button>}>
        content
      </Modal>,
    );
    expect(screen.getByRole("button", { name: /confirm/i })).toBeInTheDocument();
  });
});

// ─── DataTable ───────────────────────────────────────────────────────────────

interface SampleRow {
  id: number;
  name: string;
  score?: number;
}

const columns = [
  { key: "name", header: "Name" },
  { key: "score", header: "Score" },
];

const rows: SampleRow[] = [
  { id: 1, name: "Alice", score: 90 },
  { id: 2, name: "Bob" },
];

describe("DataTable", () => {
  test("renders column headers", () => {
    render(<DataTable columns={columns} data={[] as SampleRow[]} rowKey={(r) => r.id} />);
    expect(screen.getByText("Name")).toBeInTheDocument();
    expect(screen.getByText("Score")).toBeInTheDocument();
  });

  test("renders cell values with an em-dash fallback for missing fields", () => {
    render(<DataTable columns={columns} data={rows} rowKey={(r) => r.id} />);
    expect(screen.getByText("Alice")).toBeInTheDocument();
    expect(screen.getByText("90")).toBeInTheDocument();
    expect(screen.getByText("Bob")).toBeInTheDocument();
    expect(screen.getByText("—")).toBeInTheDocument();
  });

  test("uses the custom render function when provided", () => {
    const customColumns = [
      { key: "name", header: "Name", render: (r: SampleRow) => <strong>{r.name}!</strong> },
    ];
    render(<DataTable columns={customColumns} data={rows} rowKey={(r) => r.id} />);
    expect(screen.getByText("Alice!")).toBeInTheDocument();
  });

  test("shows the empty message when there is no data", () => {
    render(
      <DataTable
        columns={columns}
        data={[] as SampleRow[]}
        rowKey={(r) => r.id}
        emptyMessage="Nothing here"
      />,
    );
    expect(screen.getByText("Nothing here")).toBeInTheDocument();
  });

  test("calls onRowClick with the clicked row", async () => {
    const onRowClick = jest.fn();
    render(
      <DataTable columns={columns} data={rows} rowKey={(r) => r.id} onRowClick={onRowClick} />,
    );
    await userEvent.click(screen.getByText("Alice"));
    expect(onRowClick).toHaveBeenCalledWith(rows[0]);
  });

  test("renders pagination controls when page/total/onPageChange are provided", async () => {
    const onPageChange = jest.fn();
    render(
      <DataTable
        columns={columns}
        data={rows}
        rowKey={(r) => r.id}
        page={1}
        total={40}
        pageSize={10}
        onPageChange={onPageChange}
      />,
    );
    const next = screen.getByRole("button", { name: /next/i });
    await userEvent.click(next);
    expect(onPageChange).toHaveBeenCalledWith(2);
  });

  test("skips pagination when the props are absent", () => {
    render(<DataTable columns={columns} data={rows} rowKey={(r) => r.id} />);
    expect(screen.queryByRole("button", { name: /next/i })).not.toBeInTheDocument();
  });
});
