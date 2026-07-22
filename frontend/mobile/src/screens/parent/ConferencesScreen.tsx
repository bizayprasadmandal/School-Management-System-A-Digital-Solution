/**
 * Parent ConferencesScreen — Book conference slots for your children
 * and join Zoom meetings for booked slots.
 */

import React, { useState } from "react";
import {
  View, Text, TextInput, ScrollView, StyleSheet, TouchableOpacity,
  Linking, RefreshControl, Alert,
} from "react-native";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import dayjs from "dayjs";
import { mobileApi } from "../../api/client";
import { SkeletonList, EmptyState } from "../../components";

const BRAND = "#7c3aed";

type TabId = "available" | "booked";

export default function ParentConferencesScreen() {
  const [date, setDate] = useState(dayjs().format("YYYY-MM-DD"));
  const [activeTab, setActiveTab] = useState<TabId>("available");
  const [selectedChild, setSelectedChild] = useState<string>("");
  const qc = useQueryClient();

  // Children list
  const { data: childrenData } = useQuery({
    queryKey: ["mob-par-conf-children"],
    queryFn: () => mobileApi.get<{ results: any[] }>("/students/"),
  });
  const children = childrenData?.results ?? [];

  // Available slots
  const { data: availData, isLoading: availLoading, refetch: refetchAvail } = useQuery({
    queryKey: ["mob-par-conf-avail", date],
    queryFn: () =>
      mobileApi.get<{ results: any[] }>("/conferences/conference-slots/", { date }),
    select: (data) => (data.results ?? []).filter((s: any) => !s.is_booked),
  });

  // Booked slots
  const { data: bookedData, isLoading: bookedLoading, refetch: refetchBooked } = useQuery({
    queryKey: ["mob-par-conf-booked"],
    queryFn: () =>
      mobileApi.get<{ results: any[] }>("/conferences/conference-slots/", { is_booked: true }),
    select: (data) => data.results ?? [],
  });

  const bookMut = useMutation({
    mutationFn: (slotId: string) =>
      mobileApi.post(`/conferences/conference-slots/${slotId}/book/`, {
        student_id: selectedChild,
      }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["mob-par-conf-avail"] });
      qc.invalidateQueries({ queryKey: ["mob-par-conf-booked"] });
      Alert.alert("Booked!", "Conference slot has been booked successfully.");
    },
    onError: (e: any) =>
      Alert.alert("Error", e?.response?.data?.detail ?? "Failed to book slot"),
  });

  const availableSlots = availData ?? [];
  const bookedSlots = bookedData ?? [];

  const handleJoinZoom = (url: string) => {
    Linking.canOpenURL(url).then(() => Linking.openURL(url));
  };

  const tabs: { id: TabId; label: string; count: number }[] = [
    { id: "available", label: "Available", count: availableSlots.length },
    { id: "booked", label: "My Booked", count: bookedSlots.length },
  ];

  const isLoading = activeTab === "available" ? availLoading : bookedLoading;

  return (
    <ScrollView
      style={styles.root}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl
          refreshing={isLoading}
          onRefresh={activeTab === "available" ? refetchAvail : refetchBooked}
          tintColor={BRAND}
        />
      }
    >
      <Text style={styles.heading}>Conference Scheduler</Text>
      <Text style={styles.sub}>
        {activeTab === "available"
          ? "Book parent-teacher conferences for your children"
          : "View your booked conferences and join Zoom meetings"}
      </Text>

      {/* Date + Child filters */}
      <View style={styles.filters}>
        <TextInput
          value={date}
          onChangeText={setDate}
          style={styles.input}
          placeholderTextColor="#94a3b8"
        />
        {activeTab === "available" && children.length > 0 && (
          <View style={styles.childPicker}>
            <Text style={styles.childLabel}>Child</Text>
            <View style={styles.chipRow}>
              <TouchableOpacity
                style={[styles.chip, !selectedChild && styles.chipActive]}
                onPress={() => setSelectedChild("")}
              >
                <Text style={[styles.chipTxt, !selectedChild && styles.chipTxtActive]}>
                  All
                </Text>
              </TouchableOpacity>
              {children.map((c: any) => (
                <TouchableOpacity
                  key={c.id}
                  style={[styles.chip, selectedChild === c.id && styles.chipActive]}
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
      </View>

      {/* Tabs */}
      <View style={styles.tabRow}>
        {tabs.map((tab) => (
          <TouchableOpacity
            key={tab.id}
            style={[styles.tab, activeTab === tab.id && styles.tabActive]}
            onPress={() => setActiveTab(tab.id)}
          >
            <Text
              style={[styles.tabTxt, activeTab === tab.id && styles.tabTxtActive]}
            >
              {tab.label} ({tab.count})
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      {/* Available Slots */}
      {activeTab === "available" && (
        <>
          {availLoading ? (
            <SkeletonList />
          ) : availableSlots.length === 0 ? (
            <EmptyState
              icon="📅"
              title="No available slots"
              sub="No conference slots available for this date. Try another date."
            />
          ) : (
            <View style={styles.list}>
              {availableSlots.map((slot: any) => (
                <View key={slot.id} style={styles.card}>
                  <View style={styles.cardMain}>
                    <View style={styles.timeCol}>
                      <Text style={styles.timeStart}>
                        {slot.start_time?.slice(0, 5)}
                      </Text>
                      <Text style={styles.timeEnd}>
                        —{slot.end_time?.slice(0, 5)}
                      </Text>
                    </View>
                    <View style={styles.infoCol}>
                      <Text style={styles.teacherName}>{slot.teacher_name}</Text>
                      {slot.notes && (
                        <Text style={styles.notes} numberOfLines={2}>
                          {slot.notes}
                        </Text>
                      )}
                    </View>
                  </View>
                  <TouchableOpacity
                    style={[
                      styles.bookBtn,
                      !selectedChild && styles.bookBtnDisabled,
                    ]}
                    onPress={() => bookMut.mutate(slot.id)}
                    disabled={!selectedChild}
                  >
                    <Text
                      style={[
                        styles.bookBtnTxt,
                        !selectedChild && styles.bookBtnTxtDisabled,
                      ]}
                    >
                      Book
                    </Text>
                  </TouchableOpacity>
                </View>
              ))}
              {!selectedChild && availableSlots.length > 0 && (
                <Text style={styles.hint}>Select a child above to enable booking</Text>
              )}
            </View>
          )}
        </>
      )}

      {/* Booked Slots with Zoom */}
      {activeTab === "booked" && (
        <>
          {bookedLoading ? (
            <SkeletonList />
          ) : bookedSlots.length === 0 ? (
            <EmptyState
              icon="📅"
              title="No booked slots"
              sub="You haven't booked any conference slots yet. Switch to Available to book one."
            />
          ) : (
            <View style={styles.list}>
              {bookedSlots.map((slot: any) => (
                <View key={slot.id} style={[styles.card, styles.cardBooked]}>
                  <View style={styles.cardMain}>
                    <View style={styles.timeCol}>
                      <Text style={styles.timeStart}>
                        {slot.start_time?.slice(0, 5)}
                      </Text>
                      <Text style={styles.timeEnd}>
                        —{slot.end_time?.slice(0, 5)}
                      </Text>
                    </View>
                    <View style={styles.infoCol}>
                      <Text style={styles.teacherName}>{slot.teacher_name}</Text>
                      <Text style={styles.studentName}>
                        {slot.student_name ?? "Student"}
                      </Text>
                      {slot.notes && (
                        <Text style={styles.notes} numberOfLines={2}>
                          {slot.notes}
                        </Text>
                      )}
                      {slot.is_zoom_created && (
                        <View style={styles.zoomBadge}>
                          <Text style={styles.zoomBadgeTxt}>🔗 Zoom ready</Text>
                        </View>
                      )}
                    </View>
                  </View>

                  {slot.is_zoom_created && slot.zoom_join_url ? (
                    <TouchableOpacity
                      style={styles.joinBtn}
                      onPress={() => handleJoinZoom(slot.zoom_join_url)}
                      activeOpacity={0.8}
                    >
                      <Text style={styles.joinBtnTxt}>🎥 Join Meeting</Text>
                    </TouchableOpacity>
                  ) : slot.is_booked && !slot.is_zoom_created ? (
                    <Text style={styles.pending}>Zoom link pending</Text>
                  ) : null}

                  {slot.is_zoom_created && slot.zoom_meeting_id && (
                    <View style={styles.zoomDetails}>
                      <Text style={styles.zoomId}>
                        ID:{" "}
                        <Text style={styles.zoomIdValue}>
                          {slot.zoom_meeting_id}
                        </Text>
                      </Text>
                      {slot.zoom_password && (
                        <Text style={styles.zoomPwd}>
                          Pass:{" "}
                          <Text style={styles.zoomPwdValue}>
                            {slot.zoom_password}
                          </Text>
                        </Text>
                      )}
                      <Text style={styles.zoomDate}>{slot.date}</Text>
                    </View>
                  )}
                </View>
              ))}
            </View>
          )}
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 40 },
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b" },
  sub: { fontSize: 13, color: "#64748b", marginTop: 4, marginBottom: 16 },
  filters: { gap: 10, marginBottom: 16 },
  input: {
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 14,
    color: "#1e293b",
    backgroundColor: "#fff",
  },
  childPicker: {},
  childLabel: { fontSize: 12, fontWeight: "600", color: "#374151", marginBottom: 6 },
  chipRow: { flexDirection: "row", flexWrap: "wrap", gap: 6 },
  chip: {
    borderRadius: 16,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    paddingHorizontal: 12,
    paddingVertical: 5,
    backgroundColor: "#fff",
  },
  chipActive: { backgroundColor: BRAND, borderColor: BRAND },
  chipTxt: { fontSize: 12, fontWeight: "600", color: "#64748b" },
  chipTxtActive: { color: "#fff" },
  tabRow: { flexDirection: "row", gap: 8, marginBottom: 16 },
  tab: {
    flex: 1,
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: "center",
    backgroundColor: "#fff",
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  tabActive: { backgroundColor: BRAND, borderColor: BRAND },
  tabTxt: { fontSize: 13, fontWeight: "600", color: "#64748b" },
  tabTxtActive: { color: "#fff" },
  list: { gap: 10 },
  card: {
    backgroundColor: "#fff",
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  cardBooked: { borderColor: "#ddd6fe", backgroundColor: "#f5f3ff" },
  cardMain: { flexDirection: "row", gap: 12 },
  timeCol: { alignItems: "center", width: 56 },
  timeStart: { fontSize: 16, fontWeight: "700", color: BRAND },
  timeEnd: { fontSize: 11, color: "#94a3b8", marginTop: 2 },
  infoCol: { flex: 1 },
  teacherName: { fontSize: 15, fontWeight: "700", color: "#1e293b" },
  studentName: { fontSize: 12, fontWeight: "600", color: BRAND, marginTop: 2 },
  notes: { fontSize: 12, color: "#64748b", marginTop: 4, lineHeight: 16 },
  zoomBadge: {
    marginTop: 6,
    alignSelf: "flex-start",
    backgroundColor: "#dcfce7",
    borderRadius: 6,
    paddingHorizontal: 8,
    paddingVertical: 3,
  },
  zoomBadgeTxt: { fontSize: 11, fontWeight: "600", color: "#15803d" },
  bookBtn: {
    marginTop: 10,
    backgroundColor: BRAND,
    borderRadius: 8,
    paddingVertical: 8,
    alignItems: "center",
  },
  bookBtnDisabled: { backgroundColor: "#e2e8f0" },
  bookBtnTxt: { fontSize: 13, fontWeight: "700", color: "#fff" },
  bookBtnTxtDisabled: { color: "#94a3b8" },
  joinBtn: {
    marginTop: 10,
    backgroundColor: BRAND,
    borderRadius: 8,
    paddingVertical: 8,
    alignItems: "center",
  },
  joinBtnTxt: { fontSize: 13, fontWeight: "700", color: "#fff" },
  pending: {
    marginTop: 10,
    fontSize: 12,
    color: "#94a3b8",
    fontStyle: "italic",
    textAlign: "center",
  },
  zoomDetails: {
    marginTop: 8,
    paddingTop: 8,
    borderTopWidth: 1,
    borderTopColor: "#f1f5f9",
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 12,
  },
  zoomId: { fontSize: 11, color: "#64748b" },
  zoomIdValue: { fontFamily: "monospace", color: "#334155", fontWeight: "600" },
  zoomPwd: { fontSize: 11, color: "#64748b" },
  zoomPwdValue: { fontFamily: "monospace", color: "#334155", fontWeight: "600" },
  zoomDate: { fontSize: 11, color: "#94a3b8" },
  hint: { fontSize: 12, color: "#a16207", fontStyle: "italic", textAlign: "center", marginTop: 4 },
});
