/**
 * Parent Home Screen — children overview, recent notifications, upcoming events
 */

import React from "react";
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, RefreshControl } from "react-native";
import { useNavigation } from "@react-navigation/native";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { useAuthStore } from "../../hooks/useAuthStore";
import {
  useParentChildren,
  useNotifications,
  useUpcomingEvents,
} from "../../hooks/useApi";
import { SkeletonChildrenScreen, Card, Badge, SectionHeader } from "../../components";

const BRAND = "#7c3aed";

export default function ParentHomeScreen() {
  const { user } = useAuthStore();
  const navigation = useNavigation<any>();

  const {
    data: childrenData,
    isLoading: childrenLoading,
    refetch: refetchChildren,
  } = useParentChildren();

  const { data: notifData } = useNotifications(3);
  const { data: eventsData } = useUpcomingEvents();

  const children = childrenData?.results ?? [];
  const notifications = notifData?.results ?? [];
  const events = eventsData ?? [];

  if (childrenLoading) return <SkeletonChildrenScreen />;

  return (
    <ScrollView
      style={styles.root}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={childrenLoading} onRefresh={refetchChildren} tintColor={BRAND} />
      }
    >
      <Text style={styles.greeting}>Hello, {user?.first_name}! 👋</Text>
      <Text style={styles.sub}>Monitor your children's academic progress</Text>

      {/* Children summary stats */}
      <View style={styles.statsRow}>
        <Card style={[styles.statCard, { borderLeftColor: BRAND, borderLeftWidth: 3 }]}>
          <Text style={[styles.statVal, { color: BRAND }]}>{children.length}</Text>
          <Text style={styles.statLbl}>Children</Text>
        </Card>
        <Card
          style={[
            styles.statCard,
            { borderLeftColor: notifications.filter((n: any) => !n.read_at).length > 0 ? "#ef4444" : "#94a3b8", borderLeftWidth: 3 },
          ]}
        >
          <Text
            style={[
              styles.statVal,
              { color: notifications.filter((n: any) => !n.read_at).length > 0 ? "#ef4444" : "#64748b" },
            ]}
          >
            {notifications.filter((n: any) => !n.read_at).length}
          </Text>
          <Text style={styles.statLbl}>Unread</Text>
        </Card>
      </View>

      {/* Children list */}
      <SectionHeader title="My Children" action="See All" onAction={() => navigation.navigate("Children")} />
      {children.length === 0 ? (
        <Card>
          <Text style={styles.empty}>No children linked yet. Contact your school admin.</Text>
        </Card>
      ) : (
        children.slice(0, 3).map((child: any) => (
          <TouchableOpacity key={child.id} activeOpacity={0.8} onPress={() => navigation.navigate("Grades")}>
            <Card style={styles.childCard}>
              <View style={styles.ava}>
                <Text style={styles.avaTxt}>
                  {(child.full_name ?? "")
                    .split(" ")
                    .map((n: string) => n[0])
                    .join("")
                    .slice(0, 2)
                    .toUpperCase()}
                </Text>
              </View>
              <View style={{ flex: 1 }}>
                <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
                  <Text style={styles.name}>{child.full_name}</Text>
                  <Badge label={child.is_active ? "Active" : "Inactive"} color={child.is_active ? "green" : "slate"} dot />
                </View>
                <Text style={styles.meta}>
                  {child.current_class ?? "—"} · Adm: {child.admission_number}
                </Text>
              </View>
            </Card>
          </TouchableOpacity>
        ))
      )}

      {/* Events */}
      {events.length > 0 && (
        <>
          <SectionHeader title="Upcoming Events" />
          {events.slice(0, 3).map((event: any) => (
            <Card key={event.id} style={styles.eventCard}>
              <View style={styles.eventDateBox}>
                <Text style={styles.eventDay}>{dayjs(event.start_date).format("D")}</Text>
                <Text style={styles.eventMonth}>{dayjs(event.start_date).format("MMM")}</Text>
              </View>
              <View style={{ flex: 1, paddingLeft: 12 }}>
                <Text style={styles.eventTitle}>{event.title}</Text>
                <Text style={styles.eventType}>{event.event_type ?? "Event"}</Text>
              </View>
            </Card>
          ))}
        </>
      )}

      {/* Notifications */}
      {notifications.length > 0 && (
        <>
          <SectionHeader title="Recent Notifications" action="See All" onAction={() => navigation.navigate("Notifications")} />
          {notifications.map((n: any) => (
            <View key={n.id} style={[styles.notifCard, !n.read_at && styles.notifUnread]}>
              {!n.read_at && <View style={styles.dot} />}
              <View style={{ flex: 1, paddingLeft: n.read_at ? 0 : 8 }}>
                <Text style={styles.notifTitle} numberOfLines={1}>{n.title}</Text>
                <Text style={styles.notifBody} numberOfLines={2}>{n.body}</Text>
              </View>
            </View>
          ))}
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 20, paddingBottom: 40 },
  greeting: { fontSize: 22, fontWeight: "800", color: "#0f172a" },
  sub: { fontSize: 14, color: "#64748b", marginTop: 4, marginBottom: 20 },
  statsRow: { flexDirection: "row", gap: 12, marginBottom: 20 },
  statCard: { flex: 1, padding: 14 },
  statVal: { fontSize: 22, fontWeight: "800" },
  statLbl: { fontSize: 11, color: "#64748b", marginTop: 2 },
  childCard: { flexDirection: "row", gap: 14, marginBottom: 10, alignItems: "center" },
  ava: { width: 52, height: 52, borderRadius: 14, backgroundColor: "#ede9fe", alignItems: "center", justifyContent: "center", flexShrink: 0 },
  avaTxt: { fontSize: 16, fontWeight: "800", color: "#7c3aed" },
  name: { fontSize: 15, fontWeight: "700", color: "#1e293b" },
  meta: { fontSize: 12, color: "#64748b", marginTop: 2 },
  eventCard: { flexDirection: "row", alignItems: "center", marginBottom: 8, padding: 14 },
  eventDateBox: { width: 50, height: 50, borderRadius: 12, backgroundColor: "#eef2ff", alignItems: "center", justifyContent: "center", flexShrink: 0 },
  eventDay: { fontSize: 18, fontWeight: "800", color: BRAND },
  eventMonth: { fontSize: 10, fontWeight: "700", color: BRAND, textTransform: "uppercase" },
  eventTitle: { fontSize: 14, fontWeight: "600", color: "#1e293b" },
  eventType: { fontSize: 11, color: "#64748b", marginTop: 2, textTransform: "capitalize" },
  empty: { textAlign: "center", color: "#94a3b8", padding: 20 },
  notifCard: { backgroundColor: "#fff", borderRadius: 12, padding: 12, marginBottom: 8, flexDirection: "row", alignItems: "flex-start" },
  notifUnread: { backgroundColor: "#faf5ff", borderWidth: 1, borderColor: "#ddd6fe" },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: BRAND, marginTop: 4 },
  notifTitle: { fontSize: 13, fontWeight: "600", color: "#1e293b" },
  notifBody: { fontSize: 12, color: "#64748b", marginTop: 2 },
});
