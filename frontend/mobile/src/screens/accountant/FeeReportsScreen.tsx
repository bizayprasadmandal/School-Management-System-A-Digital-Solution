import React from "react";
import { View, Text, ScrollView, StyleSheet, RefreshControl } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { mobileApi } from "../../api/client";
import { Card } from "../../components";

const BRAND = "#059669";

export default function FeeReportsScreen() {
  const { data: report, isLoading, refetch } = useQuery({
    queryKey: ["mob-fee-report"],
    queryFn: () => mobileApi.get<any>("/reporting/fee-report/"),
  });

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor={BRAND} />}>
      {/* Summary cards */}
      <View style={styles.row}>
        <Card style={styles.card}><Text style={styles.cardVal}>${Number(report?.total_collected ?? 0).toLocaleString()}</Text><Text style={styles.cardLbl}>Collected</Text></Card>
        <Card style={styles.card}><Text style={styles.cardVal}>${Number(report?.outstanding ?? 0).toLocaleString()}</Text><Text style={styles.cardLbl}>Outstanding</Text></Card>
      </View>
      <View style={styles.row}>
        <Card style={styles.card}><Text style={styles.cardVal}>{report?.collection_rate ?? 0}%</Text><Text style={styles.cardLbl}>Collection Rate</Text></Card>
        <Card style={styles.card}><Text style={styles.cardVal}>{report?.total_invoices ?? 0}</Text><Text style={styles.cardLbl}>Invoices</Text></Card>
      </View>
      <View style={styles.row}>
        <Card style={styles.card}><Text style={styles.cardVal}>${Number(report?.total_refunded ?? 0).toLocaleString()}</Text><Text style={styles.cardLbl}>Refunded</Text></Card>
        <Card style={styles.card}><Text style={styles.cardVal}>{report?.overdue_count ?? 0}</Text><Text style={styles.cardLbl}>Overdue</Text></Card>
      </View>

      {/* Category breakdown */}
      {report?.category_breakdown && (
        <>
          <Text style={styles.sectionTitle}>By Category</Text>
          {report.category_breakdown.map((cat: any, i: number) => (
            <View key={i} style={styles.catRow}>
              <Text style={styles.catName}>{cat.name}</Text>
              <View style={styles.catBarBg}>
                <View style={[styles.catBar, { width: `${Math.min((cat.collected / (cat.total || 1)) * 100, 100)}%` }]} />
              </View>
              <Text style={styles.catVal}>${Number(cat.collected).toLocaleString()} / ${Number(cat.total).toLocaleString()}</Text>
            </View>
          ))}
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 40 },
  row: { flexDirection: "row", gap: 12, marginBottom: 12 },
  card: { flex: 1, padding: 16, alignItems: "center" },
  cardVal: { fontSize: 20, fontWeight: "800", color: BRAND },
  cardLbl: { fontSize: 11, color: "#64748b", marginTop: 4 },
  sectionTitle: { fontSize: 16, fontWeight: "700", color: "#0f172a", marginBottom: 12, marginTop: 8 },
  catRow: { marginBottom: 12 },
  catName: { fontSize: 13, fontWeight: "600", color: "#334155", marginBottom: 4 },
  catBarBg: { height: 8, backgroundColor: "#e2e8f0", borderRadius: 4, marginBottom: 4 },
  catBar: { height: 8, backgroundColor: BRAND, borderRadius: 4 },
  catVal: { fontSize: 11, color: "#64748b" },
});
