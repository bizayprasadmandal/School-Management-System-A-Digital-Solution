import { useAuthStore } from "../useAuthStore";

afterEach(() => {
  useAuthStore.getState().logout();
});

describe("useAuthStore", () => {
  it("starts logged out", () => {
    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.tokens).toBeNull();
  });

  it("setAuth marks the user authenticated with tokens", () => {
    const user = { id: 1, email: "student@example.com", role: "student" };
    const tokens = { access: "abc", refresh: "def" };

    useAuthStore.getState().setAuth(user, tokens);

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(true);
    expect(state.user).toEqual(user);
    expect(state.tokens).toEqual(tokens);
  });

  it("logout clears auth state", () => {
    useAuthStore
      .getState()
      .setAuth({ id: 2, email: "t@example.com", role: "teacher" }, { access: "x", refresh: "y" });

    useAuthStore.getState().logout();

    const state = useAuthStore.getState();
    expect(state.isAuthenticated).toBe(false);
    expect(state.user).toBeNull();
    expect(state.tokens).toBeNull();
  });
});
