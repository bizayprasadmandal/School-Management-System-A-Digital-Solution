import React from "react";
import { View, Text, ScrollView, StyleSheet } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { mobileApi } from "../../api/client";
import { SkeletonTimetableScreen, SectionHeader, Card } from "../../components";

const DAYS = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday"];
const COLORS = ["#eef2ff","#f0fdf4","#fffbeb","#fdf4ff","#fff1f2","#f0fdfa"];
const BORDER_COLORS = ["#6366f1","#22c55e","#f59e0b","#a855f7","#ef4444","#14b8a6"];

export default function StudentTimetableScreen() {
  const { data: profile } = useQuery({ queryKey: ["student-me-tt-mob"], queryFn: () => mobileApi.get<any>("/students/me/") });
  const classroomId = profile?.enrollments?.[0]?.classroom;
  const { data: weekly, isLoading } = useQuery({
    queryKey: ["student-timetable-mob", classroomId],
    queryFn: () => mobileApi.get<any>(`/timetable/slots/weekly/?classroom_id=${classroomId}`),
    enabled: !!classroomId,
  });

  if (isLoading) return <SkeletonTimetableScreen />;

  const subjectColorMap: Record<string,number> = {};
  let ci = 0;
  if (weekly) Object.values(weekly).flat().forEach((s: any) => { if (subjectColorMap[s.subject_name] === undefined) subjectColorMap[s.subject_name] = ci++; });

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}>
      {DAYS.map(day => {
        const slots: any[] = weekly?.[day] ?? [];
        return (
          <View key={day} style={styles.dayBlock}>
            <Text style={styles.dayTitle}>{day}</Text>
            {slots.length === 0
              ? <Text style={styles.noClass}>No classes</Text>
              : slots.map((s: any, i: number) => {
                  const colorIdx = (subjectColorMap[s.subject_name] ?? 0) % COLORS.length;
                  return (
                    <View key={i} style={[styles.slot, { backgroundColor: COLORS[colorIdx], borderLeftColor: BORDER_COLORS[colorIdx] }]}>
                      <Text style={[styles.slotSubject, { color: BORDER_COLORS[colorIdx] }]}>{s.subject_name}</Text>
                      <Text style={styles.slotMeta}>{s.start_time?.slice(0,5)}–{s.end_time?.slice(0,5)} · {s.teacher_name}</Text>
                    </View>
                  );
                })
            }
          </View>
        );
      })}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 40 },
  dayBlock: { marginBottom: 16 },
  dayTitle: { fontSize: 14, fontWeight: "700", color: "#1e293b", marginBottom: 8 },
  noClass: { fontSize: 12, color: "#94a3b8", paddingLeft: 8 },
  slot: { borderRadius: 10, borderLeftWidth: 3, padding: 12, marginBottom: 6 },
  slotSubject: { fontSize: 13, fontWeight: "700" },
  slotMeta: { fontSize: 11, color: "#64748b", marginTop: 2 },
});
