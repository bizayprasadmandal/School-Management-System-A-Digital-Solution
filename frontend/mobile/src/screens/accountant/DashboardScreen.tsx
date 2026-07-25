import React from "react";
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, RefreshControl } from "react-native";
import { useNavigation } from "@react-navigation/native";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { mobileApi } from "../../api/client";
import { useAuthStore } from "../../hooks/useAuthStore";
import { Card, SectionHeader } from "../../components";

const BRAND = "#059669"; // Emerald-600

export default function AccountantDashboardScreen() {
  const { user } = useAuthStore();
  const navigation = useNavigation<any>();

  const { data: report, isLoading, refetch } = useQuery({
    queryKey: ["mob-accountant-home"],
    queryFn: () => mobileApi.get<any>("/reporting/fee-report/"),
  });

  const { data: paymentsData } = useQuery({
    queryKey: ["mob-accountant-recent-payments"],
    queryFn: () => mobileApi.get<any>("/fees/payments/?page_size=5"),
  });

  const recentPayments = paymentsData?.results ?? [];

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor={BRAND} />}>
      <Text style={styles.greeting}>Hello, {user?.first_name ?? "Accountant"}! 📊</Text>
      <Text style={styles.date}>{dayjs().format("dddd, MMMM D")}</Text>

      {/* Quick stats */}
      <View style={styles.statsRow}>
        <Card style={[styles.statCard, { borderLeftColor: BRAND, borderLeftWidth: 3 }]}>
          <Text style={[styles.statVal, { color: BRAND }]}>
            {report?.total_collected ? `$${Number(report.total_collected).toLocaleString()}` : "—"}
          </Text>
          <Text style={styles.statLbl}>Total Collected</Text>
        </Card>
        <Card style={[styles.statCard, { borderLeftColor: "#8b5cf6", borderLeftWidth: 3 }]}>
          <Text style={[styles.statVal, { color: "#8b5cf6" }]}>
            {report?.outstanding ? `$${Number(report.outstanding).toLocaleString()}` : "—"}
          </Text>
          <Text style={styles.statLbl}>Outstanding</Text>
        </Card>
      </View>

      <View style={styles.statsRow}>
        <Card style={[styles.statCard, { borderLeftColor: "#f59e0b", borderLeftWidth: 3 }]}>
          <Text style={[styles.statVal, { color: "#f59e0b" }]}>{report?.collection_rate ?? "—"}%</Text>
          <Text style={styles.statLbl}>Collection Rate</Text>
        </Card>
        <Card style={[styles.statCard, { borderLeftColor: "#ef4444", borderLeftWidth: 3 }]}>
          <Text style={[styles.statVal, { color: "#ef4444" }]}>
            {report?.total_refunded ? `$${Number(report.total_refunded).toLocaleString()}` : "$0"}
          </Text>
          <Text style={styles.statLbl}>Refunded</Text>
        </Card>
      </View>

      {/* Quick actions */}
      <SectionHeader title="Quick Actions" />
      <View style={styles.actionRow}>
        <TouchableOpacity style={styles.actionBtn} onPress={() => navigation.navigate("PaymentHistory" as never)} activeOpacity={0.8}>
          <Text style={styles.actionIcon}>💰</Text>
          <Text style={styles.actionText}>Payments</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn} onPress={() => navigation.navigate("FeeReports" as never)} activeOpacity={0.8}>
          <Text style={styles.actionIcon}>📈</Text>
          <Text style={styles.actionText}>Reports</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn} onPress={() => navigation.navigate("Refunds" as never)} activeOpacity={0.8}>
          <Text style={styles.actionIcon}>↩️</Text>
          <Text style={styles.actionText}>Refunds</Text>
        </TouchableOpacity>
      </View>

      {/* Recent payments */}
      {recentPayments.length > 0 && (
        <>
          <SectionHeader title="Recent Payments" action="See All" onAction={() => navigation.navigate("PaymentHistory" as never)} />
          {recentPayments.map((p: any) => (
            <View key={p.id} style={styles.paymentCard}>
              <View style={{ flex: 1 }}>
                <Text style={styles.payName}>{p.invoice?.student_name ?? "Student"}</Text>
                <Text style={styles.payRef}>{p.receipt_number ?? p.id?.slice(0, 8)}</Text>
              </View>
              <View style={{ alignItems: "flex-end" }}>
                <Text style={styles.payAmount}>${Number(p.amount).toLocaleString()}</Text>
                <Text style={[styles.payStatus, {
                  color: p.status === "completed" ? "#059669" : p.status === "pending" ? "#f59e0b" : "#ef4444",
                }]}>{p.status}</Text>
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
  paymentCard: {
    backgroundColor: "#fff", borderRadius: 12, padding: 14, marginBottom: 8,
    flexDirection: "row", alignItems: "center",
  },
  payName: { fontSize: 14, fontWeight: "600", color: "#1e293b" },
  payRef: { fontSize: 11, color: "#94a3b8", marginTop: 2 },
  payAmount: { fontSize: 15, fontWeight: "700", color: "#0f172a" },
  payStatus: { fontSize: 11, fontWeight: "600", marginTop: 2, textTransform: "capitalize" },
});
