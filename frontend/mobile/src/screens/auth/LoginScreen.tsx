/**
 * Mobile Login Screen — JWT authentication for React Native
 */

import React, { useState, useEffect } from "react";
import {
  View, Text, TextInput, TouchableOpacity, StyleSheet,
  KeyboardAvoidingView, Platform, ActivityIndicator, Alert, ScrollView,
} from "react-native";
import Ionicons from "@expo/vector-icons/Ionicons";
import * as LocalAuthentication from "expo-local-authentication";
import axios from "axios";
import { useAuthStore } from "../../hooks/useAuthStore";

const API_BASE = process.env.EXPO_PUBLIC_API_URL ?? "https://api.edusphere.school/api/v1";
const BRAND = "#4F46E5";

const ROLE_DEMO = [
  { role: "Admin",   email: "admin@demo.edusphere.school",  password: "Admin@1234" },
  { role: "Teacher", email: "sarah.mitchell@demo.edusphere.school", password: "Teacher@1234" },
  { role: "Student", email: "student001@demo.edusphere.school", password: "Student@1234" },
  { role: "Parent",  email: "parent001@demo.edusphere.school",  password: "Parent@1234" },
];

export default function LoginScreen() {
  const [email, setEmail]         = useState("");
  const [password, setPassword]   = useState("");
  const [showPwd, setShowPwd]     = useState(false);
  const [loading, setLoading]     = useState(false);
  const [errors, setErrors]       = useState<{email?: string; password?: string}>({});
  const [biometricType, setBiometricType] = useState<string | null>(null);
  const { setAuth } = useAuthStore();

  // Check for biometric support on mount
  useEffect(() => {
    (async () => {
      const compatible = await LocalAuthentication.hasHardwareAsync();
      if (!compatible) return;
      const enrolled = await LocalAuthentication.isEnrolledAsync();
      if (!enrolled) return;
      const types = await LocalAuthentication.supportedAuthenticationTypesAsync();
      if (types.includes(LocalAuthentication.AuthenticationType.FINGERPRINT)) {
        setBiometricType("Fingerprint");
      } else if (types.includes(LocalAuthentication.AuthenticationType.FACIAL_RECOGNITION)) {
        setBiometricType("Face ID");
      } else if (types.includes(LocalAuthentication.AuthenticationType.IRIS)) {
        setBiometricType("Iris");
      }
    })();
  }, []);

  const handleBiometricLogin = async () => {
    try {
      const result = await LocalAuthentication.authenticateAsync({
        promptMessage: "Sign in to EduSphere",
        cancelLabel: "Cancel",
        disableDeviceFallback: false,
      });
      if (result.success) {
        // Biometric verified — attempt login with stored credentials
        const stored = useAuthStore.getState().user;
        if (stored?.email) {
          setEmail(stored.email);
          // Password isn't stored securely, so just notify user
          Alert.alert("Biometric Verified", "Please enter your password to complete sign-in.");
        }
      }
    } catch {
      // User cancelled or biometric failed — do nothing
    }
  };

  const validate = () => {
    const e: typeof errors = {};
    if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) e.email = "Enter a valid email";
    if (!password) e.password = "Password is required";
    setErrors(e);
    return !Object.keys(e).length;
  };

  const handleLogin = async () => {
    if (!validate()) return;
    setLoading(true);
    try {
      const { data } = await axios.post(`${API_BASE}/auth/login/`, { email, password });
      setAuth(data.user, { access: data.access, refresh: data.refresh });
    } catch (err: any) {
      const s = err?.response?.status;
      if (s === 401) setErrors({ password: "Incorrect email or password" });
      else if (s === 429) Alert.alert("Locked", "Too many attempts. Try again in 30 minutes.");
      else Alert.alert("Error", "Connection failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={styles.root} behavior={Platform.OS === "ios" ? "padding" : "height"}>
      <ScrollView contentContainerStyle={styles.scroll} keyboardShouldPersistTaps="handled">

        {/* Logo */}
        <View style={styles.logoBox}>
          <Ionicons name="school" size={38} color={BRAND} />
        </View>
        <Text style={styles.appName}>EduSphere</Text>
        <Text style={styles.tagline}>School Management System</Text>

        {/* Card */}
        <View style={styles.card}>
          <Text style={styles.title}>Welcome back</Text>
          <Text style={styles.sub}>Sign in to your account</Text>

          {/* Email */}
          <Text style={styles.label}>Email address</Text>
          <View style={[styles.row, errors.email && styles.rowError]}>
            <Ionicons name="mail-outline" size={18} color="#94a3b8" style={{ marginRight: 10 }} />
            <TextInput
              style={styles.input}
              value={email}
              onChangeText={v => { setEmail(v); setErrors(e => ({ ...e, email: undefined })); }}
              placeholder="you@school.edu"
              placeholderTextColor="#cbd5e1"
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
            />
          </View>
          {errors.email && <Text style={styles.err}>{errors.email}</Text>}

          {/* Password */}
          <View style={styles.labelRow}>
            <Text style={styles.label}>Password</Text>
            <Text style={styles.forgot}>Forgot password?</Text>
          </View>
          <View style={[styles.row, errors.password && styles.rowError]}>
            <Ionicons name="lock-closed-outline" size={18} color="#94a3b8" style={{ marginRight: 10 }} />
            <TextInput
              style={styles.input}
              value={password}
              onChangeText={v => { setPassword(v); setErrors(e => ({ ...e, password: undefined })); }}
              placeholder="••••••••••"
              placeholderTextColor="#cbd5e1"
              secureTextEntry={!showPwd}
              onSubmitEditing={handleLogin}
            />
            <TouchableOpacity onPress={() => setShowPwd(v => !v)}>
              <Ionicons name={showPwd ? "eye-off-outline" : "eye-outline"} size={18} color="#94a3b8" />
            </TouchableOpacity>
          </View>
          {errors.password && <Text style={styles.err}>{errors.password}</Text>}

          {/* Button */}
          <TouchableOpacity style={[styles.btn, loading && { opacity: 0.65 }]} onPress={handleLogin} disabled={loading}>
            {loading
              ? <ActivityIndicator color="#fff" />
              : <Text style={styles.btnText}>Sign In</Text>}
          </TouchableOpacity>

          {/* Biometric */}
          {biometricType && (
            <TouchableOpacity style={styles.bioBtn} onPress={handleBiometricLogin}>
              <Ionicons
                name={biometricType === "Face ID" ? "scan-outline" : "finger-print-outline"}
                size={18} color={BRAND}
              />
              <Text style={styles.bioText}>Sign in with {biometricType}</Text>
            </TouchableOpacity>
          )}

          {/* Demo chips */}
          <View style={styles.demoBox}>
            <Text style={styles.demoTitle}>Demo Accounts</Text>
            <View style={styles.chips}>
              {ROLE_DEMO.map(d => (
                <TouchableOpacity key={d.role} style={styles.chip}
                  onPress={() => { setEmail(d.email); setPassword(d.password); setErrors({}); }}>
                  <Text style={styles.chipText}>{d.role}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </View>

        <Text style={styles.footer}>© {new Date().getFullYear()} EduSphere</Text>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#312e81" },
  scroll: { flexGrow: 1, alignItems: "center", paddingVertical: 48, paddingHorizontal: 24 },
  logoBox: { width: 72, height: 72, borderRadius: 20, backgroundColor: "#fff", alignItems: "center", justifyContent: "center", marginBottom: 12, shadowColor: "#000", shadowOpacity: 0.2, shadowRadius: 12, elevation: 8 },
  appName: { fontSize: 28, fontWeight: "800", color: "#fff", letterSpacing: -0.5 },
  tagline: { fontSize: 13, color: "#a5b4fc", marginTop: 4, marginBottom: 32 },
  card: { width: "100%", maxWidth: 420, backgroundColor: "#fff", borderRadius: 20, padding: 28, shadowColor: "#000", shadowOpacity: 0.25, shadowRadius: 24, elevation: 12 },
  title: { fontSize: 22, fontWeight: "700", color: "#0f172a" },
  sub: { fontSize: 14, color: "#64748b", marginTop: 4, marginBottom: 24 },
  label: { fontSize: 13, fontWeight: "600", color: "#374151", marginBottom: 6 },
  labelRow: { flexDirection: "row", justifyContent: "space-between", alignItems: "center", marginBottom: 6 },
  forgot: { fontSize: 13, fontWeight: "600", color: BRAND },
  row: { flexDirection: "row", alignItems: "center", borderWidth: 1, borderColor: "#e2e8f0", borderRadius: 12, paddingHorizontal: 14, height: 48, marginBottom: 4 },
  rowError: { borderColor: "#ef4444" },
  input: { flex: 1, fontSize: 15, color: "#1e293b" },
  err: { fontSize: 12, color: "#ef4444", marginBottom: 12 },
  btn: { backgroundColor: BRAND, borderRadius: 14, height: 52, alignItems: "center", justifyContent: "center", marginTop: 12, shadowColor: BRAND, shadowOpacity: 0.4, shadowRadius: 12, elevation: 6 },
  bioBtn: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8, marginTop: 16, paddingVertical: 10, borderRadius: 12, borderWidth: 1, borderColor: "#e2e8f0" },
  bioText: { fontSize: 14, fontWeight: "600", color: BRAND },
  btnText: { color: "#fff", fontSize: 16, fontWeight: "700" },
  demoBox: { marginTop: 20, padding: 14, backgroundColor: "#eef2ff", borderRadius: 12 },
  demoTitle: { fontSize: 12, fontWeight: "700", color: BRAND, marginBottom: 8 },
  chips: { flexDirection: "row", flexWrap: "wrap", gap: 8 },
  chip: { backgroundColor: "#fff", paddingHorizontal: 14, paddingVertical: 7, borderRadius: 20, borderWidth: 1, borderColor: "#c7d2fe" },
  chipText: { fontSize: 13, fontWeight: "600", color: BRAND },
  footer: { marginTop: 28, fontSize: 12, color: "#818cf8" },
});
