import React, { useState } from "react";
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from "react-native";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { mobileApi } from "../../api/client";
import { SkeletonAttendanceScreen, Card, StatCard, SectionHeader } from "../../components";

const STATUS_COLOR: Record<string,string> = { P: "#22c55e", A: "#ef4444", L: "#f59e0b", E: "#3b82f6" };
const STATUS_BG: Record<string,string> = { P: "#dcfce7", A: "#fee2e2", L: "#fef9c3", E: "#dbeafe" };

export default function StudentAttendanceScreen() {
  const [month, setMonth] = useState(dayjs().month() + 1);
  const [year] = useState(dayjs().year());

  const { data: profile } = useQuery({ queryKey: ["mob-stu-att-profile"], queryFn: () => mobileApi.get<any>("/students/me/") });
  const { data: report, isLoading } = useQuery({
    queryKey: ["mob-stu-att", profile?.id, month, year],
    queryFn: () => mobileApi.get<any>(`/attendance/student-report/?student_id=${profile?.id}&month=${month}&year=${year}`),
    enabled: !!profile?.id,
  });

  if (isLoading) return <SkeletonAttendanceScreen />;

  const pct = report?.percentage ?? 0;
  const records = report?.records ?? [];
  const daysInMonth = dayjs(`${year}-${String(month).padStart(2,"0")}-01`).daysInMonth();
  const firstDayOffset = (dayjs(`${year}-${String(month).padStart(2,"0")}-01`).day() + 6) % 7;

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>Attendance</Text>

      {/* Month picker */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 16 }}>
        {Array.from({ length: 12 }, (_, i) => i + 1).map(m => (
          <TouchableOpacity key={m} onPress={() => setMonth(m)}
            style={[styles.monthBtn, month === m && styles.monthBtnActive]}>
            <Text style={[styles.monthTxt, month === m && styles.monthTxtActive]}>{dayjs().month(m-1).format("MMM")}</Text>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <View style={styles.statsRow}>
        <StatCard label="Total" value={report?.total_school_days ?? 0} color="#6366f1" />
        <StatCard label="Present" value={report?.present ?? 0} color="#22c55e" />
        <StatCard label="Absent" value={report?.absent ?? 0} color="#ef4444" />
        <StatCard label="%" value={`${pct.toFixed(0)}%`} color={pct >= 90 ? "#22c55e" : pct >= 75 ? "#f59e0b" : "#ef4444"} />
      </View>

      {/* Progress bar */}
      <Card style={{ marginBottom: 20 }}>
        <View style={{ flexDirection: "row", justifyContent: "space-between", marginBottom: 8 }}>
          <Text style={{ fontSize: 13, fontWeight: "600", color: "#374151" }}>Attendance Rate</Text>
          <Text style={{ fontSize: 13, fontWeight: "700", color: pct >= 75 ? "#22c55e" : "#ef4444" }}>{pct.toFixed(1)}%</Text>
        </View>
        <View style={styles.bar}><View style={[styles.barFill, { width: `${Math.min(pct,100)}%` as any, backgroundColor: pct >= 90 ? "#22c55e" : pct >= 75 ? "#f59e0b" : "#ef4444" }]} /></View>
        {pct < 75 && <Text style={styles.warning}>⚠️ Below 75% minimum required attendance</Text>}
      </Card>

      {/* Calendar */}
      <SectionHeader title={dayjs(`${year}-${String(month).padStart(2,"0")}-01`).format("MMMM YYYY")} />
      <Card>
        <View style={styles.calHeader}>
          {["M","T","W","T","F","S","S"].map((d,i) => <Text key={i} style={styles.calHeaderTxt}>{d}</Text>)}
        </View>
        <View style={styles.calGrid}>
          {Array.from({ length: firstDayOffset }, (_,i) => <View key={`pad-${i}`} style={styles.calCell} />)}
          {Array.from({ length: daysInMonth }, (_,i) => {
            const day = i + 1;
            const rec = records.find((r: any) => dayjs(r.date).date() === day);
            const s = rec?.status;
            return (
              <View key={day} style={[styles.calCell, s && { backgroundColor: STATUS_BG[s] ?? "#f1f5f9" }]}>
                <Text style={[styles.calDay, s && { color: STATUS_COLOR[s] ?? "#64748b", fontWeight: "700" }]}>{day}</Text>
              </View>
            );
          })}
        </View>
        <View style={styles.legend}>
          {[["P","Present","#22c55e"],["A","Absent","#ef4444"],["L","Late","#f59e0b"],["E","Excused","#3b82f6"]].map(([k,l,c]) => (
            <View key={k} style={{ flexDirection: "row", alignItems: "center", gap: 4 }}>
              <View style={{ width: 10, height: 10, borderRadius: 3, backgroundColor: c }} />
              <Text style={{ fontSize: 11, color: "#64748b" }}>{l}</Text>
            </View>
          ))}
        </View>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 40 },
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b", marginBottom: 16 },
  monthBtn: { paddingHorizontal: 14, paddingVertical: 8, borderRadius: 20, backgroundColor: "#f1f5f9", marginRight: 8 },
  monthBtnActive: { backgroundColor: "#6366f1" },
  monthTxt: { fontSize: 13, fontWeight: "600", color: "#64748b" },
  monthTxtActive: { color: "#fff" },
  statsRow: { flexDirection: "row", gap: 8, marginBottom: 16 },
  bar: { height: 8, backgroundColor: "#f1f5f9", borderRadius: 4, overflow: "hidden" },
  barFill: { height: "100%", borderRadius: 4 },
  warning: { fontSize: 12, color: "#dc2626", marginTop: 8 },
  calHeader: { flexDirection: "row", marginBottom: 8 },
  calHeaderTxt: { flex: 1, textAlign: "center", fontSize: 11, fontWeight: "700", color: "#94a3b8" },
  calGrid: { flexDirection: "row", flexWrap: "wrap" },
  calCell: { width: "14.28%", aspectRatio: 1, alignItems: "center", justifyContent: "center", borderRadius: 6, marginBottom: 2 },
  calDay: { fontSize: 13, color: "#374151" },
  legend: { flexDirection: "row", gap: 12, marginTop: 12, flexWrap: "wrap" },
});
