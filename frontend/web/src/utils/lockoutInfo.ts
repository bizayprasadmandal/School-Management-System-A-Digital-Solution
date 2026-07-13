/**
 * lockoutInfo — Shared helper for detecting backup-code lockout or
 * remaining-attempts info from a normalized API error.
 */
import type { NormalizedError } from "../api/client";

export type LockoutInfo = {
  type: "lockout" | "attempts";
  message: string;
  remaining: number;
} | null;

/**
 * Detect backup-code lockout or remaining-attempts info from an API error.
 * Returns structured info if the error is a lockout (429) or contains
 * attempt-count info (400 with "remaining" in the message).
 */
export function getLockoutInfo(err: NormalizedError): LockoutInfo {
  if (err.status === 429) {
    return { type: "lockout", message: err.message, remaining: 0 };
  }
  if (err.status === 400 && err.message.toLowerCase().includes("remaining")) {
    const match = err.message.match(/\d+/);
    const remaining = match ? parseInt(match[0], 10) : 0;
    return { type: "attempts", message: err.message, remaining };
  }
  return null;
}
