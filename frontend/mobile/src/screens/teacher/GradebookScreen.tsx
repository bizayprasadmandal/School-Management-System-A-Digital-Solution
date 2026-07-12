import React, { useState } from "react";
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, TextInput, Alert } from "react-native";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { mobileApi } from "../../api/client";
import { SkeletonGradebookScreen, Card, Button, SectionHeader } from "../../components";

export default function TeacherGradebookScreen() {
  const qc = useQueryClient();
  const [examId, setExamId] = useState<string | null>(null);
  const [grades, setGrades] = useState<Record<string, string>>({});

  const { data: exams, isLoading } = useQuery({
    queryKey: ["mob-exams"],
    queryFn: () => mobileApi.get<any>("/gradebook/exams/?status=ongoing"),
  });

  const { data: students } = useQuery({
    queryKey: ["mob-exam-students", examId],
    queryFn: () => mobileApi.get<any>(`/gradebook/grades/?exam_id=${examId}`),
    enabled: !!examId,
  });

  const submit = useMutation({
    mutationFn: (data: any) => mobileApi.post("/gradebook/grades/bulk/", data),
    onSuccess: () => { Alert.alert("Saved", "Grades submitted successfully."); qc.invalidateQueries({ queryKey: ["mob-exam-students"] }); },
    onError: () => Alert.alert("Error", "Failed to save grades."),
  });

  if (isLoading) return <SkeletonGradebookScreen />;
  const examList = exams?.results ?? [];

  if (!examId) return (
    <ScrollView style={styles.root} contentContainerStyle={{ padding: 16 }}>
      <Text style={styles.heading}>Select Exam</Text>
      {examList.length === 0
        ? <Card><Text style={styles.empty}>No active exams found.</Text></Card>
        : examList.map((e: any) => (
          <TouchableOpacity key={e.id} style={styles.examCard} onPress={() => setExamId(e.id)} activeOpacity={0.8}>
            <View style={{ flex: 1 }}>
              <Text style={styles.examName}>{e.name}</Text>
              <Text style={styles.examMeta}>{e.exam_type_name} · {e.schedule_count} subjects</Text>
            </View>
            <Text style={{ color: "#94a3b8", fontSize: 18 }}>›</Text>
          </TouchableOpacity>
        ))
      }
    </ScrollView>
  );

  const studentList = students?.results ?? [];
  return (
    <View style={{ flex: 1, backgroundColor: "#f8fafc" }}>
      <TouchableOpacity style={styles.backRow} onPress={() => setExamId(null)}>
        <Text style={{ color: "#6366f1" }}>‹ Back to Exams</Text>
      </TouchableOpacity>
      <ScrollView contentContainerStyle={{ padding: 16, paddingBottom: 100 }}>
        <SectionHeader title="Enter Grades" />
        {studentList.map((g: any) => (
          <Card key={g.id} style={styles.gradeRow}>
            <View style={{ flex: 1 }}>
              <Text style={styles.stuName}>{g.student_name}</Text>
              <Text style={styles.stuMeta}>{g.subject_name}</Text>
            </View>
            <TextInput
              style={styles.marksInput}
              keyboardType="numeric"
              placeholder="—"
              value={grades[g.id] ?? String(g.marks_obtained ?? "")}
              onChangeText={v => setGrades(prev => ({ ...prev, [g.id]: v }))}
            />
          </Card>
        ))}
      </ScrollView>
      <View style={styles.footer}>
        <Button label="Submit Grades" onPress={() => {
          Alert.alert("Submit", "Are you sure?", [
            { text: "Cancel", style: "cancel" },
            { text: "Submit", onPress: () => submit.mutate({ grades: Object.entries(grades).map(([id, m]) => ({ grade_id: id, marks_obtained: m })) }) },
          ]);
        }} loading={submit.isPending} size="lg" style={{ flex: 1 }} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  heading: { fontSize: 20, fontWeight: "800", color: "#1e293b", marginBottom: 16 },
  examCard: { flexDirection: "row", alignItems: "center", backgroundColor: "#fff", borderRadius: 14, padding: 16, marginBottom: 10, shadowColor: "#000", shadowOpacity: 0.04, shadowRadius: 6, elevation: 1 },
  examName: { fontSize: 15, fontWeight: "700", color: "#1e293b" },
  examMeta: { fontSize: 12, color: "#64748b", marginTop: 2 },
  backRow: { padding: 16, borderBottomWidth: 1, borderBottomColor: "#f1f5f9", backgroundColor: "#fff" },
  gradeRow: { flexDirection: "row", alignItems: "center", marginBottom: 8 },
  stuName: { fontSize: 13, fontWeight: "600", color: "#1e293b" },
  stuMeta: { fontSize: 11, color: "#64748b" },
  marksInput: { width: 64, borderWidth: 1, borderColor: "#e2e8f0", borderRadius: 8, padding: 8, textAlign: "center", fontSize: 14, fontWeight: "700", color: "#4F46E5" },
  footer: { padding: 16, backgroundColor: "#fff", borderTopWidth: 1, borderTopColor: "#e2e8f0" },
  empty: { textAlign: "center", color: "#94a3b8", padding: 20 },
});
