import React, { useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { AcademicCapIcon } from "@heroicons/react/24/outline";
import { Button, Input } from "../../components/common";
import { api } from "../../api/client";
import toast from "react-hot-toast";

export default function ResetPasswordPage() {
  const { token } = useParams<{token:string}>();
  const navigate = useNavigate();
  const [pw, setPw] = useState(""); const [pw2, setPw2] = useState(""); const [loading, setLoading] = useState(false);
  const handleReset = async () => {
    if (pw !== pw2) { toast.error("Passwords don't match"); return; }
    if (pw.length < 10) { toast.error("Password must be at least 10 characters"); return; }
    setLoading(true);
    try { await api.post("/auth/password-reset/confirm/", { token, new_password: pw }); toast.success("Password reset!"); navigate("/login"); }
    catch { toast.error("Reset failed. Link may have expired."); }
    finally { setLoading(false); }
  };
  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-950 via-indigo-900 to-violet-900 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        <div className="text-center mb-8"><div className="inline-flex h-16 w-16 items-center justify-center rounded-2xl bg-white/10 mb-4"><AcademicCapIcon className="h-9 w-9 text-white"/></div><h1 className="text-3xl font-bold text-white">EduSphere</h1></div>
        <div className="rounded-2xl bg-white p-8 shadow-2xl">
          <h2 className="text-xl font-bold text-slate-900 mb-1">Set new password</h2>
          <p className="text-sm text-slate-500 mb-6">Choose a strong password (min. 10 characters)</p>
          <div className="space-y-4">
            <Input label="New Password" type="password" value={pw} onChange={e=>setPw(e.target.value)} placeholder="••••••••••"/>
            <Input label="Confirm Password" type="password" value={pw2} onChange={e=>setPw2(e.target.value)} placeholder="••••••••••"/>
          </div>
          <Button variant="primary" className="w-full mt-5" loading={loading} onClick={handleReset}>Reset Password</Button>
          <Link to="/login" className="block text-center mt-4 text-sm text-indigo-600">← Back to login</Link>
        </div>
      </div>
    </div>
  );
}
