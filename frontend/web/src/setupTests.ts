// jest-dom adds custom jest matchers for asserting on DOM nodes.
// allows you to do things like:
// expect(element).toHaveTextContent(/react/i)
// learn more: https://github.com/testing-library/jest-dom
import "@testing-library/jest-dom";

// ─── Day.js plugins ────────────────────────────────────────────────────────────
// Load shared plugins so components that use dayjs.fromNow() etc. work in tests.
import dayjs from "dayjs";
import relativeTime from "dayjs/plugin/relativeTime";
dayjs.extend(relativeTime);

// ─── ResizeObserver stub ───────────────────────────────────────────────────────
// recharts' ResponsiveContainer observes its container via ResizeObserver, which
// jsdom doesn't implement — stub it so chart components render in tests.
class ResizeObserverStub {
  observe() {}
  unobserve() {}
  disconnect() {}
}
(window as unknown as { ResizeObserver: unknown }).ResizeObserver = ResizeObserverStub;
