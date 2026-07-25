import React, { useState } from "react";
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, TextInput, RefreshControl } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { mobileApi } from "../../api/client";
import { Card } from "../../components";

const BRAND = "#059669";
const STATUS_COLORS: Record<string, string> = {
  completed: "#059669", pending: "#f59e0b", failed: "#ef4444", refunded: "#8b5cf6",
};

export default function PaymentHistoryScreen() {
  const [filter, setFilter] = useState("");

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["mob-payments", filter],
    queryFn: () => mobileApi.get<any>(`/fees/payments/${filter ? `?status=${filter}` : ""}`),
  });

  const payments = data?.results ?? [];

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor={BRAND} />}>
      {/* Filter chips */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.filterRow}>
        {["", "completed", "pending", "failed", "refunded"].map((s) => (
          <TouchableOpacity
            key={s}
            style={[styles.filterChip, filter === s && styles.filterChipActive]}
            onPress={() => setFilter(s)}
          >
            <Text style={[styles.filterText, filter === s && styles.filterTextActive]}>
              {s || "All"}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <Text style={styles.count}>{payments.length} payment{payments.length !== 1 ? "s" : ""}</Text>

      {payments.map((p: any) => (
        <Card key={p.id} style={styles.payCard}>
          <View style={styles.payHeader}>
            <Text style={styles.payName}>{p.invoice?.student_name ?? "Student"}</Text>
            <Text style={[styles.payStatus, { color: STATUS_COLORS[p.status] ?? "#64748b" }]}>
              {p.status}
            </Text>
          </View>
          <View style={styles.payDetail}>
            <Text style={styles.payRef}>Ref: {p.receipt_number ?? p.id?.slice(0, 8)}</Text>
            <Text style={styles.payAmount}>${Number(p.amount).toLocaleString()}</Text>
          </View>
          {p.payment_method && (
            <Text style={styles.payMethod}>via {p.payment_method}</Text>
          )}
        </Card>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 40 },
  filterRow: { marginBottom: 12 },
  filterChip: {
    paddingHorizontal: 16, paddingVertical: 8, borderRadius: 20,
    backgroundColor: "#f1f5f9", marginRight: 8,
  },
  filterChipActive: { backgroundColor: BRAND },
  filterText: { fontSize: 13, fontWeight: "600", color: "#64748b", textTransform: "capitalize" },
  filterTextActive: { color: "#fff" },
  count: { fontSize: 12, color: "#94a3b8", marginBottom: 12 },
  payCard: { marginBottom: 10, padding: 14 },
  payHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  payName: { fontSize: 15, fontWeight: "600", color: "#1e293b" },
  payStatus: { fontSize: 12, fontWeight: "700", textTransform: "uppercase" },
  payDetail: { flexDirection: "row", justifyContent: "space-between", marginTop: 6 },
  payRef: { fontSize: 12, color: "#94a3b8" },
  payAmount: { fontSize: 16, fontWeight: "700", color: "#0f172a" },
  payMethod: { fontSize: 11, color: "#94a3b8", marginTop: 4 },
});
