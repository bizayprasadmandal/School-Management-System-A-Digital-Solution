/**
 * Teacher AssignmentsScreen — Create homework/quizzes/projects,
 * view student submissions, and grade them with marks + feedback.
 */

import React, { useState } from "react";
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  TextInput,
  RefreshControl,
  Alert,
  Modal,
  Platform,
  Linking,
} from "react-native";
import * as DocumentPicker from "expo-document-picker";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import dayjs from "dayjs";
import { mobileApi, mobileApiClient } from "../../api/client";
import { SkeletonList, EmptyState } from "../../components";

const BRAND = "#059669";

const TYPE_OPTIONS = [
  { value: "homework", label: "Homework", icon: "📝", color: "#3b82f6", bg: "#eff6ff" },
  { value: "quiz", label: "Quiz", icon: "❓", color: "#8b5cf6", bg: "#f5f3ff" },
  { value: "project", label: "Project", icon: "📊", color: "#f59e0b", bg: "#fffbeb" },
  { value: "classwork", label: "Class Work", icon: "📋", color: "#059669", bg: "#ecfdf5" },
  { value: "lab", label: "Lab Work", icon: "🔬", color: "#e11d48", bg: "#fce7f3" },
];

// ─── Create Assessment Modal ─────────────────────────────────────────────────

function CreateModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [title, setTitle] = useState("");
  const [type, setType] = useState("homework");
  const [dueDate, setDueDate] = useState(dayjs().add(7, "day").format("YYYY-MM-DD"));
  const [maxMarks, setMaxMarks] = useState("100");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState<{ name: string; uri: string; mimeType: string } | null>(null);
  const [assignmentId, setAssignmentId] = useState<number | null>(null);

  const { data: assignmentsData } = useQuery({
    queryKey: ["mob-teacher-assignments-list"],
    queryFn: () => mobileApi.get<any[]>("/academics/assignments/my-assignments/"),
  });
  const myAssignments = assignmentsData ?? [];

  const handlePickFile = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: "*/*",
        copyToCacheDirectory: true,
      });
      if (!result.canceled && result.assets?.[0]) {
        const a = result.assets[0];
        setFile({ name: a.name, uri: a.uri, mimeType: a.mimeType ?? "application/octet-stream" });
      }
    } catch {
      /* noop */
    }
  };

  const handleCreate = async () => {
    if (!title.trim()) {
      Alert.alert("Validation", "Title is required.");
      return;
    }
    if (!assignmentId) {
      Alert.alert("Validation", "Please select a class and subject.");
      return;
    }
    try {
      const fd = new FormData();
      fd.append("title", title.trim());
      fd.append("assessment_type", type);
      fd.append("due_date", dueDate);
      fd.append("max_marks", maxMarks);
      fd.append("description", description.trim());
      fd.append("assignment", String(assignmentId));
      if (file) {
        fd.append("attachment", { uri: file.uri, name: file.name, type: file.mimeType } as any);
      }
      await mobileApiClient.post("/gradebook/assessments/", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      Alert.alert("Created!", "Assessment has been created.");
      onCreated();
      onClose();
    } catch (e: any) {
      Alert.alert("Error", e?.response?.data?.detail ?? "Failed to create.");
    }
  };

  return (
    <Modal visible transparent animationType="slide" onRequestClose={onClose}>
      <View style={styles.modalOverlay}>
        <View style={styles.modal}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Create Assessment</Text>
            <TouchableOpacity onPress={onClose}>
              <Text style={styles.modalClose}>✕</Text>
            </TouchableOpacity>
          </View>
          <ScrollView style={{ maxHeight: 450 }}>
            <Text style={styles.label}>Title *</Text>
            <TextInput
              value={title}
              onChangeText={setTitle}
              placeholder="e.g. Chapter 5 Homework"
              style={styles.input}
              placeholderTextColor="#94a3b8"
            />

            <Text style={styles.label}>Class & Subject *</Text>
            <View style={styles.chipRow}>
              {myAssignments.map((a: any) => (
                <TouchableOpacity
                  key={a.id}
                  style={[styles.chip, assignmentId === a.id && styles.chipActive]}
                  onPress={() => setAssignmentId(a.id)}
                >
                  <Text style={[styles.chipTxt, assignmentId === a.id && styles.chipTxtActive]}>
                    {a.subject_name} — {a.classroom_name}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <View style={styles.row}>
              <View style={{ flex: 1 }}>
                <Text style={styles.label}>Type *</Text>
                <View style={styles.chipRow}>
                  {TYPE_OPTIONS.map((o) => (
                    <TouchableOpacity
                      key={o.value}
                      style={[styles.chip, type === o.value && { backgroundColor: o.color }]}
                      onPress={() => setType(o.value)}
                    >
                      <Text style={[styles.chipTxt, type === o.value && { color: "#fff" }]}>
                        {o.icon} {o.label}
                      </Text>
                    </TouchableOpacity>
                  ))}
                </View>
              </View>
            </View>

            <View style={styles.row}>
              <View style={{ flex: 1, marginRight: 8 }}>
                <Text style={styles.label}>Due Date *</Text>
                <TextInput
                  value={dueDate}
                  onChangeText={setDueDate}
                  style={styles.input}
                  placeholderTextColor="#94a3b8"
                />
              </View>
              <View style={{ width: 80 }}>
                <Text style={styles.label}>Max Marks</Text>
                <TextInput
                  value={maxMarks}
                  onChangeText={setMaxMarks}
                  keyboardType="numeric"
                  style={styles.input}
                  placeholderTextColor="#94a3b8"
                />
              </View>
            </View>

            <Text style={styles.label}>Attachment (optional)</Text>
            <TouchableOpacity
              style={styles.filePicker}
              onPress={handlePickFile}
              activeOpacity={0.7}
            >
              {file ? (
                <View style={styles.fileSelected}>
                  <Text style={styles.fileName}>📎 {file.name}</Text>
                  <TouchableOpacity onPress={() => setFile(null)}>
                    <Text style={styles.fileRemove}>Remove</Text>
                  </TouchableOpacity>
                </View>
              ) : (
                <Text style={styles.filePickerTxt}>Tap to upload attachment</Text>
              )}
            </TouchableOpacity>

            <Text style={styles.label}>Description</Text>
            <TextInput
              value={description}
              onChangeText={setDescription}
              placeholder="Describe the assignment…"
              multiline
              style={[styles.input, { minHeight: 60 }]}
              placeholderTextColor="#94a3b8"
            />
          </ScrollView>

          <View style={styles.modalActions}>
            <TouchableOpacity style={styles.modalCancel} onPress={onClose}>
              <Text style={styles.modalCancelTxt}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity style={styles.modalConfirm} onPress={handleCreate}>
              <Text style={styles.modalConfirmTxt}>Create</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

// ─── Grade Modal ──────────────────────────────────────────────────────────────

function GradeModal({
  assessment,
  onClose,
  onGraded,
}: {
  assessment: any;
  onClose: () => void;
  onGraded: () => void;
}) {
  const [grades, setGrades] = useState<Record<number, string>>({});
  const [feedbacks, setFeedbacks] = useState<Record<number, string>>({});
  const [saving, setSaving] = useState<number | null>(null);

  const { data: subsData, isLoading } = useQuery({
    queryKey: ["mob-grade-subs", assessment.id],
    queryFn: () =>
      mobileApi.get<{ results: any[] }>("/gradebook/submissions/", { assessment: assessment.id }),
  });
  const submissions = subsData?.results ?? [];

  const handleGrade = async (sub: any) => {
    const marks = parseFloat(grades[sub.id] as string);
    if (isNaN(marks) || marks < 0) {
      Alert.alert("Validation", "Enter valid marks");
      return;
    }
    setSaving(sub.id);
    try {
      await mobileApiClient.patch(`/gradebook/submissions/${sub.id}/`, {
        marks_obtained: marks,
        remarks: feedbacks[sub.id] ?? "",
      });
      Alert.alert("Graded!", `Marks saved for ${sub.student_name}`);
      onGraded();
    } catch (e: any) {
      Alert.alert("Error", e?.response?.data?.detail ?? "Failed to grade.");
    } finally {
      setSaving(null);
    }
  };

  return (
    <Modal visible transparent animationType="slide" onRequestClose={onClose}>
      <View style={styles.modalOverlay}>
        <View style={[styles.modal, { maxHeight: 550 }]}>
          {isLoading ? (
            <SkeletonList />
          ) : (
            <>
              <View style={styles.modalHeader}>
                <Text style={styles.modalTitle}>Grade Submissions</Text>
                <TouchableOpacity onPress={onClose}>
                  <Text style={styles.modalClose}>✕</Text>
                </TouchableOpacity>
              </View>
              <Text style={styles.modalAssTitle}>{assessment.title}</Text>
              <Text style={styles.modalAssMeta}>
                {assessment.subject_name} · Max: {assessment.max_marks}
              </Text>

              {submissions.length === 0 ? (
                <EmptyState
                  icon="📭"
                  title="No submissions"
                  sub="No student submissions for this assessment yet."
                />
              ) : (
                <ScrollView style={{ maxHeight: 350 }}>
                  {submissions.map((sub: any) => (
                    <View key={sub.id} style={styles.gradeRow}>
                      <View style={styles.gradeStudent}>
                        <Text style={styles.gradeName}>{sub.student_name}</Text>
                        {sub.marks_obtained != null ? (
                          <Text style={styles.gradedLabel}>
                            ✅ {sub.marks_obtained}/{assessment.max_marks}
                          </Text>
                        ) : (
                          <Text style={styles.pendingLabel}>⏳ Pending</Text>
                        )}
                        {sub.is_late && <Text style={styles.lateTxt}>Late</Text>}
                      </View>
                      {sub.marks_obtained == null ? (
                        <View style={styles.gradeInputs}>
                          <TextInput
                            value={grades[sub.id] ?? ""}
                            onChangeText={(v) => setGrades((g) => ({ ...g, [sub.id]: v }))}
                            keyboardType="numeric"
                            placeholder={`0-${assessment.max_marks}`}
                            style={styles.marksInput}
                            placeholderTextColor="#94a3b8"
                          />
                          <TextInput
                            value={feedbacks[sub.id] ?? ""}
                            onChangeText={(v) => setFeedbacks((f) => ({ ...f, [sub.id]: v }))}
                            placeholder="Feedback"
                            style={styles.feedbackInput}
                            placeholderTextColor="#94a3b8"
                          />
                          <TouchableOpacity
                            style={[styles.gradeBtn, saving === sub.id && { opacity: 0.5 }]}
                            onPress={() => handleGrade(sub)}
                            disabled={saving === sub.id}
                          >
                            <Text style={styles.gradeBtnTxt}>
                              {saving === sub.id ? "…" : "Grade"}
                            </Text>
                          </TouchableOpacity>
                        </View>
                      ) : (
                        <Text style={styles.doneLabel}>Done</Text>
                      )}
                    </View>
                  ))}
                </ScrollView>
              )}
            </>
          )}
        </View>
      </View>
    </Modal>
  );
}

// ─── Main Screen ──────────────────────────────────────────────────────────────

export default function TeacherAssignmentsScreen() {
  const [showCreate, setShowCreate] = useState(false);
  const [gradeTarget, setGradeTarget] = useState<any>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  const qc = useQueryClient();

  const {
    data: assData,
    isLoading,
    refetch,
  } = useQuery({
    queryKey: ["mob-teacher-assessments"],
    queryFn: () => mobileApi.get<{ results: any[] }>("/gradebook/assessments/"),
  });
  const assessments = assData?.results ?? [];

  const onChanged = () => {
    qc.invalidateQueries({ queryKey: ["mob-teacher-assessments"] });
    qc.invalidateQueries({ queryKey: ["mob-grade-subs"] });
  };

  if (isLoading) return <SkeletonList />;

  return (
    <View style={{ flex: 1, backgroundColor: "#f8fafc" }}>
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor={BRAND} />
        }
      >
        <View style={styles.headerRow}>
          <View style={{ flex: 1 }}>
            <Text style={styles.heading}>Assignments</Text>
            <Text style={styles.sub}>Create and grade homework, quizzes, and projects</Text>
          </View>
          <TouchableOpacity style={styles.addBtn} onPress={() => setShowCreate(true)}>
            <Text style={styles.addBtnTxt}>+ Create</Text>
          </TouchableOpacity>
        </View>

        {/* Stats */}
        {assessments.length > 0 && (
          <View style={styles.statsRow}>
            {[
              { label: "Total", value: assessments.length, color: "#64748b", bg: "#f8fafc" },
              {
                label: "Homework",
                value: assessments.filter((a: any) => a.assessment_type === "homework").length,
                color: "#3b82f6",
                bg: "#eff6ff",
              },
              {
                label: "Quizzes",
                value: assessments.filter((a: any) => a.assessment_type === "quiz").length,
                color: "#8b5cf6",
                bg: "#f5f3ff",
              },
              {
                label: "Projects",
                value: assessments.filter((a: any) => a.assessment_type === "project").length,
                color: "#f59e0b",
                bg: "#fffbeb",
              },
            ].map(({ label, value, color, bg }) => (
              <View key={label} style={[styles.statCard, { backgroundColor: bg }]}>
                <Text style={[styles.statVal, { color }]}>{value}</Text>
                <Text style={styles.statLbl}>{label}</Text>
              </View>
            ))}
          </View>
        )}

        {/* List */}
        {assessments.length === 0 ? (
          <EmptyState
            icon="📚"
            title="No assignments yet"
            sub="Create your first assessment for your students."
          />
        ) : (
          <View style={styles.list}>
            {assessments.map((ass: any) => {
              const expanded = expandedId === ass.id;
              return (
                <View key={ass.id} style={styles.card}>
                  <TouchableOpacity
                    style={styles.cardHeader}
                    onPress={() => setExpandedId(expanded ? null : ass.id)}
                    activeOpacity={0.7}
                  >
                    <View style={{ flex: 1 }}>
                      <View style={styles.cardHeaderTop}>
                        <View
                          style={[
                            styles.typeBadge,
                            {
                              backgroundColor:
                                TYPE_OPTIONS.find((o) => o.value === ass.assessment_type)?.bg ??
                                "#f1f5f9",
                            },
                          ]}
                        >
                          <Text style={styles.typeIcon}>
                            {TYPE_OPTIONS.find((o) => o.value === ass.assessment_type)?.icon ??
                              "📋"}
                          </Text>
                          <Text
                            style={[
                              styles.typeText,
                              {
                                color:
                                  TYPE_OPTIONS.find((o) => o.value === ass.assessment_type)
                                    ?.color ?? "#64748b",
                              },
                            ]}
                          >
                            {ass.assessment_type.charAt(0).toUpperCase() +
                              ass.assessment_type.slice(1)}
                          </Text>
                        </View>
                        <Text style={styles.marksBadge}>{ass.max_marks} marks</Text>
                      </View>
                      <Text style={styles.cardTitle}>{ass.title}</Text>
                      <Text style={styles.cardMeta}>
                        {ass.subject_name} · {ass.classroom_name} · Due{" "}
                        {dayjs(ass.due_date).format("MMM D")}
                      </Text>
                    </View>
                    <Text style={styles.expandIcon}>{expanded ? "▲" : "▼"}</Text>
                  </TouchableOpacity>

                  {expanded && (
                    <View style={styles.expanded}>
                      {ass.description && <Text style={styles.desc}>{ass.description}</Text>}
                      {ass.attachment && (
                        <TouchableOpacity
                          style={styles.attachBtn}
                          onPress={() => Linking.openURL(ass.attachment)}
                        >
                          <Text style={styles.attachBtnTxt}>📎 View attachment</Text>
                        </TouchableOpacity>
                      )}
                      <TouchableOpacity
                        style={styles.gradeActionBtn}
                        onPress={() => setGradeTarget(ass)}
                      >
                        <Text style={styles.gradeActionTxt}>⭐ Grade Submissions</Text>
                      </TouchableOpacity>
                    </View>
                  )}
                </View>
              );
            })}
          </View>
        )}
      </ScrollView>

      {showCreate && <CreateModal onClose={() => setShowCreate(false)} onCreated={onChanged} />}
      {gradeTarget && (
        <GradeModal
          assessment={gradeTarget}
          onClose={() => setGradeTarget(null)}
          onGraded={onChanged}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  content: { padding: 16, paddingBottom: 40 },
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b" },
  sub: { fontSize: 13, color: "#64748b", marginTop: 4, marginBottom: 16 },
  headerRow: { flexDirection: "row", alignItems: "flex-start", marginBottom: 16 },
  addBtn: { backgroundColor: BRAND, borderRadius: 10, paddingHorizontal: 14, paddingVertical: 8 },
  addBtnTxt: { fontSize: 13, fontWeight: "700", color: "#fff" },
  statsRow: { flexDirection: "row", gap: 6, marginBottom: 16 },
  statCard: { flex: 1, borderRadius: 10, padding: 10, alignItems: "center" },
  statVal: { fontSize: 18, fontWeight: "800" },
  statLbl: { fontSize: 10, color: "#64748b", marginTop: 2 },
  list: { gap: 10 },
  card: {
    backgroundColor: "#fff",
    borderRadius: 14,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    overflow: "hidden",
  },
  cardHeader: { padding: 14, flexDirection: "row", alignItems: "center" },
  cardHeaderTop: { flexDirection: "row", alignItems: "center", gap: 6, marginBottom: 4 },
  typeBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 3,
    borderRadius: 8,
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  typeIcon: { fontSize: 11 },
  typeText: { fontSize: 9, fontWeight: "700" },
  marksBadge: { fontSize: 10, fontWeight: "700", color: "#64748b" },
  cardTitle: { fontSize: 14, fontWeight: "700", color: "#1e293b" },
  cardMeta: { fontSize: 11, color: "#64748b", marginTop: 2 },
  expandIcon: { fontSize: 10, color: "#94a3b8", marginLeft: 8 },
  expanded: { padding: 14, borderTopWidth: 1, borderTopColor: "#f1f5f9", paddingTop: 10 },
  desc: { fontSize: 13, color: "#475569", lineHeight: 18, marginBottom: 10 },
  attachBtn: {
    backgroundColor: "#eff6ff",
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 8,
    marginBottom: 10,
    alignSelf: "flex-start",
  },
  attachBtnTxt: { fontSize: 12, fontWeight: "600", color: BRAND },
  gradeActionBtn: {
    backgroundColor: "#f59e0b",
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 10,
    alignItems: "center",
  },
  gradeActionTxt: { fontSize: 13, fontWeight: "700", color: "#fff" },
  // Modal styles
  modalOverlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.4)", justifyContent: "flex-end" },
  modal: {
    backgroundColor: "#fff",
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    paddingBottom: Platform.OS === "ios" ? 40 : 20,
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  modalTitle: { fontSize: 18, fontWeight: "700", color: "#1e293b" },
  modalClose: { fontSize: 20, color: "#94a3b8", padding: 4 },
  modalAssTitle: { fontSize: 15, fontWeight: "700", color: "#1e293b" },
  modalAssMeta: { fontSize: 12, color: "#64748b", marginTop: 2, marginBottom: 12 },
  label: { fontSize: 12, fontWeight: "600", color: "#374151", marginBottom: 6, marginTop: 4 },
  input: {
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 13,
    color: "#1e293b",
    marginBottom: 10,
    backgroundColor: "#fff",
  },
  chipRow: { flexDirection: "row", flexWrap: "wrap", gap: 6, marginBottom: 10 },
  chip: {
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    paddingHorizontal: 10,
    paddingVertical: 5,
    backgroundColor: "#fff",
  },
  chipActive: { backgroundColor: BRAND, borderColor: BRAND },
  chipTxt: { fontSize: 11, fontWeight: "600", color: "#64748b" },
  chipTxtActive: { color: "#fff" },
  row: { flexDirection: "row", alignItems: "flex-start" },
  filePicker: {
    borderWidth: 2,
    borderColor: "#e2e8f0",
    borderStyle: "dashed",
    borderRadius: 10,
    padding: 14,
    alignItems: "center",
    marginBottom: 10,
  },
  fileSelected: { flexDirection: "row", alignItems: "center", gap: 8 },
  fileName: { fontSize: 12, fontWeight: "600", color: BRAND, flex: 1 },
  fileRemove: { fontSize: 11, color: "#dc2626", fontWeight: "600" },
  filePickerTxt: { fontSize: 12, color: "#94a3b8" },
  modalActions: { flexDirection: "row", gap: 10, marginTop: 8 },
  modalCancel: {
    flex: 1,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    paddingVertical: 12,
    alignItems: "center",
  },
  modalCancelTxt: { fontSize: 14, fontWeight: "600", color: "#64748b" },
  modalConfirm: {
    flex: 1,
    backgroundColor: BRAND,
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: "center",
  },
  modalConfirmTxt: { fontSize: 14, fontWeight: "700", color: "#fff" },
  gradeRow: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#f1f5f9",
  },
  gradeStudent: { flex: 1 },
  gradeName: { fontSize: 13, fontWeight: "700", color: "#1e293b" },
  gradedLabel: { fontSize: 11, color: "#15803d", fontWeight: "600", marginTop: 2 },
  pendingLabel: { fontSize: 11, color: "#d97706", fontWeight: "600", marginTop: 2 },
  lateTxt: { fontSize: 10, color: "#dc2626", fontWeight: "600" },
  gradeInputs: { flexDirection: "row", gap: 4, alignItems: "center" },
  marksInput: {
    width: 50,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 6,
    paddingHorizontal: 6,
    paddingVertical: 4,
    fontSize: 12,
    color: "#1e293b",
    textAlign: "center",
  },
  feedbackInput: {
    width: 80,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 6,
    paddingHorizontal: 6,
    paddingVertical: 4,
    fontSize: 11,
    color: "#1e293b",
  },
  gradeBtn: { backgroundColor: BRAND, borderRadius: 6, paddingHorizontal: 10, paddingVertical: 6 },
  gradeBtnTxt: { fontSize: 11, fontWeight: "700", color: "#fff" },
  doneLabel: { fontSize: 11, color: "#15803d", fontWeight: "600" },
});
