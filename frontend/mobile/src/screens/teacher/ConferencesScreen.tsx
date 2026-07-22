/**
 * Teacher ConferencesScreen — Manage your conference slots,
 * create/cancel/complete bookings, and create Zoom meetings.
 */

import React, { useState } from "react";
import {
  View, Text, TextInput, ScrollView, StyleSheet, TouchableOpacity,
  Alert, RefreshControl, Modal, Platform,
} from "react-native";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import dayjs from "dayjs";
import { mobileApi } from "../../api/client";
import { SkeletonList, EmptyState, Button } from "../../components";

const BRAND = "#059669";

export default function TeacherConferencesScreen() {
  const [date, setDate] = useState(dayjs().format("YYYY-MM-DD"));
  const [showForm, setShowForm] = useState(false);
  const [newSlot, setNewSlot] = useState({ start_time: "09:00", end_time: "09:30", notes: "" });
  const qc = useQueryClient();

  const { data: slotsData, isLoading, refetch } = useQuery({
    queryKey: ["mob-teacher-conf", date],
    queryFn: () =>
      mobileApi.get<{ results: any[] }>("/conferences/conference-slots/", { date }),
  });

  const slots = slotsData?.results ?? [];

  const createMut = useMutation({
    mutationFn: (data: { date: string; start_time: string; end_time: string; notes: string }) =>
      mobileApi.post("/conferences/conference-slots/", data),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["mob-teacher-conf"] });
      setShowForm(false);
      setNewSlot({ start_time: "09:00", end_time: "09:30", notes: "" });
    },
    onError: (e: any) => Alert.alert("Error", e?.response?.data?.detail ?? "Failed to create slot"),
  });

  const cancelMut = useMutation({
    mutationFn: (id: string) => mobileApi.post(`/conferences/conference-slots/${id}/cancel/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["mob-teacher-conf"] }),
  });

  const completeMut = useMutation({
    mutationFn: (id: string) => mobileApi.post(`/conferences/conference-slots/${id}/complete/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["mob-teacher-conf"] }),
  });

  const createZoomMut = useMutation({
    mutationFn: (slotId: string) =>
      mobileApi.post(`/conferences/conference-slots/${slotId}/create-zoom/`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["mob-teacher-conf"] }),
    onError: (e: any) => Alert.alert("Zoom Error", e?.response?.data?.detail ?? "Failed"),
  });

  if (isLoading) return <SkeletonList />;

  return (
    <View style={{ flex: 1, backgroundColor: "#f8fafc" }}>
      <ScrollView contentContainerStyle={styles.content}
        refreshControl={<RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor={BRAND} />}
      >
        <View style={styles.header}>
          <View style={{ flex: 1 }}>
            <Text style={styles.heading}>My Slots</Text>
            <Text style={styles.sub}>Manage your parent-teacher conference availability</Text>
          </View>
          <TouchableOpacity style={styles.addBtn} onPress={() => setShowForm(true)} activeOpacity={0.8}>
            <Text style={styles.addBtnTxt}>+ Add Slot</Text>
          </TouchableOpacity>
        </View>

        {/* Date */}
        <View style={styles.dateRow}>
          <Text style={styles.dateLabel}>Date</Text>
          <TextInput
            value={date}
            onChangeText={setDate}
            style={styles.dateInput}
            placeholderTextColor="#94a3b8"
          />
        </View>

        {slots.length === 0 ? (
          <EmptyState icon="📅" title="No slots" sub="Create your first conference slot for this date" />
        ) : (
          <View style={styles.list}>
            {slots.map((slot: any) => (
              <View key={slot.id}
                style={[styles.card, slot.is_booked && styles.cardBooked]}
              >
                <View style={styles.cardMain}>
                  <View style={styles.timeCol}>
                    <Text style={styles.timeStart}>{slot.start_time?.slice(0, 5)}</Text>
                    <Text style={styles.timeEnd}>—{slot.end_time?.slice(0, 5)}</Text>
                  </View>
                  <View style={styles.infoCol}>
                    {slot.is_booked ? (
                      <>
                        <Text style={styles.bookedName}>Booked — {slot.student_name}</Text>
                        {slot.notes && <Text style={styles.notes}>{slot.notes}</Text>}
                      </>
                    ) : (
                      <>
                        <Text style={styles.availableTxt}>Available</Text>
                        {slot.notes && <Text style={styles.notes}>{slot.notes}</Text>}
                      </>
                    )}
                    {slot.is_zoom_created && (
                      <View style={styles.zoomBadge}>
                        <Text style={styles.zoomBadgeTxt}>🎥 Zoom ready</Text>
                      </View>
                    )}
                  </View>
                </View>

                {/* Action buttons */}
                <View style={styles.actions}>
                  {slot.is_booked ? (
                    <>
                      {slot.is_zoom_created && slot.zoom_join_url ? (
                        <TouchableOpacity
                          style={styles.joinBtn}
                          onPress={() => Linking.openURL(slot.zoom_join_url)}
                        >
                          <Text style={styles.actionTxt}>Join</Text>
                        </TouchableOpacity>
                      ) : (
                        <TouchableOpacity
                          style={styles.zoomBtn}
                          onPress={() => createZoomMut.mutate(slot.id)}
                        >
                          <Text style={styles.actionTxt}>🔗 Zoom</Text>
                        </TouchableOpacity>
                      )}
                      <TouchableOpacity
                        style={styles.completeBtn}
                        onPress={() => completeMut.mutate(slot.id)}
                      >
                        <Text style={styles.actionTxt}>✓ Done</Text>
                      </TouchableOpacity>
                      <TouchableOpacity
                        style={styles.cancelBtn}
                        onPress={() => cancelMut.mutate(slot.id)}
                      >
                        <Text style={styles.cancelTxt}>✕</Text>
                      </TouchableOpacity>
                    </>
                  ) : (
                    <TouchableOpacity
                      style={styles.removeBtn}
                      onPress={() => {
                        Alert.alert("Remove Slot", "Remove this available slot?", [
                          { text: "Cancel", style: "cancel" },
                          { text: "Remove", style: "destructive", onPress: () => cancelMut.mutate(slot.id) },
                        ]);
                      }}
                    >
                      <Text style={styles.cancelTxt}>Remove</Text>
                    </TouchableOpacity>
                  )}
                </View>

                {/* Zoom details */}
                {slot.is_zoom_created && slot.zoom_meeting_id && (
                  <View style={styles.zoomDetails}>
                    <Text style={styles.zoomId}>ID: {slot.zoom_meeting_id}</Text>
                    {slot.zoom_password && (
                      <Text style={styles.zoomPwd}>Pass: {slot.zoom_password}</Text>
                    )}
                  </View>
                )}
              </View>
            ))}
          </View>
        )}
      </ScrollView>

      {/* Create Slot Modal */}
      <Modal visible={showForm} transparent animationType="slide" onRequestClose={() => setShowForm(false)}>
        <View style={styles.modalOverlay}>
          <View style={styles.modal}>
            <Text style={styles.modalTitle}>Create Conference Slot</Text>

            <Text style={styles.label}>Date</Text>
            <TextInput value={date} editable={false} style={[styles.input, styles.inputDisabled]} />

            <View style={styles.timeRow}>
              <View style={{ flex: 1 }}>
                <Text style={styles.label}>Start</Text>
                <TextInput
                  value={newSlot.start_time}
                  onChangeText={v => setNewSlot(p => ({ ...p, start_time: v }))}
                  style={styles.input}
                  placeholder="09:00"
                />
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.label}>End</Text>
                <TextInput
                  value={newSlot.end_time}
                  onChangeText={v => setNewSlot(p => ({ ...p, end_time: v }))}
                  style={styles.input}
                  placeholder="09:30"
                />
              </View>
            </View>

            <Text style={styles.label}>Notes (optional)</Text>
            <TextInput
              value={newSlot.notes}
              onChangeText={v => setNewSlot(p => ({ ...p, notes: v }) ) }
              style={[styles.input, { minHeight: 60 }]}
              multiline
              placeholder="Any notes..."
            />

            <View style={styles.modalActions}>
              <TouchableOpacity style={styles.modalCancel} onPress={() => setShowForm(false)}>
                <Text style={styles.modalCancelTxt}>Cancel</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={styles.modalConfirm}
                onPress={() => createMut.mutate({ date, ...newSlot })}
              >
                <Text style={styles.modalConfirmTxt}>Create Slot</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  content: { padding: 16, paddingBottom: 40 },
  header: { flexDirection: "row", alignItems: "flex-start", marginBottom: 16 },
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b" },
  sub: { fontSize: 13, color: "#64748b", marginTop: 4 },
  addBtn: {
    backgroundColor: BRAND,
    borderRadius: 10,
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  addBtnTxt: { fontSize: 13, fontWeight: "700", color: "#fff" },
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
  list: { gap: 10 },
  card: {
    backgroundColor: "#fff",
    borderRadius: 14,
    padding: 14,
    borderWidth: 1,
    borderColor: "#e2e8f0",
  },
  cardBooked: { borderColor: "#a7f3d0", backgroundColor: "#f0fdf4" },
  cardMain: { flexDirection: "row", gap: 12 },
  timeCol: { alignItems: "center", width: 56 },
  timeStart: { fontSize: 16, fontWeight: "700", color: BRAND },
  timeEnd: { fontSize: 11, color: "#94a3b8", marginTop: 2 },
  infoCol: { flex: 1 },
  bookedName: { fontSize: 14, fontWeight: "600", color: "#065f46" },
  availableTxt: { fontSize: 14, fontWeight: "600", color: BRAND },
  notes: { fontSize: 12, color: "#64748b", marginTop: 4 },
  zoomBadge: { marginTop: 6, alignSelf: "flex-start", backgroundColor: "#dcfce7", borderRadius: 6, paddingHorizontal: 8, paddingVertical: 3 },
  zoomBadgeTxt: { fontSize: 11, fontWeight: "600", color: "#15803d" },
  actions: { flexDirection: "row", gap: 8, marginTop: 10, flexWrap: "wrap" },
  joinBtn: { backgroundColor: BRAND, borderRadius: 8, paddingHorizontal: 12, paddingVertical: 6 },
  zoomBtn: { backgroundColor: "#dbeafe", borderRadius: 8, paddingHorizontal: 12, paddingVertical: 6 },
  completeBtn: { backgroundColor: "#dcfce7", borderRadius: 8, paddingHorizontal: 12, paddingVertical: 6 },
  cancelBtn: { borderRadius: 8, paddingHorizontal: 10, paddingVertical: 6, borderWidth: 1, borderColor: "#fecaca" },
  removeBtn: { borderRadius: 8, paddingHorizontal: 12, paddingVertical: 6, borderWidth: 1, borderColor: "#fecaca" },
  actionTxt: { fontSize: 12, fontWeight: "700", color: "#1e293b" },
  cancelTxt: { fontSize: 12, fontWeight: "600", color: "#dc2626" },
  zoomDetails: { marginTop: 8, paddingTop: 8, borderTopWidth: 1, borderTopColor: "#f1f5f9", flexDirection: "row", gap: 16 },
  zoomId: { fontSize: 11, color: "#64748b" },
  zoomPwd: { fontSize: 11, color: "#64748b" },
  modalOverlay: { flex: 1, backgroundColor: "rgba(0,0,0,0.4)", justifyContent: "flex-end" },
  modal: { backgroundColor: "#fff", borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 24, paddingBottom: Platform.OS === "ios" ? 40 : 24 },
  modalTitle: { fontSize: 18, fontWeight: "700", color: "#1e293b", marginBottom: 20 },
  label: { fontSize: 12, fontWeight: "600", color: "#374151", marginBottom: 6 },
  input: { borderWidth: 1, borderColor: "#e2e8f0", borderRadius: 10, paddingHorizontal: 12, paddingVertical: 10, fontSize: 14, color: "#1e293b", marginBottom: 14, backgroundColor: "#fff" },
  inputDisabled: { backgroundColor: "#f8fafc", color: "#94a3b8" },
  timeRow: { flexDirection: "row", gap: 12 },
  modalActions: { flexDirection: "row", gap: 12, marginTop: 8 },
  modalCancel: { flex: 1, borderRadius: 10, borderWidth: 1, borderColor: "#e2e8f0", paddingVertical: 12, alignItems: "center" },
  modalCancelTxt: { fontSize: 14, fontWeight: "600", color: "#64748b" },
  modalConfirm: { flex: 1, backgroundColor: BRAND, borderRadius: 10, paddingVertical: 12, alignItems: "center" },
  modalConfirmTxt: { fontSize: 14, fontWeight: "700", color: "#fff" },
});
