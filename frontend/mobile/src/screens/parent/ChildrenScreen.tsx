import React from "react";
import { View, Text, ScrollView, StyleSheet, TouchableOpacity } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { mobileApi } from "../../api/client";
import { SkeletonChildrenScreen, Card, Badge, EmptyState, SectionHeader } from "../../components";

export default function ParentChildrenScreen() {
  const { data, isLoading } = useQuery({
    queryKey: ["mob-parent-children"],
    queryFn: () => mobileApi.get<any>("/students/"),
  });

  if (isLoading) return <SkeletonChildrenScreen />;
  const children = data?.results ?? [];

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}>
      <Text style={styles.heading}>My Children</Text>
      {children.length === 0
        ? <EmptyState icon="👨‍👩‍👧" title="No children linked" sub="Contact your school admin to link your children." />
        : children.map((child: any) => (
          <Card key={child.id} style={styles.childCard}>
            <View style={styles.ava}><Text style={styles.avaTxt}>{child.full_name.split(" ").map((n:string)=>n[0]).join("").slice(0,2).toUpperCase()}</Text></View>
            <View style={{ flex: 1 }}>
              <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}>
                <Text style={styles.name}>{child.full_name}</Text>
                <Badge label={child.is_active ? "Active" : "Inactive"} color={child.is_active ? "green" : "slate"} dot />
              </View>
              <Text style={styles.meta}>{child.current_class ?? "—"} · Adm: {child.admission_number}</Text>
              <View style={styles.infoRow}>
                {[
                  ["DOB", child.date_of_birth ? new Date(child.date_of_birth).toLocaleDateString() : "—"],
                  ["Gender", child.gender === "M" ? "Male" : child.gender === "F" ? "Female" : "Other"],
                ].map(([l,v]) => (
                  <View key={l} style={styles.infoItem}>
                    <Text style={styles.infoLabel}>{l}</Text>
                    <Text style={styles.infoValue}>{v}</Text>
                  </View>
                ))}
              </View>
            </View>
          </Card>
        ))
      }
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 40 },
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b", marginBottom: 16 },
  childCard: { flexDirection: "row", gap: 14, marginBottom: 12 },
  ava: { width: 56, height: 56, borderRadius: 16, backgroundColor: "#ede9fe", alignItems: "center", justifyContent: "center", flexShrink: 0 },
  avaTxt: { fontSize: 18, fontWeight: "800", color: "#7c3aed" },
  name: { fontSize: 16, fontWeight: "700", color: "#1e293b" },
  meta: { fontSize: 12, color: "#64748b", marginTop: 2 },
  infoRow: { flexDirection: "row", gap: 16, marginTop: 10 },
  infoItem: {},
  infoLabel: { fontSize: 10, color: "#94a3b8", fontWeight: "600", textTransform: "uppercase" },
  infoValue: { fontSize: 13, fontWeight: "600", color: "#374151", marginTop: 2 },
});
