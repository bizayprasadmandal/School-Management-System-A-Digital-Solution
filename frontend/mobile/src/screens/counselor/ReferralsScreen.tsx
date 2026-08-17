import React from "react";
import { View, Text, ScrollView, StyleSheet, RefreshControl } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { counselingApi } from "../../services/api";
import { Card } from "../../components";

const BRAND = "#8b5cf6";
const STATUS_COLORS: Record<string, string> = {
  new: "#0ea5e9",
  under_review: "#f59e0b",
  actioned: "#8b5cf6",
  closed: "#64748b",
};
const PRIORITY_LABELS: Record<string, string> = {
  low: "Low",
  medium: "Medium",
  high: "High",
  urgent: "Urgent",
};

export default function ReferralsScreen() {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["mob-counselor-referrals"],
    queryFn: () => counselingApi.referrals(),
  });

  const referrals = data?.results ?? [];

  return (
    <ScrollView
      style={styles.root}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor={BRAND} />
      }
    >
      <Text style={styles.count}>
        {referrals.length} referral{referrals.length !== 1 ? "s" : ""}
      </Text>

      {referrals.map((r: any) => (
        <Card key={r.id} style={styles.card}>
          <View style={styles.header}>
            <Text style={styles.student}>{r.student_name ?? "Student"}</Text>
            <Text style={[styles.status, { color: STATUS_COLORS[r.status] ?? "#64748b" }]}>
              {r.status?.replace("_", " ")}
            </Text>
          </View>
          {r.student_grade && r.student_class && (
            <Text style={styles.meta}>
              {r.student_grade} · {r.student_class}
            </Text>
          )}
          <Text style={styles.priority}>Priority: {PRIORITY_LABELS[r.priority] ?? r.priority}</Text>
          {r.reason && <Text style={styles.reason}>{r.reason}</Text>}
          {r.notes && <Text style={styles.notes}>{r.notes}</Text>}
          {r.assigned_to_name && (
            <Text style={styles.assigned}>Assigned to: {r.assigned_to_name}</Text>
          )}
          {r.created_at && (
            <Text style={styles.date}>
              {new Date(r.created_at).toLocaleDateString("en-US", {
                month: "short",
                day: "numeric",
                year: "numeric",
              })}
            </Text>
          )}
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
  student: { fontSize: 15, fontWeight: "600", color: "#1e293b", flex: 1 },
  status: { fontSize: 11, fontWeight: "700", textTransform: "uppercase" },
  meta: { fontSize: 12, color: "#64748b", marginTop: 2 },
  priority: { fontSize: 11, color: "#8b5cf6", fontWeight: "600", marginTop: 4 },
  reason: { fontSize: 13, color: "#334155", marginTop: 6, fontStyle: "italic" },
  notes: { fontSize: 12, color: "#64748b", marginTop: 4 },
  assigned: { fontSize: 12, color: "#475569", marginTop: 6 },
  date: { fontSize: 11, color: "#94a3b8", marginTop: 4 },
});
