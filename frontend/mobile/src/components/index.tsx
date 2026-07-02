/**
 * Mobile Shared Components — used across all role screens
 */

import React from "react";
import {
  View, Text, TouchableOpacity, ActivityIndicator,
  StyleSheet, TextInput, StyleProp, ViewStyle,
} from "react-native";

const BRAND = "#4F46E5";

// ─── Button ───────────────────────────────────────────────────────────────────

interface ButtonProps {
  label: string;
  onPress: () => void;
  variant?: "primary" | "secondary" | "danger" | "ghost";
  size?: "sm" | "md" | "lg";
  loading?: boolean;
  disabled?: boolean;
  style?: StyleProp<ViewStyle>;
}

export function Button({ label, onPress, variant = "primary", size = "md", loading, disabled, style }: ButtonProps) {
  const bg = { primary: BRAND, secondary: "#fff", danger: "#ef4444", ghost: "transparent" }[variant];
  const border = { primary: BRAND, secondary: "#e2e8f0", danger: "#ef4444", ghost: "transparent" }[variant];
  const textColor = variant === "secondary" ? "#374151" : variant === "ghost" ? "#6366f1" : "#fff";
  const pad = { sm: { paddingHorizontal: 12, paddingVertical: 8 }, md: { paddingHorizontal: 20, paddingVertical: 12 }, lg: { paddingHorizontal: 28, paddingVertical: 16 } }[size];
  const fontSize = { sm: 12, md: 14, lg: 16 }[size];

  return (
    <TouchableOpacity
      onPress={onPress}
      disabled={disabled || loading}
      activeOpacity={0.8}
      style={[styles.btn, { backgroundColor: bg, borderColor: border, opacity: disabled ? 0.5 : 1, ...pad }, style]}
    >
      {loading
        ? <ActivityIndicator color={textColor} size="small" />
        : <Text style={{ color: textColor, fontSize, fontWeight: "700", textAlign: "center" }}>{label}</Text>}
    </TouchableOpacity>
  );
}

// ─── Card ─────────────────────────────────────────────────────────────────────

export function Card({ children, style }: { children: React.ReactNode; style?: StyleProp<ViewStyle> }) {
  return <View style={[styles.card, style]}>{children}</View>;
}

// ─── Badge ────────────────────────────────────────────────────────────────────

type BadgeColor = "green" | "red" | "amber" | "blue" | "purple" | "slate";

const BADGE_STYLES: Record<BadgeColor, { bg: string; text: string; dot: string }> = {
  green:  { bg: "#dcfce7", text: "#15803d", dot: "#22c55e" },
  red:    { bg: "#fee2e2", text: "#dc2626", dot: "#ef4444" },
  amber:  { bg: "#fef9c3", text: "#d97706", dot: "#f59e0b" },
  blue:   { bg: "#dbeafe", text: "#2563eb", dot: "#3b82f6" },
  purple: { bg: "#f3e8ff", text: "#7c3aed", dot: "#8b5cf6" },
  slate:  { bg: "#f1f5f9", text: "#475569", dot: "#94a3b8" },
};

export function Badge({ label, color = "slate", dot }: { label: string; color?: BadgeColor; dot?: boolean }) {
  const s = BADGE_STYLES[color];
  return (
    <View style={[styles.badge, { backgroundColor: s.bg }]}>
      {dot && <View style={[styles.badgeDot, { backgroundColor: s.dot }]} />}
      <Text style={{ color: s.text, fontSize: 11, fontWeight: "600" }}>{label}</Text>
    </View>
  );
}

// ─── Stat Card ────────────────────────────────────────────────────────────────

export function StatCard({ label, value, color, sub }: { label: string; value: string | number; color: string; sub?: string }) {
  return (
    <Card style={[styles.statCard, { borderLeftColor: color, borderLeftWidth: 3 }]}>
      <Text style={[styles.statValue, { color }]}>{value}</Text>
      <Text style={styles.statLabel}>{label}</Text>
      {sub && <Text style={styles.statSub}>{sub}</Text>}
    </Card>
  );
}

// ─── Section Header ───────────────────────────────────────────────────────────

export function SectionHeader({ title, action, onAction }: { title: string; action?: string; onAction?: () => void }) {
  return (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionTitle}>{title}</Text>
      {action && onAction && (
        <TouchableOpacity onPress={onAction}>
          <Text style={{ color: BRAND, fontSize: 13, fontWeight: "600" }}>{action}</Text>
        </TouchableOpacity>
      )}
    </View>
  );
}

