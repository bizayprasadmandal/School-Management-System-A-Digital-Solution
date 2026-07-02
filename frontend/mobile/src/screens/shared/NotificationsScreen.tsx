import React from "react";
import { View, Text, FlatList, StyleSheet, TouchableOpacity, ActivityIndicator } from "react-native";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { mobileApi } from "../../api/client";
import dayjs from "dayjs";

const BRAND = "#4F46E5";

export default function NotificationsScreen() {
  const qc = useQueryClient();
  const { data, isLoading, refetch } = useQuery({
    queryKey: ["notifications-mob"],
    queryFn: () => mobileApi.get<any>("/communication/notifications/?channel=in_app&page_size=30"),
    refetchInterval: 30000,
  });

  const markRead = useMutation({
    mutationFn: (id: string) => mobileApi.patch(`/communication/notifications/${id}/mark-read/`, {}),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications-mob"] }),
  });

  const markAll = useMutation({
    mutationFn: () => mobileApi.post("/communication/notifications/mark-all-read/", {}),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["notifications-mob"] }),
  });

  const notifications = data?.results ?? [];
  const unreadCount = notifications.filter((n: any) => !n.read_at).length;

  if (isLoading) return <View style={styles.center}><ActivityIndicator color={BRAND} size="large" /></View>;

  return (
    <View style={styles.root}>
      {unreadCount > 0 && (
        <View style={styles.banner}>
          <Text style={styles.bannerText}>{unreadCount} unread notifications</Text>
          <TouchableOpacity onPress={() => markAll.mutate()} disabled={markAll.isPending}>
            <Text style={styles.markAllBtn}>Mark all read</Text>
          </TouchableOpacity>
        </View>
      )}
      <FlatList
        data={notifications}
        keyExtractor={item => item.id}
        onRefresh={refetch}
        refreshing={isLoading}
        contentContainerStyle={{ padding: 16, paddingBottom: 40 }}
        ItemSeparatorComponent={() => <View style={{ height: 8 }} />}
        ListEmptyComponent={() => (
          <View style={styles.empty}>
            <Text style={styles.emptyIcon}>🔔</Text>
            <Text style={styles.emptyTitle}>All caught up!</Text>
            <Text style={styles.emptySub}>No notifications right now.</Text>
          </View>
        )}
        renderItem={({ item }) => (
          <TouchableOpacity
            onPress={() => !item.read_at && markRead.mutate(item.id)}
            activeOpacity={0.8}
            style={[styles.card, !item.read_at && styles.cardUnread]}
          >
            <View style={styles.cardContent}>
              {!item.read_at && <View style={styles.dot} />}
              <View style={{ flex: 1, paddingLeft: item.read_at ? 0 : 8 }}>
                <Text style={[styles.title, !item.read_at && styles.titleUnread]}>{item.title}</Text>
                <Text style={styles.body} numberOfLines={2}>{item.body}</Text>
                <Text style={styles.time}>{dayjs(item.created_at).fromNow()}</Text>
              </View>
            </View>
          </TouchableOpacity>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  center: { flex: 1, alignItems: "center", justifyContent: "center" },
  banner: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", backgroundColor: "#eef2ff", padding: 14, borderBottomWidth: 1, borderBottomColor: "#c7d2fe" },
  bannerText: { fontSize: 13, fontWeight: "600", color: "#4338ca" },
  markAllBtn: { fontSize: 13, fontWeight: "600", color: BRAND },
  card: { backgroundColor: "#fff", borderRadius: 14, padding: 14, shadowColor: "#000", shadowOpacity: 0.04, shadowRadius: 6, elevation: 1 },
  cardUnread: { backgroundColor: "#f5f3ff", borderWidth: 1, borderColor: "#ddd6fe" },
  cardContent: { flexDirection: "row", alignItems: "flex-start" },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: BRAND, marginTop: 5 },
  title: { fontSize: 14, fontWeight: "600", color: "#374151" },
  titleUnread: { fontWeight: "700", color: "#1e293b" },
  body: { fontSize: 12, color: "#6b7280", marginTop: 3, lineHeight: 18 },
  time: { fontSize: 11, color: "#9ca3af", marginTop: 6 },
  empty: { alignItems: "center", paddingTop: 60 },
  emptyIcon: { fontSize: 48, marginBottom: 12 },
  emptyTitle: { fontSize: 18, fontWeight: "700", color: "#374151" },
  emptySub: { fontSize: 14, color: "#9ca3af", marginTop: 6 },
});
