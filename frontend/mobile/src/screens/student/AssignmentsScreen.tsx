/**
 * Student AssignmentsScreen — View homework/quizzes/projects,
 * submit work with file upload, and view graded results.
 */

import React, { useState } from "react";
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  TextInput, RefreshControl, Alert, Modal, Platform, Linking,
} from "react-native";
import * as DocumentPicker from "expo-document-picker";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import dayjs from "dayjs";
import { mobileApi, mobileApiClient } from "../../api/client";
import { SkeletonList, EmptyState } from "../../components";

const BRAND = "#6366f1";

const TYPE_ICONS: Record<string, string> = {
  homework: "📝",
  quiz: "❓",
  project: "📊",
  classwork: "📋",
  lab: "🔬",
};

const TYPE_COLORS: Record<string, string> = {
  homework: "#3b82f6",
  quiz: "#8b5cf6",
  project: "#f59e0b",
  classwork: "#059669",
  lab: "#e11d48",
};

const TYPE_BG: Record<string, string> = {
  homework: "#eff6ff",
  quiz: "#f5f3ff",
  project: "#fffbeb",
  classwork: "#ecfdf5",
  lab: "#fce7f3",
};

type FilterTab = "pending" | "submitted" | "graded" | "all";

// ─── Submit Modal ─────────────────────────────────────────────────────────────

