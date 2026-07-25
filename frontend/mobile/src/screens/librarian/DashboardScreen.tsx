import React from "react";
import { View, Text, ScrollView, StyleSheet, TouchableOpacity, RefreshControl } from "react-native";
import { useNavigation } from "@react-navigation/native";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { mobileApi } from "../../api/client";
import { useAuthStore } from "../../hooks/useAuthStore";
import { Card, SectionHeader } from "../../components";

const BRAND = "#0ea5e9"; // Sky-500

export default function LibrarianDashboardScreen() {
  const { user } = useAuthStore();
  const navigation = useNavigation<any>();

  const { data: booksData, isLoading, refetch } = useQuery({
    queryKey: ["mob-librarian-home"],
    queryFn: () => mobileApi.get<any>("/library/books/?page_size=5"),
  });

  const { data: loansData } = useQuery({
    queryKey: ["mob-librarian-loans"],
    queryFn: () => mobileApi.get<any>("/library/loans/?status=active&page_size=5"),
  });

  const recentBooks = booksData?.results ?? [];
  const activeLoans = loansData?.results ?? [];

  return (
    <ScrollView style={styles.root} contentContainerStyle={styles.content}
      refreshControl={<RefreshControl refreshing={isLoading} onRefresh={refetch} tintColor={BRAND} />}>
      <Text style={styles.greeting}>Hello, {user?.first_name ?? "Librarian"}! 📚</Text>
      <Text style={styles.date}>{dayjs().format("dddd, MMMM D")}</Text>

      {/* Stats */}
      <View style={styles.statsRow}>
        <Card style={[styles.statCard, { borderLeftColor: BRAND, borderLeftWidth: 3 }]}>
          <Text style={[styles.statVal, { color: BRAND }]}>{booksData?.count ?? "—"}</Text>
          <Text style={styles.statLbl}>Total Books</Text>
        </Card>
        <Card style={[styles.statCard, { borderLeftColor: "#f59e0b", borderLeftWidth: 3 }]}>
          <Text style={[styles.statVal, { color: "#f59e0b" }]}>{activeLoans.length}</Text>
          <Text style={styles.statLbl}>Active Loans</Text>
        </Card>
      </View>

      {/* Quick actions */}
      <SectionHeader title="Quick Actions" />
      <View style={styles.actionRow}>
        <TouchableOpacity style={styles.actionBtn} onPress={() => navigation.navigate("Books" as never)} activeOpacity={0.8}>
          <Text style={styles.actionIcon}>📖</Text>
          <Text style={styles.actionText}>Books</Text>
        </TouchableOpacity>
        <TouchableOpacity style={styles.actionBtn} onPress={() => navigation.navigate("Checkouts" as never)} activeOpacity={0.8}>
          <Text style={styles.actionIcon}>✅</Text>
          <Text style={styles.actionText}>Checkouts</Text>
        </TouchableOpacity>
      </View>

      {/* Recent books */}
      {recentBooks.length > 0 && (
        <>
          <SectionHeader title="Recent Books" action="See All" onAction={() => navigation.navigate("Books" as never)} />
          {recentBooks.map((b: any) => (
            <View key={b.id} style={styles.bookCard}>
              <Text style={styles.bookTitle}>{b.title}</Text>
              <Text style={styles.bookAuthor}>{b.author}</Text>
              <Text style={[styles.bookStatus, {
                color: b.available ? BRAND : "#ef4444",
              }]}>{b.available ? "Available" : "Checked Out"}</Text>
            </View>
          ))}
        </>
      )}

      {/* Active loans */}
      {activeLoans.length > 0 && (
        <>
          <SectionHeader title="Active Loans" />
          {activeLoans.map((l: any) => (
            <View key={l.id} style={styles.loanCard}>
              <Text style={styles.loanTitle}>{l.book?.title ?? "Book"}</Text>
              <Text style={styles.loanUser}>Borrower: {l.student_name ?? l.user_name ?? "—"}</Text>
              {l.due_date && (
                <Text style={[styles.loanDue, {
                  color: new Date(l.due_date) < new Date() ? "#ef4444" : "#64748b",
                }]}>Due: {new Date(l.due_date).toLocaleDateString()}</Text>
              )}
            </View>
          ))}
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#f8fafc" },
  content: { padding: 20, paddingBottom: 40 },
  greeting: { fontSize: 22, fontWeight: "800", color: "#0f172a" },
  date: { fontSize: 13, color: "#64748b", marginTop: 2, marginBottom: 20 },
  statsRow: { flexDirection: "row", gap: 12, marginBottom: 12 },
  statCard: { flex: 1, padding: 14 },
  statVal: { fontSize: 22, fontWeight: "800" },
  statLbl: { fontSize: 11, color: "#64748b", marginTop: 2 },
  actionRow: { flexDirection: "row", gap: 12, marginBottom: 20 },
  actionBtn: {
    flex: 1, backgroundColor: "#fff", borderRadius: 12, padding: 16,
    alignItems: "center", borderWidth: 1, borderColor: "#e2e8f0",
  },
  actionIcon: { fontSize: 24 },
  actionText: { fontSize: 12, fontWeight: "600", color: "#475569", marginTop: 4 },
  bookCard: {
    backgroundColor: "#fff", borderRadius: 12, padding: 14, marginBottom: 8,
  },
  bookTitle: { fontSize: 14, fontWeight: "600", color: "#1e293b" },
  bookAuthor: { fontSize: 12, color: "#64748b", marginTop: 2 },
  bookStatus: { fontSize: 11, fontWeight: "700", marginTop: 4 },
  loanCard: {
    backgroundColor: "#fff", borderRadius: 12, padding: 14, marginBottom: 8,
  },
  loanTitle: { fontSize: 14, fontWeight: "600", color: "#1e293b" },
  loanUser: { fontSize: 12, color: "#64748b", marginTop: 2 },
  loanDue: { fontSize: 11, fontWeight: "600", marginTop: 2 },
});
