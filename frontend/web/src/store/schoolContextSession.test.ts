/**
 * A super admin's switched school context must not outlive its session.
 *
 * Regression: `sms-school-context` persisted across sign-out, so the next
 * person to sign in on the same browser (e.g. a school admin) saw the panel
 * labelled with — and the "exit" link pointing at — the previous super
 * admin's school instead of their own.
 */
import { useAuthStore } from "./authStore";
import { useSchoolContextStore } from "./schoolContextStore";
import type { User } from "../types";

const SCHOOL = {
  id: "505f2c9e-0fc6-4c17-be10-0b6c6df9b5a2",
  name: "Bright Future Academy",
  code: "BFA",
  subdomain: "brightfuture",
};

const user = (role: User["role"]): User =>
  ({ id: "u-1", email: "x@y.z", full_name: "Test", role }) as User;

const tokens = { access: "a", refresh: "r" };

beforeEach(() => {
  useAuthStore.setState({
    user: null,
    tokens: null,
    isAuthenticated: false,
    planFeatures: null,
  });
  useSchoolContextStore.setState({ activeSchool: null });
});

describe("school context lifetime", () => {
  it("sign-out clears the selected school", () => {
    useSchoolContextStore.getState().setActiveSchool(SCHOOL);
    useAuthStore.setState({
      user: user("super_admin"),
      tokens,
      isAuthenticated: true,
    });

    useAuthStore.getState().logout();

    expect(useSchoolContextStore.getState().activeSchool).toBeNull();
    expect(useAuthStore.getState().isAuthenticated).toBe(false);
  });

  it("a school-admin sign-in drops a stale context from a previous super admin", () => {
    useSchoolContextStore.getState().setActiveSchool(SCHOOL);

    useAuthStore.getState().setAuth(user("school_admin"), tokens);

    expect(useSchoolContextStore.getState().activeSchool).toBeNull();
    expect(useAuthStore.getState().user?.role).toBe("school_admin");
  });

  it("a super-admin sign-in keeps the chosen school", () => {
    useSchoolContextStore.getState().setActiveSchool(SCHOOL);

    useAuthStore.getState().setAuth(user("super_admin"), tokens);

    expect(useSchoolContextStore.getState().activeSchool).toEqual(SCHOOL);
  });
});
