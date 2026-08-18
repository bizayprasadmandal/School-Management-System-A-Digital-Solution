import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    port: 3000,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      "/ws": {
        target: "ws://localhost:8000",
        ws: true,
      },
    },
  },
  build: {
    outDir: "build",
    sourcemap: true,
  },
  // Map CRA's process.env.REACT_APP_* to Vite's import.meta.env.VITE_* at build
  // time. Source code uses process.env.REACT_APP_* (CRA-compatible) so Jest tests
  // work without extra transforms; Vite replaces them at build time with the
  // values from .env or the build args.
  define: {
    "process.env.REACT_APP_API_URL": JSON.stringify(
      process.env.VITE_API_URL || process.env.REACT_APP_API_URL || "http://localhost:8000/api/v1",
    ),
    "process.env.REACT_APP_WS_URL": JSON.stringify(
      process.env.VITE_WS_URL || process.env.REACT_APP_WS_URL || "ws://localhost:8000",
    ),
    "process.env.REACT_APP_SENTRY_DSN": JSON.stringify(
      process.env.VITE_SENTRY_DSN || process.env.REACT_APP_SENTRY_DSN || "",
    ),
    "process.env.REACT_APP_SENTRY_RELEASE": JSON.stringify(
      process.env.VITE_SENTRY_RELEASE || process.env.REACT_APP_SENTRY_RELEASE || "",
    ),
    "process.env.REACT_APP_SHOW_DEMO_CREDENTIALS": JSON.stringify(
      process.env.VITE_SHOW_DEMO_CREDENTIALS || process.env.REACT_APP_SHOW_DEMO_CREDENTIALS || "",
    ),
  },
});
