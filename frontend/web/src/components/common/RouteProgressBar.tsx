/**
 * RouteProgressBar — thin animated bar at the top of the viewport
 * that appears when React Router is loading a new route.
 * Uses useNavigation() (available in react-router-dom v6.4+).
 */

import React, { useState, useEffect, useRef } from "react";
import { useNavigation } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";

export default function RouteProgressBar() {
  const navigation = useNavigation();
  const isIdle = navigation.state === "idle";
  const [visible, setVisible] = useState(false);
  const [progress, setProgress] = useState(0);
  const timerRef = useRef<ReturnType<typeof setInterval>>();

  useEffect(() => {
    if (!isIdle) {
      // Navigation started — show bar and animate to ~90%
      setVisible(true);
      setProgress(0);

      // Quickly ramp to 70% after the initial 0% renders
      setTimeout(() => setProgress(70), 16);

      // Then slowly creep toward 90%
      timerRef.current = setInterval(() => {
        setProgress((p) => Math.min(p + 3, 90));
      }, 200);
    } else {
      // Navigation finished — snap to 100% then hide
      setProgress(100);
      clearInterval(timerRef.current);

      const hideTimer = setTimeout(() => setVisible(false), 400);
      return () => clearTimeout(hideTimer);
    }

    return () => {
      clearInterval(timerRef.current);
    };
  }, [isIdle]);

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
