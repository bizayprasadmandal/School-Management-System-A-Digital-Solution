import React, { useState } from "react";
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, Alert, Switch } from "react-native";
import { useAuthStore } from "../../hooks/useAuthStore";
import { mobileApi } from "../../api/client";
import { Card, Button, Divider } from "../../components";

const ROLE_LABELS: Record<string, string> = { school_admin: "Administrator", teacher: "Teacher", student: "Student", parent: "Parent", super_admin: "Super Admin" };

export default function ProfileScreen() {
  const { user, logout } = useAuthStore();
  const [pushEnabled, setPushEnabled] = useState(user?.notify_push ?? true);
  const [emailEnabled, setEmailEnabled] = useState(user?.notify_email ?? true);

  const handleLogout = () => {
    Alert.alert("Sign Out", "Are you sure you want to sign out?", [
      { text: "Cancel", style: "cancel" },
      { text: "Sign Out", style: "destructive", onPress: logout },
    ]);
  };

  const updatePref = async (key: string, value: boolean) => {
    try { await mobileApi.patch("/auth/profile/", { [key]: value }); }
    catch { Alert.alert("Error", "Failed to update preference."); }
  };

  if (!user) return null;

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}>
      {/* Avatar + name */}
      <View style={styles.avatarSection}>
        <View style={styles.avatar}>
          <Text style={styles.avatarTxt}>{user.first_name?.[0]}{user.last_name?.[0]}</Text>
        </View>
        <Text style={styles.name}>{user.first_name} {user.last_name}</Text>
        <Text style={styles.role}>{ROLE_LABELS[user.role] ?? user.role}</Text>
        {user.school && <Text style={styles.school}>{user.school.name}</Text>}
      </View>

      {/* Info card */}
      <Card style={{ marginBottom: 16 }}>
        {[
          ["Email", user.email],
          ["Phone", user.phone || "—"],
          ["Role", ROLE_LABELS[user.role] ?? user.role],
        ].map(([l, v]) => (
          <View key={l}>
            <View style={styles.infoRow}>
              <Text style={styles.infoLabel}>{l}</Text>
              <Text style={styles.infoValue} numberOfLines={1}>{v}</Text>
            </View>
            <Divider />
          </View>
        ))}
      </Card>

      {/* Notification prefs */}
      <Card style={{ marginBottom: 16 }}>
        <Text style={styles.sectionTitle}>Notifications</Text>
        <View style={styles.prefRow}>
          <Text style={styles.prefLabel}>Push Notifications</Text>
          <Switch value={pushEnabled} onValueChange={v => { setPushEnabled(v); updatePref("notify_push", v); }} trackColor={{ true: "#6366f1" }} />
        </View>
        <Divider />
        <View style={styles.prefRow}>
          <Text style={styles.prefLabel}>Email Notifications</Text>
          <Switch value={emailEnabled} onValueChange={v => { setEmailEnabled(v); updatePref("notify_email", v); }} trackColor={{ true: "#6366f1" }} />
        </View>
      </Card>

      {/* Sign out */}
      <Button label="Sign Out" onPress={handleLogout} variant="danger" size="lg" style={{ marginTop: 8 }} />
      <Text style={styles.version}>EduSphere v2.0</Text>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 20, paddingBottom: 40 },
  avatarSection: { alignItems: "center", marginBottom: 24 },
  avatar: { width: 88, height: 88, borderRadius: 24, backgroundColor: "#e0e7ff", alignItems: "center", justifyContent: "center", marginBottom: 12 },
  avatarTxt: { fontSize: 32, fontWeight: "800", color: "#4338ca" },
  name: { fontSize: 22, fontWeight: "800", color: "#1e293b" },
  role: { fontSize: 14, color: "#6366f1", fontWeight: "600", marginTop: 4 },
  school: { fontSize: 13, color: "#64748b", marginTop: 2 },
  sectionTitle: { fontSize: 13, fontWeight: "700", color: "#374151", marginBottom: 12 },
  infoRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: 12 },
  infoLabel: { fontSize: 13, color: "#64748b" },
  infoValue: { fontSize: 13, fontWeight: "600", color: "#1e293b", maxWidth: "60%", textAlign: "right" },
  prefRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", paddingVertical: 12 },
  prefLabel: { fontSize: 14, color: "#374151" },
  version: { textAlign: "center", fontSize: 12, color: "#94a3b8", marginTop: 24 },
});
