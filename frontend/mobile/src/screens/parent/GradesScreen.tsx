import React from "react";
import { View, Text, ScrollView, StyleSheet } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { mobileApi } from "../../api/client";
import { SkeletonGradesScreen, Card, Badge } from "../../components";

export default function ParentGradesScreen() {
  const { data: children } = useQuery({ queryKey: ["mob-par-children-gr"], queryFn: () => mobileApi.get<any>("/students/") });
  const childId = children?.results?.[0]?.id;

  const { data: rcData, isLoading } = useQuery({
    queryKey: ["mob-par-rc", childId],
    queryFn: () => mobileApi.get<any>(`/gradebook/report-cards/?student=${childId}`),
    enabled: !!childId,
  });

  if (isLoading) return <SkeletonGradesScreen />;
  const rcs = rcData?.results ?? [];

  return (
    <ScrollView style={{ flex: 1, backgroundColor: "#f8fafc" }} contentContainerStyle={{ padding: 16, paddingBottom: 40 }}>
      <Text style={styles.heading}>Grades</Text>
      {rcs.length === 0
        ? <Card><Text style={styles.empty}>No published results yet.</Text></Card>
        : rcs.map((r: any) => (
          <Card key={r.id} style={styles.card}>
            <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" }}>
              <View style={{ flex: 1 }}>
                <Text style={styles.exam}>{r.exam_name}</Text>
                <Text style={styles.year}>{r.academic_year_name}</Text>
              </View>
              <View style={{ alignItems: "flex-end" }}>
                <Text style={[styles.pct, { color: Number(r.percentage) >= 75 ? "#15803d" : "#dc2626" }]}>{Number(r.percentage).toFixed(1)}%</Text>
                <Text style={styles.grade}>{r.grade_letter}</Text>
              </View>
            </View>
            <View style={{ flexDirection: "row", gap: 12, marginTop: 10 }}>
              <Text style={styles.meta}>{r.obtained_marks}/{r.total_marks} marks</Text>
              {r.rank_in_class && <Text style={styles.meta}>Rank #{r.rank_in_class}</Text>}
              <Badge label={r.status} color={r.status === "published" ? "green" : "slate"} />
            </View>
          </Card>
        ))
      }
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b", marginBottom: 16 },
  card: { marginBottom: 10 },
  exam: { fontSize: 15, fontWeight: "700", color: "#1e293b" },
  year: { fontSize: 12, color: "#64748b", marginTop: 2 },
  pct: { fontSize: 22, fontWeight: "800" },
  grade: { fontSize: 14, color: "#64748b" },
  meta: { fontSize: 12, color: "#64748b" },
  empty: { textAlign: "center", color: "#94a3b8", padding: 20 },
});
