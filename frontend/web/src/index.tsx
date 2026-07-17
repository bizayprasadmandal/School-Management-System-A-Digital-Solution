import ReactDOM from "react-dom/client";
import "./index.css";

// ─── Sentry error monitoring ────────────────────────────────────────────────
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: process.env.REACT_APP_SENTRY_DSN || "https://1d07b7ecc3b227d21f1649829f886ad5@o4511743482789888.ingest.de.sentry.io/4511743491309648",
  environment: process.env.NODE_ENV || "development",
  integrations: [
    Sentry.browserTracingIntegration(),
    Sentry.replayIntegration(),
  ],
  // Performance monitoring (sample rate 10% in dev, 50% in prod)
  tracesSampleRate: process.env.NODE_ENV === "production" ? 0.5 : 0.1,
  // Session replay (sample rate 0% in dev, 10% in prod)
  replaysSessionSampleRate: process.env.NODE_ENV === "production" ? 0.1 : 0.0,
  replaysOnErrorSampleRate: 1.0, // Always capture replays on error
});


// ─── Global dayjs configuration ─────────────────────────────────────────────
// Extend dayjs with plugins at the entry point so all code-split chunks
// inherit the extended methods (e.g., .fromNow(), .toISOString()).
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
import duration from "dayjs/plugin/duration";
dayjs.extend(relativeTime);
dayjs.extend(duration);

// ─── i18n — Internationalization ────────────────────────────────────────────
import "./i18n";

import App from "./App";

const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);
root.render(<App />);

// Hide the pre-React loading screen once the app mounts
const loader = document.getElementById("app-loading");
if (loader) {
  loader.classList.add("hidden");
  setTimeout(() => loader.remove(), 400);
}
