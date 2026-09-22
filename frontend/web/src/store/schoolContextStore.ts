/**
 * School Context Store — Zustand store for super admin school switching.
 *
 * When a super admin selects a school via the SchoolSwitcher dropdown,
 * the active school ID is stored here. The API client picks it up and
 * sends it as the X-School-ID header, which the backend TenantMiddleware
 * uses to override the tenant context.
 */

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { QueryClient } from "@tanstack/react-query";

/**
 * Module-level handle to the app QueryClient, set once in App.tsx.
 * Lets non-React modules invalidate queries when the tenant context
 * changes so school-scoped data refetches immediately.
 */
let _queryClient: QueryClient | null = null;
export const registerQueryClient = (qc: QueryClient) => {
  _queryClient = qc;
};

/** Invalidate every cached query — used on tenant switches. */
export const invalidateAllQueries = () => {
  void _queryClient?.invalidateQueries();
};

export interface SchoolContext {
  id: string;
  name: string;
  code: string;
  subdomain: string;
}

interface SchoolContextState {
  /** The currently selected school context (null = own context / no switch). */
  activeSchool: SchoolContext | null;
  /** Set the active school context. */
  setActiveSchool: (school: SchoolContext | null) => void;
  /** Clear the school context (revert to own user context). */
  clearSchoolContext: () => void;
}

export const useSchoolContextStore = create<SchoolContextState>()(
  persist(
    (set) => ({
      activeSchool: null,
      setActiveSchool: (school) => set({ activeSchool: school }),
      clearSchoolContext: () => set({ activeSchool: null }),
    }),
    {
      name: "sms-school-context",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ activeSchool: state.activeSchool }),
    },
  ),
);
