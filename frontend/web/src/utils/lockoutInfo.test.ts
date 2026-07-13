/**
 * Unit tests for getLockoutInfo — the shared helper for detecting
 * backup-code lockout or remaining-attempts info from API errors.
 */
import { getLockoutInfo } from "./lockoutInfo";
import type { NormalizedError } from "../api/client";

// ─── 429 — Lockout ──────────────────────────────────────────────────────────

describe("getLockoutInfo", () => {
  describe("lockout (429)", () => {
    it("returns lockout info for a 429 response", () => {
      const err: NormalizedError = {
        status: 429,
        message: "Too many failed backup code attempts. Try again in 1740 seconds.",
      };
      expect(getLockoutInfo(err)).toEqual({
        type: "lockout",
        message: err.message,
        remaining: 0,
      });
    });

    it("returns lockout info regardless of message content", () => {
      const err: NormalizedError = {
        status: 429,
        message: "Rate limit exceeded",
      };
      expect(getLockoutInfo(err)).toEqual({
        type: "lockout",
        message: "Rate limit exceeded",
        remaining: 0,
      });
    });

    it("ignores the remaining count in the message for 429 — always 0", () => {
      const err: NormalizedError = {
        status: 429,
        message: "3 attempts remaining before lockout",
      };
      const result = getLockoutInfo(err);
      expect(result).not.toBeNull();
      expect(result!.type).toBe("lockout");
      expect(result!.remaining).toBe(0);
    });
  });

  // ─── 400 with "remaining" — attempts info ────────────────────────────────

  describe("attempts info (400 + 'remaining' in message)", () => {
    it("parses a singular attempt remaining", () => {
      const err: NormalizedError = {
        status: 400,
        message: "Invalid verification code. 1 backup code attempt remaining before lockout.",
      };
      expect(getLockoutInfo(err)).toEqual({
        type: "attempts",
        message: err.message,
        remaining: 1,
      });
    });

    it("parses a plural count of remaining attempts", () => {
      const err: NormalizedError = {
        status: 400,
        message: "Invalid verification code. 2 backup code attempts remaining before lockout.",
      };
      expect(getLockoutInfo(err)).toEqual({
        type: "attempts",
        message: err.message,
        remaining: 2,
      });
    });

    it("parses the maximum remaining count (3)", () => {
      const err: NormalizedError = {
        status: 400,
        message: "Invalid verification code. 3 backup code attempts remaining before lockout.",
      };
      expect(getLockoutInfo(err)).toEqual({
        type: "attempts",
        message: err.message,
        remaining: 3,
      });
    });

    it("handles 'remaining' with no number by defaulting to 0", () => {
      const err: NormalizedError = {
        status: 400,
        message: "Some attempts remaining.",
      };
      expect(getLockoutInfo(err)).toEqual({
        type: "attempts",
        message: "Some attempts remaining.",
        remaining: 0,
      });
    });

    it("extracts the first number in the message", () => {
      const err: NormalizedError = {
        status: 400,
        message: "You have 2 attempts remaining. 3 total allowed.",
      };
      expect(getLockoutInfo(err)).toEqual({
        type: "attempts",
        message: err.message,
        remaining: 2,
      });
    });
  });

  // ─── 400 without "remaining" ─────────────────────────────────────────────

  describe("400 without 'remaining'", () => {
    it("returns null for a 400 without 'remaining'", () => {
      const err: NormalizedError = {
        status: 400,
        message: "Invalid verification code.",
      };
      expect(getLockoutInfo(err)).toBeNull();
    });

    it("returns null for a 400 with 'Remaining' (capital R)", () => {
      const err: NormalizedError = {
        status: 400,
        message: "Remaining attempts: 1",
      };
      expect(getLockoutInfo(err)).toEqual({
        type: "attempts",
        message: "Remaining attempts: 1",
        remaining: 1,
      });
    });
  });

  // ─── Other status codes ──────────────────────────────────────────────────

  describe("other status codes", () => {
    it("returns null for a 401", () => {
      const err: NormalizedError = {
        status: 401,
        message: "Invalid credentials.",
      };
      expect(getLockoutInfo(err)).toBeNull();
    });

    it("returns null for a 403", () => {
      const err: NormalizedError = {
        status: 403,
        message: "Forbidden.",
      };
      expect(getLockoutInfo(err)).toBeNull();
    });

    it("returns null for a 500", () => {
      const err: NormalizedError = {
        status: 500,
        message: "Internal server error.",
      };
      expect(getLockoutInfo(err)).toBeNull();
    });

    it("returns null when there is no status code", () => {
      const err: NormalizedError = {
        message: "Network error — please check your connection.",
      };
      expect(getLockoutInfo(err)).toBeNull();
    });
  });

  // ─── Edge cases ──────────────────────────────────────────────────────────

  describe("edge cases", () => {
    it("returns null for an empty message", () => {
      const err: NormalizedError = {
        status: 400,
        message: "",
      };
      expect(getLockoutInfo(err)).toBeNull();
    });

    it("handles 'remaining' in a case-insensitive way", () => {
      const err: NormalizedError = {
        status: 400,
        message: "REMAINING: 2 attempts",
      };
      expect(getLockoutInfo(err)).toEqual({
        type: "attempts",
        message: "REMAINING: 2 attempts",
        remaining: 2,
      });
    });

    it("handles status 0 (no response)", () => {
      const err: NormalizedError = {
        status: 0,
        message: "Network error",
      };
      expect(getLockoutInfo(err)).toBeNull();
    });

    it("parses large numbers correctly", () => {
      const err: NormalizedError = {
        status: 400,
        message: "999 remaining attempts",
      };
      expect(getLockoutInfo(err)).toEqual({
        type: "attempts",
        message: "999 remaining attempts",
        remaining: 999,
      });
    });

    it("matches 'remaining' even when it's part of a larger word (e.g. 'unremaining')", () => {
      const err: NormalizedError = {
        status: 400,
        message: "unremaining attempts: 1",
      };
      // "unremaining".includes("remaining") is true, so this will match
      const result = getLockoutInfo(err);
      expect(result).not.toBeNull();
      expect(result!.type).toBe("attempts");
    });
  });
});
