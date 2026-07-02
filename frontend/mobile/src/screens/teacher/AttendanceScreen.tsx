import React, { useState, useEffect } from "react";
import {
  View, Text, ScrollView, TouchableOpacity, StyleSheet,
  ActivityIndicator, Alert,
} from "react-native";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { mobileApi } from "../../api/client";
import { LoadingScreen, Button, Badge } from "../../components";

const BRAND = "#059669";
type Status = "P" | "A" | "L" | "E";
const STATUS: Record<Status, { label: string; color: string; bg: string }> = {
  P: { label: "P", color: "#15803d", bg: "#dcfce7" },
  A: { label: "A", color: "#dc2626", bg: "#fee2e2" },
  L: { label: "L", color: "#d97706", bg: "#fef9c3" },
  E: { label: "E", color: "#2563eb", bg: "#dbeafe" },
};

export default function TeacherAttendanceScreen() {
  const today = dayjs().format("YYYY-MM-DD");
  const [cls, setCls] = useState<any>(null);
  const [entries, setEntries] = useState<Record<string, Status>>({});
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  const { data: clsData, isLoading: clsLoad } = useQuery({
    queryKey: ["teacher-cls"],
    queryFn: () => mobileApi.get<any>("/students/classrooms/"),
  });
  const { data: students, isLoading: stuLoad } = useQuery({
    queryKey: ["cls-students", cls?.id],
    queryFn: () => mobileApi.get<any[]>(`/students/classrooms/${cls.id}/students/`),
    enabled: !!cls,
  });

  useEffect(() => {
    if (students) {
      const init: Record<string,Status> = {};
      students.forEach((s: any) => { init[s.id] = "P"; });
      setEntries(init); setSaved(false);
    }
  }, [students]);

  const stats = {
    P: Object.values(entries).filter(v=>v==="P").length,
    A: Object.values(entries).filter(v=>v==="A").length,
    L: Object.values(entries).filter(v=>v==="L").length,
    total: Object.keys(entries).length,
  };

  const submit = async () => {
    setSaving(true);
    try {
      await mobileApi.post("/attendance/bulk-record/", {
        classroom_id: cls.id, date: today,
        records: Object.entries(entries).map(([id,status]) => ({ student_id: id, status })),
      });
      setSaved(true);
      Alert.alert("Saved", `Attendance recorded for ${stats.total} students.`);
    } catch { Alert.alert("Error", "Failed to save. Try again."); }
    finally { setSaving(false); }
  };

  if (clsLoad) return <LoadingScreen text="Loading..." />;
  const classrooms = clsData?.results ?? [];

  if (!cls) return (
    <ScrollView style={styles.root} contentContainerStyle={{ padding: 16 }}>
      <Text style={styles.heading}>Select Classroom</Text>
      <Text style={styles.sub}>{dayjs().format("dddd, MMMM D")}</Text>
      {classrooms.map((c: any) => (
        <TouchableOpacity key={c.id} style={styles.clsCard} onPress={() => setCls(c)} activeOpacity={0.8}>
          <View style={styles.clsIcon}><Text style={{ fontSize: 16, fontWeight: "700", color: BRAND }}>{c.name[0]}</Text></View>
          <View style={{ flex: 1 }}>
            <Text style={styles.clsName}>{c.grade_name} {c.name}</Text>
            <Text style={styles.clsMeta}>{c.student_count} students</Text>
          </View>
          <Text style={{ color: "#94a3b8", fontSize: 18 }}>›</Text>
        </TouchableOpacity>
      ))}
    </ScrollView>
  );

  if (stuLoad) return <LoadingScreen text="Loading students..." />;

  return (
    <View style={{ flex: 1, backgroundColor: "#f8fafc" }}>
      <View style={styles.header}>
        <TouchableOpacity onPress={() => setCls(null)} style={styles.back}><Text style={{ color: BRAND, fontSize: 16 }}>‹</Text></TouchableOpacity>
        <View style={{ flex: 1 }}>
          <Text style={styles.headerTitle}>{cls.grade_name} {cls.name}</Text>
          <Text style={styles.headerDate}>{dayjs().format("ddd, MMM D")}</Text>
        </View>
      </View>
      <View style={styles.statsRow}>
        {[["Present",stats.P,"#15803d"],["Absent",stats.A,"#dc2626"],["Late",stats.L,"#d97706"]].map(([l,v,c]) => (
          <View key={String(l)} style={styles.statBox}><Text style={[styles.statVal, { color: String(c) }]}>{v}</Text><Text style={styles.statLbl}>{l}</Text></View>
        ))}
      </View>
      <View style={styles.markAllRow}>
        <Text style={styles.markAllLbl}>Mark all:</Text>
        {(["P","A","L"] as Status[]).map(s => (
          <TouchableOpacity key={s} onPress={() => { const n={...entries}; Object.keys(n).forEach(k=>{ n[k]=s; }); setEntries(n); setSaved(false); }}
            style={[styles.markBtn, { backgroundColor: STATUS[s].bg }]}>
            <Text style={[styles.markBtnTxt, { color: STATUS[s].color }]}>{STATUS[s].label}</Text>
          </TouchableOpacity>
        ))}
      </View>
      <ScrollView style={{ flex: 1 }}>
        {(students ?? []).map((s: any, i: number) => (
          <View key={s.id} style={[styles.row, i%2===0 ? {} : { backgroundColor: "#fafafa" }]}>
            <View style={styles.ava}><Text style={styles.avaTxt}>{s.full_name.split(" ").map((n:string)=>n[0]).join("").slice(0,2)}</Text></View>
            <View style={{ flex: 1 }}>
              <Text style={styles.stuName} numberOfLines={1}>{s.full_name}</Text>
              <Text style={styles.stuAdm}>{s.admission_number}</Text>
            </View>
            <View style={{ flexDirection: "row", gap: 4 }}>
              {(["P","A","L","E"] as Status[]).map(st => (
                <TouchableOpacity key={st} onPress={() => { setEntries(p=>({...p,[s.id]:st})); setSaved(false); }}
                  style={[styles.stBtn, entries[s.id]===st && { backgroundColor: STATUS[st].bg, borderColor: STATUS[st].color }]}>
                  <Text style={[styles.stBtnTxt, entries[s.id]===st && { color: STATUS[st].color, fontWeight:"700" }]}>{st}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        ))}
        <View style={{ height: 90 }} />
      </ScrollView>
      <View style={styles.footer}>
        <Button label={saving ? "Saving..." : saved ? "✓ Saved" : `Save (${stats.total})`}
          onPress={submit} disabled={saving || saved} variant={saved?"secondary":"primary"} size="lg" style={{ flex: 1 }} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b" },
  sub: { fontSize: 13, color: "#64748b", marginTop: 4, marginBottom: 16 },
  clsCard: { flexDirection: "row", alignItems: "center", gap: 14, backgroundColor: "#fff", borderRadius: 14, padding: 16, marginBottom: 10, shadowColor: "#000", shadowOpacity: 0.04, shadowRadius: 6, elevation: 1 },
  clsIcon: { width: 44, height: 44, borderRadius: 12, backgroundColor: "#d1fae5", alignItems: "center", justifyContent: "center" },
  clsName: { fontSize: 15, fontWeight: "700", color: "#1e293b" },
  clsMeta: { fontSize: 12, color: "#64748b", marginTop: 2 },
  header: { flexDirection: "row", alignItems: "center", gap: 12, backgroundColor: "#fff", paddingHorizontal: 16, paddingVertical: 12, borderBottomWidth: 1, borderBottomColor: "#f1f5f9" },
  back: { width: 32, height: 32, alignItems: "center", justifyContent: "center" },
  headerTitle: { fontSize: 16, fontWeight: "700", color: "#1e293b" },
  headerDate: { fontSize: 12, color: "#64748b" },
  statsRow: { flexDirection: "row", backgroundColor: "#fff", borderBottomWidth: 1, borderBottomColor: "#f1f5f9", paddingVertical: 8 },
  statBox: { flex: 1, alignItems: "center" },
  statVal: { fontSize: 20, fontWeight: "800" },
  statLbl: { fontSize: 10, color: "#94a3b8" },
  markAllRow: { flexDirection: "row", alignItems: "center", gap: 8, paddingHorizontal: 14, paddingVertical: 8, backgroundColor: "#f8fafc", borderBottomWidth: 1, borderBottomColor: "#e2e8f0" },
  markAllLbl: { fontSize: 12, color: "#64748b", fontWeight: "600" },
  markBtn: { borderRadius: 7, paddingHorizontal: 12, paddingVertical: 5 },
  markBtnTxt: { fontSize: 12, fontWeight: "600" },
  row: { flexDirection: "row", alignItems: "center", gap: 10, paddingHorizontal: 12, paddingVertical: 10, backgroundColor: "#fff" },
  ava: { width: 34, height: 34, borderRadius: 10, backgroundColor: "#e0e7ff", alignItems: "center", justifyContent: "center" },
  avaTxt: { fontSize: 11, fontWeight: "700", color: "#4338ca" },
  stuName: { fontSize: 13, fontWeight: "600", color: "#1e293b" },
  stuAdm: { fontSize: 10, color: "#94a3b8" },
  stBtn: { width: 27, height: 27, borderRadius: 7, borderWidth: 1, borderColor: "#e2e8f0", alignItems: "center", justifyContent: "center", backgroundColor: "#f8fafc" },
  stBtnTxt: { fontSize: 10, fontWeight: "600", color: "#64748b" },
  footer: { flexDirection: "row", padding: 14, backgroundColor: "#fff", borderTopWidth: 1, borderTopColor: "#e2e8f0" },
});