function SubmitModal({
  assessment,
  onClose,
  onSubmitted,
}: {
  assessment: any;
  onClose: () => void;
  onSubmitted: () => void;
}) {
  const [remarks, setRemarks] = useState("");
  const [file, setFile] = useState<{ name: string; uri: string; mimeType: string } | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handlePickFile = async () => {
    try {
      const result = await DocumentPicker.getDocumentAsync({
        type: "*/*",
        copyToCacheDirectory: true,
      });
      if (!result.canceled && result.assets?.[0]) {
        const asset = result.assets[0];
        setFile({ name: asset.name, uri: asset.uri, mimeType: asset.mimeType ?? "application/octet-stream" });
      }
    } catch {
      Alert.alert("Error", "Failed to pick file.");
    }
  };

  const handleSubmit = async () => {
    if (!file && !remarks.trim()) {
      Alert.alert("Validation", "Please upload a file or add remarks.");
      return;
    }
    setIsSubmitting(true);
    try {
      const fd = new FormData();
      fd.append("assessment", String(assessment.id));
      if (file) {
        fd.append("file", {
          uri: file.uri,
          name: file.name,
          type: file.mimeType,
        } as any);
      }
      if (remarks.trim()) fd.append("remarks", remarks.trim());
      await mobileApiClient.post("/gradebook/submissions/", fd, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      Alert.alert("Submitted!", "Your assignment has been submitted.");
      onSubmitted();
      onClose();
    } catch (e: any) {
      Alert.alert("Error", e?.response?.data?.detail ?? "Failed to submit.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal visible transparent animationType="slide" onRequestClose={onClose}>
      <View style={styles.modalOverlay}>
        <View style={styles.modal}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Submit Assignment</Text>
            <TouchableOpacity onPress={onClose}>
              <Text style={styles.modalClose}>✕</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={{ maxHeight: 400 }}>
            <Text style={styles.modalAssTitle}>{assessment.title}</Text>
            <Text style={styles.modalAssMeta}>
              {assessment.subject_name} · Due {dayjs(assessment.due_date).format("MMM D, YYYY")}
            </Text>
            {assessment.description && (
              <Text style={styles.modalDesc}>{assessment.description}</Text>
            )}

            {/* File picker */}
            <Text style={styles.label}>Attachment (optional)</Text>
            <TouchableOpacity style={styles.filePicker} onPress={handlePickFile} activeOpacity={0.7}>
              {file ? (
                <View style={styles.fileSelected}>
                  <Text style={styles.fileName}>📎 {file.name}</Text>
                  <TouchableOpacity onPress={() => setFile(null)}>
                    <Text style={styles.fileRemove}>Remove</Text>
                  </TouchableOpacity>
                </View>
              ) : (
                <View style={styles.fileEmpty}>
                  <Text style={styles.fileEmptyIcon}>📄</Text>
                  <Text style={styles.fileEmptyTxt}>Tap to upload a file</Text>
                  <Text style={styles.fileEmptySub}>PDF, images, or documents</Text>
                </View>
              )}
            </TouchableOpacity>

            {/* Remarks */}
            <Text style={styles.label}>Remarks (optional)</Text>
            <TextInput
              value={remarks}
              onChangeText={setRemarks}
              placeholder="Add any notes for your teacher…"
              placeholderTextColor="#94a3b8"
              multiline
              style={styles.remarksInput}
            />
          </ScrollView>

          <View style={styles.modalActions}>
            <TouchableOpacity style={styles.modalCancel} onPress={onClose}>
              <Text style={styles.modalCancelTxt}>Cancel</Text>
            </TouchableOpacity>
            <TouchableOpacity
              style={[styles.modalConfirm, isSubmitting && { opacity: 0.6 }]}
              onPress={handleSubmit}
              disabled={isSubmitting}
            >
              <Text style={styles.modalConfirmTxt}>
                {isSubmitting ? "Submitting…" : "Submit Assignment"}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </Modal>
  );
}

// ─── Detail Modal ─────────────────────────────────────────────────────────────

function DetailModal({
  submission,
  assessment,
  onClose,
}: {
  submission: any;
  assessment: any;
  onClose: () => void;
}) {
  return (
    <Modal visible transparent animationType="fade" onRequestClose={onClose}>
      <View style={styles.modalOverlay}>
        <View style={[styles.modal, { maxHeight: 500 }]}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Submission Details</Text>
            <TouchableOpacity onPress={onClose}>
              <Text style={styles.modalClose}>✕</Text>
            </TouchableOpacity>
          </View>

          <ScrollView>
            <Text style={styles.modalAssTitle}>{assessment.title}</Text>
            <Text style={styles.modalAssMeta}>{assessment.subject_name}</Text>

            {submission.submitted_at && (
              <View style={styles.detailRow}>
                <Text style={styles.detailLabel}>Submitted</Text>
                <Text style={styles.detailValue}>
                  {dayjs(submission.submitted_at).format("MMM D, YYYY h:mm A")}
                </Text>
                {submission.is_late && (
                  <Text style={styles.lateBadge}>Late</Text>
                )}
              </View>
            )}

            {submission.file && (
              <TouchableOpacity
                style={styles.fileLink}
                onPress={() => Linking.openURL(submission.file)}
              >
                <Text style={styles.fileLinkTxt}>📎 View submitted file</Text>
              </TouchableOpacity>
            )}

            {submission.remarks && (
              <View style={styles.remarksBox}>
                <Text style={styles.remarksLabel}>Your remarks</Text>
                <Text style={styles.remarksContent}>{submission.remarks}</Text>
              </View>
            )}

            {submission.marks_obtained != null && (
              <View style={styles.gradeBox}>
                <View>
                  <Text style={styles.gradeLabel}>Grade</Text>
                  <Text style={styles.gradeValue}>
                    {submission.marks_obtained} / {assessment.max_marks}
                  </Text>
                </View>
                <View style={{ alignItems: "flex-end" }}>
                  <Text style={styles.gradeLabel}>Percentage</Text>
                  <Text style={styles.gradeValue}>
                    {submission.percentage?.toFixed(1) ?? "—"}%
                  </Text>
                </View>
              </View>
            )}
          </ScrollView>

          <TouchableOpacity style={styles.closeBtn} onPress={onClose}>
            <Text style={styles.closeBtnTxt}>Close</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

// ─── Main Screen ──────────────────────────────────────────────────────────────

export default function StudentAssignmentsScreen() {
  const [filter, setFilter] = useState<FilterTab>("pending");
  const [submitTarget, setSubmitTarget] = useState<any>(null);
  const [detailTarget, setDetailTarget] = useState<{ sub: any; assessment: any } | null>(null);
  const qc = useQueryClient();

  const { data: profile } = useQuery({
    queryKey: ["mob-student-me-ass"],
    queryFn: () => mobileApi.get<any>("/students/me/"),
  });
  const studentId = profile?.id ?? "";

  const { data: assData, isLoading: assLoading, refetch: refetchAss } = useQuery({
    queryKey: ["mob-student-ass", studentId],
    queryFn: () => mobileApi.get<{ results: any[] }>("/gradebook/assessments/", { student: studentId }),
    enabled: !!studentId,
  });

  const { data: subData, isLoading: subLoading } = useQuery({
    queryKey: ["mob-student-submissions", studentId],
    queryFn: () => mobileApi.get<{ results: any[] }>("/gradebook/submissions/"),
    enabled: !!studentId,
  });

  const assessments = assData?.results ?? [];
  const submissions = subData?.results ?? [];

  // Build lookup: assessment_id → submission
  const subMap = new Map<number, any>();
  submissions.forEach((s: any) => subMap.set(s.assessment, s));

  // Categorize
  const now = dayjs();
  const categorized = assessments.map((a: any) => {
    const sub = subMap.get(a.id);
    const pastDue = now.isAfter(dayjs(a.due_date));
    let category: FilterTab;
    if (sub?.marks_obtained != null) category = "graded";
    else if (sub) category = "submitted";
    else category = "pending";
    return { assessment: a, submission: sub, category, pastDue };
  });

  const filtered = filter === "all" ? categorized : categorized.filter((c: any) => c.category === filter);

  const counts = {
    pending: categorized.filter((c: any) => c.category === "pending").length,
    submitted: categorized.filter((c: any) => c.category === "submitted").length,
    graded: categorized.filter((c: any) => c.category === "graded").length,
  };

  const isLoading = assLoading || subLoading;

  const handleSubmitted = () => {
    qc.invalidateQueries({ queryKey: ["mob-student-ass"] });
    qc.invalidateQueries({ queryKey: ["mob-student-submissions"] });
  };

  if (isLoading) return <SkeletonList />;

  return (
    <View style={{ flex: 1, backgroundColor: "#f8fafc" }}>
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={isLoading} onRefresh={refetchAss} tintColor={BRAND} />}
      >
        <Text style={styles.heading}>My Assignments</Text>
        <Text style={styles.sub}>Homework, quizzes, projects, and lab work</Text>

        {/* Quick stats */}
        <View style={styles.statsRow}>
          {[
            { label: "Pending", value: counts.pending, color: "#f59e0b", bg: "#fffbeb", icon: "⏳" },
            { label: "Submitted", value: counts.submitted, color: "#3b82f6", bg: "#eff6ff", icon: "📤" },
            { label: "Graded", value: counts.graded, color: "#22c55e", bg: "#f0fdf4", icon: "✅" },
          ].map(({ label, value, color, bg, icon }) => (
            <TouchableOpacity
              key={label}
              style={[styles.statCard, { backgroundColor: bg }]}
              onPress={() => setFilter(label.toLowerCase() as FilterTab)}
              activeOpacity={0.8}
            >
              <Text style={styles.statIcon}>{icon}</Text>
              <Text style={[styles.statVal, { color }]}>{value}</Text>
              <Text style={styles.statLbl}>{label}</Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Filter tabs */}
        <View style={styles.tabRow}>
          {(["pending", "submitted", "graded", "all"] as FilterTab[]).map((tab) => (
            <TouchableOpacity
              key={tab}
              style={[styles.tab, filter === tab && styles.tabActive]}
              onPress={() => setFilter(tab)}
            >
              <Text style={[styles.tabTxt, filter === tab && styles.tabTxtActive]}>
                {tab === "all"
                  ? "All"
                  : `${tab.charAt(0).toUpperCase() + tab.slice(1)} (${counts[tab as keyof typeof counts]})`}
              </Text>
            </TouchableOpacity>
          ))}
        </View>

        {/* Assignment list */}
        {filtered.length === 0 ? (
          <View style={styles.emptySection}>
            <EmptyState
              icon="📚"
              title={filter === "all" ? "No assignments yet" : `No ${filter} assignments`}
              sub={filter === "pending" ? "You're all caught up!" : "Nothing to show here."}
            />
          </View>
        ) : (
          <View style={styles.list}>
            {filtered.map(({ assessment, submission, category, pastDue }: any) => (
              <View
                key={assessment.id}
                style={[
                  styles.card,
                  pastDue && !submission && styles.cardOverdue,
                ]}
              >
                {/* Header */}
                <View style={styles.cardHeader}>
                  <View style={styles.cardHeaderLeft}>
                    <View
                      style={[
                        styles.typeBadge,
                        { backgroundColor: (TYPE_BG as any)[assessment.assessment_type] ?? "#f1f5f9" },
                      ]}
                    >
                      <Text style={styles.typeIcon}>
                        {(TYPE_ICONS as any)[assessment.assessment_type] ?? "📋"}
                      </Text>
                      <Text
                        style={[
                          styles.typeText,
                          { color: (TYPE_COLORS as any)[assessment.assessment_type] ?? "#64748b" },
                        ]}
                      >
                        {assessment.assessment_type.charAt(0).toUpperCase() +
                          assessment.assessment_type.slice(1)}
                      </Text>
                    </View>
                    {pastDue && !submission && (
                      <View style={styles.overdueBadge}>
                        <Text style={styles.overdueTxt}>Overdue</Text>
                      </View>
                    )}
                  </View>
                  <View style={{ alignItems: "flex-end" }}>
                    <Text style={styles.maxMarksLabel}>Max marks</Text>
                    <Text style={styles.maxMarksVal}>{assessment.max_marks}</Text>
                  </View>
                </View>

                {/* Title */}
                <Text style={styles.cardTitle}>{assessment.title}</Text>

                {/* Meta */}
                <View style={styles.cardMeta}>
                  <Text style={styles.metaItem}>
                    📚 {assessment.subject_name}
                  </Text>
                  <Text style={styles.metaItem}>
                    ⏰ Due {dayjs(assessment.due_date).format("MMM D, YYYY")}
                  </Text>
                </View>

                {/* Description */}
                {assessment.description && (
                  <Text style={styles.cardDesc} numberOfLines={2}>
                    {assessment.description}
                  </Text>
                )}

                {/* Status + Actions */}
                <View style={styles.cardFooter}>
                  {submission?.marks_obtained != null ? (
                    <View style={styles.gradedBadge}>
                      <Text style={styles.gradedTxt}>
                        ✅ Graded: {submission.marks_obtained}/{assessment.max_marks}
                      </Text>
                    </View>
                  ) : submission ? (
                    <View style={styles.submittedBadge}>
                      <Text style={styles.submittedTxt}>
                        📤 Submitted{submission.is_late ? " (late)" : ""}
                      </Text>
                    </View>
                  ) : (
                    <Text style={styles.notSubmitted}>Not submitted</Text>
                  )}

                  <View style={styles.cardActions}>
                    {submission && (
                      <TouchableOpacity
                        style={styles.actionBtn}
                        onPress={() => setDetailTarget({ sub: submission, assessment })}
                      >
                        <Text style={styles.actionBtnTxt}>View</Text>
                      </TouchableOpacity>
                    )}
                    {!submission && (
                      <TouchableOpacity
                        style={styles.submitBtn}
                        onPress={() => setSubmitTarget(assessment)}
                      >
                        <Text style={styles.submitBtnTxt}>Submit</Text>
                      </TouchableOpacity>
                    )}
                  </View>
                </View>
              </View>
            ))}
          </View>
        )}
      </ScrollView>

      {/* Modals */}
      {submitTarget && (
        <SubmitModal
          assessment={submitTarget}
          onClose={() => setSubmitTarget(null)}
          onSubmitted={handleSubmitted}
        />
      )}
      {detailTarget && (
        <DetailModal
          submission={detailTarget.sub}
          assessment={detailTarget.assessment}
          onClose={() => setDetailTarget(null)}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  content: { padding: 16, paddingBottom: 40 },
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b" },
  sub: { fontSize: 13, color: "#64748b", marginTop: 4, marginBottom: 16 },
  statsRow: { flexDirection: "row", gap: 8, marginBottom: 16 },
  statCard: {
    flex: 1,
    borderRadius: 12,
    padding: 12,
    alignItems: "center",
  },
  statIcon: { fontSize: 18, marginBottom: 4 },
  statVal: { fontSize: 22, fontWeight: "800" },
  statLbl: { fontSize: 11, color: "#64748b", marginTop: 2 },
  tabRow: { flexDirection: "row", gap: 6, marginBottom: 16 },
  tab: {
    flex: 1,
    paddingVertical: 8,
    borderRadius: 8,
    alignItems: "center",
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  tabActive: { backgroundColor: BRAND, borderColor: BRAND },
  tabTxt: { fontSize: 11, fontWeight: "600", color: "#64748b" },
  tabTxtActive: { color: "#fff" },
  emptySection: { paddingTop: 40 },
  list: { gap: 12 },
  card: {
    backgroundColor: "#fff",
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  cardOverdue: { borderColor: "#fecaca", backgroundColor: "#fff5f5" },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 8,
  },
  cardHeaderLeft: { flexDirection: "row", gap: 6, flex: 1, flexWrap: "wrap" },
  typeBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 4,
    borderRadius: 12,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  typeIcon: { fontSize: 12 },
  typeText: { fontSize: 10, fontWeight: "700" },
  overdueBadge: {
    backgroundColor: "#fef2f2",
    borderRadius: 8,
    paddingHorizontal: 6,
    paddingVertical: 2,
  },
  overdueTxt: { fontSize: 10, fontWeight: "700", color: "#dc2626" },
  maxMarksLabel: { fontSize: 10, color: "#94a3b8" },
  maxMarksVal: { fontSize: 18, fontWeight: "800", color: "#334155" },
  cardTitle: { fontSize: 15, fontWeight: "700", color: "#1e293b", marginBottom: 6 },
  cardMeta: { flexDirection: "row", gap: 12, marginBottom: 6 },
  metaItem: { fontSize: 11, color: "#64748b" },
  cardDesc: { fontSize: 12, color: "#475569", lineHeight: 18, marginBottom: 8 },
  cardFooter: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: "#f1f5f9",
  },
  gradedBadge: {
    backgroundColor: "#f0fdf4",
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  gradedTxt: { fontSize: 11, fontWeight: "600", color: "#15803d" },
  submittedBadge: {
    backgroundColor: "#eff6ff",
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  submittedTxt: { fontSize: 11, fontWeight: "600", color: "#2563eb" },
  notSubmitted: { fontSize: 11, color: "#94a3b8", fontStyle: "italic" },
  cardActions: { flexDirection: "row", gap: 6 },
  actionBtn: {
    borderRadius: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    paddingHorizontal: 12,
    paddingVertical: 5,
  },
  actionBtnTxt: { fontSize: 11, fontWeight: "600", color: "#64748b" },
  submitBtn: {
    backgroundColor: BRAND,
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 6,
  },
  submitBtnTxt: { fontSize: 11, fontWeight: "700", color: "#fff" },
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
  modalAssMeta: { fontSize: 12, color: "#64748b", marginTop: 2, marginBottom: 8 },
  modalDesc: {
    fontSize: 13,
    color: "#475569",
    backgroundColor: "#f8fafc",
    borderRadius: 10,
    padding: 12,
    lineHeight: 18,
    marginBottom: 16,
  },
  label: { fontSize: 12, fontWeight: "600", color: "#374151", marginBottom: 6, marginTop: 4 },
  filePicker: {
    borderWidth: 2,
    borderColor: "#e2e8f0",
    borderStyle: "dashed",
    borderRadius: 12,
    padding: 16,
    alignItems: "center",
    marginBottom: 14,
  },
  fileSelected: { flexDirection: "row", alignItems: "center", gap: 8 },
  fileName: { fontSize: 13, fontWeight: "600", color: BRAND, flex: 1 },
  fileRemove: { fontSize: 12, color: "#dc2626", fontWeight: "600" },
  fileEmpty: { alignItems: "center" },
  fileEmptyIcon: { fontSize: 28, marginBottom: 4 },
  fileEmptyTxt: { fontSize: 13, fontWeight: "600", color: "#64748b" },
  fileEmptySub: { fontSize: 11, color: "#94a3b8", marginTop: 2 },
  remarksInput: {
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 10,
    fontSize: 13,
    color: "#1e293b",
    minHeight: 60,
    marginBottom: 14,
    textAlignVertical: "top",
  },
  modalActions: { flexDirection: "row", gap: 10, marginTop: 4 },
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
  detailRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    marginBottom: 12,
  },
  detailLabel: { fontSize: 12, color: "#64748b" },
  detailValue: { fontSize: 12, fontWeight: "600", color: "#334155" },
  lateBadge: {
    fontSize: 10,
    fontWeight: "700",
    color: "#e11d48",
    backgroundColor: "#fce7f3",
    borderRadius: 4,
    paddingHorizontal: 5,
    paddingVertical: 1,
  },
  fileLink: {
    backgroundColor: "#eff6ff",
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 10,
    marginBottom: 12,
  },
  fileLinkTxt: { fontSize: 13, fontWeight: "600", color: BRAND },
  remarksBox: { marginBottom: 12 },
  remarksLabel: { fontSize: 11, fontWeight: "600", color: "#64748b", marginBottom: 4 },
  remarksContent: {
    fontSize: 13,
    color: "#475569",
    backgroundColor: "#f8fafc",
    borderRadius: 8,
    padding: 10,
    lineHeight: 18,
  },
  gradeBox: {
    flexDirection: "row",
    justifyContent: "space-between",
    backgroundColor: "#f0fdf4",
    borderRadius: 12,
    borderWidth: 1,
    borderColor: "#bbf7d0",
    padding: 14,
    marginBottom: 8,
  },
  gradeLabel: { fontSize: 11, fontWeight: "600", color: "#15803d", marginBottom: 4 },
  gradeValue: { fontSize: 20, fontWeight: "800", color: "#166534" },
  closeBtn: {
    marginTop: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    paddingVertical: 10,
    alignItems: "center",
  },
  closeBtnTxt: { fontSize: 14, fontWeight: "600", color: "#64748b" },
});
