/**
 * Error Route Config — shared definitions for error/pages
 *
 * Keeps the lazy imports and route structure for error-related
 * pages in one place so App.tsx stays lean.
 */

import React from "react";
import { Route } from "react-router-dom";

const NotFoundPage      = React.lazy(() => import("../pages/NotFoundPage"));
const AccessDeniedPage  = React.lazy(() => import("../pages/AccessDeniedPage"));

/** JSX fragment — embed directly inside <Routes> via {ErrorRoutes} */
export const ErrorRoutes = (
  <>
    <Route path="/unauthorized" element={<AccessDeniedPage />} />
    <Route path="*" element={<NotFoundPage />} />
  </>
);
