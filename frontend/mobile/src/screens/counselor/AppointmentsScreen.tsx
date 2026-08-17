import React from "react";
import { View, Text, ScrollView, StyleSheet, RefreshControl } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { counselingApi } from "../../services/api";
import { Card } from "../../components";

const BRAND = "#8b5cf6";
const STATUS_COLORS: Record<string, string> = {
  scheduled: "#f59e0b",
  completed: "#059669",
  cancelled: "#ef4444",
  "in-progress": BRAND,
};

export default function AppointmentsScreen() {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["mob-counselor-appointments"],
    queryFn: () => counselingApi.appointments(),
  });

  const appointments = data?.results ?? [];

  return (
    <ScrollView
      style={styles.root}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor={BRAND} />
      }
    >
      <Text style={styles.count}>
        {appointments.length} appointment{appointments.length !== 1 ? "s" : ""}
      </Text>

      {appointments.map((a: any) => (
        <Card key={a.id} style={styles.card}>
          <View style={styles.header}>
            <Text style={styles.student}>
              {a.student_name ?? a.student?.user?.full_name ?? "Student"}
            </Text>
            <Text style={[styles.status, { color: STATUS_COLORS[a.status] ?? "#64748b" }]}>
              {a.status}
            </Text>
          </View>
          <Text style={styles.date}>
            {a.scheduled_date
              ? new Date(a.scheduled_date).toLocaleDateString("en-US", {
                  weekday: "short",
                  month: "short",
                  day: "numeric",
                  hour: "2-digit",
                  minute: "2-digit",
                })
              : "—"}
          </Text>
          {a.reason && <Text style={styles.reason}>{a.reason}</Text>}
          {a.notes && <Text style={styles.notes}>{a.notes}</Text>}
        </Card>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 40 },
  count: { fontSize: 12, color: "#94a3b8", marginBottom: 12 },
  card: { marginBottom: 10, padding: 14 },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  student: { fontSize: 15, fontWeight: "600", color: "#1e293b" },
  status: { fontSize: 11, fontWeight: "700", textTransform: "uppercase" },
  date: { fontSize: 12, color: "#64748b", marginTop: 4 },
  reason: { fontSize: 13, color: "#334155", marginTop: 6, fontStyle: "italic" },
  notes: { fontSize: 12, color: "#64748b", marginTop: 4 },
});
