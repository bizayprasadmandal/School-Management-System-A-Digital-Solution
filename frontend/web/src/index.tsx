import ReactDOM from "react-dom/client";
import "./index.css";
import "./i18n";

// ─── Sentry error monitoring ────────────────────────────────────────────────
import * as Sentry from "@sentry/react";

// Only initialize when a DSN is configured (set REACT_APP_SENTRY_DSN).
// No hardcoded fallback: dev/CI builds and bundles built without the DSN
// stay Sentry-free instead of pushing noise to a real project.
const sentryDsn = process.env.REACT_APP_SENTRY_DSN;
if (sentryDsn) {
  Sentry.init({
    dsn: sentryDsn,
    environment: process.env.NODE_ENV || "development",
    release: process.env.REACT_APP_SENTRY_RELEASE || undefined,
    integrations: [Sentry.browserTracingIntegration(), Sentry.replayIntegration()],
    // Performance monitoring (sample rate 10% in dev, 50% in prod)
    tracesSampleRate: process.env.NODE_ENV === "production" ? 0.5 : 0.1,
    // Session replay (sample rate 0% in dev, 10% in prod)
    replaysSessionSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 0.0,
    replaysOnErrorSampleRate: 1.0, // Always capture replays on error
  });
}

// ─── Global dayjs configuration ─────────────────────────────────────────────
// Extend dayjs with plugins at the entry point so all code-split chunks
// inherit the extended methods (e.g., .fromNow(), .toISOString()).
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import duration from "dayjs/plugin/duration";
dayjs.extend(relativeTime);
dayjs.extend(duration);

// ─── Main App ────────────────────────────────────────────────────────────────
import App from "./App";

// Clear the chunk-reload flag after a successful load so subsequent reloads
// work correctly if the user triggers a rebuild mid-session.
window.addEventListener("load", () => {
  sessionStorage.removeItem("chunkReloaded");
});

const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);
root.render(<App />);

// ─── Chunk-loading error recovery ───────────────────────────────────────────
// CRA generates code-split chunks with content hashes. When the Docker
// container restarts, old chunks are removed and new ones are generated.
// The browser may have cached index.html referencing old chunk names,
// causing "Loading chunk X failed" errors. This handler catches those
// errors and reloads the page to pick up the fresh index.html.
window.addEventListener(
  "error",
  (event) => {
    const target = event.target as HTMLElement | null;
    if (
      target?.tagName === "SCRIPT" &&
      (target as HTMLScriptElement).src?.includes("/static/js/") &&
      !sessionStorage.getItem("chunkReloaded")
    ) {
      sessionStorage.setItem("chunkReloaded", "true");
      // Show a brief visual hint before reloading
      const root = document.getElementById("root");
      if (root) {
        root.innerHTML = `<div style="display:flex;height:100vh;align-items:center;justify-content:center;flex-direction:column;gap:12px;background:#f8fafc;color:#475569;font-family:system-ui">
        <div style="width:32px;height:32px;border:3px solid #6366f1;border-top-color:transparent;border-radius:50%;animation:spin .8s linear infinite"></div>
        <p style="font-size:14px">Updating app…</p>
        <style>@keyframes spin{to{transform:rotate(360deg)}}</style>
      </div>`;
      }
      setTimeout(() => window.location.reload(), 600);
    }
  },
  true,
);

// Suppress duplicate chunk errors in the console after the reload flag is set
window.addEventListener(
  "error",
  (event) => {
    const target = event.target as HTMLElement | null;
    if (
      target?.tagName === "SCRIPT" &&
      (target as HTMLScriptElement).src?.includes("/static/js/") &&
      sessionStorage.getItem("chunkReloaded")
    ) {
      event.preventDefault();
    }
  },
  true,
);

// ─── Hide pre-React loading screen ───────────────────────────────────────────
const loader = document.getElementById("app-loading");
if (loader) {
  loader.classList.add("hidden");
  setTimeout(() => loader.remove(), 400);
}
