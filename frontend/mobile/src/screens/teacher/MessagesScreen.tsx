import React, { useState, useRef } from "react";
import { View, Text, FlatList, TextInput, TouchableOpacity, StyleSheet, KeyboardAvoidingView, Platform } from "react-native";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import dayjs from "dayjs";
import { mobileApi } from "../../api/client";
import { LoadingScreen, Card, EmptyState } from "../../components";

export default function TeacherMessagesScreen() {
  const qc = useQueryClient();
  const [activeThread, setActiveThread] = useState<string | null>(null);
  const [msg, setMsg] = useState("");

  const { data: inbox, isLoading } = useQuery({
    queryKey: ["mob-inbox"],
    queryFn: () => mobileApi.get<any>("/communication/messages/inbox/"),
  });

  const { data: thread } = useQuery({
    queryKey: ["mob-thread", activeThread],
    queryFn: () => mobileApi.get<any>(`/communication/messages/conversation/${activeThread}/`),
    enabled: !!activeThread,
    refetchInterval: 5000,
  });

  const send = useMutation({
    mutationFn: (content: string) => mobileApi.post("/communication/messages/", { recipient: activeThread, content }),
    onSuccess: () => { setMsg(""); qc.invalidateQueries({ queryKey: ["mob-thread", activeThread] }); },
  });

  const threads = inbox ?? [];

  if (isLoading) return <LoadingScreen text="Loading messages..." />;

  if (!activeThread) return (
    <View style={{ flex: 1, backgroundColor: "#f8fafc" }}>
      <Text style={styles.heading}>Messages</Text>
      {threads.length === 0
        ? <EmptyState icon="💬" title="No messages yet" sub="Messages from students and parents appear here." />
        : <FlatList data={threads} keyExtractor={i => i.partner.id}
            renderItem={({ item }) => (
              <TouchableOpacity style={styles.threadCard} onPress={() => setActiveThread(item.partner.id)} activeOpacity={0.8}>
                <View style={styles.avatar}><Text style={styles.avatarTxt}>{item.partner.name.slice(0,2).toUpperCase()}</Text></View>
                <View style={{ flex: 1 }}>
                  <View style={{ flexDirection: "row", justifyContent: "space-between" }}>
                    <Text style={styles.partnerName}>{item.partner.name}</Text>
                    <Text style={styles.time}>{dayjs(item.last_message.sent_at).fromNow()}</Text>
                  </View>
                  <Text style={styles.preview} numberOfLines={1}>{item.last_message.content}</Text>
                </View>
                {item.unread_count > 0 && <View style={styles.badge}><Text style={styles.badgeTxt}>{item.unread_count}</Text></View>}
              </TouchableOpacity>
            )} />
      }
    </View>
  );

  const messages = thread ?? [];
  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: "#f8fafc" }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <TouchableOpacity style={styles.backRow} onPress={() => setActiveThread(null)}>
        <Text style={{ color: "#6366f1" }}>‹ Back</Text>
      </TouchableOpacity>
      <FlatList data={messages} keyExtractor={i => i.id} inverted
        contentContainerStyle={{ padding: 12 }}
        renderItem={({ item }) => (
          <View style={[styles.bubble, item.is_mine ? styles.bubbleMine : styles.bubbleOther]}>
            <Text style={[styles.bubbleTxt, item.is_mine && { color: "#fff" }]}>{item.content}</Text>
          </View>
        )} />
      <View style={styles.inputBar}>
        <TextInput style={styles.input} value={msg} onChangeText={setMsg} placeholder="Type a message…" multiline />
        <TouchableOpacity style={styles.sendBtn} onPress={() => msg.trim() && send.mutate(msg)} disabled={send.isPending}>
          <Text style={styles.sendTxt}>Send</Text>
        </TouchableOpacity>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  heading: { fontSize: 22, fontWeight: "800", color: "#1e293b", padding: 20 },
  threadCard: { flexDirection: "row", alignItems: "center", gap: 12, backgroundColor: "#fff", padding: 14, borderBottomWidth: 1, borderBottomColor: "#f1f5f9" },
  avatar: { width: 44, height: 44, borderRadius: 12, backgroundColor: "#e0e7ff", alignItems: "center", justifyContent: "center" },
  avatarTxt: { fontSize: 13, fontWeight: "700", color: "#4338ca" },
  partnerName: { fontSize: 14, fontWeight: "700", color: "#1e293b" },
  time: { fontSize: 11, color: "#94a3b8" },
  preview: { fontSize: 12, color: "#64748b", marginTop: 2 },
  badge: { width: 20, height: 20, borderRadius: 10, backgroundColor: "#6366f1", alignItems: "center", justifyContent: "center" },
  badgeTxt: { fontSize: 10, fontWeight: "700", color: "#fff" },
  backRow: { padding: 16, borderBottomWidth: 1, borderBottomColor: "#f1f5f9", backgroundColor: "#fff" },
  bubble: { maxWidth: "75%", borderRadius: 14, padding: 10, marginBottom: 6 },
  bubbleMine: { backgroundColor: "#6366f1", alignSelf: "flex-end" },
  bubbleOther: { backgroundColor: "#fff", alignSelf: "flex-start", borderWidth: 1, borderColor: "#e2e8f0" },
  bubbleTxt: { fontSize: 14, color: "#1e293b" },
  inputBar: { flexDirection: "row", gap: 8, padding: 12, backgroundColor: "#fff", borderTopWidth: 1, borderTopColor: "#e2e8f0" },
  input: { flex: 1, borderWidth: 1, borderColor: "#e2e8f0", borderRadius: 12, paddingHorizontal: 14, paddingVertical: 10, fontSize: 14 },
  sendBtn: { backgroundColor: "#6366f1", borderRadius: 12, paddingHorizontal: 16, justifyContent: "center" },
  sendTxt: { fontSize: 14, fontWeight: "700", color: "#fff" },
});
