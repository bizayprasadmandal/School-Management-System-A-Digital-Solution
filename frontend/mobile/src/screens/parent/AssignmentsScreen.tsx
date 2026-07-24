/**
 * Parent AssignmentsScreen — View each child's assignments,
 * submissions, and graded results.
 */

import React, { useState } from "react";
import {
  View, Text, ScrollView, StyleSheet, TouchableOpacity,
  RefreshControl, Alert, Modal, Platform, Linking,
} from "react-native";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { mobileApi } from "../../api/client";
import { SkeletonList, EmptyState } from "../../components";

const BRAND = "#7c3aed";

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
            <Text style={styles.modalAssMeta}>
              {assessment.subject_name} · {assessment.assessment_type}
            </Text>

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

            {submission.remarks && (
              <View style={[styles.remarksBox, submission.marks_obtained != null && { borderColor: '#bbf7d0', backgroundColor: '#f0fdf4' }]}>
                <Text style={styles.remarksLabel}>
                  {submission.marks_obtained != null ? "Teacher's feedback" : "Student's remarks"}
                </Text>
                <Text style={styles.remarksContent}>{submission.remarks}</Text>
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

export default function ParentAssignmentsScreen() {
  const [selectedChild, setSelectedChild] = useState<string>("");
  const [filter, setFilter] = useState<FilterTab>("pending");
  const [detailTarget, setDetailTarget] = useState<{ sub: any; assessment: any } | null>(null);

  // Children list
  const { data: childrenData } = useQuery({
    queryKey: ["mob-par-ass-children"],
    queryFn: () => mobileApi.get<{ results: any[] }>("/students/"),
  });
  const children = childrenData?.results ?? [];

  // Assessments
  const { data: assData, isLoading: assLoading, refetch: refetchAss } = useQuery({
    queryKey: ["mob-par-ass", selectedChild],
    queryFn: () =>
      mobileApi.get<{ results: any[] }>("/gradebook/assessments/", {
        student: selectedChild,
      }),
    enabled: !!selectedChild,
  });

  // Submissions
  const { data: subData, isLoading: subLoading } = useQuery({
    queryKey: ["mob-par-ass-submissions", selectedChild],
    queryFn: () => mobileApi.get<{ results: any[] }>("/gradebook/submissions/"),
    enabled: !!selectedChild,
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

  const filtered =
    filter === "all"
      ? categorized
      : categorized.filter((c: any) => c.category === filter);

  const counts = {
    pending: categorized.filter((c: any) => c.category === "pending").length,
    submitted: categorized.filter((c: any) => c.category === "submitted").length,
    graded: categorized.filter((c: any) => c.category === "graded").length,
  };

  const isLoading = assLoading || subLoading;
  const selectedChildName =
    children.find((c: any) => c.id === selectedChild)?.full_name ??
    children.find((c: any) => c.id === selectedChild)?.user?.full_name ??
    "";

  return (
    <View style={{ flex: 1, backgroundColor: "#f8fafc" }}>
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={isLoading}
            onRefresh={refetchAss}
            tintColor={BRAND}
          />
        }
      >
        <Text style={styles.heading}>Assignments</Text>
        <Text style={styles.sub}>View your children's assignments and grades</Text>

        {/* Child selector */}
        {children.length > 0 && (
          <View style={styles.childSection}>
            <Text style={styles.childLabel}>Select a child</Text>
            <View style={styles.chipRow}>
              {children.map((c: any) => (
                <TouchableOpacity
                  key={c.id}
                  style={[
                    styles.chip,
                    selectedChild === c.id && styles.chipActive,
                  ]}
                  onPress={() => setSelectedChild(c.id)}
                >
                  <Text
                    style={[
                      styles.chipTxt,
                      selectedChild === c.id && styles.chipTxtActive,
                    ]}
                    numberOfLines={1}
                  >
                    {c.full_name ?? c.user?.full_name ?? `Child ${c.id.slice(0, 6)}`}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        )}

        {!selectedChild ? (
          <View style={styles.emptySection}>
            <EmptyState
              icon="👆"
              title="Select a child"
              sub="Choose a child above to see their assignments and grades."
            />
          </View>
        ) : isLoading ? (
          <SkeletonList />
        ) : assessments.length === 0 ? (
          <View style={styles.emptySection}>
            <EmptyState
              icon="📚"
              title="No assignments"
              sub={`No assignments found for ${selectedChildName}.`}
            />
          </View>
        ) : (
          <>
            {/* Child name heading */}
            <View style={styles.selectedHeading}>
              <Text style={styles.selectedName}>{selectedChildName}</Text>
              <Text style={styles.selectedSub}>
                {categorized.length} assignment{categorized.length !== 1 ? "s" : ""}
              </Text>
            </View>

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
                  <Text
                    style={[styles.tabTxt, filter === tab && styles.tabTxtActive]}
                  >
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
                  title={
                    filter === "all"
                      ? "No assignments yet"
                      : `No ${filter} assignments`
                  }
                  sub={
                    filter === "pending"
                      ? `${selectedChildName} is all caught up!`
                      : "Nothing to show here."
                  }
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
                            {
                              backgroundColor:
                                (TYPE_BG as any)[assessment.assessment_type] ?? "#f1f5f9",
                            },
                          ]}
                        >
                          <Text style={styles.typeIcon}>
                            {(TYPE_ICONS as any)[assessment.assessment_type] ?? "📋"}
                          </Text>
                          <Text
                            style={[
                              styles.typeText,
                              {
                                color:
                                  (TYPE_COLORS as any)[assessment.assessment_type] ??
                                  "#64748b",
                              },
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
                        <Text style={styles.maxMarksVal}>
                          {assessment.max_marks}
                        </Text>
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
                        ⏰ Due{" "}
                        {dayjs(assessment.due_date).format("MMM D, YYYY")}
                      </Text>
                    </View>

                    {/* Description */}
                    {assessment.description && (
                      <Text style={styles.cardDesc} numberOfLines={2}>
                        {assessment.description}
                      </Text>
                    )}

                    {/* Status + View button */}
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

                      {submission && (
                        <TouchableOpacity
                          style={styles.viewBtn}
                          onPress={() =>
                            setDetailTarget({ sub: submission, assessment })
                          }
                        >
                          <Text style={styles.viewBtnTxt}>View</Text>
                        </TouchableOpacity>
                      )}
                    </View>
                  </View>
                ))}
              </View>
            )}
          </>
        )}
      </ScrollView>

      {/* Detail Modal */}
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
  emptySection: { paddingTop: 40 },
  childSection: { marginBottom: 16 },
  childLabel: { fontSize: 13, fontWeight: "600", color: "#374151", marginBottom: 8 },
  chipRow: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  chip: {
    borderRadius: 18,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    paddingHorizontal: 14,
    paddingVertical: 6,
    backgroundColor: "#fff",
  },
  chipActive: { backgroundColor: BRAND, borderColor: BRAND },
  chipTxt: { fontSize: 13, fontWeight: "600", color: "#64748b" },
  chipTxtActive: { color: "#fff" },
  selectedHeading: { marginBottom: 12 },
  selectedName: { fontSize: 17, fontWeight: "700", color: BRAND },
  selectedSub: { fontSize: 12, color: "#64748b", marginTop: 2 },
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
  viewBtn: {
    borderRadius: 8,
    backgroundColor: BRAND,
    paddingHorizontal: 16,
    paddingVertical: 6,
  },
  viewBtnTxt: { fontSize: 11, fontWeight: "700", color: "#fff" },
  // Modal styles
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
    backgroundColor: "#f5f3ff",
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
