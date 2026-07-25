import React, { useState } from "react";
import { View, Text, ScrollView, StyleSheet, TextInput, TouchableOpacity, RefreshControl } from "react-native";
import { useQuery } from "@tanstack/react-query";
import { mobileApi } from "../../api/client";
import { Card } from "../../components";

const BRAND = "#0ea5e9";

export default function BookManagementScreen() {
  const [search, setSearch] = useState("");

  const { data, isLoading, refetch } = useQuery({
    queryKey: ["mob-books", search],
    queryFn: () => mobileApi.get<any>(`/library/books/${search ? `?search=${search}` : ""}`),
  });

  const books = data?.results ?? [];

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor={BRAND} />}>
      {/* Search */}
      <TextInput
        style={styles.searchInput}
        placeholder="Search books by title or author..."
        placeholderTextColor="#94a3b8"
        value={search}
        onChangeText={setSearch}
      />

      <Text style={styles.count}>{data?.count ?? books.length} book{(data?.count ?? books.length) !== 1 ? "s" : ""}</Text>

      {books.map((b: any) => (
        <Card key={b.id} style={styles.bookCard}>
          <View style={styles.header}>
            <View style={{ flex: 1 }}>
              <Text style={styles.title}>{b.title}</Text>
              <Text style={styles.author}>{b.author}</Text>
            </View>
            <Text style={[styles.status, { color: b.available ? BRAND : "#ef4444" }]}>
              {b.available ? "In" : "Out"}
            </Text>
          </View>
          {b.isbn && <Text style={styles.isbn}>ISBN: {b.isbn}</Text>}
        </Card>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 16, paddingBottom: 40 },
  searchInput: {
    backgroundColor: "#fff", borderRadius: 12, padding: 14, fontSize: 14,
    borderWidth: 1, borderColor: "#e2e8f0", marginBottom: 12,
  },
  count: { fontSize: 12, color: "#94a3b8", marginBottom: 12 },
  bookCard: { marginBottom: 10, padding: 14 },
  header: { flexDirection: "row", justifyContent: "space-between", alignItems: "flex-start" },
  title: { fontSize: 15, fontWeight: "600", color: "#1e293b" },
  author: { fontSize: 12, color: "#64748b", marginTop: 2 },
  status: { fontSize: 12, fontWeight: "700" },
  isbn: { fontSize: 11, color: "#94a3b8", marginTop: 4 },
});
