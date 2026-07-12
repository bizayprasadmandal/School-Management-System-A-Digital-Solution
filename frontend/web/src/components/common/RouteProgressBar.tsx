/**
 * RouteProgressBar — thin animated bar at the top of the viewport
 * that appears briefly when navigating between routes.
 * Compatible with traditional <BrowserRouter> (no data-router needed).
 */

import React, { useState, useEffect, useRef } from "react";
import { useLocation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";

export default function RouteProgressBar() {
  const location = useLocation();
  const prevKey = useRef(location.key);
  const [visible, setVisible] = useState(false);
  const [progress, setProgress] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval>>();

  useEffect(() => {
    // Detect route change by comparing location keys
    if (location.key !== prevKey.current) {
      prevKey.current = location.key;

      // Show bar and quickly animate
      setVisible(true);
      setProgress(0);

      const rampTimer = setTimeout(() => setProgress(70), 20);

      timerRef.current = setInterval(() => {
        setProgress((p) => Math.min(p + 5, 90));
      }, 100);

      // Complete & hide after a brief moment
      const completeTimer = setTimeout(() => {
        setProgress(100);
        clearInterval(timerRef.current);
        setTimeout(() => setVisible(false), 400);
      }, 600);

      return () => {
        clearTimeout(rampTimer);
        clearTimeout(completeTimer);
        clearInterval(timerRef.current);
      };
    }
  }, [location]);

  return (
    <AnimatePresence>
      {visible && (
        <motion.div
          className="fixed top-0 left-0 right-0 z-[100] h-0.5"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0, transition: { duration: 0.3 } }}
        >
          <motion.div
            className="h-full w-full bg-gradient-to-r from-indigo-500 via-violet-500 to-pink-500"
            style={{ scaleX: progress / 100, transformOrigin: "left" }}
          />
        </motion.div>
      )}
    </AnimatePresence>
  );
}
