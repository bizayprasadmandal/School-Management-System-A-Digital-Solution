/**
 * Push Notification Service — Expo Notifications handler
 *
 * Responsibilities:
 * 1. Request notification permissions on app startup
 * 2. Get the Expo push token
 * 3. Register the token with the backend
 * 4. Handle incoming notifications (foreground display, background, tapped)
 */

import { Platform } from "react-native";
import * as Notifications from "expo-notifications";
import * as Device from "expo-device";
import { mobileApi } from "../api/client";

// ─── Configure how notifications are shown when app is in foreground ─────────

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: true,
    shouldSetBadge: true,
    shouldShowBanner: true,
    shouldShowList: true,
  }),
});

// ─── Helper: Extract notification data ───────────────────────────────────────

export interface NotificationData {
  type?: string;
  title?: string;
  body?: string;
  route?: string;
  id?: string;
  [key: string]: unknown;
}

export function parseNotificationData(
  notification: Notifications.Notification
): NotificationData {
  return (notification.request.content.data ?? {}) as NotificationData;
}

// ─── Request permissions and get Expo push token ─────────────────────────────

export async function registerForPushNotifications(): Promise<string | null> {
  // Check if running on a physical device (push tokens don't work on simulators)
  if (!Device.isDevice) {
    console.log(
      "Push notifications: running on simulator — using mock token"
    );
    return null;
  }

  // Check and request permissions
  const { status: existingStatus } =
    await Notifications.getPermissionsAsync();
  let finalStatus = existingStatus;

  if (existingStatus !== "granted") {
    const { status } = await Notifications.requestPermissionsAsync();
    finalStatus = status;
  }

  if (finalStatus !== "granted") {
    console.log("Push notifications: permission not granted");
    return null;
  }

  // Get the Expo push token
  const tokenData = await Notifications.getExpoPushTokenAsync({
    projectId: process.env.EXPO_PUBLIC_EAS_PROJECT_ID ?? undefined,
  });

  const token = tokenData.data;

  // Android: set notification channel
  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("default", {
      name: "Default",
      importance: Notifications.AndroidImportance.MAX,
      vibrationPattern: [0, 250, 250, 250],
      lightColor: "#4F46E5",
      sound: "default",
    });
  }

  return token;
}

// ─── Register/update push token on the backend ───────────────────────────────

export async function syncPushTokenToBackend(
  token: string,
  deviceType: "ios" | "android" = Platform.OS as "ios" | "android"
): Promise<void> {
  try {
    await mobileApi.post("/communication/push-tokens/", {
      token,
      device_type: deviceType,
    });
    console.log("Push token registered with backend:", token.slice(0, 20) + "...");
  } catch (error) {
    console.warn("Failed to register push token:", error);
  }
}

// ─── Notification event listeners ────────────────────────────────────────────

type NotificationListener = (notification: Notifications.Notification) => void;
type ResponseListener = (response: Notifications.NotificationResponse) => void;

/**
 * Subscribe to foreground notifications (app is open and visible).
 * Returns an unsubscribe function — call it on cleanup.
 */
export function onForegroundNotification(
  handler: NotificationListener
): () => void {
  const sub = Notifications.addNotificationReceivedListener(handler);
  return () => sub.remove();
}

/**
 * Subscribe to notification taps (user tapped a notification).
 * Returns an unsubscribe function — call it on cleanup.
 */
export function onNotificationTapped(
  handler: ResponseListener
): () => void {
  const sub = Notifications.addNotificationResponseReceivedListener(handler);
  return () => sub.remove();
}

/**
 * Get the notification that launched the app (if any).
 * Call this during app initialization to handle deep links from cold starts.
 */
export async function getInitialNotification(): Promise<NotificationData | null> {
  const response =
    await Notifications.getLastNotificationResponseAsync();
  if (response) {
    return parseNotificationData(response.notification);
  }
  return null;
}

// ─── Badge management ────────────────────────────────────────────────────────

export async function setBadgeCount(count: number): Promise<void> {
  await Notifications.setBadgeCountAsync(count);
}

export async function clearBadge(): Promise<void> {
  await Notifications.setBadgeCountAsync(0);
}
