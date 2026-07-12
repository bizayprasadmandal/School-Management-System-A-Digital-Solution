import React from "react";
import { View, Text, ScrollView, StyleSheet } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { mobileApi } from "../../api/client";
import { SkeletonFeesScreen, Card, Badge, StatCard } from "../../components";

const FEE_COLOR: Record<string, any> = { paid: "green", unpaid: "amber", overdue: "red", partial: "blue" };

export default function ParentFeesScreen() {
  const { data: children } = useQuery({ queryKey: ["mob-par-children-fee"], queryFn: () => mobileApi.get<any>("/students/") });
  const childId = children?.results?.[0]?.id;

  const { data: inv, isLoading } = useQuery({
    queryKey: ["mob-par-inv", childId],
    queryFn: () => mobileApi.get<any>(`/fees/invoices/?student=${childId}`),
    enabled: !!childId,
  });

  if (isLoading) return <SkeletonFeesScreen />;
  const invoices = inv?.results ?? [];
  const totalDue = invoices.filter((i: any) => ["unpaid","overdue","partial"].includes(i.status)).reduce((s: number, i: any) => s + Number(i.outstanding_amount), 0);
  const totalPaid = invoices.reduce((s: number, i: any) => s + Number(i.paid_amount), 0);

  return (
    <ScrollView style={{ flex: 1, backgroundColor: "#f8fafc" }} contentContainerStyle={{ padding: 16, paddingBottom: 40 }}>
      <Text style={styles.heading}>Fee Management</Text>
      <View style={styles.statsRow}>
        <StatCard label="Paid" value={`$${totalPaid.toFixed(0)}`} color="#22c55e" />
        <StatCard label="Outstanding" value={`$${totalDue.toFixed(0)}`} color={totalDue > 0 ? "#ef4444" : "#94a3b8"} />
      </View>
      {totalDue > 0 && (
        <View style={styles.alert}><Text style={styles.alertTxt}>💳 ${totalDue.toFixed(2)} outstanding — please pay promptly to avoid late fees.</Text></View>
      )}
      {invoices.map((inv: any) => (
        <Card key={inv.id} style={styles.card}>
          <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" }}>
            <View style={{ flex: 1 }}>
              <Text style={styles.invNo}>{inv.invoice_number}</Text>
              <Text style={styles.meta}>Due: {new Date(inv.due_date).toLocaleDateString()}</Text>
            </View>
            <Badge label={inv.status} color={FEE_COLOR[inv.status] ?? "slate"} />
          </View>
          <View style={{ flexDirection: "row", justifyContent: "space-between", marginTop: 8 }}>
            <Text style={styles.amt}>Total: ${Number(inv.total_amount).toFixed(2)}</Text>
            {Number(inv.outstanding_amount) > 0 && <Text style={[styles.amt, { color: "#dc2626" }]}>Due: ${Number(inv.outstanding_amount).toFixed(2)}</Text>}
          </View>
        </Card>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b", marginBottom: 16 },
  statsRow: { flexDirection: "row", gap: 12, marginBottom: 16 },
  alert: { backgroundColor: "#fff7ed", borderRadius: 12, padding: 14, marginBottom: 16, borderWidth: 1, borderColor: "#fed7aa" },
  alertTxt: { fontSize: 13, color: "#c2410c", fontWeight: "600" },
  card: { marginBottom: 10 },
  invNo: { fontSize: 14, fontWeight: "700", color: "#1e293b", fontVariant: ["tabular-nums"] as any },
  meta: { fontSize: 12, color: "#64748b", marginTop: 2 },
  amt: { fontSize: 13, fontWeight: "600", color: "#374151" },
});
