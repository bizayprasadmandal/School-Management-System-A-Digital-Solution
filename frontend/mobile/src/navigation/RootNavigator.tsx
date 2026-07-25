/**
 * React Native SMS App — Root Navigator
 * Supports: iOS & Android | Roles: Student, Parent, Teacher
 */

import React, { useEffect } from "react";
import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { createBottomTabNavigator } from "@react-navigation/bottom-tabs";
import { StatusBar, Platform } from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";

// Auth screens
import LoginScreen from "../screens/auth/LoginScreen";
import ForgotPasswordScreen from "../screens/auth/ForgotPasswordScreen";

// Student screens
import StudentHomeScreen from "../screens/student/HomeScreen";
import StudentAttendanceScreen from "../screens/student/AttendanceScreen";
import StudentGradesScreen from "../screens/student/GradesScreen";
import StudentTimetableScreen from "../screens/student/TimetableScreen";
import StudentMessagesScreen from "../screens/student/MessagesScreen";
import StudentFeesScreen from "../screens/student/FeesScreen";
import StudentAssignmentsScreen from "../screens/student/AssignmentsScreen";

// Teacher screens
import TeacherHomeScreen from "../screens/teacher/HomeScreen";
import TeacherAttendanceScreen from "../screens/teacher/AttendanceScreen";
import TeacherGradebookScreen from "../screens/teacher/GradebookScreen";
import TeacherTimetableScreen from "../screens/teacher/TimetableScreen";
import TeacherMessagesScreen from "../screens/teacher/MessagesScreen";
import TeacherAssignmentsScreen from "../screens/teacher/AssignmentsScreen";

// Parent screens
import ParentHomeScreen from "../screens/parent/HomeScreen";
import ParentChildrenScreen from "../screens/parent/ChildrenScreen";
import ParentAttendanceScreen from "../screens/parent/AttendanceScreen";
import ParentAssignmentsScreen from "../screens/parent/AssignmentsScreen";
import ParentGradesScreen from "../screens/parent/GradesScreen";
import ParentMessagesScreen from "../screens/parent/MessagesScreen";

// Accountant screens
import AccountantDashboardScreen from "../screens/accountant/DashboardScreen";
import AccountantPaymentHistoryScreen from "../screens/accountant/PaymentHistoryScreen";
import AccountantFeeReportsScreen from "../screens/accountant/FeeReportsScreen";
import AccountantRefundsScreen from "../screens/accountant/RefundsScreen";

// Librarian screens
import LibrarianDashboardScreen from "../screens/librarian/DashboardScreen";
import LibrarianBookManagementScreen from "../screens/librarian/BookManagementScreen";

// Counselor screens
import CounselorDashboardScreen from "../screens/counselor/DashboardScreen";
import CounselorAppointmentsScreen from "../screens/counselor/AppointmentsScreen";

// Shared screens
import NotificationsScreen from "../screens/shared/NotificationsScreen";
import ProfileScreen from "../screens/shared/ProfileScreen";

// Conference screens
import StudentConferencesScreen from "../screens/student/ConferencesScreen";
import TeacherConferencesScreen from "../screens/teacher/ConferencesScreen";
import ParentConferencesScreen from "../screens/parent/ConferencesScreen";

import { useAuthStore } from "../hooks/useAuthStore";
import RouteProgressBar from "../components/RouteProgressBar";
import { navigationRef } from "../services/navigation";

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

const BRAND = "#4F46E5";  // Indigo-600

// ─── Student Tab Navigator ─────────────────────────────────────────────────────

function StudentTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          const icons: Record<string, [string, string]> = {
            Home:       ["home",              "home-outline"],
            Attendance: ["calendar",          "calendar-outline"],
            Assignments:["document-text",     "document-text-outline"],
            Grades:     ["school",            "school-outline"],
            Fees:       ["wallet",            "wallet-outline"],
            Timetable:  ["time",              "time-outline"],
            Messages:   ["chatbubble-ellipses","chatbubble-ellipses-outline"],
          };
          const [active, inactive] = icons[route.name] ?? ["help", "help-outline"];
          return (
            <Ionicons
              name={focused ? active : inactive}
              size={size}
              color={color}
            />
          );
        },
        tabBarActiveTintColor: BRAND,
        tabBarInactiveTintColor: "#94a3b8",
        tabBarStyle: {
          borderTopColor: "#e2e8f0",
          paddingBottom: Platform.OS === "ios" ? 24 : 8,
          height: Platform.OS === "ios" ? 84 : 60,
        },
        headerStyle: { backgroundColor: BRAND },
        headerTintColor: "#fff",
        headerTitleStyle: { fontWeight: "700" },
      })}
    >
      <Tab.Screen name="Home" component={StudentHomeScreen} options={{ title: "Dashboard" }} />
      <Tab.Screen name="Attendance" component={StudentAttendanceScreen} />
      <Tab.Screen name="Assignments" component={StudentAssignmentsScreen} options={{ title: "Assignments" }} />
      <Tab.Screen name="Grades" component={StudentGradesScreen} />
      <Tab.Screen name="Fees" component={StudentFeesScreen} />
      <Tab.Screen name="Timetable" component={StudentTimetableScreen} />
      <Tab.Screen name="Messages" component={StudentMessagesScreen} />
    </Tab.Navigator>
  );
}

