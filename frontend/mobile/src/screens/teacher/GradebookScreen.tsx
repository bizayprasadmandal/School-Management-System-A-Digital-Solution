/**
 * Teacher Gradebook Screen — View marks, analytics, and enter grades
 *
 * Flow: Pick Exam → Pick Classroom → Pick Subject (ExamSchedule)
 * View: Stats summary, student marks table (editable), leaderboard
 */

import React, { useState, useMemo } from "react";
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  TextInput, RefreshControl, Alert, Modal, Platform,
} from "react-native";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { mobileApi, mobileApiClient } from "../../api/client";
import {
  SkeletonGradebookScreen, Card, Badge,
  EmptyState, Button,
} from "../../components";

const BRAND = "#059669";

type ScreenStep = "pick_exam" | "exam_detail";

interface GradeEntry {
  student_id: string;
  full_name: string;
  admission_number: string;
  marks_obtained: string;
  is_absent: boolean;
  remarks: string;
}

// ─── Helper: format percentage with color ────────────────────────────────────

function PctBadge({ pct }: { pct: number | null }) {
  if (pct === null) return <Text style={styles.pctNone}>—</Text>;
  const color = pct >= 75 ? "#15803d" : pct >= 40 ? "#d97706" : "#dc2626";
  return <Text style={[styles.pctValue, { color }]}>{pct.toFixed(1)}%</Text>;
}

// ─── Grade Row Component ─────────────────────────────────────────────────────

function GradeRow({
  entry, idx, maxMarks, passingMarks, onChange,
}: {
  entry: GradeEntry;
  idx: number;
  maxMarks: number;
  passingMarks: number;
  onChange: (id: string, field: keyof GradeEntry, value: string | boolean) => void;
}) {
  const marks = parseFloat(entry.marks_obtained);
  const pct = !isNaN(marks) && maxMarks > 0 ? (marks / maxMarks) * 100 : null;
  const pass = pct !== null && marks >= passingMarks;

  return (
    <View style={[styles.gradeRow, entry.is_absent && styles.gradeRowAbsent]}>
      <View style={styles.gradeRowNum}>
        <Text style={styles.gradeRowNumTxt}>{idx + 1}</Text>
      </View>

      <View style={styles.gradeRowInfo}>
        <Text style={styles.gradeRowName} numberOfLines={1}>
          {entry.full_name}
        </Text>
        <Text style={styles.gradeRowAdm}>{entry.admission_number}</Text>
      </View>

      {/* Absent toggle */}
      <TouchableOpacity
        style={[styles.absentBtn, entry.is_absent && styles.absentBtnActive]}
        onPress={() => onChange(entry.student_id, "is_absent", !entry.is_absent)}
      >
        <Text style={[styles.absentBtnTxt, entry.is_absent && styles.absentBtnTxtActive]}>
          {entry.is_absent ? "A" : "P"}
        </Text>
      </TouchableOpacity>

      {/* Marks input */}
      <TextInput
        style={[styles.marksInput, entry.is_absent && styles.marksInputDisabled]}
        keyboardType="numeric"
        placeholder="—"
        placeholderTextColor="#cbd5e1"
        value={entry.marks_obtained}
        onChangeText={v => onChange(entry.student_id, "marks_obtained", v)}
        editable={!entry.is_absent}
      />

      {/* Percentage */}
      <View style={styles.pctCol}>
        {!entry.is_absent && <PctBadge pct={pct} />}
      </View>

      {/* Pass/Fail */}
      <View style={styles.resultCol}>
        {!entry.is_absent && entry.marks_obtained !== "" && (
          <Text style={pass ? styles.passIcon : styles.failIcon}>
            {pass ? "✓" : "✗"}
          </Text>
        )}
      </View>

      {/* Remarks */}
      <TextInput
        style={styles.remarksInput}
        placeholder="Note"
        placeholderTextColor="#cbd5e1"
        value={entry.remarks}
        onChangeText={v => onChange(entry.student_id, "remarks", v)}
      />
    </View>
  );
}

// ─── Main Screen ─────────────────────────────────────────────────────────────

