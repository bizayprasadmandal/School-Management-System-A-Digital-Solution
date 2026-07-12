import React, { useState } from "react";
import { View, Text, FlatList, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform } from "react-native";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { mobileApi } from "../../api/client";
import { SkeletonMessagesScreen, EmptyState } from "../../components";

export default function ParentMessagesScreen() {
  const qc = useQueryClient();
  const [active, setActive] = useState<string | null>(null);
  const [msg, setMsg] = useState("");

  const { data: inbox, isLoading } = useQuery({ queryKey: ["mob-par-inbox"], queryFn: () => mobileApi.get<any>("/communication/messages/inbox/") });
  const { data: thread } = useQuery({ queryKey: ["mob-par-thread", active], queryFn: () => mobileApi.get<any[]>(`/communication/messages/conversation/${active}/`), enabled: !!active, refetchInterval: 5000 });
  const send = useMutation({ mutationFn: (c: string) => mobileApi.post("/communication/messages/", { recipient: active, content: c }), onSuccess: () => { setMsg(""); qc.invalidateQueries({ queryKey: ["mob-par-thread", active] }); } });

  const threads = inbox ?? [];
  if (isLoading) return <SkeletonMessagesScreen />;

  if (!active) return (
    <View style={{ flex: 1, backgroundColor: "#f8fafc" }}>
      <Text style={styles.heading}>Messages</Text>
      {threads.length === 0
        ? <EmptyState icon="💬" title="No messages" sub="Contact teachers directly through the school portal." />
        : <FlatList data={threads} keyExtractor={i => i.partner.id} renderItem={({ item }) => (
            <TouchableOpacity style={styles.thread} onPress={() => setActive(item.partner.id)} activeOpacity={0.8}>
              <View style={styles.ava}><Text style={styles.avaTxt}>{item.partner.name.slice(0,2).toUpperCase()}</Text></View>
              <View style={{ flex: 1 }}><Text style={styles.pName}>{item.partner.name}</Text><Text style={styles.preview} numberOfLines={1}>{item.last_message?.content}</Text></View>
              {item.unread_count > 0 && <View style={styles.badge}><Text style={styles.badgeTxt}>{item.unread_count}</Text></View>}
            </TouchableOpacity>
          )} />
      }
    </View>
  );

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: "#f8fafc" }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <TouchableOpacity style={styles.back} onPress={() => setActive(null)}><Text style={{ color: "#7c3aed" }}>‹ Back</Text></TouchableOpacity>
      <FlatList data={thread ?? []} keyExtractor={i => i.id} inverted contentContainerStyle={{ padding: 12 }}
        renderItem={({ item }) => <View style={[styles.bubble, item.is_mine ? styles.mine : styles.theirs]}><Text style={[styles.bubbleTxt, item.is_mine && { color: "#fff" }]}>{item.content}</Text></View>} />
      <View style={styles.bar}>
        <TextInput style={styles.input} value={msg} onChangeText={setMsg} placeholder="Message a teacher…" multiline />
        <TouchableOpacity style={styles.sendBtn} onPress={() => msg.trim() && send.mutate(msg)}><Text style={styles.sendTxt}>Send</Text></TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b", padding: 20 },
  thread: { flexDirection: "row", alignItems: "center", gap: 12, padding: 14, backgroundColor: "#fff", borderBottomWidth: 1, borderBottomColor: "#f1f5f9" },
  ava: { width: 44, height: 44, borderRadius: 12, backgroundColor: "#f3e8ff", alignItems: "center", justifyContent: "center" },
  avaTxt: { fontSize: 13, fontWeight: "700", color: "#7c3aed" },
  pName: { fontSize: 14, fontWeight: "700", color: "#1e293b" },
  preview: { fontSize: 12, color: "#64748b", marginTop: 2 },
  badge: { width: 20, height: 20, borderRadius: 10, backgroundColor: "#7c3aed", alignItems: "center", justifyContent: "center" },
  badgeTxt: { fontSize: 10, fontWeight: "700", color: "#fff" },
  back: { padding: 16, borderBottomWidth: 1, borderBottomColor: "#f1f5f9", backgroundColor: "#fff" },
  bubble: { maxWidth: "75%", borderRadius: 14, padding: 10, marginBottom: 6 },
  mine: { backgroundColor: "#7c3aed", alignSelf: "flex-end" },
  theirs: { backgroundColor: "#fff", alignSelf: "flex-start", borderWidth: 1, borderColor: "#e2e8f0" },
  bubbleTxt: { fontSize: 14, color: "#1e293b" },
  bar: { flexDirection: "row", gap: 8, padding: 12, backgroundColor: "#fff", borderTopWidth: 1, borderTopColor: "#e2e8f0" },
  input: { flex: 1, borderWidth: 1, borderColor: "#e2e8f0", borderRadius: 12, paddingHorizontal: 14, paddingVertical: 10, fontSize: 14 },
  sendBtn: { backgroundColor: "#7c3aed", borderRadius: 12, paddingHorizontal: 16, justifyContent: "center" },
  sendTxt: { fontSize: 14, fontWeight: "700", color: "#fff" },
});
