/**
 * Student GradesScreen — Report cards, cumulative GPA, subject breakdown,
 * grade trends, and PDF download.
 */

import React, { useState, useMemo } from "react";
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  TouchableOpacity,
  RefreshControl,
  Alert,
  Modal,
  Platform,
  Linking,
  DimensionValue,
} from "react-native";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { mobileApi, mobileApiClient } from "../../api/client";
import { SkeletonGradesScreen, Card, Badge, StatCard } from "../../components";

const BRAND = "#6366f1";

// ─── Color helper ────────────────────────────────────────────────────────────

function scoreColor(pct: number): string {
  if (pct >= 75) return "#15803d";
  if (pct >= 50) return "#d97706";
  return "#dc2626";
}

function scoreBg(pct: number): string {
  if (pct >= 75) return "#dcfce7";
  if (pct >= 50) return "#fef9c7";
  return "#fee2e2";
}

// ─── Detail Modal ─────────────────────────────────────────────────────────────

function ReportCardDetailModal({
  reportCard,
  subjectData,
  onClose,
}: {
  reportCard: any;
  subjectData: {
    subject: string;
    marks_obtained: number | null;
    max_marks: number;
    percentage: number | null;
  }[];
  onClose: () => void;
}) {
  const pct = Number(reportCard.percentage);
  const color = scoreColor(pct);

  const handleDownloadPDF = async () => {
    if (!reportCard.pdf_url && !reportCard.pdf_file) {
      Alert.alert("No PDF", "This report card has no PDF file attached.");
      return;
    }
    const url = reportCard.pdf_url ?? reportCard.pdf_file;
    try {
      await Linking.openURL(url);
    } catch {
      Alert.alert("Error", "Could not open PDF. Try downloading from the web portal.");
    }
  };

  return (
    <Modal visible transparent animationType="slide" onRequestClose={onClose}>
      <View style={styles.modalOverlay}>
        <View style={styles.modal}>
          <View style={styles.modalHeader}>
            <Text style={styles.modalTitle}>Report Card</Text>
            <TouchableOpacity onPress={onClose}>
              <Text style={styles.modalClose}>✕</Text>
            </TouchableOpacity>
          </View>

          <ScrollView style={{ maxHeight: 500 }}>
            {/* Hero section */}
            <View style={[styles.detailHero, { backgroundColor: BRAND }]}>
              <Text style={styles.detailExamName}>{reportCard.exam_name}</Text>
              <Text style={styles.detailYear}>{reportCard.academic_year_name}</Text>
              <View style={styles.detailHeroStats}>
                <View style={styles.detailHeroStat}>
                  <Text style={styles.detailHeroVal}>{pct.toFixed(1)}%</Text>
                  <Text style={styles.detailHeroLbl}>Score</Text>
                </View>
                <View style={styles.detailHeroStat}>
                  <Text style={styles.detailHeroVal}>{reportCard.grade_letter}</Text>
                  <Text style={styles.detailHeroLbl}>Grade</Text>
                </View>
                {reportCard.rank_in_class && (
                  <View style={styles.detailHeroStat}>
                    <Text style={styles.detailHeroVal}>#{reportCard.rank_in_class}</Text>
                    <Text style={styles.detailHeroLbl}>Rank</Text>
                  </View>
                )}
              </View>
              {reportCard.gpa && (
                <View style={styles.detailGpaBadge}>
                  <Text style={styles.detailGpaLbl}>GPA</Text>
                  <Text style={styles.detailGpaVal}>{Number(reportCard.gpa).toFixed(2)}</Text>
                </View>
              )}
            </View>

            {/* Marks summary */}
            <View style={styles.marksSummary}>
              <View style={styles.marksCard}>
                <Text style={styles.marksLbl}>Total Marks</Text>
                <Text style={styles.marksVal}>{reportCard.total_marks}</Text>
              </View>
              <View style={styles.marksCard}>
                <Text style={styles.marksLbl}>Obtained</Text>
                <Text style={[styles.marksVal, { color }]}>{reportCard.obtained_marks}</Text>
              </View>
              <View style={styles.marksCard}>
                <Text style={styles.marksLbl}>Status</Text>
                <Badge
                  label={reportCard.status}
                  color={reportCard.status === "published" ? "green" : "slate"}
                />
              </View>
              {reportCard.attendance_percentage != null && (
                <View style={styles.marksCard}>
                  <Text style={styles.marksLbl}>Attendance</Text>
                  <Text style={styles.marksVal}>
                    {Number(reportCard.attendance_percentage).toFixed(1)}%
                  </Text>
                </View>
              )}
            </View>

            {/* Subject breakdown */}
            {subjectData.length > 0 && (
              <View style={styles.section}>
                <Text style={styles.sectionTitle}>Subject Performance</Text>
                {subjectData.map((subj, idx) => {
                  const subPct = subj.percentage;
                  const barColor = subPct != null ? scoreColor(subPct) : "#e2e8f0";
                  const barWidth = subPct != null ? `${Math.min(subPct, 100)}%` : "0%";
                  return (
                    <View key={idx} style={styles.subjRow}>
                      <View style={styles.subjInfo}>
                        <Text style={styles.subjName} numberOfLines={1}>
                          {subj.subject}
                        </Text>
                        <Text style={styles.subjMarks}>
                          {subj.marks_obtained != null
                            ? `${subj.marks_obtained}/${subj.max_marks}`
                            : "—"}
                        </Text>
                      </View>
                      <View style={styles.subjBarContainer}>
                        <View style={styles.subjBarBg}>
                          <View
                            style={[
                              styles.subjBarFill,
                              { width: barWidth as DimensionValue, backgroundColor: barColor },
                            ]}
                          />
                        </View>
                        <Text style={[styles.subjPct, { color: barColor }]}>
                          {subPct != null ? `${subPct.toFixed(0)}%` : "—"}
                        </Text>
                      </View>
                    </View>
                  );
                })}
              </View>
            )}

            {/* Teacher remarks */}
            {reportCard.teacher_remarks && (
              <View style={styles.remarksBox}>
                <Text style={styles.remarksLabel}>Teacher's Remarks</Text>
                <Text style={styles.remarksContent}>{reportCard.teacher_remarks}</Text>
              </View>
            )}

            {/* Principal remarks */}
            {reportCard.principal_remarks && (
              <View style={styles.remarksBox}>
                <Text style={styles.remarksLabel}>Principal's Remarks</Text>
                <Text style={styles.remarksContent}>{reportCard.principal_remarks}</Text>
              </View>
            )}

            {/* PDF Download */}
            {(reportCard.pdf_url || reportCard.pdf_file) && (
              <TouchableOpacity style={styles.pdfBtn} onPress={handleDownloadPDF}>
                <Text style={styles.pdfBtnIcon}>📄</Text>
                <Text style={styles.pdfBtnTxt}>Download Report Card PDF</Text>
              </TouchableOpacity>
            )}
          </ScrollView>

          <TouchableOpacity style={styles.modalDoneBtn} onPress={onClose}>
            <Text style={styles.modalDoneBtnTxt}>Close</Text>
          </TouchableOpacity>
        </View>
      </View>
    </Modal>
  );
}

