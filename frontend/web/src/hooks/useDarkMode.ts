/**
 * useDarkMode — toggle dark mode with localStorage persistence
 * Syncs the `dark` class on <html> element for Tailwind dark mode
 */

import { useState, useEffect, useCallback } from "react";

const STORAGE_KEY = "sms-theme";

function getInitialTheme(): boolean {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "dark") return true;
    if (stored === "light") return false;
    // Fall back to system preference
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  } catch {
    return false;
  }
}

function applyTheme(isDark: boolean): void {
  document.documentElement.classList.toggle("dark", isDark);
}

export function useDarkMode(): [boolean, () => void] {
  const [isDark, setIsDark] = useState<boolean>(getInitialTheme);

  useEffect(() => {
    applyTheme(isDark);
    try {
      localStorage.setItem(STORAGE_KEY, isDark ? "dark" : "light");
    } catch {
      // localStorage may be unavailable
    }
  }, [isDark]);

  const toggle = useCallback(() => setIsDark((prev) => !prev), []);

  return [isDark, toggle];
}