// ─── Empty State ─────────────────────────────────────────────────────────────

export function EmptyState({ icon, title, sub }: { icon?: string; title: string; sub?: string }) {
  return (
    <View style={styles.emptyState}>
      {icon && <Text style={{ fontSize: 40, marginBottom: 8 }}>{icon}</Text>}
      <Text style={styles.emptyTitle}>{title}</Text>
      {sub && <Text style={styles.emptySub}>{sub}</Text>}
    </View>
  );
}

// ─── Input ────────────────────────────────────────────────────────────────────

interface MobileInputProps {
  label?: string;
  error?: string;
  value: string;
  onChangeText: (text: string) => void;
  placeholder?: string;
  secureTextEntry?: boolean;
  keyboardType?: "default" | "email-address" | "numeric" | "phone-pad";
  autoCapitalize?: "none" | "sentences" | "words" | "characters";
  multiline?: boolean;
  numberOfLines?: number;
}

export function MobileInput({ label, error, ...props }: MobileInputProps) {
  return (
    <View style={{ marginBottom: 16 }}>
      {label && <Text style={styles.inputLabel}>{label}</Text>}
      <TextInput
        style={[styles.input, error && styles.inputError, props.multiline && { height: props.numberOfLines ? props.numberOfLines * 20 + 24 : 80, textAlignVertical: "top" }]}
        placeholderTextColor="#94a3b8"
        {...props}
      />
      {error && <Text style={styles.inputErr}>{error}</Text>}
    </View>
  );
}

// ─── Loading ──────────────────────────────────────────────────────────────────

export function LoadingScreen({ text = "Loading…" }: { text?: string }) {
  return (
    <View style={styles.center}>
      <ActivityIndicator color={BRAND} size="large" />
      <Text style={{ color: "#94a3b8", marginTop: 12, fontSize: 14 }}>{text}</Text>
    </View>
  );
}

// ─── Divider ─────────────────────────────────────────────────────────────────

export function Divider({ style }: { style?: StyleProp<ViewStyle> }) {
  return <View style={[{ height: 1, backgroundColor: "#f1f5f9" }, style]} />;
}

// ─── Styles ───────────────────────────────────────────────────────────────────

const styles = StyleSheet.create({
  btn: {
    borderRadius: 14, borderWidth: 1,
    alignItems: "center", justifyContent: "center",
    shadowColor: "#000", shadowOpacity: 0.05, shadowRadius: 4, elevation: 1,
  },
  card: {
    backgroundColor: "#fff", borderRadius: 16, padding: 16,
    shadowColor: "#000", shadowOpacity: 0.05, shadowRadius: 8, elevation: 2,
  },
  badge: {
    flexDirection: "row", alignItems: "center", gap: 4,
    borderRadius: 20, paddingHorizontal: 10, paddingVertical: 4,
    alignSelf: "flex-start",
  },
  badgeDot: { width: 6, height: 6, borderRadius: 3 },
  statCard: { flex: 1, padding: 14 },
  statValue: { fontSize: 22, fontWeight: "800" },
  statLabel: { fontSize: 11, color: "#64748b", marginTop: 2 },
  statSub: { fontSize: 10, color: "#94a3b8", marginTop: 1 },
  sectionHeader: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 12 },
  sectionTitle: { fontSize: 16, fontWeight: "700", color: "#1e293b" },
  emptyState: { alignItems: "center", justifyContent: "center", padding: 40 },
  emptyTitle: { fontSize: 16, fontWeight: "600", color: "#64748b", textAlign: "center" },
  emptySub: { fontSize: 13, color: "#94a3b8", textAlign: "center", marginTop: 6 },
  inputLabel: { fontSize: 13, fontWeight: "600", color: "#374151", marginBottom: 6 },
  input: {
    borderWidth: 1, borderColor: "#e2e8f0", borderRadius: 12,
    paddingHorizontal: 14, paddingVertical: 12, fontSize: 15, color: "#1e293b",
    backgroundColor: "#fff",
  },
  inputError: { borderColor: "#ef4444" },
  inputErr: { marginTop: 4, fontSize: 12, color: "#ef4444" },
  center: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: "#f8fafc" },
});
