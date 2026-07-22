import React, { useMemo } from "react";
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { mobileApi } from "../../api/client";
import { SkeletonFeesScreen, Card, Badge, StatCard } from "../../components";

const FEE_COLOR: Record<string, string> = {
  paid: "green", unpaid: "amber", overdue: "red", partial: "blue",
};

export default function StudentFeesScreen() {
  const { data: profile } = useQuery({
    queryKey: ["mob-stu-fee-profile"],
    queryFn: () => mobileApi.get<any>("/students/me/"),
  });

  const { data: inv, isLoading } = useQuery({
    queryKey: ["mob-stu-fees", profile?.id],
    queryFn: () => mobileApi.get<any>(`/fees/invoices/?student=${profile?.id}`),
    enabled: !!profile?.id,
  });

  const invoices = inv?.results ?? [];

  const summary = useMemo(() => {
    const totalDue = invoices
      .filter((i: any) => ["unpaid", "overdue", "partial"].includes(i.status))
      .reduce((s: number, i: any) => s + Number(i.outstanding_amount), 0);
    const totalPaid = invoices.reduce((s: number, i: any) => s + Number(i.paid_amount), 0);
    const nextDue = invoices
      .filter((i: any) => i.status === "unpaid" || i.status === "partial")
      .sort((a: any, b: any) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime())[0];
    return { totalDue, totalPaid, nextDue, count: invoices.length };
  }, [invoices]);

  if (isLoading) return <SkeletonFeesScreen />;

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>My Fees</Text>

      {/* Summary cards */}
      <View style={styles.statsRow}>
        <StatCard label="Paid" value={`$${summary.totalPaid.toFixed(0)}`} color="#22c55e" />
        <StatCard
          label="Outstanding"
          value={`$${summary.totalDue.toFixed(0)}`}
          color={summary.totalDue > 0 ? "#ef4444" : "#94a3b8"}
        />
      </View>

      {/* Outstanding alert */}
      {summary.totalDue > 0 && (
        <View style={styles.alert}>
          <Text style={styles.alertTxt}>
            💳 ${summary.totalDue.toFixed(2)} outstanding
            {summary.nextDue
              ? ` — due ${new Date(summary.nextDue.due_date).toLocaleDateString()}`
              : ""}
          </Text>
        </View>
      )}

      {/* All paid */}
      {summary.count > 0 && summary.totalDue === 0 && (
        <View style={[styles.alert, { backgroundColor: "#f0fdf4", borderColor: "#bbf7d0" }]}>
          <Text style={[styles.alertTxt, { color: "#15803d" }]}>✅ All invoices paid. No outstanding balance.</Text>
        </View>
      )}

      {/* Invoice list */}
      {invoices.length === 0 ? (
        <View style={styles.empty}>
          <Text style={styles.emptyIcon}>📄</Text>
          <Text style={styles.emptyTitle}>No invoices yet</Text>
          <Text style={styles.emptySub}>Fee invoices will appear here once generated.</Text>
        </View>
      ) : (
        invoices.map((inv: any) => (
          <Card key={inv.id} style={styles.card}>
            <View style={styles.cardHeader}>
              <View style={{ flex: 1 }}>
                <Text style={styles.invNo}>{inv.invoice_number}</Text>
                <Text style={styles.meta}>
                  Due: {new Date(inv.due_date).toLocaleDateString()}
                </Text>
              </View>
              <Badge label={inv.status} color={(FEE_COLOR as any)[inv.status] ?? "slate"} />
            </View>
            <View style={styles.cardFooter}>
              <Text style={styles.amt}>
                Total: ${Number(inv.total_amount).toFixed(2)}
              </Text>
              {Number(inv.outstanding_amount) > 0 && (
                <Text style={[styles.amt, { color: "#dc2626" }]}>
                  Due: ${Number(inv.outstanding_amount).toFixed(2)}
                </Text>
              )}
            </View>
            {inv.description && (
              <Text style={styles.desc} numberOfLines={2}>
                {inv.description}
              </Text>
            )}
          </Card>
        ))
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 40 },
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b", marginBottom: 16 },
  statsRow: { flexDirection: "row", gap: 12, marginBottom: 16 },
  alert: {
    backgroundColor: "#fff7ed",
    borderRadius: 12,
    padding: 14,
    marginBottom: 16,
    borderWidth: 1,
    borderColor: "#fed7aa",
  },
  alertTxt: { fontSize: 13, color: "#c2410c", fontWeight: "600" },
  card: { marginBottom: 10 },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
  },
  invNo: {
    fontSize: 14,
    fontWeight: "700",
    color: "#1e293b",
    fontVariant: ["tabular-nums"] as any,
  },
  meta: { fontSize: 12, color: "#64748b", marginTop: 2 },
  cardFooter: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 8,
  },
  amt: { fontSize: 13, fontWeight: "600", color: "#374151" },
  desc: { fontSize: 11, color: "#94a3b8", marginTop: 6, lineHeight: 16 },
  empty: { alignItems: "center", paddingTop: 60 },
  emptyIcon: { fontSize: 40, marginBottom: 12 },
  emptyTitle: { fontSize: 16, fontWeight: "700", color: "#374151" },
  emptySub: { fontSize: 13, color: "#94a3b8", marginTop: 4 },
});
