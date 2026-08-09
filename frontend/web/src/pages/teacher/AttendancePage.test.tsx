/**
 * Teacher AttendancePage — smoke + interaction tests
 *
 * Covers the bulk attendance recording flow: classroom selection → roster
 * render → per-student status toggles → bulk actions → remarks → submit
 * (success payload + failure toast).
 */
import React from "react";
import { fireEvent, screen, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import dayjs from "dayjs";
import TeacherAttendancePage from "./AttendancePage";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { useClassrooms, useBulkRecordAttendance } from "../../api/hooks";
import { queryClient, makeUser, renderWithProviders } from "../../testUtils";

// ─── Mocks ────────────────────────────────────────────────────────────────────

const mockNavigate = jest.fn();
jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => mockNavigate,
}));

jest.mock("react-hot-toast", () => ({
  __esModule: true,
  default: { success: jest.fn(), error: jest.fn() },
}));
import toast from "react-hot-toast";

const mockToast = jest.mocked(toast);

jest.mock("../../api/client", () => ({
  api: { get: jest.fn() },
}));

jest.mock("../../api/hooks", () => ({
  useClassrooms: jest.fn(),
  useBulkRecordAttendance: jest.fn(),
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

const mockStudents = [
  {
    id: "1",
    admission_number: "A001",
    full_name: "Alice Johnson",
    email: "alice@demo.edusphere.school",
    gender: "female",
    is_active: true,
  },
  {
    id: "2",
    admission_number: "A002",
    full_name: "Bob Smith",
    email: "bob@demo.edusphere.school",
    gender: "male",
    is_active: true,
  },
];

function mockBulkRecord(resolver: jest.Mock) {
  (useBulkRecordAttendance as jest.Mock).mockReturnValue({
    mutateAsync: resolver,
    isPending: false,
  });
  return resolver;
}

/** Selects the Grade 5 5A classroom and waits for the roster to render. */
async function selectClassroom(user: ReturnType<typeof userEvent.setup>) {
  await user.selectOptions(screen.getByRole("combobox"), "1");
  expect(await screen.findByText("Alice Johnson")).toBeInTheDocument();
  expect(screen.getByText("Bob Smith")).toBeInTheDocument();
}

function rowFor(name: string): HTMLElement {
  const row = screen.getByText(name).closest("tr");
  if (!row) throw new Error(`No row found for ${name}`);
  return row;
}

/** Asserts a stat like "2 Present" by exact textContent (stat spans nest a number + label). */
function expectStat(text: string) {
  expect(screen.getByText((_, el) => el?.textContent === text)).toBeInTheDocument();
}

describe("Teacher AttendancePage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({
      user: makeUser({ role: "teacher", email: "sarah@demo.edusphere.school" }),
    });
    (useClassrooms as jest.Mock).mockReturnValue({ data: mockClassrooms, isLoading: false });
    mockBulkRecord(jest.fn().mockResolvedValue({}));
    (api.get as jest.Mock).mockResolvedValue(mockStudents);
  });

  // ─── Smoke ───────────────────────────────────────────────────────────────────

  test("renders the heading and classroom selector options", () => {
    renderWithProviders(<TeacherAttendancePage />);
    expect(screen.getByRole("heading", { name: "Record Attendance" })).toBeInTheDocument();
    expect(screen.getByRole("option", { name: "Grade 5 5A" })).toBeInTheDocument();
  });

  test("shows the student roster after selecting a classroom", async () => {
    const user = userEvent.setup();
    renderWithProviders(<TeacherAttendancePage />);
    await selectClassroom(user);
  });

  // ─── Interaction: status toggles + live summary ──────────────────────────────

  test("defaults every student to Present and updates stats as statuses change", async () => {
    const user = userEvent.setup();
    renderWithProviders(<TeacherAttendancePage />);
    await selectClassroom(user);

    // Defaults: 2 Present, 0 of everything else.
    expectStat("2 Present");
    expectStat("0 Absent");

    // Mark Alice absent → live stats update.
    await user.click(within(rowFor("Alice Johnson")).getByRole("button", { name: "Absent" }));
    expectStat("1 Present");
    expectStat("1 Absent");

    // Mark Bob late → stats follow (nobody is Present anymore).
    await user.click(within(rowFor("Bob Smith")).getByRole("button", { name: "Late" }));
    expectStat("0 Present");
    expectStat("1 Absent");
    expectStat("1 Late");
  });

  test("Mark All Absent / Mark All Present bulk actions apply to every row", async () => {
    const user = userEvent.setup();
    renderWithProviders(<TeacherAttendancePage />);
    await selectClassroom(user);

    await user.click(screen.getByRole("button", { name: "Mark All Absent" }));
    expectStat("0 Present");
    expectStat("2 Absent");

    // Active status is announced via aria-pressed on both rows.
    expect(within(rowFor("Alice Johnson")).getByRole("button", { name: "Absent" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );
    expect(within(rowFor("Bob Smith")).getByRole("button", { name: "Absent" })).toHaveAttribute(
      "aria-pressed",
      "true",
    );

    // Round-trip back to Present.
    await user.click(screen.getByRole("button", { name: "Mark All Present" }));
    expectStat("2 Present");
    expectStat("0 Absent");
    expect(
      within(rowFor("Alice Johnson")).getByRole("button", { name: "Present" }),
    ).toHaveAttribute("aria-pressed", "true");
  });

  test("submits the date picked in the date control, not just today", async () => {
    const user = userEvent.setup();
    const mutateAsync = mockBulkRecord(jest.fn().mockResolvedValue({}));
    renderWithProviders(<TeacherAttendancePage />);
    await selectClassroom(user);

    // Pick yesterday — valid because the input caps at today.
    const pastDate = dayjs().subtract(1, "day").format("YYYY-MM-DD");
    fireEvent.change(screen.getByLabelText("Date"), { target: { value: pastDate } });

    await user.click(screen.getByRole("button", { name: "Save Attendance" }));

    expect(mutateAsync).toHaveBeenCalledWith(
      expect.objectContaining({
        classroom_id: 1,
        date: pastDate,
        records: [
          { student_id: "1", status: "P", remarks: "" },
          { student_id: "2", status: "P", remarks: "" },
        ],
      }),
    );
  });

  // ─── Interaction: submit payload ─────────────────────────────────────────────

  test("submits the bulk payload with statuses, remarks and the selected date", async () => {
    const user = userEvent.setup();
    const mutateAsync = mockBulkRecord(jest.fn().mockResolvedValue({}));
    renderWithProviders(<TeacherAttendancePage />);
    await selectClassroom(user);

    // Toggle Alice to absent + leave a remark; keep Bob present with no remark.
    await user.click(within(rowFor("Alice Johnson")).getByRole("button", { name: "Absent" }));
    await user.type(within(rowFor("Alice Johnson")).getByPlaceholderText("Optional note…"), "sick");

    await user.click(screen.getByRole("button", { name: "Save Attendance" }));

    expect(mutateAsync).toHaveBeenCalledWith({
      classroom_id: 1,
      date: dayjs().format("YYYY-MM-DD"),
      records: [
        { student_id: "1", status: "A", remarks: "sick" },
        { student_id: "2", status: "P", remarks: "" },
      ],
    });
    expect(mockToast.success).toHaveBeenCalledWith("Attendance recorded for 2 students");

    // Success state: button flips to saved and disables.
    expect(screen.getByRole("button", { name: "✓ Attendance Saved" })).toBeDisabled();
  });

  test("shows an error toast and stays editable when the submission fails", async () => {
    const user = userEvent.setup();
    mockBulkRecord(jest.fn().mockRejectedValue(new Error("network")));
    renderWithProviders(<TeacherAttendancePage />);
    await selectClassroom(user);

    await user.click(screen.getByRole("button", { name: "Save Attendance" }));

    expect(mockToast.error).toHaveBeenCalledWith("Failed to record attendance. Please try again.");
    expect(mockToast.success).not.toHaveBeenCalled();
    // Not marked saved → the button is still the editable label and enabled.
    expect(screen.getByRole("button", { name: "Save Attendance" })).not.toBeDisabled();
  });
});
