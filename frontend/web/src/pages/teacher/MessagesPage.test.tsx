/**
 * Teacher MessagesPage — smoke + conversation-view tests.
 */
import React from "react";
import { screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import MessagesPage from "./MessagesPage";
import { useAuthStore } from "../../store/authStore";
import { api } from "../../api/client";
import { queryClient, makeUser, renderWithProviders } from "../../testUtils";

jest.mock("react-router-dom", () => ({
  ...jest.requireActual("react-router-dom"),
  useNavigate: () => jest.fn(),
}));

jest.mock("react-hot-toast", () => ({
  __esModule: true,
  default: { success: jest.fn(), error: jest.fn() },
}));

jest.mock("../../api/client", () => ({
  api: { get: jest.fn(), post: jest.fn(), patch: jest.fn(), delete: jest.fn() },
}));

const mockThreads = [
  {
    partner: { id: "p1", name: "Jane Smith" },
    last_message: { content: "Is the homework due Friday?", sent_at: "2024-06-09T10:00:00Z" },
    unread_count: 2,
  },
  {
    partner: { id: "p2", name: "Mr. Patel" },
    last_message: { content: "Thanks for the update.", sent_at: "2024-06-08T09:00:00Z" },
    unread_count: 0,
  },
];

describe("Teacher MessagesPage", () => {
  beforeEach(() => {
    queryClient.clear();
    jest.clearAllMocks();
    useAuthStore.setState({ user: makeUser({ role: "teacher" }) });
    (api.get as jest.Mock).mockImplementation((url: string) => {
      if (url.includes("messages/inbox")) return Promise.resolve(mockThreads);
      if (url.includes("conversation/")) {
        return Promise.resolve([
          {
            id: "m1",
            content: "Hello, is this class going on a trip?",
            sent_at: "2024-06-09T09:00:00Z",
            is_mine: false,
          },
          {
            id: "m2",
            content: "Yes, permission slips next week.",
            sent_at: "2024-06-09T09:05:00Z",
            is_mine: true,
          },
        ]);
      }
      return Promise.resolve([]);
    });
    (api.post as jest.Mock).mockResolvedValue({});
  });

  test("renders the thread list", async () => {
    renderWithProviders(<MessagesPage />);
    expect(screen.getByRole("heading", { name: "Messages" })).toBeInTheDocument();
    expect(await screen.findByText("Jane Smith")).toBeInTheDocument();
    expect(screen.getByText("Mr. Patel")).toBeInTheDocument();
  });

  test("opens a conversation and renders messages", async () => {
    const user = userEvent.setup();
    renderWithProviders(<MessagesPage />);
    await user.click(await screen.findByText("Jane Smith"));
    expect(await screen.findByText("Hello, is this class going on a trip?")).toBeInTheDocument();
    expect(screen.getByText("Yes, permission slips next week.")).toBeInTheDocument();
  });

  test("sends a reply from the compose bar", async () => {
    const user = userEvent.setup();
    renderWithProviders(<MessagesPage />);
    await user.click(await screen.findByText("Jane Smith"));
    await screen.findByText("Hello, is this class going on a trip?");

    await user.type(screen.getByPlaceholderText("Type your reply…"), "Yes, forms are out");
    await user.click(screen.getByRole("button", { name: /Send/ }));

    expect(api.post).toHaveBeenCalledWith("/communication/messages/", {
      recipient: "p1",
      content: "Yes, forms are out",
    });
  });

  test("shows empty state when the inbox has no threads", async () => {
    (api.get as jest.Mock).mockResolvedValue([]);
    renderWithProviders(<MessagesPage />);
    expect(await screen.findByText("No messages yet")).toBeInTheDocument();
  });
});