export default function TeacherGradebookScreen() {
  const qc = useQueryClient();
  const [step, setStep] = useState<ScreenStep>("pick_exam");
  const [selectedExamId, setSelectedExamId] = useState<string | null>(null);
  const [selectedExamName, setSelectedExamName] = useState("");
  const [selectedScheduleId, setSelectedScheduleId] = useState<number | null>(null);
  const [selectedSubject, setSelectedSubject] = useState("");

  const [maxMarks, setMaxMarks] = useState(100);
  const [passingMarks, setPassingMarks] = useState(35);
  const [search, setSearch] = useState("");
  const [saved, setSaved] = useState(false);
  const [showLeaderboard, setShowLeaderboard] = useState(false);

  // ── Exams list ──────────────────────────────────────────────────────────
  const { data: examsData, isLoading: examsLoading, refetch: refetchExams } = useQuery({
    queryKey: ["mob-teacher-gradebook-exams"],
    queryFn: () => mobileApi.get<{ results: any[] }>("/gradebook/exams/"),
  });
  const exams = examsData?.results ?? [];

  // ── Leaderboard ─────────────────────────────────────────────────────────
  const { data: leaderboardData, isLoading: lbLoading } = useQuery({
    queryKey: ["mob-leaderboard", selectedExamId],
    queryFn: () =>
      mobileApi.get<{ results: any[] }>(
        `/gradebook/exams/${selectedExamId}/leaderboard/`
      ),
    enabled: !!selectedExamId,
  });

  // ── Grades for selected exam (grouped by subject) ───────────────────────
  const { data: gradesAllData, isLoading: gradesLoading } = useQuery({
    queryKey: ["mob-gradebook-all-grades", selectedExamId],
    queryFn: () =>
      mobileApi.get<{ results: any[] }>("/gradebook/grades/", {
        exam_id: selectedExamId,
      }),
    enabled: !!selectedExamId,
  });
  const allGrades = gradesAllData?.results ?? [];

  // ── Extract unique subjects from grades ─────────────────────────────────
  const subjects = useMemo(() => {
    const map = new Map<number, any>();
    allGrades.forEach((g: any) => {
      const sid = g.exam_schedule_id ?? g.exam_schedule;
      if (sid && !map.has(sid)) {
        map.set(sid, {
          id: sid,
          subject_name: g.subject_name ?? g.subject?.name ?? `Subject ${sid}`,
          classroom_name: g.classroom_name ?? g.classroom?.name ?? "",
          max_marks: g.max_marks ?? 100,
          passing_marks: g.passing_marks ?? 35,
        });
      }
    });
    return Array.from(map.values());
  }, [allGrades]);

  // ── Build grade entries from grades data ────────────────────────────────
  const entries = useMemo(() => {
    if (!selectedScheduleId || !allGrades.length) return [] as GradeEntry[];
    const scheduleGrades = allGrades.filter(
      (g: any) => (g.exam_schedule_id ?? g.exam_schedule) === selectedScheduleId
    );

    return scheduleGrades.map((g: any) => ({
      student_id: g.student_id ?? g.student,
      full_name: g.student_name ?? g.full_name ?? g.student__user__full_name ?? "Unknown",
      admission_number: g.admission_number ?? "",
      marks_obtained: g.marks_obtained != null ? String(g.marks_obtained) : "",
      is_absent: g.is_absent ?? false,
      remarks: g.remarks ?? "",
    } as GradeEntry));
  }, [selectedScheduleId, allGrades]);

  // ── Stats ───────────────────────────────────────────────────────────────
  const stats = useMemo(() => {
    const entered = entries.filter(
      (e) => e.marks_obtained !== "" || e.is_absent
    ).length;
    const marked = entries.filter((e) => !e.is_absent && e.marks_obtained !== "");
    const passing = marked.filter(
      (e) => parseFloat(e.marks_obtained) >= passingMarks
    ).length;
    const failing = marked.filter(
      (e) => parseFloat(e.marks_obtained) < passingMarks
    ).length;
    const absent = entries.filter((e) => e.is_absent).length;
    const avgScore =
      marked.length > 0
        ? marked.reduce((s, e) => s + parseFloat(e.marks_obtained), 0) /
          marked.length
        : 0;
    return { entered, total: entries.length, passing, failing, absent, avgScore };
  }, [entries, passingMarks]);

  // ── Local edit state (overrides derived values) ─────────────────────────
  const [localEdits, setLocalEdits] = useState<Record<string, Partial<GradeEntry>>>({});

  const updateField = (id: string, field: keyof GradeEntry, value: string | boolean) => {
    setLocalEdits((prev) => ({
      ...prev,
      [id]: { ...(prev[id] ?? {}), [field]: value },
    }));
    setSaved(false);
  };

  const mergedEntries = useMemo(() => {
    return entries.map((e) => {
      const edit = localEdits[e.student_id] ?? {};
      return { ...e, ...edit };
    });
  }, [entries, localEdits]);

  const mergedFiltered = useMemo(() => {
    if (!search.trim()) return mergedEntries;
    const q = search.toLowerCase();
    return mergedEntries.filter(
      (e) =>
        e.full_name.toLowerCase().includes(q) ||
        e.admission_number.toLowerCase().includes(q)
    );
  }, [mergedEntries, search]);

  // ── Submit grades ───────────────────────────────────────────────────────
  const submitMutation = useMutation({
    mutationFn: (data: any) =>
      mobileApiClient.post("/gradebook/grades/bulk/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["mob-gradebook-all-grades"] });
      qc.invalidateQueries({ queryKey: ["mob-leaderboard"] });
      setSaved(true);
      Alert.alert("Saved", "Grades submitted successfully.");
    },
    onError: (e: any) =>
      Alert.alert("Error", e?.response?.data?.detail ?? "Failed to save grades."),
  });

  const handleSubmit = () => {
    if (!selectedScheduleId) return;
    const grades = mergedEntries
      .filter((e) => e.marks_obtained !== "" || e.is_absent)
      .map((e) => ({
        student_id: e.student_id,
        marks_obtained: e.is_absent ? null : parseFloat(e.marks_obtained) || null,
        is_absent: e.is_absent,
        remarks: e.remarks,
      }));
    if (grades.length === 0) {
      Alert.alert("No data", "Enter marks for at least one student.");
      return;
    }
    submitMutation.mutate({ exam_schedule_id: selectedScheduleId, grades });
  };

  // ── Handle exam selection ───────────────────────────────────────────────
  const selectExam = (exam: any) => {
    setSelectedExamId(exam.id);
    setSelectedExamName(exam.name);
    setSelectedScheduleId(null);
    setSelectedSubject("");
    setMaxMarks(100);
    setPassingMarks(35);
    setLocalEdits({});
    setSaved(false);
    setSearch("");
    setStep("exam_detail");
  };

  // ── Handle subject selection ────────────────────────────────────────────
  const selectSubject = (subj: any) => {
    setSelectedScheduleId(subj.id);
    setSelectedSubject(subj.subject_name);
    setMaxMarks(parseFloat(subj.max_marks) || 100);
    setPassingMarks(parseFloat(subj.passing_marks) || 35);
    setLocalEdits({});
    setSaved(false);
  };

  // ── Exam Picker Step ────────────────────────────────────────────────────
  if (step === "pick_exam") {
    if (examsLoading) return <SkeletonGradebookScreen />;
    return (
      <ScrollView
        style={styles.root}
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={examsLoading} onRefresh={refetchExams} tintColor={BRAND} />
        }
      >
        <Text style={styles.heading}>Gradebook</Text>
        <Text style={styles.sub}>Select an exam to view and enter marks</Text>

        {exams.length === 0 ? (
          <Card>
            <Text style={styles.emptyText}>No exams found.</Text>
          </Card>
        ) : (
          exams.map((exam: any) => (
            <TouchableOpacity
              key={exam.id}
              style={styles.examCard}
              onPress={() => selectExam(exam)}
              activeOpacity={0.8}
            >
              <View style={styles.examCardInfo}>
                <Text style={styles.examCardName}>{exam.name}</Text>
                <Text style={styles.examCardMeta}>
                  {exam.exam_type_name ?? exam.exam_type ?? "Exam"} ·{" "}
                  {exam.schedule_count ?? "—"} subjects
                </Text>
                {exam.start_date && (
                  <Text style={styles.examCardDate}>
                    {exam.start_date} – {exam.end_date}
                  </Text>
                )}
              </View>
              <View style={styles.examCardRight}>
                <Badge
                  label={exam.status ?? "ongoing"}
                  color={exam.status === "completed" ? "green" : "blue"}
                />
                <Text style={styles.chevron}>›</Text>
              </View>
            </TouchableOpacity>
          ))
        )}
      </ScrollView>
    );
  }

  // ── Exam Detail Step ────────────────────────────────────────────────────
  const isLoading = gradesLoading;

  return (
    <View style={{ flex: 1, backgroundColor: "#f8fafc" }}>
      {/* Header with back button */}
      <View style={styles.detailHeader}>
        <TouchableOpacity
          onPress={() => {
            setStep("pick_exam");
            setSelectedExamId(null);
            setSelectedScheduleId(null);
            setLocalEdits({});
          }}
          style={styles.backBtn}
        >
          <Text style={styles.backBtnTxt}>‹ Exams</Text>
        </TouchableOpacity>
        <Text style={styles.detailHeaderTitle} numberOfLines={1}>
          {selectedExamName}
        </Text>
        <View style={styles.backBtn} />
      </View>

      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={isLoading}
            onRefresh={() => qc.invalidateQueries({ queryKey: ["mob-gradebook-all-grades"] })}
            tintColor={BRAND}
          />
        }
      >
        {/* Subject / Classroom picker */}
        {subjects.length > 0 && (
          <View style={styles.schedulePicker}>
            <Text style={styles.pickerLabel}>Subject / Class</Text>
            <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.scheduleScroll}>
              <View style={styles.scheduleChips}>
                {subjects.map((subj: any) => {
                  const isActive = selectedScheduleId === subj.id;
                  return (
                    <TouchableOpacity
                      key={subj.id}
                      style={[styles.scheduleChip, isActive && styles.scheduleChipActive]}
                      onPress={() => selectSubject(subj)}
                    >
                      <Text style={[styles.scheduleChipTxt, isActive && styles.scheduleChipTxtActive]}>
                        {subj.subject_name}
                      </Text>
                      <Text style={[styles.scheduleChipSub, isActive && styles.scheduleChipSubActive]}>
                        {subj.classroom_name}
                      </Text>
                    </TouchableOpacity>
                  );
                })}
              </View>
            </ScrollView>
          </View>
        )}

        {!selectedScheduleId ? (
          <EmptyState
            icon="👆"
            title="Select a subject"
            sub="Choose a subject above to view and enter marks for that exam schedule."
          />
        ) : isLoading ? (
          <SkeletonGradebookScreen />
        ) : (
          <>
            {/* Selected subject info */}
            <View style={styles.subjectBar}>
              <View>
                <Text style={styles.subjectName}>{selectedSubject}</Text>
                <Text style={styles.subjectMeta}>
                  Max {maxMarks} · Pass {passingMarks} · {entries.length} students
                </Text>
              </View>
              <TouchableOpacity
                style={styles.lbBtn}
                onPress={() => setShowLeaderboard(true)}
              >
                <Text style={styles.lbBtnTxt}>🏆 Rank</Text>
              </TouchableOpacity>
            </View>

            {/* Stats overview */}
            {entries.length > 0 && (
              <View style={styles.statsRow}>
                {[
                  { label: "Entered", value: `${stats.entered}/${stats.total}`, color: BRAND },
                  { label: "Passing", value: stats.passing, color: "#15803d" },
                  { label: "Failing", value: stats.failing, color: "#dc2626" },
                  { label: "Absent", value: stats.absent, color: "#d97706" },
                  { label: "Avg", value: stats.avgScore.toFixed(1), color: "#475569" },
                ].map(({ label, value, color }) => (
                  <View key={label} style={styles.statPill}>
                    <Text style={[styles.statPillVal, { color }]}>{value}</Text>
                    <Text style={styles.statPillLbl}>{label}</Text>
                  </View>
                ))}
              </View>
            )}

            {/* Search */}
            {entries.length > 0 && (
              <View style={styles.searchRow}>
                <Text style={styles.searchIcon}>🔍</Text>
                <TextInput
                  style={styles.searchInput}
                  placeholder="Search student…"
                  placeholderTextColor="#94a3b8"
                  value={search}
                  onChangeText={setSearch}
                />
                {search ? (
                  <TouchableOpacity onPress={() => setSearch("")}>
                    <Text style={styles.searchClear}>✕</Text>
                  </TouchableOpacity>
                ) : null}
              </View>
            )}

            {/* Column headers */}
            {mergedFiltered.length > 0 && (
              <View style={styles.colHeaders}>
                <View style={{ width: 24 }} />
                <View style={{ flex: 1 }} />
                <View style={{ width: 36, alignItems: "center" }}>
                  <Text style={styles.colHeader}>A/P</Text>
                </View>
                <View style={{ width: 60, alignItems: "center" }}>
                  <Text style={styles.colHeader}>Marks</Text>
                </View>
                <View style={{ width: 60, alignItems: "center" }}>
                  <Text style={styles.colHeader}>%</Text>
                </View>
                <View style={{ width: 24, alignItems: "center" }} />
                <View style={{ width: 56 }} />
              </View>
            )}

            {/* Student marks list */}
            {mergedFiltered.length === 0 ? (
              <EmptyState
                icon="📋"
                title={
                  entries.length === 0
                    ? "No students"
                    : "No matching students"
                }
                sub={
                  entries.length === 0
                    ? "No students found for this classroom."
                    : "Try adjusting your search."
                }
              />
            ) : (
              <View style={styles.gradeList}>
                {mergedFiltered.map((entry, idx) => (
                  <GradeRow
                    key={entry.student_id}
                    entry={entry}
                    idx={idx}
                    maxMarks={maxMarks}
                    passingMarks={passingMarks}
                    onChange={updateField}
                  />
                ))}
              </View>
            )}

            {/* Submit button */}
            {mergedEntries.length > 0 && (
              <View style={styles.submitRow}>
                <Button
                  label={saved ? "✓ Grades Saved" : "Save Grades"}
                  onPress={handleSubmit}
                  loading={submitMutation.isPending}
                  disabled={saved || submitMutation.isPending}
                  size="lg"
                  style={{ flex: 1 }}
                />
              </View>
            )}
          </>
        )}
      </ScrollView>

      {/* Leaderboard Modal */}
      <Modal visible={showLeaderboard} transparent animationType="slide" onRequestClose={() => setShowLeaderboard(false)}>
        <View style={styles.modalOverlay}>
          <View style={styles.modal}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>🏆 Leaderboard</Text>
              <TouchableOpacity onPress={() => setShowLeaderboard(false)}>
                <Text style={styles.modalClose}>✕</Text>
              </TouchableOpacity>
            </View>
            <Text style={styles.modalSub}>{selectedExamName}</Text>

            {lbLoading ? (
              <SkeletonGradebookScreen />
            ) : !leaderboardData?.results?.length ? (
              <EmptyState
                icon="🏆"
                title="No rankings yet"
                sub="Enter grades to see student rankings."
              />
            ) : (
              <ScrollView style={{ maxHeight: 450 }}>
                {leaderboardData.results.map((entry: any, idx: number) => (
                  <View
                    key={entry.student_id ?? entry.id ?? idx}
                    style={[styles.lbRow, idx < 3 && styles.lbRowTop]}
                  >
                    <View style={styles.lbRank}>
                      <Text
                        style={[
                          styles.lbRankTxt,
                          idx === 0 && { color: "#f59e0b", fontSize: 18 },
                          idx === 1 && { color: "#94a3b8", fontSize: 16 },
                          idx === 2 && { color: "#a16207", fontSize: 15 },
                        ]}
                      >
                        #{idx + 1}
                      </Text>
                    </View>
                    <View style={styles.lbInfo}>
                      <Text style={styles.lbName} numberOfLines={1}>
                        {entry.student_name ?? entry.full_name ?? `Student ${idx + 1}`}
                      </Text>
                      <Text style={styles.lbMeta}>
                        {entry.classroom_name ?? entry.admission_number ?? ""}
                      </Text>
                    </View>
                    <View style={styles.lbScore}>
                      <Text style={styles.lbPct}>
                        {entry.percentage != null
                          ? `${parseFloat(entry.percentage).toFixed(1)}%`
                          : "—"}
                      </Text>
                      {entry.grade_letter && (
                        <Badge label={entry.grade_letter} color="green" />
                      )}
                    </View>
                  </View>
                ))}
              </ScrollView>
            )}

            <TouchableOpacity
              style={styles.modalDoneBtn}
              onPress={() => setShowLeaderboard(false)}
            >
              <Text style={styles.modalDoneBtnTxt}>Close</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 60 },

  // ── Exam Picker ─────────────────────────────────────────────────────────
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b" },
  sub: { fontSize: 13, color: "#64748b", marginTop: 4, marginBottom: 16 },
  emptyText: { textAlign: "center", color: "#94a3b8", padding: 20, fontSize: 14 },
  examCard: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    borderRadius: 14,
    padding: 16,
    marginBottom: 10,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  examCardInfo: { flex: 1 },
  examCardName: { fontSize: 15, fontWeight: "700", color: "#1e293b" },
  examCardMeta: { fontSize: 12, color: "#64748b", marginTop: 2 },
  examCardDate: { fontSize: 11, color: "#94a3b8", marginTop: 2 },
  examCardRight: { flexDirection: "row", alignItems: "center", gap: 8 },
  chevron: { fontSize: 20, color: "#94a3b8", marginLeft: 4 },

  // ── Detail Header ───────────────────────────────────────────────────────
  detailHeader: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: "#fff",
    borderBottomWidth: 1,
    borderBottomColor: "#f1f5f9",
  },
  backBtn: { width: 70 },
  backBtnTxt: { fontSize: 15, fontWeight: "600", color: BRAND },
  detailHeaderTitle: {
    flex: 1,
    fontSize: 16,
    fontWeight: "700",
    color: "#1e293b",
    textAlign: "center",
  },

  // ── Schedule Picker ─────────────────────────────────────────────────────
  schedulePicker: { marginBottom: 16 },
  pickerLabel: {
    fontSize: 12,
    fontWeight: "600",
    color: "#64748b",
    marginBottom: 8,
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  scheduleScroll: { marginBottom: 4 },
  scheduleChips: { flexDirection: "row", gap: 8 },
  scheduleChip: {
    backgroundColor: "#fff",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    paddingHorizontal: 14,
    paddingVertical: 10,
    minWidth: 100,
  },
  scheduleChipActive: {
    backgroundColor: BRAND,
    borderColor: BRAND,
  },
  scheduleChipTxt: { fontSize: 13, fontWeight: "600", color: "#374151" },
  scheduleChipTxtActive: { color: "#fff" },
  scheduleChipSub: { fontSize: 10, color: "#94a3b8", marginTop: 2 },
  scheduleChipSubActive: { color: "#d1fae5" },

  // ── Subject Bar ─────────────────────────────────────────────────────────
  subjectBar: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 14,
  },
  subjectName: { fontSize: 17, fontWeight: "700", color: "#1e293b" },
  subjectMeta: { fontSize: 11, color: "#64748b", marginTop: 2 },
  lbBtn: {
    backgroundColor: "#fffbeb",
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#fde68a",
    paddingHorizontal: 12,
    paddingVertical: 6,
  },
  lbBtnTxt: { fontSize: 12, fontWeight: "700", color: "#d97706" },

  // ── Stats ───────────────────────────────────────────────────────────────
  statsRow: {
    flexDirection: "row",
    gap: 6,
    marginBottom: 16,
    flexWrap: "wrap",
  },
  statPill: {
    backgroundColor: "#fff",
    borderRadius: 10,
    paddingHorizontal: 10,
    paddingVertical: 8,
    alignItems: "center",
    minWidth: 56,
    borderWidth: 1,
    borderColor: "#f1f5f9",
  },
  statPillVal: { fontSize: 16, fontWeight: "800" },
  statPillLbl: { fontSize: 9, color: "#94a3b8", marginTop: 1 },

  // ── Search ──────────────────────────────────────────────────────────────
  searchRow: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    paddingHorizontal: 10,
    marginBottom: 8,
  },
  searchIcon: { fontSize: 14, marginRight: 6 },
  searchInput: {
    flex: 1,
    paddingVertical: 10,
    fontSize: 13,
    color: "#1e293b",
  },
  searchClear: { fontSize: 16, color: "#94a3b8", padding: 4 },

  // ── Column Headers ──────────────────────────────────────────────────────
  colHeaders: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 6,
    paddingHorizontal: 4,
    marginBottom: 4,
  },
  colHeader: { fontSize: 10, fontWeight: "600", color: "#94a3b8", textTransform: "uppercase" },

  // ── Grade List ──────────────────────────────────────────────────────────
  gradeList: { gap: 4, marginBottom: 16 },
  gradeRow: {
    flexDirection: "row",
    alignItems: "center",
    backgroundColor: "#fff",
    borderRadius: 10,
    paddingVertical: 8,
    paddingHorizontal: 6,
    borderWidth: 1,
    borderColor: "#f1f5f9",
    gap: 4,
  },
  gradeRowAbsent: { opacity: 0.65, backgroundColor: "#fef2f2" },
  gradeRowNum: { width: 24, alignItems: "center" },
  gradeRowNumTxt: { fontSize: 11, color: "#94a3b8", fontWeight: "600" },
  gradeRowInfo: { flex: 1 },
  gradeRowName: { fontSize: 12, fontWeight: "600", color: "#1e293b" },
  gradeRowAdm: { fontSize: 9, color: "#94a3b8", marginTop: 1 },

  absentBtn: {
    width: 36,
    height: 28,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    alignItems: "center",
    justifyContent: "center",
  },
  absentBtnActive: { backgroundColor: "#fef2f2", borderColor: "#fca5a5" },
  absentBtnTxt: { fontSize: 11, fontWeight: "700", color: "#64748b" },
  absentBtnTxtActive: { color: "#dc2626" },

  marksInput: {
    width: 56,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 6,
    paddingVertical: 4,
    paddingHorizontal: 6,
    textAlign: "center",
    fontSize: 13,
    fontWeight: "700",
    color: BRAND,
  },
  marksInputDisabled: { backgroundColor: "#f1f5f9", color: "#94a3b8" },

  pctCol: { width: 60, alignItems: "center" },
  pctValue: { fontSize: 12, fontWeight: "700" },
  pctNone: { fontSize: 12, color: "#cbd5e1" },

  resultCol: { width: 24, alignItems: "center" },
  passIcon: { fontSize: 14, color: "#22c55e", fontWeight: "700" },
  failIcon: { fontSize: 14, color: "#ef4444", fontWeight: "700" },

  remarksInput: {
    width: 56,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 6,
    paddingVertical: 4,
    paddingHorizontal: 4,
    fontSize: 10,
    color: "#475569",
  },

  // ── Submit ──────────────────────────────────────────────────────────────
  submitRow: { flexDirection: "row", marginTop: 8 },

  // ── Leaderboard Modal ───────────────────────────────────────────────────
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.4)",
    justifyContent: "flex-end",
  },
  modal: {
    backgroundColor: "#fff",
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    paddingBottom: Platform.OS === "ios" ? 40 : 20,
    maxHeight: "80%",
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
  },
  modalTitle: { fontSize: 20, fontWeight: "800", color: "#1e293b" },
  modalClose: { fontSize: 20, color: "#94a3b8", padding: 4 },
  modalSub: { fontSize: 12, color: "#64748b", marginBottom: 16 },
  lbRow: {
    flexDirection: "row",
    alignItems: "center",
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#f1f5f9",
    gap: 10,
  },
  lbRowTop: { backgroundColor: "#fffbeb", borderRadius: 8, paddingHorizontal: 8 },
  lbRank: { width: 36, alignItems: "center" },
  lbRankTxt: { fontSize: 14, fontWeight: "700", color: "#64748b" },
  lbInfo: { flex: 1 },
  lbName: { fontSize: 14, fontWeight: "600", color: "#1e293b" },
  lbMeta: { fontSize: 10, color: "#94a3b8", marginTop: 1 },
  lbScore: { alignItems: "flex-end", gap: 4 },
  lbPct: { fontSize: 14, fontWeight: "700", color: BRAND },
  modalDoneBtn: {
    marginTop: 16,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    paddingVertical: 12,
    alignItems: "center",
  },
  modalDoneBtnTxt: { fontSize: 14, fontWeight: "600", color: "#64748b" },
});