// ─── Teacher Tab Navigator ────────────────────────────────────────────────────

function TeacherTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          const icons: Record<string, [string, string]> = {
            Home:       ["home",           "home-outline"],
            Attendance: ["checkmark-done", "checkmark-done-outline"],
            Assignments:["document-text",  "document-text-outline"],
            Gradebook:  ["bar-chart",      "bar-chart-outline"],
            Timetable:  ["time",           "time-outline"],
            Messages:   ["chatbubble",     "chatbubble-outline"],
          };
          const [active, inactive] = icons[route.name] ?? ["help", "help-outline"];
          return <Ionicons name={focused ? active : inactive} size={size} color={color} />;
        },
        tabBarActiveTintColor: BRAND,
        tabBarInactiveTintColor: "#94a3b8",
        headerStyle: { backgroundColor: BRAND },
        headerTintColor: "#fff",
      })}
    >
      <Tab.Screen name="Home" component={TeacherHomeScreen} options={{ title: "Dashboard" }} />
      <Tab.Screen name="Attendance" component={TeacherAttendanceScreen} />
      <Tab.Screen name="Assignments" component={TeacherAssignmentsScreen} options={{ title: "Assignments" }} />
      <Tab.Screen name="Gradebook" component={TeacherGradebookScreen} />
      <Tab.Screen name="Timetable" component={TeacherTimetableScreen} />
      <Tab.Screen name="Messages" component={TeacherMessagesScreen} />
    </Tab.Navigator>
  );
}

// ─── Accountant Tab Navigator ────────────────────────────────────────────────

function AccountantTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          const icons: Record<string, [string, string]> = {
            Home:     ["wallet",    "wallet-outline"],
            Payments: ["card",     "card-outline"],
            Reports:  ["bar-chart","bar-chart-outline"],
            Refunds:  ["return-up-back","return-up-back-outline"],
          };
          const [active, inactive] = icons[route.name] ?? ["help", "help-outline"];
          return <Ionicons name={focused ? active : inactive} size={size} color={color} />;
        },
        tabBarActiveTintColor: "#059669",
        tabBarInactiveTintColor: "#94a3b8",
        headerStyle: { backgroundColor: "#059669" },
        headerTintColor: "#fff",
      })}
    >
      <Tab.Screen name="Home" component={AccountantDashboardScreen} options={{ title: "Dashboard" }} />
      <Tab.Screen name="Payments" component={AccountantPaymentHistoryScreen} options={{ title: "Payments" }} />
      <Tab.Screen name="Reports" component={AccountantFeeReportsScreen} options={{ title: "Reports" }} />
      <Tab.Screen name="Refunds" component={AccountantRefundsScreen} options={{ title: "Refunds" }} />
    </Tab.Navigator>
  );
}

// ─── Librarian Tab Navigator ──────────────────────────────────────────────────

function LibrarianTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          const icons: Record<string, [string, string]> = {
            Home:  ["library",     "library-outline"],
            Books: ["book",       "book-outline"],
          };
          const [active, inactive] = icons[route.name] ?? ["help", "help-outline"];
          return <Ionicons name={focused ? active : inactive} size={size} color={color} />;
        },
        tabBarActiveTintColor: "#0ea5e9",
        tabBarInactiveTintColor: "#94a3b8",
        headerStyle: { backgroundColor: "#0ea5e9" },
        headerTintColor: "#fff",
      })}
    >
      <Tab.Screen name="Home" component={LibrarianDashboardScreen} options={{ title: "Dashboard" }} />
      <Tab.Screen name="Books" component={LibrarianBookManagementScreen} options={{ title: "Books" }} />
    </Tab.Navigator>
  );
}

// ─── Counselor Tab Navigator ──────────────────────────────────────────────────

function CounselorTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          const icons: Record<string, [string, string]> = {
            Home:         ["heart",       "heart-outline"],
            Appointments: ["calendar",    "calendar-outline"],
          };
          const [active, inactive] = icons[route.name] ?? ["help", "help-outline"];
          return <Ionicons name={focused ? active : inactive} size={size} color={color} />;
        },
        tabBarActiveTintColor: "#8b5cf6",
        tabBarInactiveTintColor: "#94a3b8",
        headerStyle: { backgroundColor: "#8b5cf6" },
        headerTintColor: "#fff",
      })}
    >
      <Tab.Screen name="Home" component={CounselorDashboardScreen} options={{ title: "Dashboard" }} />
      <Tab.Screen name="Appointments" component={CounselorAppointmentsScreen} options={{ title: "Appointments" }} />
    </Tab.Navigator>
  );
}

