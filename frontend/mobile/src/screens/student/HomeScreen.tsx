import React from "react";
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, RefreshControl } from "react-native";
import { useNavigation } from "@react-navigation/native";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { mobileApi } from "../../api/client";
import { useAuthStore } from "../../hooks/useAuthStore";
import { SkeletonStudentDashboard, Card, Badge, SectionHeader } from "../../components";

const BRAND = "#6366f1";

export default function StudentHomeScreen() {
  const { user } = useAuthStore();
  const navigation = useNavigation<any>();

  const { data: profile, isLoading, refetch } = useQuery({
    queryKey: ["mob-student-home"],
    queryFn: () => mobileApi.get<any>("/students/me/"),
  });

  const { data: rcData } = useQuery({
    queryKey: ["mob-student-latest-rc", profile?.id],
    queryFn: () => mobileApi.get<any>(`/gradebook/report-cards/?student=${profile?.id}&page_size=1`),
    enabled: !!profile?.id,
  });

  const { data: notifData } = useQuery({
    queryKey: ["mob-student-notifs"],
    queryFn: () => mobileApi.get<any>("/communication/notifications/?channel=in_app&page_size=3"),
    refetchInterval: 30000,
  });

  if (isLoading) return <SkeletonStudentDashboard />;

  const latestRC = rcData?.results?.[0];
  const notifications = notifData?.results ?? [];
  const unread = notifications.filter((n: any) => !n.read_at).length;

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor={BRAND} />}>
      <Text style={styles.greeting}>Hello, {profile?.first_name ?? user?.first_name}! 👋</Text>
      <Text style={styles.date}>{dayjs().format("dddd, MMMM D")}</Text>

      {/* Quick stats */}
      <View style={styles.statsRow}>
        <Card style={[styles.statCard, { borderLeftColor: "#6366f1", borderLeftWidth: 3 }]}>
          <Text style={[styles.statVal, { color: "#6366f1" }]}>{profile?.current_class ?? "—"}</Text>
          <Text style={styles.statLbl}>My Class</Text>
        </Card>
        <Card style={[styles.statCard, { borderLeftColor: unread > 0 ? "#ef4444" : "#94a3b8", borderLeftWidth: 3 }]}>
          <Text style={[styles.statVal, { color: unread > 0 ? "#ef4444" : "#64748b" }]}>{unread}</Text>
          <Text style={styles.statLbl}>Unread</Text>
        </Card>
      </View>

      {/* Latest result */}
      {latestRC && (
        <>
          <SectionHeader title="Latest Result" />
          <TouchableOpacity style={styles.rcCard} onPress={() => navigation.navigate("Grades")} activeOpacity={0.9}>
            <View>
              <Text style={styles.rcExam}>{latestRC.exam_name}</Text>
              <Text style={styles.rcYear}>{latestRC.academic_year_name}</Text>
            </View>
            <View style={styles.rcStats}>
              <View style={styles.rcStat}><Text style={styles.rcVal}>{Number(latestRC.percentage).toFixed(1)}%</Text><Text style={styles.rcKey}>Score</Text></View>
              <View style={styles.rcStat}><Text style={styles.rcVal}>{latestRC.grade_letter}</Text><Text style={styles.rcKey}>Grade</Text></View>
              {latestRC.rank_in_class && <View style={styles.rcStat}><Text style={styles.rcVal}>#{latestRC.rank_in_class}</Text><Text style={styles.rcKey}>Rank</Text></View>}
            </View>
          </TouchableOpacity>
        </>
      )}

      {/* Notifications */}
      {notifications.length > 0 && (
        <>
          <SectionHeader title="Notifications" action="See All" onAction={() => navigation.navigate("Notifications")} />
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
  date: { fontSize: 13, color: "#64748b", marginTop: 2, marginBottom: 20 },
  statsRow: { flexDirection: "row", gap: 12, marginBottom: 20 },
  statCard: { flex: 1, padding: 14 },
  statVal: { fontSize: 22, fontWeight: "800" },
  statLbl: { fontSize: 11, color: "#64748b", marginTop: 2 },
  rcCard: { backgroundColor: "#4F46E5", borderRadius: 16, padding: 20, marginBottom: 20 },
  rcExam: { fontSize: 16, fontWeight: "700", color: "#fff" },
  rcYear: { fontSize: 12, color: "#c7d2fe", marginTop: 2 },
  rcStats: { flexDirection: "row", gap: 24, marginTop: 14 },
  rcStat: { alignItems: "center" },
  rcVal: { fontSize: 24, fontWeight: "800", color: "#fff" },
  rcKey: { fontSize: 10, color: "#c7d2fe", marginTop: 2 },
  notifCard: { backgroundColor: "#fff", borderRadius: 12, padding: 12, marginBottom: 8, flexDirection: "row", alignItems: "flex-start" },
  notifUnread: { backgroundColor: "#faf5ff", borderWidth: 1, borderColor: "#ddd6fe" },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: BRAND, marginTop: 4 },
  notifTitle: { fontSize: 13, fontWeight: "600", color: "#1e293b" },
  notifBody: { fontSize: 12, color: "#64748b", marginTop: 2 },
});

const BRAND = "#6366f1";