// ─── Main Screen ─────────────────────────────────────────────────────────────

export default function StudentGradesScreen() {
  const qc = useQueryClient();
  const [detailTarget, setDetailTarget] = useState<any>(null);

  // ── Student profile ──────────────────────────────────────────────────────
  const { data: profile, isLoading: profileLoading } = useQuery({
    queryKey: ["student-me-mob"],
    queryFn: () => mobileApi.get<any>("/students/me/"),
  });

  // ── Report cards ─────────────────────────────────────────────────────────
  const {
    data: rcData,
    isLoading: rcLoading,
    refetch: refetchRc,
  } = useQuery({
    queryKey: ["report-cards-mob", profile?.id],
    queryFn: () =>
      mobileApi.get<{ results: any[] }>("/gradebook/report-cards/", {
        student: profile?.id,
      }),
    enabled: !!profile?.id,
  });
  const reportCards = rcData?.results ?? [];
  const latest = reportCards.find((r: any) => r.status === "published") ?? reportCards[0];

  // ── Cumulative GPA ───────────────────────────────────────────────────────
  const { data: gpaData, isLoading: gpaLoading } = useQuery({
    queryKey: ["student-gpa-mob", profile?.id],
    queryFn: () => mobileApi.get<any>(`/students/${profile!.id}/cumulative-gpa/`),
    enabled: !!profile?.id,
  });

  // ── Grade summary (subject breakdown) ────────────────────────────────────
  const { data: gradeSummaryData, isLoading: gsLoading } = useQuery({
    queryKey: ["student-grade-summary-mob", profile?.id],
    queryFn: () => mobileApi.get<{ grades: any[] }>(`/students/${profile!.id}/grade-summary/`),
    enabled: !!profile?.id,
  });

  const isLoading = profileLoading || rcLoading || gpaLoading;

  // ── Stats ────────────────────────────────────────────────────────────────
  const stats = useMemo(() => {
    const total = reportCards.length;
    if (total === 0) return { total: 0, avgScore: null, bestScore: null, published: 0 };
    const percentages = reportCards.map((r: any) => Number(r.percentage));
    const avg = Math.round(percentages.reduce((a, b) => a + b, 0) / total);
    const best = Math.round(Math.max(...percentages));
    const published = reportCards.filter((r: any) => r.status === "published").length;
    return { total, avgScore: avg, bestScore: best, published };
  }, [reportCards]);

  // ── Subject data for detail modal ────────────────────────────────────────
  const subjectDataForDetail = useMemo(() => {
    if (!gradeSummaryData?.grades) return [];
    return gradeSummaryData.grades.map((g: any) => ({
      subject: g.subject,
      marks_obtained: g.marks_obtained,
      max_marks: g.max_marks,
      percentage: g.percentage != null ? Number(g.percentage) : null,
    }));
  }, [gradeSummaryData]);

  const openDetail = (rc: any) => {
    setDetailTarget(rc);
  };

  if (isLoading && reportCards.length === 0) return <SkeletonGradesScreen />;

  const heroPct = latest ? Number(latest.percentage) : null;

  return (
    <View style={{ flex: 1, backgroundColor: "#f8fafc" }}>
      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl
            refreshing={isLoading}
            onRefresh={() => {
              qc.invalidateQueries({ queryKey: ["report-cards-mob"] });
              qc.invalidateQueries({ queryKey: ["student-gpa-mob"] });
              qc.invalidateQueries({ queryKey: ["student-grade-summary-mob"] });
            }}
            tintColor={BRAND}
          />
        }
      >
        <Text style={styles.heading}>My Grades</Text>
        <Text style={styles.sub}>Exam results, GPA, and performance</Text>

        {/* Latest Result Hero */}
        {latest ? (
          <View style={[styles.heroCard, { backgroundColor: BRAND }]}>
            <View style={styles.heroTop}>
              <View style={styles.heroLeft}>
                <Text style={styles.heroLabel}>
                  {latest.status === "published" ? "Latest Result" : "Latest"}
                </Text>
                <Text style={styles.heroExamName}>{latest.exam_name}</Text>
              </View>
              {gpaData && (
                <View style={styles.heroGpa}>
                  <Text style={styles.heroGpaLbl}>GPA</Text>
                  <Text style={styles.heroGpaVal}>{gpaData.cumulative_gpa.toFixed(2)}</Text>
                  <Text style={styles.heroGpaSub}>{gpaData.total_exams} exams</Text>
                </View>
              )}
            </View>
            <View style={styles.heroStats}>
              <View style={styles.heroStatItem}>
                <Text style={styles.heroStatVal}>{heroPct?.toFixed(1)}%</Text>
                <Text style={styles.heroStatLbl}>Score</Text>
              </View>
              <View style={styles.heroStatItem}>
                <Text style={styles.heroStatVal}>{latest.grade_letter}</Text>
                <Text style={styles.heroStatLbl}>Grade</Text>
              </View>
              {latest.rank_in_class && (
                <View style={styles.heroStatItem}>
                  <Text style={styles.heroStatVal}>#{latest.rank_in_class}</Text>
                  <Text style={styles.heroStatLbl}>Rank</Text>
                </View>
              )}
              <View style={styles.heroStatItem}>
                <Text style={styles.heroStatVal}>
                  {latest.obtained_marks}/{latest.total_marks}
                </Text>
                <Text style={styles.heroStatLbl}>Marks</Text>
              </View>
            </View>
          </View>
        ) : reportCards.length === 0 ? (
          <Card style={styles.emptyCard}>
            <Text style={styles.emptyEmoji}>📋</Text>
            <Text style={styles.emptyTitle}>No results yet</Text>
            <Text style={styles.emptySub}>Your exam results will appear here once published.</Text>
          </Card>
        ) : null}

        {/* Stats row */}
        {reportCards.length > 0 && (
          <View style={styles.statsRow}>
            {[
              { label: "Exams", value: stats.total, color: "#6366f1" },
              {
                label: "Average",
                value: stats.avgScore != null ? `${stats.avgScore}%` : "—",
                color: "#059669",
              },
              {
                label: "Best",
                value: stats.bestScore != null ? `${stats.bestScore}%` : "—",
                color: "#d97706",
              },
              { label: "Published", value: stats.published, color: "#6366f1" },
            ].map(({ label, value, color }) => (
              <View key={label} style={styles.statPill}>
                <Text style={[styles.statVal, { color }]}>{value}</Text>
                <Text style={styles.statLbl}>{label}</Text>
              </View>
            ))}
          </View>
        )}

        {/* Subject performance section (if we have grade summary) */}
        {gradeSummaryData && gradeSummaryData.grades && gradeSummaryData.grades.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Subject Performance</Text>
            {gradeSummaryData.grades.slice(0, 5).map((g: any, idx: number) => {
              const subPct = g.percentage != null ? Number(g.percentage) : null;
              const barColor = subPct != null ? scoreColor(subPct) : "#e2e8f0";
              const barWidth = subPct != null ? `${Math.min(subPct, 100)}%` : "0%";
              return (
                <View key={idx} style={styles.subjRow}>
                  <View style={styles.subjInfo}>
                    <Text style={styles.subjName} numberOfLines={1}>
                      {g.subject}
                    </Text>
                  </View>
                  <View style={styles.subjBarContainer}>
                    <View style={styles.subjBarBg}>
                      <View
                        style={[
                          styles.subjBarFill,
                          { width: barWidth as DimensionValue, backgroundColor: barColor },
                        ]}
                      />
                    </View>
                    <Text style={[styles.subjPct, { color: barColor }]}>
                      {subPct != null ? `${subPct.toFixed(0)}%` : "—"}
                    </Text>
                  </View>
                </View>
              );
            })}
          </View>
        )}

        {/* Report Cards List */}
        {reportCards.length > 0 && (
          <>
            <View style={styles.listHeader}>
              <Text style={styles.sectionTitle}>All Report Cards</Text>
              <Badge label={`${reportCards.length} total`} color="blue" />
            </View>

            {reportCards.map((rc: any) => {
              const pct = Number(rc.percentage);
              const color = scoreColor(pct);
              const bg = scoreBg(pct);
              return (
                <TouchableOpacity
                  key={rc.id}
                  style={styles.cardRow}
                  onPress={() => openDetail(rc)}
                  activeOpacity={0.7}
                >
                  <View style={styles.cardLeft}>
                    <Text style={styles.cardExam}>{rc.exam_name}</Text>
                    <Text style={styles.cardYear}>{rc.academic_year_name}</Text>
                    <View style={styles.cardMetaRow}>
                      <Text style={styles.cardMeta}>
                        {rc.obtained_marks}/{rc.total_marks} marks
                      </Text>
                      {rc.gpa && (
                        <Text style={styles.cardMetaGpa}>GPA {Number(rc.gpa).toFixed(2)}</Text>
                      )}
                    </View>
                  </View>
                  <View style={styles.cardRight}>
                    <View style={[styles.cardScoreBadge, { backgroundColor: bg }]}>
                      <Text style={[styles.cardScore, { color }]}>{pct.toFixed(1)}%</Text>
                      <Text style={styles.cardGrade}>{rc.grade_letter}</Text>
                    </View>
                    {rc.rank_in_class && <Text style={styles.cardRank}>#{rc.rank_in_class}</Text>}
                    <Badge
                      label={rc.status}
                      color={rc.status === "published" ? "green" : "slate"}
                    />
                  </View>
                </TouchableOpacity>
              );
            })}
          </>
        )}
      </ScrollView>

      {/* Detail Modal */}
      {detailTarget && (
        <ReportCardDetailModal
          reportCard={detailTarget}
          subjectData={subjectDataForDetail}
          onClose={() => setDetailTarget(null)}
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  content: { padding: 16, paddingBottom: 60 },
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b" },
  sub: { fontSize: 13, color: "#64748b", marginTop: 4, marginBottom: 16 },

  // ── Hero Card ───────────────────────────────────────────────────────────
  heroCard: {
    borderRadius: 18,
    padding: 20,
    marginBottom: 16,
  },
  heroTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: 16,
  },
  heroLeft: { flex: 1 },
  heroLabel: { fontSize: 12, color: "#c7d2fe" },
  heroExamName: { fontSize: 18, fontWeight: "800", color: "#fff", marginTop: 2 },
  heroGpa: {
    backgroundColor: "rgba(255,255,255,0.15)",
    borderRadius: 12,
    paddingHorizontal: 14,
    paddingVertical: 8,
    alignItems: "center",
  },
  heroGpaLbl: { fontSize: 10, color: "#c7d2fe" },
  heroGpaVal: { fontSize: 20, fontWeight: "800", color: "#fff", marginTop: 1 },
  heroGpaSub: { fontSize: 9, color: "#c7d2fe", marginTop: 1 },
  heroStats: { flexDirection: "row", gap: 16 },
  heroStatItem: { alignItems: "center", flex: 1 },
  heroStatVal: { fontSize: 22, fontWeight: "800", color: "#fff" },
  heroStatLbl: { fontSize: 10, color: "#c7d2fe", marginTop: 2 },

  // ── Empty State ─────────────────────────────────────────────────────────
  emptyCard: { alignItems: "center", padding: 30, marginBottom: 16 },
  emptyEmoji: { fontSize: 40, marginBottom: 8 },
  emptyTitle: { fontSize: 16, fontWeight: "600", color: "#64748b" },
  emptySub: { fontSize: 13, color: "#94a3b8", marginTop: 4, textAlign: "center" },

  // ── Stats ───────────────────────────────────────────────────────────────
  statsRow: {
    flexDirection: "row",
    gap: 6,
    marginBottom: 20,
  },
  statPill: {
    flex: 1,
    backgroundColor: "#fff",
    borderRadius: 12,
    paddingVertical: 10,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#f1f5f9",
  },
  statVal: { fontSize: 16, fontWeight: "800" },
  statLbl: { fontSize: 9, color: "#94a3b8", marginTop: 2 },

  // ── Sections ────────────────────────────────────────────────────────────
  section: { marginBottom: 20 },
  sectionTitle: {
    fontSize: 15,
    fontWeight: "700",
    color: "#1e293b",
    marginBottom: 12,
  },

  // ── Subject breakdown ───────────────────────────────────────────────────
  subjRow: {
    marginBottom: 10,
  },
  subjInfo: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 4,
  },
  subjName: { fontSize: 13, fontWeight: "600", color: "#374151", flex: 1 },
  subjMarks: { fontSize: 11, color: "#64748b" },
  subjBarContainer: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
  },
  subjBarBg: {
    flex: 1,
    height: 8,
    backgroundColor: "#f1f5f9",
    borderRadius: 4,
    overflow: "hidden",
  },
  subjBarFill: { height: "100%", borderRadius: 4 },
  subjPct: { fontSize: 11, fontWeight: "700", width: 40, textAlign: "right" },

  // ── Report Card List ────────────────────────────────────────────────────
  listHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
  },
  cardRow: {
    flexDirection: "row",
    backgroundColor: "#fff",
    borderRadius: 14,
    padding: 14,
    marginBottom: 8,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  cardLeft: { flex: 1, marginRight: 10 },
  cardExam: { fontSize: 14, fontWeight: "700", color: "#1e293b" },
  cardYear: { fontSize: 11, color: "#64748b", marginTop: 2 },
  cardMetaRow: { flexDirection: "row", gap: 12, marginTop: 4 },
  cardMeta: { fontSize: 11, color: "#94a3b8" },
  cardMetaGpa: { fontSize: 11, color: BRAND, fontWeight: "600" },
  cardRight: { alignItems: "flex-end", gap: 4 },
  cardScoreBadge: {
    borderRadius: 10,
    paddingHorizontal: 10,
    paddingVertical: 4,
    alignItems: "center",
    minWidth: 60,
  },
  cardScore: { fontSize: 14, fontWeight: "800" },
  cardGrade: { fontSize: 9, color: "#64748b", marginTop: 1 },
  cardRank: { fontSize: 11, fontWeight: "600", color: "#64748b" },

  // ── Detail Modal ────────────────────────────────────────────────────────
  modalOverlay: {
    flex: 1,
    backgroundColor: "rgba(0,0,0,0.4)",
    justifyContent: "flex-end",
  },
  modal: {
    backgroundColor: "#f8fafc",
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    padding: 20,
    paddingBottom: Platform.OS === "ios" ? 40 : 20,
    maxHeight: "90%",
  },
  modalHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 16,
  },
  modalTitle: { fontSize: 18, fontWeight: "700", color: "#1e293b" },
  modalClose: { fontSize: 20, color: "#94a3b8", padding: 4 },

  detailHero: {
    borderRadius: 16,
    padding: 18,
    marginBottom: 16,
    alignItems: "center",
  },
  detailExamName: { fontSize: 17, fontWeight: "800", color: "#fff" },
  detailYear: { fontSize: 11, color: "#c7d2fe", marginTop: 2 },
  detailHeroStats: {
    flexDirection: "row",
    gap: 20,
    marginTop: 14,
  },
  detailHeroStat: { alignItems: "center" },
  detailHeroVal: { fontSize: 24, fontWeight: "800", color: "#fff" },
  detailHeroLbl: { fontSize: 10, color: "#c7d2fe", marginTop: 2 },
  detailGpaBadge: {
    flexDirection: "row",
    alignItems: "center",
    gap: 6,
    backgroundColor: "rgba(255,255,255,0.2)",
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 6,
    marginTop: 12,
  },
  detailGpaLbl: { fontSize: 11, color: "#c7d2fe" },
  detailGpaVal: { fontSize: 16, fontWeight: "800", color: "#fff" },

  marksSummary: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginBottom: 16,
    backgroundColor: "#fff",
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  marksCard: { alignItems: "center", minWidth: 60 },
  marksLbl: { fontSize: 10, color: "#94a3b8" },
  marksVal: { fontSize: 16, fontWeight: "700", color: "#1e293b", marginTop: 2 },

  remarksBox: {
    backgroundColor: "#fff",
    borderRadius: 14,
    padding: 14,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  remarksLabel: { fontSize: 11, fontWeight: "600", color: "#64748b", marginBottom: 6 },
  remarksContent: { fontSize: 13, color: "#475569", lineHeight: 20 },

  pdfBtn: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
    backgroundColor: BRAND,
    borderRadius: 12,
    paddingVertical: 14,
    marginBottom: 8,
  },
  pdfBtnIcon: { fontSize: 18 },
  pdfBtnTxt: { fontSize: 14, fontWeight: "700", color: "#fff" },

  modalDoneBtn: {
    marginTop: 12,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    paddingVertical: 12,
    alignItems: "center",
    backgroundColor: "#fff",
  },
  modalDoneBtnTxt: { fontSize: 14, fontWeight: "600", color: "#64748b" },
});