// ─── Parent Tab Navigator ─────────────────────────────────────────────────────

function ParentTabs() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        tabBarIcon: ({ focused, color, size }) => {
          const icons: Record<string, [string, string]> = {
            Home:       ["home",       "home-outline"],
            Children:   ["people",     "people-outline"],
            Attendance: ["calendar",   "calendar-outline"],
            Assignments:["document-text","document-text-outline"],
            Grades:     ["ribbon",     "ribbon-outline"],
            Messages:   ["chatbubble", "chatbubble-outline"],
          };
          const [active, inactive] = icons[route.name] ?? ["help", "help-outline"];
          return <Ionicons name={focused ? active : inactive} size={size} color={color} />;
        },
        tabBarActiveTintColor: BRAND,
        tabBarInactiveTintColor: "#94a3b8",
        headerStyle: { backgroundColor: BRAND },
        headerTintColor: "#fff",
      })}
    >
      <Tab.Screen name="Home" component={ParentHomeScreen} options={{ title: "Dashboard" }} />
      <Tab.Screen name="Children" component={ParentChildrenScreen} />
      <Tab.Screen name="Attendance" component={ParentAttendanceScreen} />
      <Tab.Screen name="Assignments" component={ParentAssignmentsScreen} options={{ title: "Assignments" }} />
      <Tab.Screen name="Grades" component={ParentGradesScreen} />
      <Tab.Screen name="Messages" component={ParentMessagesScreen} />
    </Tab.Navigator>
  );
}

// ─── Root Navigator ───────────────────────────────────────────────────────────

function AppContent() {
  const { isAuthenticated, user } = useAuthStore();

  if (!isAuthenticated) {
    return (
      <Stack.Navigator screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Login" component={LoginScreen} />
        <Stack.Screen name="ForgotPassword" component={ForgotPasswordScreen} />
      </Stack.Navigator>
    );
  }

  let MainTabs: React.ComponentType<any>;
  switch (user?.role) {
    case "student":          MainTabs = StudentTabs;     break;
    case "teacher":          MainTabs = TeacherTabs;     break;
    case "parent":           MainTabs = ParentTabs;      break;
    case "accountant":       MainTabs = AccountantTabs;  break;
    case "librarian":        MainTabs = LibrarianTabs;   break;
    case "counselor":        MainTabs = CounselorTabs;   break;
    default:                 MainTabs = StudentTabs;     break;
  }

  return (
    <Stack.Navigator>
      <Stack.Screen
        name="Main"
        component={MainTabs}
        options={{ headerShown: false }}
      />
      <Stack.Screen
        name="Notifications"
        component={NotificationsScreen}
        options={{
          title: "Notifications",
          headerStyle: { backgroundColor: BRAND },
          headerTintColor: "#fff",
        }}
      />
      <Stack.Screen
        name="Profile"
        component={ProfileScreen}
        options={{
          title: "My Profile",
          headerStyle: { backgroundColor: BRAND },
          headerTintColor: "#fff",
        }}
      />
      {/* Conference screens per role */}
      {user?.role === "student" && (
        <Stack.Screen
          name="Conferences"
          component={StudentConferencesScreen}
          options={{
            title: "My Conferences",
            headerStyle: { backgroundColor: BRAND },
            headerTintColor: "#fff",
          }}
        />
      )}
      {user?.role === "student" && (
        <Stack.Screen
          name="Assignments"
          component={StudentAssignmentsScreen}
          options={{
            title: "My Assignments",
            headerStyle: { backgroundColor: BRAND },
            headerTintColor: "#fff",
          }}
        />
      )}
      {user?.role === "teacher" && (
        <Stack.Screen
          name="Conferences"
          component={TeacherConferencesScreen}
          options={{
            title: "My Slots",
            headerStyle: { backgroundColor: "#059669" },
            headerTintColor: "#fff",
          }}
        />
      )}
      {user?.role === "parent" && (
        <Stack.Screen
          name="Conferences"
          component={ParentConferencesScreen}
          options={{
            title: "Conferences",
            headerStyle: { backgroundColor: "#7c3aed" },
            headerTintColor: "#fff",
          }}
        />
      )}
    </Stack.Navigator>
  );
}

export default function RootNavigator() {
  return (
    <NavigationContainer ref={navigationRef}>
      <StatusBar barStyle="light-content" backgroundColor={BRAND} />
      <RouteProgressBar />
      <AppContent />
    </NavigationContainer>
  );
}
