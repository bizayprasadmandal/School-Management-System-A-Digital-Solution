/**
 * Auth Store — Zustand global state for authentication
 */

import { create } from "zustand";
import { persist, createJSONStorage } from "zustand/middleware";
import type { User, AuthTokens } from "../types";

/** Plan entitlements from GET /auth/me/ → plan_features. */
export interface PlanFeatures {
  plan: "basic" | "standard" | "premium";
  features: string[];
  is_premium: boolean;
}

interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  planFeatures: PlanFeatures | null;

  // Actions
  setAuth: (user: User, tokens: AuthTokens) => void;
  setUser: (user: User) => void;
  setTokens: (tokens: AuthTokens) => void;
  setPlanFeatures: (planFeatures: PlanFeatures | null) => void;
  logout: () => void;
  setLoading: (loading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      planFeatures: null,

      setAuth: (user, tokens) => set({ user, tokens, isAuthenticated: true }),

      setUser: (user) => set({ user }),

      setPlanFeatures: (planFeatures) => set({ planFeatures }),

      setTokens: (tokens) => set({ tokens }),

      logout: () => set({ user: null, tokens: null, isAuthenticated: false, planFeatures: null }),

      setLoading: (isLoading) => set({ isLoading }),
    }),
    {
      name: "sms-auth",
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        tokens: state.tokens,
        isAuthenticated: state.isAuthenticated,
        planFeatures: state.planFeatures,
      }),
    },
  ),
);

// Derived helpers
export const useUser = () => useAuthStore((s) => s.user);
export const useIsAuthenticated = () => useAuthStore((s) => s.isAuthenticated);
export const useUserRole = () => useAuthStore((s) => s.user?.role);
export const usePlanFeatures = () => useAuthStore((s) => s.planFeatures);

/** Whether the current plan unlocks a feature key (server registry is the
 * source of truth — this only reads what /auth/me/ reported). */
export const useHasFeature = (featureKey: string): boolean =>
  useAuthStore((s) => {
    if (s.user?.role === "super_admin") return true;
    return s.planFeatures?.features?.includes(featureKey) ?? false;
  });

/**
 * UI-side lock check for gating surfaces — deliberately **fail-open**: when
 * plan entitlements haven't loaded yet (or /auth/me/ failed) content renders,
 * because the backend remains the enforcement layer (403 + upgrade hint).
 * A lock notice only appears once we *positively* know the plan lacks the
 * feature, so premium schools never flash upgrade prompts on load.
 */
export const useFeatureLocked = (featureKey?: string): boolean =>
  useAuthStore((s) => {
    if (!featureKey) return false;
    if (s.user?.role === "super_admin") return false;
    const pf = s.planFeatures;
    if (!pf) return false; // unknown yet — let the backend decide
    return !pf.features.includes(featureKey);
  });
