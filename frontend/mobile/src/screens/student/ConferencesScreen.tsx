/**
 * Student ConferencesScreen — View booked parent-teacher conference slots
 * and join Zoom meetings.
 */

import React, { useState } from "react";
import {
  View, Text, TextInput, ScrollView, StyleSheet, TouchableOpacity,
  Linking, RefreshControl,
} from "react-native";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { mobileApi } from "../../api/client";
import { SkeletonList, EmptyState } from "../../components";

const BRAND = "#6366f1";

export default function StudentConferencesScreen() {
  const [date, setDate] = useState(dayjs().format("YYYY-MM-DD"));

  const { data: slotsData, isLoading, refetch } = useQuery({
    queryKey: ["mob-student-conf", date],
    queryFn: () =>
      mobileApi.get<{ results: any[] }>("/conferences/conference-slots/", {
        date,
        is_booked: true,
      }),
  });

  const slots = slotsData?.results ?? [];

  const handleJoinZoom = (url: string) => {
    Linking.canOpenURL(url).then(() => Linking.openURL(url));
  };

  if (isLoading) return <SkeletonList />;

  return (
    <ScrollView
      style={styles.root}
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor={BRAND} />
      }
    >
      <Text style={styles.heading}>My Conferences</Text>
      <Text style={styles.sub}>View your booked parent-teacher conferences</Text>

      {/* Date picker */}
      <View style={styles.dateRow}>
        <Text style={styles.dateLabel}>Date</Text>
        <TextInput
          value={date}
          onChangeText={setDate}
          placeholder="YYYY-MM-DD"
          style={styles.dateInput}
          placeholderTextColor="#94a3b8"
        />
        <Text style={styles.count}>{slots.length} slot{slots.length !== 1 ? "s" : ""}</Text>
      </View>

      {slots.length === 0 ? (
        <EmptyState
          icon="📅"
          title="No conferences booked"
          sub="You don't have any parent-teacher conferences scheduled for this date."
        />
      ) : (
        <View style={styles.list}>
          {slots.map((slot: any) => (
            <View key={slot.id} style={styles.card}>
              {/* Time + Teacher */}
              <View style={styles.cardMain}>
                <View style={styles.timeCol}>
                  <Text style={styles.timeStart}>{slot.start_time?.slice(0, 5)}</Text>
                  <Text style={styles.timeEnd}>—{slot.end_time?.slice(0, 5)}</Text>
                </View>
                <View style={styles.infoCol}>
                  <Text style={styles.teacherName}>{slot.teacher_name}</Text>
                  {slot.notes && (
                    <Text style={styles.notes} numberOfLines={2}>{slot.notes}</Text>
                  )}
                  {slot.is_zoom_created && (
                    <View style={styles.zoomBadge}>
                      <Text style={styles.zoomBadgeTxt}>🔗 Zoom ready</Text>
                    </View>
                  )}
                </View>
              </View>

              {/* Zoom join button */}
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

              {/* Zoom meeting details */}
              {slot.is_zoom_created && slot.zoom_meeting_id && (
                <View style={styles.zoomDetails}>
                  <Text style={styles.zoomId}>
                    ID: <Text style={styles.zoomIdValue}>{slot.zoom_meeting_id}</Text>
                  </Text>
                  {slot.zoom_password && (
                    <Text style={styles.zoomPwd}>
                      Pass: <Text style={styles.zoomPwdValue}>{slot.zoom_password}</Text>
                    </Text>
                  )}
                </View>
              )}
            </View>
          ))}
        </View>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 40 },
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b" },
  sub: { fontSize: 13, color: "#64748b", marginTop: 4, marginBottom: 16 },
  dateRow: { flexDirection: "row", alignItems: "center", gap: 10, marginBottom: 16 },
  dateLabel: { fontSize: 13, fontWeight: "600", color: "#374151" },
  dateInput: {
    flex: 1,
    borderWidth: 1,
    borderColor: "#e2e8f0",
    borderRadius: 10,
    paddingHorizontal: 12,
    paddingVertical: 8,
    fontSize: 14,
    color: "#1e293b",
    backgroundColor: "#fff",
  },
  count: { fontSize: 12, color: "#64748b" },
  list: { gap: 10 },
  card: {
    backgroundColor: "#fff",
    borderRadius: 14,
    padding: 16,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  cardMain: { flexDirection: "row", gap: 14 },
  timeCol: { alignItems: "center", width: 60 },
  timeStart: { fontSize: 16, fontWeight: "700", color: BRAND },
  timeEnd: { fontSize: 11, color: "#94a3b8", marginTop: 2 },
  infoCol: { flex: 1 },
  teacherName: { fontSize: 15, fontWeight: "700", color: "#1e293b" },
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
  joinBtn: {
    marginTop: 12,
    backgroundColor: BRAND,
    borderRadius: 10,
    paddingVertical: 10,
    alignItems: "center",
  },
  joinBtnTxt: { fontSize: 14, fontWeight: "700", color: "#fff" },
  pending: {
    marginTop: 12,
    fontSize: 12,
    color: "#94a3b8",
    fontStyle: "italic",
    textAlign: "center",
  },
  zoomDetails: {
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderTopColor: "#f1f5f9",
    flexDirection: "row",
    gap: 16,
  },
  zoomId: { fontSize: 11, color: "#64748b" },
  zoomIdValue: { fontFamily: "monospace", color: "#334155", fontWeight: "600" },
  zoomPwd: { fontSize: 11, color: "#64748b" },
  zoomPwdValue: { fontFamily: "monospace", color: "#334155", fontWeight: "600" },
});
