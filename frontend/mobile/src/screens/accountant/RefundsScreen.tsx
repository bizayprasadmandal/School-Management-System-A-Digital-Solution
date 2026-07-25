import React from "react";
import { View, Text, ScrollView, StyleSheet, RefreshControl } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { mobileApi } from "../../api/client";
import { Card } from "../../components";

const BRAND = "#059669";

export default function RefundsScreen() {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["mob-refunds"],
    queryFn: () => mobileApi.get<any>("/fees/payments/?status=refunded&page_size=20"),
  });

  const refunds = data?.results ?? [];

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor={BRAND} />}>
      <Text style={styles.count}>{refunds.length} refund{refunds.length !== 1 ? "s" : ""}</Text>

      {refunds.map((r: any) => (
        <Card key={r.id} style={styles.refundCard}>
          <View style={styles.header}>
            <Text style={styles.name}>{r.invoice?.student_name ?? "Student"}</Text>
            <Text style={styles.amount}>-${Number(r.amount).toLocaleString()}</Text>
          </View>
          <Text style={styles.ref}>Ref: {r.receipt_number ?? r.id?.slice(0, 8)}</Text>
          {r.gateway_response?.refund_reason && (
            <Text style={styles.reason}>Reason: {r.gateway_response.refund_reason}</Text>
          )}
          <Text style={styles.date}>
            {r.created_at ? new Date(r.created_at).toLocaleDateString() : ""}
          </Text>
        </Card>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 40 },
  count: { fontSize: 12, color: "#94a3b8", marginBottom: 12 },
  refundCard: { marginBottom: 10, padding: 14 },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "center" },
  name: { fontSize: 14, fontWeight: "600", color: "#1e293b" },
  amount: { fontSize: 16, fontWeight: "700", color: "#ef4444" },
  ref: { fontSize: 11, color: "#94a3b8", marginTop: 4 },
  reason: { fontSize: 12, color: "#64748b", marginTop: 4, fontStyle: "italic" },
  date: { fontSize: 11, color: "#94a3b8", marginTop: 4 },
});
