import React, { useState } from "react";
import { Link } from "react-router-dom";
import { AcademicCapIcon } from "@heroicons/react/24/outline";
import { Button, Input } from "../../components/common";
import { api } from "../../api/client";
import toast from "react-hot-toast";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState(""); const [sent, setSent] = useState(false); const [loading, setLoading] = useState(false);
  const handleSubmit = async () => {
    if (!email) return;
    setLoading(true);
    try { await api.post("/auth/password-reset/", { email, reset_url: window.location.origin }); setSent(true); }
    catch { toast.error("Request failed. Please try again."); }
    finally { setLoading(false); }
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-indigo-900 to-violet-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8"><div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-white/10 mb-4"><AcademicCapIcon className="h-9 w-9 text-white"/></div><h1 className="text-3xl font-bold text-white">EduSphere</h1></div>
        <div className="rounded-2xl bg-white p-8 shadow-2xl">
          {sent ? (
            <div className="text-center py-4"><p className="text-2xl mb-2">📧</p><h2 className="text-lg font-bold text-slate-900">Check your email</h2><p className="text-sm text-slate-500 mt-2">If an account exists, you&apos;ll receive a reset link.</p><Link to="/login" className="mt-4 inline-block text-sm text-indigo-600 font-medium">← Back to login</Link></div>
          ) : (
            <>
              <h2 className="text-xl font-bold text-slate-900 mb-1">Forgot password?</h2>
              <p className="text-sm text-slate-500 mb-6">Enter your email and we&apos;ll send a reset link.</p>
              <Input label="Email address" type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="you@school.edu"/>
              <Button variant="primary" className="w-full mt-4" loading={loading} onClick={handleSubmit}>Send Reset Link</Button>
              <Link to="/login" className="block text-center mt-4 text-sm text-indigo-600">← Back to login</Link>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
