/**
 * UI Store — Zustand global state for UI-level cross-component coordination.
 *
 * Kept separate from authStore so auth concerns don't get tangled with
 * transient UI state like banner dismissal flags.
 */

import { create } from "zustand";

export type WSStatus = "connecting" | "connected" | "disconnected" | "error";

interface UIState {
  /** Has the user explicitly dismissed the email-verification banner? */
  bannerDismissed: boolean;
  dismissBanner: () => void;

  /** Has the user explicitly dismissed the backup-code warning banner? */
  backupBannerDismissed: boolean;
  dismissBackupBanner: () => void;

  /** WebSocket connection status for the notification channel */
  wsStatus: WSStatus;
  setWsStatus: (status: WSStatus) => void;
}

export const useUIStore = create<UIState>()((set) => ({
  bannerDismissed: false,
  dismissBanner: () => set({ bannerDismissed: true }),

  backupBannerDismissed: false,
  dismissBackupBanner: () => set({ backupBannerDismissed: true }),

  wsStatus: "disconnected",
  setWsStatus: (status) => set({ wsStatus: status }),
}));
