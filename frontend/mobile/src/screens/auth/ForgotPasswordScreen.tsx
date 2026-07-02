import React, { useState } from "react";
import { View, Text, StyleSheet, Alert, KeyboardAvoidingView, Platform, ScrollView } from "react-native";
import { useNavigation } from "@react-navigation/native";
import { mobileApi } from "../../api/client";
import { MobileInput, Button } from "../../components";

const BRAND = "#4F46E5";

export default function ForgotPasswordScreen() {
  const navigation = useNavigation<any>();
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);

  const handleRequest = async () => {
    if (!email.trim()) { Alert.alert("Error", "Please enter your email address."); return; }
    setLoading(true);
    try {
      await mobileApi.post("/auth/password-reset/", { email: email.trim(), reset_url: "edusphere://reset-password" });
      setSent(true);
    } catch {
      Alert.alert("Error", "Failed to send reset email. Please check the address and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView style={{ flex: 1, backgroundColor: "#312e81" }} behavior={Platform.OS === "ios" ? "padding" : undefined}>
      <ScrollView contentContainerStyle={styles.container}>
        <View style={styles.header}>
          <Text style={styles.logo}>🎓</Text>
          <Text style={styles.title}>EduSphere</Text>
          <Text style={styles.sub}>Reset Password</Text>
        </View>

        <View style={styles.card}>
          {sent ? (
            <View style={{ alignItems: "center", padding: 8 }}>
              <Text style={{ fontSize: 48, marginBottom: 12 }}>📧</Text>
              <Text style={styles.sentTitle}>Email Sent</Text>
              <Text style={styles.sentBody}>
                If an account exists for {email}, you will receive a password reset link shortly.
              </Text>
              <Button label="Back to Login" onPress={() => navigation.navigate("Login")} variant="secondary" style={{ marginTop: 20, width: "100%" }} />
            </View>
          ) : (
            <>
              <Text style={styles.cardTitle}>Forgot your password?</Text>
              <Text style={styles.cardSub}>Enter your school email and we will send you a reset link.</Text>
              <View style={{ marginTop: 20, marginBottom: 8 }}>
                <MobileInput
                  label="School Email"
                  value={email}
                  onChangeText={setEmail}
                  placeholder="you@school.edu"
                  keyboardType="email-address"
                  autoCapitalize="none"
                />
              </View>
              <Button label={loading ? "Sending…" : "Send Reset Link"} onPress={handleRequest} loading={loading} size="lg" style={{ marginTop: 4 }} />
              <Button label="Back to Login" onPress={() => navigation.goBack()} variant="ghost" style={{ marginTop: 8 }} />
            </>
          )}
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: { flexGrow: 1, justifyContent: "center", padding: 24 },
  header: { alignItems: "center", marginBottom: 28 },
  logo: { fontSize: 52, marginBottom: 8 },
  title: { fontSize: 30, fontWeight: "900", color: "#fff" },
  sub: { fontSize: 14, color: "#a5b4fc", marginTop: 4 },
  card: { backgroundColor: "#fff", borderRadius: 24, padding: 28, shadowColor: "#000", shadowOpacity: 0.25, shadowRadius: 20, elevation: 10 },
  cardTitle: { fontSize: 20, fontWeight: "800", color: "#1e293b" },
  cardSub: { fontSize: 14, color: "#64748b", marginTop: 6, lineHeight: 20 },
  sentTitle: { fontSize: 20, fontWeight: "800", color: "#1e293b", textAlign: "center" },
  sentBody: { fontSize: 14, color: "#64748b", textAlign: "center", marginTop: 8, lineHeight: 22 },
});
