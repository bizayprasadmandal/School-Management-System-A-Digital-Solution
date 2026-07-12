import React from "react";
import ReactDOM from "react-dom/client";
import "./index.css";
import App from "./App";

const root = ReactDOM.createRoot(document.getElementById("root") as HTMLElement);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);

// Hide the pre-React loading screen once the app mounts
const loader = document.getElementById("app-loading");
if (loader) {
  loader.classList.add("hidden");
  setTimeout(() => loader.remove(), 400);
}
