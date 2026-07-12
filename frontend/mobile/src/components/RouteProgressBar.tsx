/**
 * RouteProgressBar (React Native)
 * Thin animated bar at the top of the screen that briefly animates
 * when the user navigates to a new route.
 *
 * Uses React Navigation's useNavigationState to detect route changes
 * and React Native's built-in Animated API for smooth animation.
 */

import React, { useEffect, useRef } from "react";
import { Animated, StyleSheet, View } from "react-native";
import { useNavigationState } from "@react-navigation/native";

const BAR_COLOR = "#4F46E5"; // Indigo-600
const BAR_HEIGHT = 3;

export default function RouteProgressBar() {
  const routeKey = useNavigationState((state) => state?.routes?.[state.index]?.key);
  const progressAnim = useRef(new Animated.Value(0)).current;
  const opacityAnim = useRef(new Animated.Value(0)).current;
  const prevKeyRef = useRef(routeKey);
  const animRef = useRef<Animated.CompositeAnimation>();

  useEffect(() => {
    // Only animate on actual route changes (skip initial mount)
    if (prevKeyRef.current === routeKey) return;
    prevKeyRef.current = routeKey;

    // Stop any previous animation
    animRef.current?.stop();

    // Reset to 0 and make visible
    progressAnim.setValue(0);

    // Step 1: Fade in + quick ramp to 70%
    const step1 = Animated.parallel([
      Animated.timing(opacityAnim, {
        toValue: 1,
        duration: 80,
        useNativeDriver: true,
      }),
      Animated.timing(progressAnim, {
        toValue: 0.7,
        duration: 300,
        useNativeDriver: false,
      }),
    ]);

    // Step 2: Slow creep to 92%
    const step2 = Animated.timing(progressAnim, {
      toValue: 0.92,
      duration: 400,
      useNativeDriver: false,
    });

    // Step 3: Snap to 100% and fade out
    const step3 = Animated.parallel([
      Animated.timing(progressAnim, {
        toValue: 1,
        duration: 100,
        useNativeDriver: false,
      }),
      Animated.timing(opacityAnim, {
        toValue: 0,
        duration: 350,
        useNativeDriver: true,
      }),
    ]);

    animRef.current = Animated.sequence([step1, step2, step3]);
    animRef.current.start();

    return () => animRef.current?.stop();
  }, [routeKey, progressAnim, opacityAnim]);

  const barWidth = progressAnim.interpolate({
    inputRange: [0, 1],
    outputRange: ["0%", "100%"],
  });

  return (
    <View style={styles.container} pointerEvents="none">
      <Animated.View
        style={[
          styles.bar,
          {
            width: barWidth,
            opacity: opacityAnim,
          },
        ]}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    height: BAR_HEIGHT,
    zIndex: 9999,
  },
  bar: {
    height: "100%",
    backgroundColor: BAR_COLOR,
    borderRadius: 1.5,
  },
});
