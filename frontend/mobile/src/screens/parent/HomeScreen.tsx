import React from "react";
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from "react-native";
import { useAuthStore } from "../../hooks/useAuthStore";
import { LoadingScreen, Card, EmptyState } from "../../components";

export default function ParentHomeScreen() {
  const { user } = useAuthStore();
  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}>
      <Text style={styles.greeting}>Hello, {user?.first_name}! 👋</Text>
      <Text style={styles.sub}>Monitor your children's academic progress</Text>
      <Card style={{ marginTop: 20 }}>
        <EmptyState icon="👨‍👩‍👧" title="Children Overview" sub="Your linked children will appear here." />
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 20 },
  greeting: { fontSize: 22, fontWeight: "800", color: "#1e293b" },
  sub: { fontSize: 14, color: "#64748b", marginTop: 4 },
});
