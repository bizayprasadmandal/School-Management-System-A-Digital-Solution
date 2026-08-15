/**
 * Role → dashboard route mapping — single source of truth for post-login
 * redirects. Route paths must match the role-scoped layouts in App.tsx.
 */
export const ROLE_ROUTES: Record<string, string> = {
  super_admin: "/admin",
  school_admin: "/admin",
  accountant: "/accountant",
  teacher: "/teacher",
  student: "/student",
  parent: "/parent",
  librarian: "/librarian",
  counselor: "/counselor",
};
