import React from "react";
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, RefreshControl } from "react-native";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { mobileApi } from "../../api/client";
import { useAuthStore } from "../../hooks/useAuthStore";
import { Card, SectionHeader } from "../../components";

const BRAND = "#8b5cf6"; // Violet-500

export default function CounselorDashboardScreen() {
  const { user } = useAuthStore();
  const navigation = useNavigation<any>();

  const { data: stats, isLoading, refetch } = useQuery({
    queryKey: ["mob-counselor-home"],
    queryFn: () => mobileApi.get<any>("/counseling/dashboard/stats/"),
  });

  const { data: appointmentsData } = useQuery({
    queryKey: ["mob-counselor-appts"],
    queryFn: () => mobileApi.get<any>("/counseling/appointments/?page_size=5"),
  });

  const recentAppts = appointmentsData?.results ?? [];

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor={BRAND} />}>
      <Text style={styles.greeting}>Hello, {user?.first_name ?? "Counselor"}! 🧠</Text>
      <Text style={styles.date}>{dayjs().format("dddd, MMMM D")}</Text>

      {/* Stats */}
      <View style={styles.statsRow}>
        <Card style={[styles.statCard, { borderLeftColor: BRAND, borderLeftWidth: 3 }]}>
          <Text style={[styles.statVal, { color: BRAND }]}>{stats?.total_appointments ?? "—"}</Text>
          <Text style={styles.statLbl}>Appointments</Text>
        </Card>
        <Card style={[styles.statCard, { borderLeftColor: "#f59e0b", borderLeftWidth: 3 }]}>
          <Text style={[styles.statVal, { color: "#f59e0b" }]}>{stats?.pending_appointments ?? "—"}</Text>
          <Text style={styles.statLbl}>Pending</Text>
        </Card>
      </View>
      <View style={styles.statsRow}>
        <Card style={[styles.statCard, { borderLeftColor: "#059669", borderLeftWidth: 3 }]}>
          <Text style={[styles.statVal, { color: "#059669" }]}>{stats?.open_referrals ?? "—"}</Text>
          <Text style={styles.statLbl}>Open Referrals</Text>
        </Card>
        <Card style={[styles.statCard, { borderLeftColor: "#0ea5e9", borderLeftWidth: 3 }]}>
          <Text style={[styles.statVal, { color: "#0ea5e9" }]}>{stats?.resolved_this_month ?? "—"}</Text>
          <Text style={styles.statLbl}>Resolved/Month</Text>
        </Card>
      </View>

      {/* Quick actions */}
      <SectionHeader title="Actions" />
      <View style={styles.actionRow}>
        <TouchableOpacity style={styles.actionBtn} onPress={() => navigation.navigate("Appointments" as never)} activeOpacity={0.8}>
          <Text style={styles.actionIcon}>📅</Text>
          <Text style={styles.actionText}>Appointments</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn} onPress={() => navigation.navigate("Referrals" as never)} activeOpacity={0.8}>
          <Text style={styles.actionIcon}>📋</Text>
          <Text style={styles.actionText}>Referrals</Text>
        </TouchableOpacity>
      </View>

      {/* Recent appointments */}
      {recentAppts.length > 0 && (
        <>
          <SectionHeader title="Recent Appointments" action="See All" onAction={() => navigation.navigate("Appointments" as never)} />
          {recentAppts.map((a: any) => (
            <View key={a.id} style={styles.apptCard}>
              <View style={{ flex: 1 }}>
                <Text style={styles.apptStudent}>{a.student_name ?? "Student"}</Text>
                <Text style={styles.apptDate}>{a.scheduled_date ? new Date(a.scheduled_date).toLocaleDateString() : ""}</Text>
              </View>
              <Text style={[styles.apptStatus, {
                color: a.status === "scheduled" ? "#f59e0b" : a.status === "completed" ? "#059669" : "#ef4444",
              }]}>{a.status}</Text>
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
  date: { fontSize: 13, color: "#64748b", marginTop: 2, marginBottom: 20 },
  statsRow: { flexDirection: "row", gap: 12, marginBottom: 12 },
  statCard: { flex: 1, padding: 14 },
  statVal: { fontSize: 20, fontWeight: "800" },
  statLbl: { fontSize: 11, color: "#64748b", marginTop: 2 },
  actionRow: { flexDirection: "row", gap: 12, marginBottom: 20 },
  actionBtn: {
    flex: 1, backgroundColor: "#fff", borderRadius: 12, padding: 16,
    alignItems: "center", borderWidth: 1, borderColor: "#e2e8f0",
  },
  actionIcon: { fontSize: 24 },
  actionText: { fontSize: 12, fontWeight: "600", color: "#475569", marginTop: 4 },
  apptCard: {
    backgroundColor: "#fff", borderRadius: 12, padding: 14, marginBottom: 8,
    flexDirection: "row", alignItems: "center",
  },
  apptStudent: { fontSize: 14, fontWeight: "600", color: "#1e293b" },
  apptDate: { fontSize: 12, color: "#64748b", marginTop: 2 },
  apptStatus: { fontSize: 11, fontWeight: "700", textTransform: "capitalize" },
});
