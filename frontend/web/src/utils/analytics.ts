/**
 * Analytics — lightweight event tracking
 *
 * Provides a `trackEvent` function that logs events to the console in
 * development mode.  Swap the implementation for a real analytics
 * provider (PostHog, Mixpanel, GA4, etc.) by changing the body of
 * `trackEvent` — the call sites stay the same.
 *
 * Usage:
 *   trackEvent("verification_email_sent", { source: "login_page" });
 */

const IS_DEV = process.env.NODE_ENV === "development";

interface TrackEventProperties {
  [key: string]: string | number | boolean | undefined;
}

/**
 * Track an analytics event.
 *
 * @param event  - Machine-readable event name (snake_case).
 * @param props  - Optional key-value properties to attach to the event.
 */
export function trackEvent(event: string, props?: TrackEventProperties): void {
  if (IS_DEV) {
    console.log(`[Analytics] ${event}`, props ?? "");
  }

  // ── Future: plug in real analytics provider here ──────────────
  // e.g. posthog.capture(event, props);
  // e.g. gtag("event", event, props);
  // e.g. mixpanel.track(event, props);
}
