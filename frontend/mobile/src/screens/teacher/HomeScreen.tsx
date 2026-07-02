/**
 * Teacher Home Screen — today's classes and quick stats
 */
import React from "react";
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, RefreshControl } from "react-native";
import { useNavigation } from "@react-navigation/native";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { mobileApi } from "../../api/client";
import { useAuthStore } from "../../hooks/useAuthStore";
import { LoadingScreen, Card, Badge, StatCard, SectionHeader, Button } from "../../components";

const BRAND = "#059669";

export default function TeacherHomeScreen() {
  const { user } = useAuthStore();
  const navigation = useNavigation<any>();
  const today = dayjs();

  const { data: classrooms, isLoading: clsLoading, refetch } = useQuery({
    queryKey: ["teacher-home-classrooms"],
    queryFn: () => mobileApi.get<any>("/students/classrooms/"),
  });

  const { data: notifications } = useQuery({
    queryKey: ["teacher-home-notifs"],
    queryFn: () => mobileApi.get<any>("/communication/notifications/?channel=in_app&page_size=3"),
  });

  if (clsLoading) return <LoadingScreen text="Loading dashboard..." />;

  const classList = classrooms?.results ?? [];
  const unread = (notifications?.results ?? []).filter((n: any) => !n.read_at).length;

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={clsLoading} onRefresh={refetch} tintColor={BRAND} />}>
      <Text style={styles.greeting}>Hello, {user?.first_name}! 👋</Text>
      <Text style={styles.date}>{today.format("dddd, MMMM D")}</Text>

      <View style={styles.statsRow}>
        <StatCard label="My Classes" value={classList.length} color={BRAND} />
        <StatCard label="Notifications" value={unread} color={unread > 0 ? "#dc2626" : "#94a3b8"} />
      </View>

      <SectionHeader title="Quick Actions" />
      <View style={styles.actionsRow}>
        <TouchableOpacity style={styles.actionCard} onPress={() => navigation.navigate("Attendance")}>
          <Text style={styles.actionIcon}>✅</Text>
          <Text style={styles.actionLabel}>Take Attendance</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionCard} onPress={() => navigation.navigate("Gradebook")}>
          <Text style={styles.actionIcon}>📝</Text>
          <Text style={styles.actionLabel}>Enter Grades</Text>
        </TouchableOpacity>
      </View>

      <SectionHeader title="My Classrooms" />
      {classList.length === 0
        ? <Card><Text style={styles.empty}>No classrooms assigned yet.</Text></Card>
        : classList.map((c: any) => (
          <Card key={c.id} style={styles.clsCard}>
            <View style={{ flex: 1 }}>
              <Text style={styles.clsName}>{c.grade_name} {c.name}</Text>
              <Text style={styles.clsMeta}>{c.student_count} students · Room {c.room_number || "TBD"}</Text>
            </View>
            <Badge label={`${c.student_count}`} color="green" />
          </Card>
        ))
      }
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 20, paddingBottom: 40 },
  greeting: { fontSize: 22, fontWeight: "800", color: "#0f172a" },
  date: { fontSize: 13, color: "#64748b", marginTop: 2, marginBottom: 20 },
  statsRow: { flexDirection: "row", gap: 12, marginBottom: 20 },
  actionsRow: { flexDirection: "row", gap: 12, marginBottom: 8 },
  actionCard: { flex: 1, backgroundColor: "#fff", borderRadius: 16, padding: 18, alignItems: "center", shadowColor: "#000", shadowOpacity: 0.05, shadowRadius: 8, elevation: 2 },
  actionIcon: { fontSize: 28, marginBottom: 8 },
  actionLabel: { fontSize: 12, fontWeight: "600", color: "#374151", textAlign: "center" },
  clsCard: { flexDirection: "row", alignItems: "center", marginBottom: 10 },
  clsName: { fontSize: 14, fontWeight: "700", color: "#1e293b" },
  clsMeta: { fontSize: 12, color: "#64748b", marginTop: 2 },
  empty: { textAlign: "center", color: "#94a3b8", padding: 20 },
});
