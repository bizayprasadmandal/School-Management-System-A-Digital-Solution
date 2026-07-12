import React from "react";
import { View, Text, ScrollView, StyleSheet } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { mobileApi } from "../../api/client";
import { SkeletonAttendanceScreen, Card, StatCard } from "../../components";

export default function ParentAttendanceScreen() {
  const { data: children, isLoading: clLoad } = useQuery({ queryKey: ["mob-par-children-att"], queryFn: () => mobileApi.get<any>("/students/") });

  const childId = children?.results?.[0]?.id;
  const { data: report, isLoading } = useQuery({
    queryKey: ["mob-par-att", childId],
    queryFn: () => mobileApi.get<any>(`/attendance/student-report/?student_id=${childId}&month=${new Date().getMonth()+1}&year=${new Date().getFullYear()}`),
    enabled: !!childId,
  });

  if (clLoad || isLoading) return <SkeletonAttendanceScreen />;
  const pct = report?.percentage ?? 0;

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>Attendance</Text>
      <Card style={{ marginBottom: 16, padding: 16 }}>
        <Text style={{ fontSize: 14, fontWeight: "600", color: "#374151", marginBottom: 4 }}>
          {children?.results?.[0]?.full_name ?? "Your child"}
        </Text>
        <Text style={{ fontSize: 12, color: "#64748b" }}>This month</Text>
      </Card>
      <View style={styles.row}>
        <StatCard label="Total" value={report?.total_school_days ?? 0} color="#6366f1" />
        <StatCard label="Present" value={report?.present ?? 0} color="#22c55e" />
        <StatCard label="Absent" value={report?.absent ?? 0} color="#ef4444" />
        <StatCard label="%" value={`${pct.toFixed(0)}%`} color={pct >= 75 ? "#22c55e" : "#ef4444"} />
      </View>
      {pct < 75 && (
        <View style={styles.alert}>
          <Text style={styles.alertTxt}>⚠️ Attendance below 75% minimum — please contact the school.</Text>
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 40 },
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b", marginBottom: 16 },
  row: { flexDirection: "row", gap: 8, marginBottom: 16 },
  alert: { backgroundColor: "#fef2f2", borderRadius: 12, padding: 14, borderWidth: 1, borderColor: "#fecaca" },
  alertTxt: { fontSize: 13, color: "#dc2626", fontWeight: "600" },
});
