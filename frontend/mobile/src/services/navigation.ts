/**
 * Navigation ref — allows navigating from outside NavigationContainer
 * (e.g., from push notification handlers)
 */
import { createNavigationContainerRef } from "@react-navigation/native";

export const navigationRef = createNavigationContainerRef<any>();
