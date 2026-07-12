import React from "react";
import { View, Text, ScrollView, StyleSheet } from "react-native";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { mobileApi } from "../../api/client";
import { useAuthStore } from "../../hooks/useAuthStore";
import { SkeletonTimetableScreen, Card, Badge, SectionHeader } from "../../components";

const DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
const COLORS = ["#eef2ff","#f0fdf4","#fffbeb","#fdf4ff","#fff1f2"];
const BORDERS = ["#6366f1","#22c55e","#f59e0b","#a855f7","#ef4444"];

export default function TeacherTimetableScreen() {
  const { user } = useAuthStore();
  const today = dayjs();
  const todayIdx = (today.day() + 6) % 7;

  const { data: slots, isLoading } = useQuery({
    queryKey: ["mob-teacher-tt", user?.id],
    queryFn: () => mobileApi.get<any[]>("/timetable/slots/teacher-schedule/"),
  });

  if (isLoading) return <SkeletonTimetableScreen />;

  const byDay: Record<string, any[]> = {};
  DAYS.forEach(d => { byDay[d] = []; });
  (slots ?? []).forEach((s: any) => {
    const dayName = DAYS[s.day_of_week];
    if (dayName) byDay[dayName].push(s);
  });
  Object.values(byDay).forEach(arr => arr.sort((a, b) => (a.start_time || "").localeCompare(b.start_time || "")));

  const colorMap: Record<string,number> = {};
  let ci = 0;
  (slots ?? []).forEach((s: any) => { if (colorMap[s.subject_name] === undefined) colorMap[s.subject_name] = ci++; });

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>My Timetable</Text>
      {DAYS.map((day, idx) => (
        <View key={day} style={[styles.dayBlock, idx === todayIdx && styles.dayBlockToday]}>
          <View style={styles.dayHeader}>
            <Text style={styles.dayTitle}>{day}</Text>
            {idx === todayIdx && <Badge label="Today" color="blue" />}
            {idx !== todayIdx && <Text style={styles.dayCount}>{byDay[day].length} periods</Text>}
          </View>
          {byDay[day].length === 0
            ? <Text style={styles.noClass}>No classes</Text>
            : byDay[day].map((s: any, i: number) => {
              const ci2 = (colorMap[s.subject_name] ?? 0) % COLORS.length;
              return (
                <View key={i} style={[styles.slot, { backgroundColor: COLORS[ci2], borderLeftColor: BORDERS[ci2] }]}>
                  <Text style={[styles.slotSubject, { color: BORDERS[ci2] }]}>{s.subject_name}</Text>
                  <Text style={styles.slotMeta}>{s.start_time?.slice(0,5)}–{s.end_time?.slice(0,5)} · {s.classroom_name}</Text>
                </View>
              );
            })
          }
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 40 },
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b", marginBottom: 16 },
  dayBlock: { marginBottom: 14, backgroundColor: "#fff", borderRadius: 14, padding: 14, shadowColor: "#000", shadowOpacity: 0.04, shadowRadius: 6, elevation: 1 },
  dayBlockToday: { borderWidth: 2, borderColor: "#6366f1" },
  dayHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 10 },
  dayTitle: { fontSize: 14, fontWeight: "700", color: "#1e293b" },
  dayCount: { fontSize: 12, color: "#94a3b8" },
  noClass: { fontSize: 12, color: "#94a3b8" },
  slot: { borderRadius: 10, borderLeftWidth: 3, padding: 10, marginBottom: 6 },
  slotSubject: { fontSize: 13, fontWeight: "700" },
  slotMeta: { fontSize: 11, color: "#64748b", marginTop: 2 },
});
