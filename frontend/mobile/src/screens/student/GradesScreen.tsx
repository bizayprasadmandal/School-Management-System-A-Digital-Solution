import React from "react";
import { View, Text, ScrollView, StyleSheet } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { mobileApi } from "../../api/client";
import { SkeletonGradesScreen, Card, Badge, StatCard, SectionHeader } from "../../components";

export default function StudentGradesScreen() {
  const { data: profile } = useQuery({ queryKey: ["student-me-mob"], queryFn: () => mobileApi.get<any>("/students/me/") });
  const { data: rcData, isLoading } = useQuery({
    queryKey: ["report-cards-mob", profile?.id],
    queryFn: () => mobileApi.get<any>(`/gradebook/report-cards/?student=${profile?.id}`),
    enabled: !!profile?.id,
  });
  const reportCards = rcData?.results ?? [];
  const latest = reportCards.find((r: any) => r.status === "published") ?? reportCards[0];

  if (isLoading) return <SkeletonGradesScreen />;

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}>
      {latest && (
        <Card style={styles.latestCard}>
          <Text style={styles.latestLabel}>Latest Result</Text>
          <Text style={styles.latestExam}>{latest.exam_name}</Text>
          <View style={styles.latestStats}>
            <View style={styles.latestStat}><Text style={styles.latestValue}>{Number(latest.percentage).toFixed(1)}%</Text><Text style={styles.latestKey}>Score</Text></View>
            <View style={styles.latestStat}><Text style={styles.latestValue}>{latest.grade_letter}</Text><Text style={styles.latestKey}>Grade</Text></View>
            {latest.rank_in_class && <View style={styles.latestStat}><Text style={styles.latestValue}>#{latest.rank_in_class}</Text><Text style={styles.latestKey}>Rank</Text></View>}
          </View>
        </Card>
      )}
      <SectionHeader title="All Report Cards" />
      {reportCards.length === 0
        ? <View style={styles.empty}><Text style={styles.emptyText}>No results published yet.</Text></View>
        : reportCards.map((r: any) => (
          <Card key={r.id} style={styles.cardRow}>
            <View style={{ flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" }}>
              <View style={{ flex: 1 }}>
                <Text style={styles.cardTitle}>{r.exam_name}</Text>
                <Text style={styles.cardSub}>{r.academic_year_name} · {r.obtained_marks}/{r.total_marks} marks</Text>
              </View>
              <View style={styles.scoreBox}>
                <Text style={[styles.scoreText, { color: Number(r.percentage) >= 75 ? "#15803d" : Number(r.percentage) >= 50 ? "#d97706" : "#dc2626" }]}>{Number(r.percentage).toFixed(1)}%</Text>
                <Text style={styles.gradeText}>{r.grade_letter}</Text>
              </View>
            </View>
          </Card>
        ))
      }
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 40 },
  latestCard: { padding: 20, marginBottom: 20, backgroundColor: "#4F46E5" },
  latestLabel: { fontSize: 12, color: "#c7d2fe" },
  latestExam: { fontSize: 18, fontWeight: "800", color: "#fff", marginTop: 4 },
  latestStats: { flexDirection: "row", gap: 24, marginTop: 16 },
  latestStat: { alignItems: "center" },
  latestValue: { fontSize: 28, fontWeight: "800", color: "#fff" },
  latestKey: { fontSize: 11, color: "#c7d2fe", marginTop: 2 },
  cardRow: { padding: 14, marginBottom: 10 },
  cardTitle: { fontSize: 14, fontWeight: "700", color: "#1e293b" },
  cardSub: { fontSize: 12, color: "#64748b", marginTop: 2 },
  scoreBox: { alignItems: "flex-end" },
  scoreText: { fontSize: 18, fontWeight: "800" },
  gradeText: { fontSize: 12, color: "#64748b", marginTop: 2 },
  empty: { alignItems: "center", padding: 40 },
  emptyText: { color: "#94a3b8", fontSize: 14 },
});
